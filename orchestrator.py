"""Orchestrator: run crawlers across all job categories, then JobScan for each job."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from config import JOB_CATEGORIES, MAX_JOBS_PER_CATEGORY_PER_SITE, MAX_JOBS_TOTAL, RESUME_TEXT
from crawlers import CRAWLERS
from crawlers.base import JobListing
from jobscan_client import run_jobscan, JobScanResult


@dataclass
class ReportRow:
    job_title: str
    company: str
    source: str
    comparison_result: Optional[JobScanResult]
    job_url: str = ""


def crawl_all_sites() -> List[JobListing]:
    """Run all crawlers for all job categories, dedupe by (title, company, source), cap total."""

    seen = set()
    out: List[JobListing] = []

    for source_name, crawler in CRAWLERS.items():
        for query in JOB_CATEGORIES:
            if len(out) >= MAX_JOBS_TOTAL:
                break
            try:
                listings = crawler.search(query, max_results=MAX_JOBS_PER_CATEGORY_PER_SITE)
                for job in listings:
                    key = (job.title.strip().lower(), job.company.strip().lower(), job.source)
                    if key in seen:
                        continue
                    seen.add(key)
                    if job.title and "(unavailable)" not in job.title.lower():
                        out.append(job)
                        if len(out) >= MAX_JOBS_TOTAL:
                            break
            except Exception:
                # If a crawler fails, skip it so others can still run.
                continue
        if len(out) >= MAX_JOBS_TOTAL:
            break

    return out


def run_comparisons(
    listings: List[JobListing],
    resume_text: str = RESUME_TEXT,
) -> List[ReportRow]:
    """Run JobScan for each listing and build report rows."""

    """We'll skip the jobscan report for now until a future date"""
    rows: List[ReportRow] = []
    for job in listings:
        desc = (job.description or "").strip()
        """
        if len(desc) < 50:
            result = JobScanResult(
                match_score=None,
                summary="Job description too short to scan",
                details="",
                raw_html="",
                success=False,
                error="Description length < 50 characters",
            )
        
        else:
            result = run_jobscan(resume_text, desc, headless=True)
        """
        ### Temporary replacement until jobscan works ###
        result = JobScanResult(
                match_score=None,
                summary="Jobscan not being used now",
                details="",
                raw_html="",
                success=True,
                error="Jobscan not being used now",
            )
        rows.append(
            ReportRow(
                job_title=job.title,
                company=job.company,
                source=job.source,
                comparison_result=result,
                job_url=job.url or "",
            )
        )
    return rows

