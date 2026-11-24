"""Simple resume health checks (the basics recruiters and ATS software look for)."""
import re
from dataclasses import dataclass


@dataclass
class CheckItem:
    name: str
    passed: bool
    tip: str


class ResumeChecker:
    EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
    PHONE = re.compile(r"\+?\d[\d\s\-]{8,}\d")

    def check(self, text: str) -> list:
        lowered = text.lower()
        words = len(text.split())
        return [
            CheckItem("Email address", bool(self.EMAIL.search(text)),
                      "Add a professional email address at the top."),
            CheckItem("Phone number", bool(self.PHONE.search(text)),
                      "Add a phone number recruiters can call."),
            CheckItem("GitHub or LinkedIn link",
                      "github.com" in lowered or "linkedin.com" in lowered,
                      "Add your GitHub and LinkedIn links."),
            CheckItem("Skills section", "skills" in lowered,
                      "Add a clear 'Skills' section."),
            CheckItem("Projects section", "project" in lowered,
                      "Add a 'Projects' section with 2-3 projects."),
            CheckItem("Education section", "education" in lowered,
                      "Add an 'Education' section."),
            CheckItem("Sensible length (150-900 words)", 150 <= words <= 900,
                      f"Your resume has {words} words. Aim for one page (about 300-600 words)."),
        ]
