"""Crawler registry for all supported job sites."""

from crawlers.base import BaseCrawler, JobListing  # noqa: F401
from crawlers.indeed_crawler import IndeedCrawler
from crawlers.linkedin_crawler import LinkedInCrawler
from crawlers.builtin_crawler import BuiltInCrawler
from crawlers.google_crawler import GoogleJobsCrawler


CRAWLERS = {
    "indeed": IndeedCrawler(),
    "linkedin": LinkedInCrawler(),
    "builtin": BuiltInCrawler(),
    "google": GoogleJobsCrawler(),
}

