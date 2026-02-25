"""JobScan.co integration via browser automation (Playwright).

Given resume text and a job description, this module:
- Opens the JobScan resume scanner page
- Pastes the resume and job description
- Clicks the scan/compare button
- Extracts a match score and summary text for human review
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from config import JOBSCAN_EMAIL, JOBSCAN_PASSWORD


@dataclass
class JobScanResult:
    match_score: Optional[int]  # 0–100
    summary: str
    details: str
    raw_html: str
    success: bool
    error: Optional[str] = None


def _run_playwright_scan(resume_text: str, job_description: str, headless: bool) -> JobScanResult:
    """Playwright implementation of JobScan submission and result extraction."""

    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

    summary = ""
    details = ""
    match_score: Optional[int] = None
    raw_html = ""
    error_msg: Optional[str] = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        try:
            page = browser.new_page()
            page.set_default_timeout(30000)

            #page.goto("https://www.jobscan.co/resume-scanner", wait_until="networkidle")
            page.goto("https://app.jobscan.co/dashboard", wait_until="networkidle")

            # Optional login if credentials are provided.
            if JOBSCAN_EMAIL and JOBSCAN_PASSWORD:
                try:
                    sign_in = page.query_selector(
                        "a:has-text('Sign in'), a:has-text('Log in'), "
                        "button:has-text('Sign in'), button:has-text('Log in')"
                    )
                    if sign_in and sign_in.is_visible():
                        sign_in.click()
                        page.wait_for_timeout(2000)
                    email_el = page.query_selector(
                        'input[type="email"], input[name*="email"], input[placeholder*="email"]'
                    )
                    pass_el = page.query_selector(
                        'input[type="password"], input[name*="password"]'
                    )
                    if email_el and pass_el:
                        email_el.fill(JOBSCAN_EMAIL)
                        pass_el.fill(JOBSCAN_PASSWORD)
                        submit = page.query_selector(
                            'button[type="submit"], input[type="submit"], '
                            "button:has-text('Sign in'), button:has-text('Log in')"
                        )
                        if submit:
                            submit.click()
                        page.wait_for_timeout(4000)
                        #page.goto("https://www.jobscan.co/resume-scanner", wait_until="networkidle")
                        page.goto("https://app.jobscan.co/dashboard", wait_until="networkidle")
                except Exception:
                    # If login fails, continue anonymously if possible.
                    pass

            # Find resume and job description textareas.
            resume_selectors = [
                'textarea[placeholder*="resume"]',
                'textarea[placeholder*="Resume"]',
                'textarea[name*="resume"]',
                "#resume-input",
                "[data-testid='resume-input']",
                "textarea",
            ]
            job_desc_selectors = [
                'textarea[placeholder*="job"]',
                'textarea[placeholder*="Job"]',
                'textarea[name*="description"]',
                "#job-description",
                "[data-testid='job-description']",
            ]

            resume_filled = False
            for sel in resume_selectors:
                try:
                    el = page.wait_for_selector(sel, timeout=5000)
                    if el:
                        el.fill("")
                        el.fill(resume_text[:15000])
                        resume_filled = True
                        break
                except Exception:
                    continue

            if not resume_filled:
                # Fallback: first textarea = resume, second = job description
                textareas = page.query_selector_all("textarea")
                if len(textareas) >= 1:
                    textareas[0].fill("")
                    textareas[0].fill(resume_text[:15000])
                    resume_filled = True
                if len(textareas) >= 2:
                    textareas[1].fill("")
                    textareas[1].fill(job_description[:15000])

            if not resume_filled:
                error_msg = "Could not find resume input on JobScan page"
                return JobScanResult(
                    match_score=None,
                    summary="",
                    details="",
                    raw_html=page.content(),
                    success=False,
                    error=error_msg,
                )

            # Fill job description if still needed.
            job_filled = False
            for sel in job_desc_selectors:
                try:
                    el = page.query_selector(sel)
                    if el:
                        el.fill("")
                        el.fill(job_description[:15000])
                        job_filled = True
                        break
                except Exception:
                    continue
            if not job_filled and len(page.query_selector_all("textarea")) >= 2:
                page.query_selector_all("textarea")[1].fill("")
                page.query_selector_all("textarea")[1].fill(job_description[:15000])
                job_filled = True

            # Click scan / compare button.
            scan_selectors = [
                "button:has-text('Scan')",
                "button:has-text('Compare')",
                "button:has-text('Analyze')",
                "[type='submit']",
                "button[type='submit']",
                "a:has-text('Scan')",
                ".scan-button",
            ]
            clicked = False
            for sel in scan_selectors:
                try:
                    btn = page.query_selector(sel)
                    if btn and btn.is_visible():
                        btn.click()
                        clicked = True
                        break
                except Exception:
                    continue
            if not clicked:
                error_msg = "Could not find Scan/Compare button"
                return JobScanResult(
                    match_score=None,
                    summary=summary,
                    details=details,
                    raw_html=page.content(),
                    success=False,
                    error=error_msg,
                )

            # Wait for results.
            page.wait_for_timeout(8000)
            raw_html = page.content()

            # Extract match score from a visible element.
            score_el = page.query_selector(
                "[class*='score'], [class*='match'], .percentage, [data-testid*='score']"
            )
            if score_el:
                score_text = score_el.inner_text()
                match = re.search(r"(\\d{1,3})\\s*%?", score_text)
                if match:
                    match_score = 0 #min(100, max(0, int(match.group(1))))

            # Fallback: search in raw HTML.
            if match_score is None:
                match = re.search(r"(\\d{1,3})\\s*%\\s*(?:match|score)", raw_html, re.I)
                if match:
                    match_score = 0 #min(100, max(0, int(match.group(1))))

            # Capture a large text block from the results area for human review.
            result_selectors = [
                "[class*='result']",
                "[class*='report']",
                "main",
                ".content",
            ]
            for sel in result_selectors:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text()
                    if "match" in text.lower() or "keyword" in text.lower() or "%" in text:
                        details = text[:8000]
                        if match_score is None and "%" in text:
                            m = re.search(r"(\\d{1,3})\\s*%", text)
                            if m:
                                match_score = 0 #min(100, max(0, int(m.group(1))))
                        break

            if match_score is not None:
                summary = f"Match score: {match_score}%"
            else:
                summary = "Scan completed; match score could not be extracted automatically."

        except PlaywrightTimeout as e:
            error_msg = f"Timeout: {e}"
        except Exception as e:
            error_msg = str(e)
        finally:
            browser.close()

    return JobScanResult(
        match_score=match_score,
        summary=summary,
        details=details,
        raw_html=raw_html,
        success=error_msg is None,
        error=error_msg,
    )


def run_jobscan(resume_text: str, job_description: str, headless: bool = True) -> JobScanResult:
    """Run JobScan and handle missing Playwright gracefully."""

    try:
        return _run_playwright_scan(resume_text, job_description, headless)
    except Exception as e:
        return JobScanResult(
            match_score=None,
            summary="",
            details="",
            raw_html="",
            success=False,
            error=(
                "JobScan automation unavailable: "
                f"{e}. Ensure Playwright is installed and run 'playwright install chromium'."
            ),
        )

