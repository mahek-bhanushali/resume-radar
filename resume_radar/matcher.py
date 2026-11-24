"""Core logic: compare the skills a job asks for with the skills a resume shows."""
import re
from dataclasses import dataclass, field

from .catalog import SkillCatalog

STOPWORDS = set("""
a an and are as at be been by can for from has have in into is it its of on or our that the
their this to was we will with you your who which where when while within without should must
also etc per over under than then them they such other more most some any all each both via
work works working good knowledge skills skill required requirements responsibilities
eligibility location experience job develop developing development use using used handle
handling basic familiarity understanding assist assisting freshers fresher students student
year years apply applying degree related team intern internship role candidate candidates
ability strong excellent preferred plus including include includes like new able make making
based looking join company position opportunity person people part full time person
final concepts applications scripts maintain developer
""".split())


@dataclass
class SkillHit:
    name: str
    category: str
    jd_count: int
    resume_count: int


@dataclass
class KeywordHit:
    word: str
    count: int
    in_resume: bool


@dataclass
class MatchResult:
    score: float
    verdict: str
    matched: list = field(default_factory=list)       # in JD and resume
    missing: list = field(default_factory=list)       # in JD, not in resume
    extra: list = field(default_factory=list)         # in resume only
    keywords: list = field(default_factory=list)      # other words from the JD


def skill_weight(jd_count: int) -> float:
    """A skill the job mentions several times matters more (1.0, 1.5, then 2.0)."""
    return 1.0 + 0.5 * min(jd_count - 1, 2)


def verdict_for(score: float, jd_skill_count: int) -> str:
    if jd_skill_count == 0:
        return "No known skills found in the job description"
    if score >= 80:
        return "Strong match - apply with confidence"
    if score >= 60:
        return "Good match - add the missing skills you really have"
    if score >= 40:
        return "Partial match - build or show a few more of the required skills"
    return "Low match - this role needs skills your resume does not show yet"


class ResumeMatcher:
    def __init__(self, catalog: SkillCatalog = None):
        self.catalog = catalog or SkillCatalog.from_json()

    def match(self, jd_text: str, resume_text: str, top_keywords: int = 10) -> MatchResult:
        jd_skills = self.catalog.find(jd_text)
        resume_skills = self.catalog.find(resume_text)

        matched, missing = [], []
        for name, jd_count in jd_skills.most_common():
            hit = SkillHit(name, self.catalog.category_of(name), jd_count,
                           resume_skills.get(name, 0))
            (matched if hit.resume_count else missing).append(hit)

        extra = [SkillHit(name, self.catalog.category_of(name), 0, count)
                 for name, count in resume_skills.most_common() if name not in jd_skills]

        total_weight = sum(skill_weight(h.jd_count) for h in matched + missing)
        got_weight = sum(skill_weight(h.jd_count) for h in matched)
        score = round(100 * got_weight / total_weight, 1) if total_weight else 0.0

        return MatchResult(
            score=score,
            verdict=verdict_for(score, len(jd_skills)),
            matched=matched,
            missing=missing,
            extra=extra,
            keywords=self.extra_keywords(jd_text, resume_text, top_keywords),
        )

    def extra_keywords(self, jd_text, resume_text, limit=10):
        """Frequent words in the job description that are not known skills."""
        skip = STOPWORDS | self.catalog.known_words()
        # hyphenated words such as "problem-solving" are skipped when every part is known
        jd_words = [w for w in self._words(jd_text)
                    if not all(part in skip for part in w.split("-"))]
        counts = {}
        for word in jd_words:
            counts[word] = counts.get(word, 0) + 1
        resume_words = set(self._words(resume_text))
        top = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
        return [KeywordHit(word, count, word in resume_words) for word, count in top]

    @staticmethod
    def _words(text: str):
        return re.findall(r"[a-z][a-z\-]{2,}", text.lower())
