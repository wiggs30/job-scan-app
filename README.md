# Job Scan – Crawl & Compare

Python Flask web application that:

1. **Crawls** job postings from **Indeed**, **LinkedIn**, **BuiltIn**, and **Google** for these categories:
   - software engineer, software developer, implementation engineer, forward deployed engineer, python developer,
     java developer, backend developer, senior software engineer, senior software developer,
     senior implementation engineer, senior python developer, senior java developer, senior backend developer
2. **Extracts** job description text from each listing.
   - On LinkedIn, it opens the job page in Playwright, clicks the **“more”** link under **“About the job”**, waits
     ~1 second, and then extracts the full description text.
3. **Runs a qualifications comparison** on [`app.jobscan.co`](https://app.jobscan.co/) using:
   - The extracted job description  
   - A **fixed resume text** (editable in `config.py`, or overridable from the UI)
4. **Produces an HTML document for human review** containing, for each job:
   - **JobScan comparison results** (match score, summary, details)
   - **Company name** that posted the job
   - **Job title**

## Setup

```bash
cd job-scan-app
python3 -m venv venv
source venv/bin/activate          # On macOS / Linux
pip install -r requirements.txt

# Install Playwright browser engines
playwright install chromium
```

## Run

```bash
cd job-scan-app
source venv/bin/activate
python app.py
```

Open `http://localhost:5000` in your browser.

- (Optional) Paste your resume text into the UI, or leave blank to use the fixed resume in `config.py`.
- Click **Run crawl & compare**. The app will:
  - Crawl the job sites and categories.
  - Extract job descriptions (including expanding LinkedIn’s “About the job” section).
  - Run a comparison on JobScan.co for each job.
  - Open a new tab with a full HTML report for human review.

You can also hit `/download` directly to trigger a crawl + compare and download the HTML report as a file.

## Configuration

- **Resume text**: Edit `config.py` → `RESUME_TEXT`, or set `JOBSCAN_RESUME_TEXT` in the environment, or paste in the UI.
- **Job categories**: `config.py` → `JOB_CATEGORIES`.
- **Crawler limits**: `MAX_JOBS_PER_CATEGORY_PER_SITE`, `MAX_JOBS_TOTAL` in `config.py`.
- **JobScan login** (optional): If JobScan requires login, set `JOBSCAN_EMAIL` and `JOBSCAN_PASSWORD` in your environment.

