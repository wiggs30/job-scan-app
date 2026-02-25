"""Flask web app: crawl job sites, run JobScan comparisons, and render a reviewable report."""

from __future__ import annotations

import io
import html
from datetime import datetime
from typing import List

from flask import Flask, render_template, request, send_file

from config import RESUME_TEXT
from orchestrator import crawl_all_sites, run_comparisons, ReportRow


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB max for any uploads (future-proofing)


def report_to_html(rows: List[ReportRow], resume_preview: str) -> str:
    """Generate an HTML document suitable for human review."""

    def esc(s: str) -> str:
        return html.escape(str(s)) if s else ""

    rows_html = []
    for r in rows:
        res = r.comparison_result
        if res:
            score = f"{res.match_score}%" if res.match_score is not None else "N/A"
            summary = res.summary or ""
            details = (res.details or "")[:3000]
            if len((res.details or "")) > 3000:
                details += "... [truncated]"
            err = res.error or ""
            job_link = f"<a href=\"{r.job_url}\">Link text</a>"
        else:
            score = "N/A"
            summary = ""
            details = ""
            err = "No result"
        rows_html.append(
            f"""
            <tr>
                <td>{esc(r.job_title)}</td>
                <td>{esc(r.company)}</td>
                <td>{esc(r.source)}</td>
                <td><a href="{{ job_link }}" target="_blank" rel="noopener noreferrer">{r.job_title}</a></td>
                <td>{esc(score)}</td>
                <td>{esc(summary)}</td>
                <td><pre style="white-space:pre-wrap;max-height:200px;overflow:auto;">{esc(details)}</pre></td>
                <td>{esc(err)}</td>
            </tr>
            """
        )
    table_body = "\n".join(rows_html)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Job Scan Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px; background: #0f0f14; color: #e8e8ed; }}
        h1 {{ color: #e8e8ed; }}
        .meta {{ color: #8888a0; margin-bottom: 24px; }}
        table {{ border-collapse: collapse; width: 100%; background: #1a1a24; box-shadow: 0 1px 3px rgba(0,0,0,0.4); }}
        th, td {{ border: 1px solid #2a2a3a; padding: 10px; text-align: left; }}
        th {{ background: #11111a; color: #8888a0; }}
        tr:nth-child(even) {{ background: #14141f; }}
        pre {{ font-size: 12px; margin: 0; color: #e8e8ed; }}
        .resume-preview {{ background: #11111a; padding: 16px; margin-bottom: 24px; max-height: 200px; overflow: auto; border: 1px solid #2a2a3a; }}
    </style>
</head>
<body>
    <h1>Job Scan Comparison Report</h1>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Jobs analyzed: {len(rows)}</p>
    <h2>Resume used for comparison</h2>
    <div class="resume-preview"><pre>{html.escape(resume_preview[:2000])}</pre></div>
    <h2>Results</h2>
    <table>
        <thead>
            <tr>
                <th>Job Title</th>
                <th>Company</th>
                <th>Source</th>
                <th>Link</th>
                <th>Match Score</th>
                <th>Summary</th>
                <th>Comparison Details</th>
                <th>Error</th>
            </tr>
        </thead>
        <tbody>
            {table_body}
        </tbody>
    </table>
</body>
</html>
"""


@app.route("/")
def index():
    # UI uses the fixed resume text; user can override inline if desired.
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_scan():
    """Trigger crawl + JobScan and return an HTML report for human review."""

    # Optional override of resume text from the form; fall back to fixed config.
    resume = (request.form.get("resume_text") or RESUME_TEXT).strip() or RESUME_TEXT

    listings = crawl_all_sites()
    if not listings:
        return "No jobs found (sites may block automated requests). Try again later.", 200

    rows = run_comparisons(listings, resume_text=resume)

    html_doc = report_to_html(rows, resume_preview=resume[:3000])
    return html_doc


@app.route("/download")
def download_report():
    """Run the scan and return an HTML file attachment."""

    resume = RESUME_TEXT
    listings = crawl_all_sites()
    if not listings:
        return "No jobs found (sites may block automated requests). Try again later.", 200
    rows = run_comparisons(listings, resume_text=resume)

    html_doc = report_to_html(rows, resume_preview=resume[:3000])
    buf = io.BytesIO(html_doc.encode("utf-8"))
    return send_file(
        buf,
        mimetype="text/html",
        as_attachment=True,
        download_name=f"job-scan-report-{datetime.now().strftime('%Y%m%d-%H%M')}.html",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

