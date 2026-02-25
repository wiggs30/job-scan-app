"""BuiltIn.com job crawler."""

from urllib.parse import urljoin

from crawlers.base import BaseCrawler, JobListing, _session, _soup, _text, _delay
from config import REQUEST_TIMEOUT


class BuiltInCrawler(BaseCrawler):
    source_name = "BuiltIn"

    def search(self, query: str, max_results: int):
        # BuiltIn has regional sites, but the main /jobs search is usually enough.
        base_url = "https://builtin.com/jobs"
        listings = []
        session = _session()
        try:
            resp = session.get(
                base_url,
                params={"search": query},
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            _delay()
        except Exception as e:
            return [
                JobListing(
                    title="(BuiltIn unavailable)",
                    company="",
                    description=f"Error: {e}",
                    url=base_url,
                    source=self.source_name,
                )
            ]

        soup = _soup(resp.text)
        cards = (
            soup.select(".job-row")
            or soup.select("article.job")
            or soup.select("[class*='job']")
            or soup.select("a[href*='/job/']")
        )
        seen_urls = set()
        for card in cards[: max_results * 2]:
            link = card if card.name == "a" else card.select_one(
                "a[href*='/job/'], a[href*='/jobs/']"
            )
            if not link:
                continue
            href = link.get("href", "")
            if href in seen_urls:
                continue
            seen_urls.add(href)
            full_url = urljoin("https://builtin.com/", href)
            title_el = card.select_one("h2, .title, .job-title, [class*='title']")
            company_el = card.select_one(".company, .company-name, [class*='company']")
            title = _text(title_el) or "Job"
            company = _text(company_el) or "Company"
            desc_el = card.select_one(".description, .snippet, [class*='description']")
            desc = _text(desc_el)
            listing = JobListing(
                title=title,
                company=company,
                description=desc,
                url=full_url,
                source=self.source_name,
            )
            if len(listings) < max_results:
                full_desc = self.fetch_description(listing)
                if full_desc:
                    listing.description = full_desc
                listings.append(listing)

        if not listings:
            listings.append(
                JobListing(
                    title=f"BuiltIn: {query}",
                    company="",
                    description="No results or page structure changed. Visit builtin.com/jobs.",
                    url=base_url,
                    source=self.source_name,
                )
            )
        return listings

    def fetch_description(self, listing: JobListing) -> str:
        if not listing.url:
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
            soup.select_one(".job-description")
            or soup.select_one("[class*='description']")
            or soup.select_one("main article")
        )
        if desc_el:
            return _text(desc_el)
        return listing.description

