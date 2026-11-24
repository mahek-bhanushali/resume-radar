import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resume_radar.catalog import SkillCatalog  # noqa: E402
from resume_radar.checker import ResumeChecker  # noqa: E402
from resume_radar.cli import main  # noqa: E402
from resume_radar.documents import read_document  # noqa: E402
from resume_radar.matcher import ResumeMatcher, skill_weight  # noqa: E402
from resume_radar.report import ReportBuilder  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
JD = ROOT / "my_files" / "job_description.txt"
RESUME = ROOT / "my_files" / "mahek_resume.txt"


@pytest.fixture(scope="module")
def catalog():
    return SkillCatalog.from_json()


def test_catalog_finds_skills_and_aliases(catalog):
    found = catalog.find("I know Python3, object-oriented programming and RESTful APIs.")
    assert {"Python", "OOP", "REST APIs"} <= set(found)


def test_sql_is_not_found_inside_mysql(catalog):
    found = catalog.find("Experience with MySQL")
    assert "MySQL" in found and "SQL" not in found


def test_git_is_not_found_inside_github(catalog):
    found = catalog.find("Projects on GitHub")
    assert "GitHub" in found and "Git" not in found


def test_symbol_skills_like_cpp(catalog):
    assert "C++" in catalog.find("Languages: C++, Java")


def test_counts_repeated_mentions(catalog):
    assert catalog.find("Python, python and PYTHON")["Python"] == 3


def test_skill_weight_grows_then_caps():
    assert [skill_weight(n) for n in (1, 2, 3, 10)] == [1.0, 1.5, 2.0, 2.0]


def test_matcher_matched_and_missing():
    result = ResumeMatcher().match("We need Python, Django and SQL.", "I know Python and SQL.")
    assert {h.name for h in result.matched} == {"Python", "SQL"}
    assert {h.name for h in result.missing} == {"Django"}
    assert result.score == 66.7


def test_perfect_and_zero_scores():
    matcher = ResumeMatcher()
    assert matcher.match("Python SQL", "python, sql").score == 100.0
    assert matcher.match("Python SQL", "I cook pasta").score == 0.0


def test_jd_without_known_skills_does_not_crash():
    result = ResumeMatcher().match("Must love tea.", "I know Python")
    assert result.score == 0.0
    assert "No known skills" in result.verdict


def test_sample_files_give_a_good_match():
    matcher = ResumeMatcher()
    result = matcher.match(read_document(JD), read_document(RESUME))
    assert result.score >= 70
    assert "Django" in {h.name for h in result.missing}
    assert "Python" in {h.name for h in result.matched}


def test_keywords_report_whether_resume_has_them():
    result = ResumeMatcher().match("Looks for dashboards storytelling storytelling", "storytelling")
    words = {k.word: k for k in result.keywords}
    assert words["storytelling"].in_resume is True
    assert words["storytelling"].count == 2


def test_checker_passes_good_resume_and_flags_bad_one():
    good = ResumeChecker().check(read_document(RESUME))
    assert all(item.passed for item in good)
    bad = ResumeChecker().check("hello")
    assert not any(item.passed for item in bad)


def test_reports_have_expected_content():
    result = ResumeMatcher().match(read_document(JD), read_document(RESUME))
    report = ReportBuilder(result, ResumeChecker().check(read_document(RESUME)))
    assert "MATCH SCORE" in report.to_text()
    assert "<html" in report.to_html()
    assert json.loads(report.to_json())["result"]["score"] == result.score


def test_html_report_escapes_text():
    result = ResumeMatcher().match("Python", "Python")
    report = ReportBuilder(result, jd_name="<script>alert(1)</script>")
    assert "<script>alert(1)</script>" not in report.to_html()


def test_read_document_errors(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_document(tmp_path / "missing.txt")
    bad = tmp_path / "resume.docx"
    bad.write_text("x")
    with pytest.raises(ValueError):
        read_document(bad)


def test_cli_end_to_end(tmp_path, capsys):
    html_file = tmp_path / "out" / "report.html"
    code = main(["--jd", str(JD), "--resume", str(RESUME), "--html", str(html_file)])
    assert code == 0
    assert html_file.exists()
    assert "MATCH SCORE" in capsys.readouterr().out


def test_cli_missing_file_returns_error(capsys):
    assert main(["--jd", "nope.txt", "--resume", str(RESUME)]) == 1
