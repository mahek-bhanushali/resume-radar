"""Command-line interface."""
import argparse
import sys
from pathlib import Path

from .checker import ResumeChecker
from .documents import read_document
from .matcher import ResumeMatcher
from .report import ReportBuilder


def build_parser():
    parser = argparse.ArgumentParser(
        prog="resume-radar",
        description="Compare your resume with a job description and see matching and missing skills.")
    parser.add_argument("--jd", required=True, help="job description file (.txt, .md or .pdf)")
    parser.add_argument("--resume", required=True, help="resume file (.txt, .md or .pdf)")
    parser.add_argument("--html", metavar="FILE", help="also save an HTML report")
    parser.add_argument("--json", metavar="FILE", help="also save a JSON report")
    parser.add_argument("--keywords", type=int, default=10, help="how many extra keywords to show")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        jd_text = read_document(args.jd)
        resume_text = read_document(args.resume)
    except (FileNotFoundError, ValueError, RuntimeError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    result = ResumeMatcher().match(jd_text, resume_text, top_keywords=args.keywords)
    report = ReportBuilder(result, ResumeChecker().check(resume_text),
                           jd_name=Path(args.jd).name, resume_name=Path(args.resume).name)
    print(report.to_text())

    for path, content in ((args.html, report.to_html), (args.json, report.to_json)):
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content(), encoding="utf-8")
            print(f"Saved: {path}")
    return 0
