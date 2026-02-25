"""Base crawler interface and shared helpers for all job sites."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT, CRAWL_DELAY


@dataclass
class JobListing:
    """Single job listing with fields needed for JobScan and reporting."""

    title: str
    company: str
    description: str
    url: str
    source: str  # indeed, linkedin, builtin, google


def _session() -> requests.Session:
    """Requests session with browser-like headers to reduce blocking."""

    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return s


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def _text(elem) -> str:
    if elem is None:
        return ""
    return " ".join(elem.get_text(strip=True).split())


def _delay():
    time.sleep(CRAWL_DELAY)


class BaseCrawler(ABC):
    """Abstract base for site-specific crawlers."""

    source_name: str = "base"

    @abstractmethod
    def search(self, query: str, max_results: int) -> List[JobListing]:
        """Search for jobs and return a list of JobListing."""
        raise NotImplementedError

    @abstractmethod
    def fetch_description(self, listing: JobListing) -> str:
        """Fetch full job description for a listing (if not already in listing)."""
        raise NotImplementedError

