"""Run:  python main.py --jd samples/job_description.txt --resume samples/sample_resume.txt"""
import sys

from resume_radar.cli import main

if __name__ == "__main__":
    sys.exit(main())
