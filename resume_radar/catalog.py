"""Skill catalog: knows which skills exist and how to spot them in text."""
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CATALOG = Path(__file__).parent / "data" / "skills.json"

# A skill must not be glued to other letters/digits (so "sql" does not match inside
# "mysql", and "git" does not match inside "github"). '+' and '#' are included so that
# "c++" and "c#" are treated as whole words.
_BOUNDARY_BEFORE = r"(?<![A-Za-z0-9+#])"
_BOUNDARY_AFTER = r"(?![A-Za-z0-9+#])"


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    aliases: tuple = ()

    def all_names(self):
        """Canonical name plus aliases, longest first so long phrases win."""
        names = {self.name.lower(), *(a.lower() for a in self.aliases)}
        return sorted(names, key=len, reverse=True)


class SkillCatalog:
    def __init__(self, skills):
        self.skills = list(skills)
        self._patterns = []
        for skill in self.skills:
            alternatives = "|".join(re.escape(n) for n in skill.all_names())
            pattern = re.compile(
                f"{_BOUNDARY_BEFORE}(?:{alternatives}){_BOUNDARY_AFTER}", re.IGNORECASE)
            self._patterns.append((skill, pattern))

    @classmethod
    def from_json(cls, path=DEFAULT_CATALOG):
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(Skill(s["name"], s["category"], tuple(s.get("aliases", []))) for s in raw)

    def find(self, text: str) -> Counter:
        """Return {skill name: number of times it appears in text}."""
        found = Counter()
        for skill, pattern in self._patterns:
            count = len(pattern.findall(text))
            if count:
                found[skill.name] = count
        return found

    def category_of(self, name: str) -> str:
        for skill in self.skills:
            if skill.name == name:
                return skill.category
        return "Other"

    def known_words(self) -> set:
        """Every single word used by any skill or alias (used to skip them as 'extra keywords')."""
        words = set()
        for skill in self.skills:
            for name in skill.all_names():
                words.update(re.findall(r"[a-z]+", name))
        return words
