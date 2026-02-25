"""Indeed.com crawler."""

from urllib.parse import quote_plus, urljoin

from crawlers.base import BaseCrawler, JobListing, _session, _soup, _text, _delay
from config import REQUEST_TIMEOUT


class IndeedCrawler(BaseCrawler):
    source_name = "Indeed"

    def search(self, query: str, max_results: int):
        listings = []
        session = _session()
        url = (
            "https://www.indeed.com/jobs"
            f"?q={quote_plus(query)}"
            "&l="
            "&start=0"
        )
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            _delay()
        except Exception as e:
            return [
                JobListing(
                    title="(Indeed unavailable)",
                    company="",
                    description=f"Error: {e}. Indeed may block automated requests.",
                    url=url,
                    source=self.source_name,
                )
            ]

        soup = _soup(resp.text)
        cards = soup.select('[data-jk]')
        for card in cards[:max_results]:
            jk = card.get("data-jk")
            if not jk:
                continue
            title_el = card.select_one('[data-testid="jobTitle"]') or card.select_one(".jobTitle")
            company_el = card.select_one('[data-testid="companyName"]') or card.select_one(".companyName")
            title = _text(title_el) or "Unknown Title"
            company = _text(company_el) or "Unknown Company"
            detail_url = urljoin("https://www.indeed.com/", f"/viewjob?jk={jk}")
            desc = _text(card.select_one(".job-snippet") or card.select_one(".jobSummary"))
            listing = JobListing(
                title=title,
                company=company,
                description=desc,
                url=detail_url,
                source=self.source_name,
            )
            full_desc = self.fetch_description(listing)
            if full_desc:
                listing.description = full_desc
            listings.append(listing)
        return listings

    def fetch_description(self, listing: JobListing) -> str:
        if not listing.url or "viewjob" not in listing.url:
            return listing.description
        session = _session()
        try:
            resp = session.get(listing.url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            _delay()
        except Exception:
            return listing.description
        soup = _soup(resp.text)
        desc_el = (
            soup.select_one("#jobDescriptionText")
            or soup.select_one('[data-testid="job-description"]')
            or soup.select_one(".jobsearch-JobComponent-description")
        )
        if desc_el:
            return _text(desc_el)
        return listing.description

