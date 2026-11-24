"""Turn a MatchResult into a text, JSON or HTML report."""
import html
import json
from dataclasses import asdict


class ReportBuilder:
    def __init__(self, result, checks=None, jd_name="job description", resume_name="resume"):
        self.result = result
        self.checks = checks or []
        self.jd_name = jd_name
        self.resume_name = resume_name

    # ---------- plain text ----------
    def to_text(self) -> str:
        r = self.result
        filled = int(r.score // 5)
        bar = "#" * filled + "-" * (20 - filled)
        lines = [
            "=" * 60,
            " RESUME RADAR - match report",
            "=" * 60,
            f" Job description : {self.jd_name}",
            f" Resume          : {self.resume_name}",
            "",
            f" MATCH SCORE: {r.score}%   [{bar}]",
            f" {r.verdict}",
            "",
            f"MATCHED SKILLS ({len(r.matched)})",
        ]
        lines += [f"  + {h.name}  ({h.category})" for h in r.matched] or ["  (none)"]
        lines += ["", f"MISSING SKILLS ({len(r.missing)})  <- add these if you really have them"]
        lines += [f"  - {h.name}  ({h.category}, asked {h.jd_count}x)" for h in r.missing] or ["  (none)"]
        lines += ["", f"EXTRA SKILLS ON YOUR RESUME ({len(r.extra)})"]
        lines += [f"  * {h.name}" for h in r.extra] or ["  (none)"]

        if r.keywords:
            lines += ["", "OTHER KEYWORDS FROM THE JOB DESCRIPTION"]
            lines += [f"  [{'x' if k.in_resume else ' '}] {k.word} ({k.count}x)" for k in r.keywords]

        if self.checks:
            passed = sum(c.passed for c in self.checks)
            lines += ["", f"RESUME CHECKLIST ({passed}/{len(self.checks)} passed)"]
            for c in self.checks:
                lines.append(f"  [{'x' if c.passed else ' '}] {c.name}" + ("" if c.passed else f"  -> {c.tip}"))
        lines += ["", "Tip: only add a skill to your resume if you can talk about it in an interview.", ""]
        return "\n".join(lines)

    # ---------- JSON ----------
    def to_dict(self) -> dict:
        return {
            "job_description": self.jd_name,
            "resume": self.resume_name,
            "result": asdict(self.result),
            "checks": [asdict(c) for c in self.checks],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    # ---------- HTML ----------
    def to_html(self) -> str:
        r = self.result
        e = html.escape

        def chips(items, css, label=lambda h: h.name):
            return "".join(f'<span class="chip {css}">{e(label(h))}</span>' for h in items) \
                or '<span class="muted">none</span>'

        keyword_rows = "".join(
            f'<span class="chip {"good" if k.in_resume else "bad"}">{e(k.word)} ({k.count}x)</span>'
            for k in r.keywords) or '<span class="muted">none</span>'
        check_rows = "".join(
            f'<li class="{"ok" if c.passed else "no"}">{"&#10003;" if c.passed else "&#10007;"} {e(c.name)}'
            f'{"" if c.passed else " &mdash; " + e(c.tip)}</li>' for c in self.checks)
        color = "#2e7d32" if r.score >= 80 else "#f9a825" if r.score >= 50 else "#c62828"

        return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Resume Radar report</title>
<style>
 body {{ font-family: Segoe UI, Arial, sans-serif; background:#f4f6f8; color:#222; margin:0; padding:24px; }}
 .card {{ max-width:820px; margin:0 auto 18px; background:#fff; border-radius:12px; padding:22px 26px;
          box-shadow:0 1px 4px rgba(0,0,0,.12); }}
 h1 {{ margin:0 0 4px; }} h2 {{ margin:0 0 12px; font-size:1.05rem; }}
 .score {{ font-size:3rem; font-weight:700; color:{color}; }}
 .bar {{ height:14px; background:#e0e0e0; border-radius:7px; overflow:hidden; margin:8px 0; }}
 .bar > div {{ height:100%; width:{r.score}%; background:{color}; }}
 .chip {{ display:inline-block; padding:4px 11px; margin:3px; border-radius:14px; font-size:.9rem; }}
 .good {{ background:#e8f5e9; color:#1b5e20; }} .bad {{ background:#ffebee; color:#b71c1c; }}
 .neutral {{ background:#e3f2fd; color:#0d47a1; }} .muted {{ color:#777; }}
 ul {{ list-style:none; padding:0; margin:0; }} li {{ padding:4px 0; }}
 li.ok {{ color:#1b5e20; }} li.no {{ color:#b71c1c; }}
</style></head><body>
<div class="card"><h1>Resume Radar</h1>
 <div class="muted">{e(self.jd_name)} &nbsp;vs&nbsp; {e(self.resume_name)}</div>
 <div class="score">{r.score}%</div><div class="bar"><div></div></div>
 <strong>{e(r.verdict)}</strong></div>
<div class="card"><h2>Matched skills ({len(r.matched)})</h2>{chips(r.matched, "good")}</div>
<div class="card"><h2>Missing skills ({len(r.missing)})</h2>{chips(r.missing, "bad")}
 <p class="muted">Add these only if you really have them.</p></div>
<div class="card"><h2>Extra skills on your resume ({len(r.extra)})</h2>{chips(r.extra, "neutral")}</div>
<div class="card"><h2>Other keywords from the job description</h2>{keyword_rows}</div>
<div class="card"><h2>Resume checklist</h2><ul>{check_rows}</ul></div>
</body></html>"""
