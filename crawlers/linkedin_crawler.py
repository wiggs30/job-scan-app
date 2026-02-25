"""LinkedIn.com crawler.

LinkedIn heavily restricts scraping and may require login/JavaScript. This crawler
uses a best-effort approach and is intended for personal experimentation only.

To extract the full job description we:
- Open the job detail page with Playwright
- Click a "more" button under the "About the job" section
- Wait ~1 second for the full text to load
"""

from urllib.parse import quote_plus

from crawlers.base import BaseCrawler, JobListing, _session, _soup, _text, _delay
from config import REQUEST_TIMEOUT


class LinkedInCrawler(BaseCrawler):
    source_name = "LinkedIn"

    def search(self, query: str, max_results: int):
        # Public job search URL; LinkedIn may change this frequently.
        url = (
            "https://www.linkedin.com/jobs/search-results/"
            #f"?keywords={quote_plus(query)}"
            f"?keywords=software engineer"
            #"&location="
            "&origin=JOB_SEARCH_PAGE_JOB_FILTER"
            "&geoId=102571732"
            "&distance=5"
            "&position=1"
            "&pageNum=0"
            "&f_TPR=r86400"
        )
        listings = []
        session = _session()
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            _delay()
        except Exception as e:
            return [
                JobListing(
                    title="(LinkedIn unavailable)",
                    company="",
                    description=f"Error: {e}. LinkedIn often blocks or requires login.",
                    url=url,
                    source=self.source_name,
                )
            ]

        soup = _soup(resp.text)
        cards = (
            soup.select(".base-card")
            or soup.select('[data-job-id]')
            or soup.select(".job-search-card")
        )
        for card in cards[:max_results]:
            link = card.select_one("a.base-card__full-link") or card.select_one(
                "a[href*='/jobs/view/']"
            )
            if not link:
                continue
            href = link.get("href", "")
            title_el = card.select_one(".base-search-card__title") or card.select_one(".job-title")
            company_el = card.select_one(".base-search-card__subtitle") or card.select_one(
                ".company-name"
            )
            title = _text(title_el) or "Unknown Title"
            company = _text(company_el) or "Unknown Company"
            snippet = card.select_one(".base-search-card__snippet") or card.select_one(".job-snippet")
            desc = _text(snippet)
            job_url = href.split("?")[0] if href else ""
            listing = JobListing(
                title=title,
                company=company,
                description=desc,
                url=job_url,
                source=self.source_name,
            )
            if job_url:
                full_desc = self.fetch_description(listing)
                if full_desc:
                    listing.description = full_desc
                _delay()
            listings.append(listing)

        if not listings:
            listings.append(
                JobListing(
                    title=f"LinkedIn jobs: {query}",
                    company="(search manually for more details)",
                    description="LinkedIn limits automated access. Open the URL to see jobs.",
                    url=url,
                    source=self.source_name,
                )
            )
        return listings

    def fetch_description(self, listing: JobListing) -> str:
        """Use Playwright to expand 'About the job' and extract full description."""

        if not listing.url or "linkedin.com" not in listing.url:
            return listing.description

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            # Playwright not installed; fall back to snippet.
            return listing.description

        full_text = ""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.set_default_timeout(REQUEST_TIMEOUT * 1000)
                page.goto(listing.url, wait_until="domcontentloaded")

                # Give the page a moment to render.
                page.wait_for_timeout(2000)

                # Click "more" under "About the job"
                more_selectors = [
                    "button:has-text('Show more')",
                    "button:has-text('more')",
                    "span:has-text('Show more')",
                    "a:has-text('Show more')",
                    "[aria-label*='more']",
                    ".show-more-less-html__button--more",
                    ".show-more-less-html__button",
                ]
                for sel in more_selectors:
                    try:
                        el = page.query_selector(sel)
                        if el and el.is_visible():
                            el.click()
                            # Wait ~1 second for content to expand as requested.
                            page.wait_for_timeout(1000)
                            break
                    except Exception:
                        continue

                # Extract text under "About the job" / main description container.
                desc_selectors = [
                    "section.jobs-description",
                    ".jobs-description__content",
                    ".jobs-box__html-content",
                    "[class*='description__content']",
                    "[class*='job-details']",
                    ".show-more-less-html__full-content",
                    "main .jobs-description",
                ]
                for sel in desc_selectors:
                    el = page.query_selector(sel)
                    if el:
                        text = el.inner_text()
                        if text:
                            full_text = " ".join(text.split())
                        if len(full_text) > 100:
                            break

                if not full_text:
                    main = page.query_selector("main")
                    if main:
                        full_text = " ".join(main.inner_text().split())
            except Exception:
                pass
            finally:
                browser.close()

        return full_text or listing.description

