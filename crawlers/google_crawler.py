"""Google.com job search crawler.

Uses standard Google search results as a very rough job signal.
"""

from urllib.parse import quote_plus

from crawlers.base import BaseCrawler, JobListing, _session, _soup, _text, _delay
from config import REQUEST_TIMEOUT


class GoogleJobsCrawler(BaseCrawler):
    source_name = "Google"

    def search(self, query: str, max_results: int):
        url = f"https://www.google.com/search?q={quote_plus(query + ' jobs')}"
        listings = []
        session = _session()
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            _delay()
        except Exception as e:
            return [
                JobListing(
                    title="(Google unavailable)",
                    company="",
                    description=f"Error: {e}",
                    url=url,
                    source=self.source_name,
                )
            ]

        soup = _soup(resp.text)
        divs = soup.select(".g")
        for g in divs[: max_results + 5]:
            link = g.select_one("a[href^='http']")
            if not link:
                continue
            href = link.get("href", "")
            if "google.com" in href or "webcache" in href or "/search" in href:
                continue
            title_el = g.select_one("h3")
            title = _text(title_el) or "Job"
            snippet = g.select_one(".VwiC3b, .s")
            desc = _text(snippet)

            company = ""
            if " - " in title:
                parts = title.split(" - ", 1)
                title = parts[0].strip()
                if len(parts) > 1:
                    company = parts[1].strip()

            listings.append(
                JobListing(
                    title=title,
                    company=company or "Various",
                    description=desc,
                    url=href,
                    source=self.source_name,
                )
            )
            if len(listings) >= max_results:
                break

        if not listings:
            listings.append(
                JobListing(
                    title=f"Google: {query} jobs",
                    company="",
                    description=(
                        "Run a Google search for job listings. "
                        "Google often requires JavaScript for the Jobs carousel."
                    ),
                    url=url,
                    source=self.source_name,
                )
            )
        return listings

    def fetch_description(self, listing: JobListing) -> str:
        # For Google results we usually only have the snippet.
        return listing.description

