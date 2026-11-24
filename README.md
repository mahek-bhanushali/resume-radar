# Resume Radar

A command-line tool that compares your **resume** with a **job description** and tells you
which skills match, which are missing, and how strong the match is. It also saves a clean
HTML or JSON report and runs a quick resume health check.

Built with plain Python (standard library only) using object-oriented design and a pytest suite.

## Features
- **Match score (0-100%)**: skills the job mentions more often count more
- **Matched / missing / extra skills**, grouped by category (Languages, Data, Databases, Tools...)
- **Smart skill detection**: understands aliases (`OOPs`, `object-oriented`, `RESTful APIs`, `Postgres`), and does not confuse `SQL` with `MySQL` or `Git` with `GitHub`
- **Other keywords** from the job description, with a check for whether your resume has them
- **Resume checklist**: email, phone, GitHub/LinkedIn link, Skills / Projects / Education sections, length
- **Reports**: terminal text, HTML page and JSON file
- Reads `.txt`, `.md` and `.pdf` files (PDF needs `pip install pypdf`)

## How it works
```
job description + resume
        |
  documents.py   -> reads the files
  catalog.py     -> finds skills using skills.json (names + aliases, whole-word matching)
  matcher.py     -> compares skills, weights them, calculates the score
  checker.py     -> resume health checks
  report.py      -> text / HTML / JSON report
  cli.py         -> command-line interface
```

## Run it
```bash
git clone https://github.com/mahek-bhanushali/resume-radar.git
cd resume-radar
python -m venv venv
venv\Scripts\activate           # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python main.py --jd samples/job_description.txt --resume samples/sample_resume.txt
```

Save an HTML report as well:
```bash
python main.py --jd samples/job_description.txt --resume samples/sample_resume.txt --html reports/report.html
```
Then open `reports/report.html` in your browser.

Use your own files: copy the job description into a `.txt` file and use your resume as `.txt` or `.pdf`.

### Options
| Option | Meaning |
|---|---|
| `--jd FILE` | job description file |
| `--resume FILE` | resume file |
| `--html FILE` | also save an HTML report |
| `--json FILE` | also save a JSON report |
| `--keywords N` | how many extra keywords to show (default 10) |

## Run the tests
```bash
pytest -v
```

## Add or change skills
Open `resume_radar/data/skills.json` and add an entry:
```json
{"name": "Streamlit", "category": "Web & APIs", "aliases": ["streamlit.io"]}
```

## Limits
This tool matches skill words, so it is a guide, not a replacement for reading the job description carefully.
Only add a skill to your resume if you can talk about it in an interview.

## Ideas to extend it
- Web interface with Flask or Streamlit
- Compare one resume against several job descriptions and rank them
- Read `.docx` resumes
