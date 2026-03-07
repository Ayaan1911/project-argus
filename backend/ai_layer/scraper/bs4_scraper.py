"""
ai_layer/scraper/bs4_scraper.py
=================================
BeautifulSoup fallback scraper for Project Argus.

Used automatically when:
    - Playwright is not installed (ImportError)
    - Playwright fails to launch the browser
    - --scraper=bs4 flag is passed to run_scraper.py

Targets static HTML pages only. Dynamic content (JS-rendered listings)
will not be available via this scraper — results may be empty on modern SPAs.

When Playwright works, prefer it. This scraper exists to ensure the pipeline
can still collect SOME data in constrained environments (e.g. CI, low-memory).
"""

import logging
import random
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from ai_layer.config import (
    CITIES,
    LOG_PREFIX,
    MAX_PAGES,
    RATE_LIMIT_MAX,
    RATE_LIMIT_MIN,
    REQUEST_TIMEOUT,
    SCRAPER_TARGETS,
    USER_AGENT,
)
from ai_layer.scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.8,*/*;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


class BS4Scraper(BaseScraper):
    """
    Static HTML fallback scraper using requests + BeautifulSoup.

    Provides the same high-level run() interface as PlaywrightScraper so
    run_scraper.py can swap scrapers without any other code changes.
    """

    platform_source: str = "99acres-bs4"

    def run(
        self,
        cities: Optional[list[str]] = None,
        dataset_manager=None,
        max_pages: int = MAX_PAGES,
    ) -> list[dict]:
        """
        Synchronous scraping loop across all cities and platforms.

        Args:
            cities:          City list override.
            dataset_manager: DatasetManager for incremental saving.
            max_pages:       Max pages per city.

        Returns:
            Dictionary containing metrics (pages, listings, skipped, errors).
        """
        target_cities = cities or CITIES
        metrics = {
            "pages_scraped": 0,
            "listings_found": 0,
            "duplicates_skipped": 0,
            "errors": 0,
        }

        for platform_slug, url_template in SCRAPER_TARGETS.items():
            for city in target_cities:
                city_listings, city_pages, city_errors = self._scrape_city(
                    platform_slug=platform_slug,
                    url_template=url_template,
                    city=city,
                    max_pages=max_pages,
                )

                metrics["pages_scraped"] += city_pages
                metrics["errors"] += city_errors
                
                found_this_city = len(city_listings)
                metrics["listings_found"] += found_this_city

                if dataset_manager:
                    added, skipped = dataset_manager.add_listings(city_listings)
                    dataset_manager.save()
                    metrics["duplicates_skipped"] += skipped
                    
                    city_ref = city.capitalize()
                    print(f"{LOG_PREFIX} {city_ref}: {found_this_city} listings discovered")
                    if skipped > 0:
                        print(f"{LOG_PREFIX} {skipped} duplicates/invalid skipped")
                    print(f"{LOG_PREFIX} Dataset updated: {added} new entries saved")

        return metrics

    async def scrape_page(self, page_url: str, city: str) -> list[dict]:
        """
        Async-compatible wrapper — delegates to synchronous _scrape_url().
        Allows BS4Scraper to satisfy the BaseScraper abstract interface.
        """
        return self._scrape_url(page_url, city)

    def _scrape_city(
        self,
        platform_slug: str,
        url_template: str,
        city: str,
        max_pages: int,
    ) -> tuple[list[dict], int, int]:
        """Iterate through pages for a single city on a single platform."""
        city_listings: list[dict] = []
        pages_count = 0
        errors_count = 0

        for page_num in range(1, max_pages + 1):
            url = self._build_url(url_template, city, page_num)
            logger.info(f"{LOG_PREFIX} [bs4/{platform_slug}] {city} — page {page_num}: {url}")

            page_results = self._scrape_url(url, city)

            if not page_results:
                logger.info(f"{LOG_PREFIX} No listings on page {page_num} — stopping.")
                break

            city_listings.extend(page_results)
            logger.info(f"{LOG_PREFIX} Page {page_num}: {len(page_results)} listings extracted.")
            pages_count += 1

            # Rate limiting
            delay = random.uniform(RATE_LIMIT_MIN, RATE_LIMIT_MAX)
            time.sleep(delay)

        return city_listings, pages_count, errors_count

    def _scrape_url(self, url: str, city: str) -> list[dict]:
        """
        Download a single page and parse listing cards with BeautifulSoup.

        Returns an empty list if the request fails or no cards are found.
        """
        try:
            response = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as err:
            logger.warning(f"{LOG_PREFIX} Request failed for {url}: {err}")
            return []

        soup = BeautifulSoup(response.content, "lxml")
        return self._parse_cards(soup, url, city)

    def _parse_cards(self, soup: BeautifulSoup, page_url: str, city: str) -> list[dict]:
        """
        Extract listing data from parsed HTML.

        NOTE: 99acres renders most content via JavaScript, so this method
        will typically yield very few or zero cards on real pages.
        For fully JS-rendered sites, use PlaywrightScraper instead.

        The selectors below reflect the minimal static markup that may be
        present before JavaScript hydration.
        """
        listings = []

        # Try common card wrappers — 99acres uses data-label or similar attrs
        cards = (
            soup.find_all(attrs={"data-label": "srp-tuple"})
            or soup.find_all("div", class_=re.compile(r"tuple|listing|srp", re.I))
        )

        for card in cards:
            listing: dict = {
                "city": city,
            }

            # Price
            price_tag = card.find(class_=re.compile(r"price|rent", re.I))
            if price_tag:
                listing["price"] = self._parse_price(price_tag.get_text())

            # Locality
            loc_tag = card.find(class_=re.compile(r"locality|location|area", re.I))
            if loc_tag:
                listing["locality"] = loc_tag.get_text(strip=True)

            # Title → property type
            title_tag = card.find(class_=re.compile(r"title|heading|name", re.I))
            if title_tag:
                listing["property_type"] = self._parse_property_type(title_tag.get_text())

            # Description
            desc_tag = card.find(class_=re.compile(r"desc|detail|info", re.I))
            if desc_tag:
                listing["description"] = desc_tag.get_text(strip=True)

            # Images
            imgs = card.find_all("img")
            image_urls = [
                img.get("data-src") or img.get("src", "")
                for img in imgs
                if (img.get("data-src") or img.get("src", "")).startswith("http")
            ]
            listing["image_urls"] = image_urls
            listing["image_count"] = len(image_urls)

            # Phone
            phone_tag = card.find(string=re.compile(r"\d{10}"))
            listing["phone_number"] = phone_tag.strip() if phone_tag else None

            # Listing URL
            link_tag = card.find("a", href=True)
            if link_tag:
                href = link_tag["href"]
                listing["listing_url"] = (
                    href if href.startswith("http") else f"https://www.99acres.com{href}"
                )
            else:
                listing["listing_url"] = page_url

            enforced = self.enforce_schema(listing)
            if enforced:
                listings.append(enforced)

        return listings

    @staticmethod
    def _build_url(template: str, city: str, page_num: int) -> str:
        base = template.format(city=city.lower().replace(" ", "-"))
        return f"{base}?page={page_num}" if page_num > 1 else base

    @staticmethod
    def _parse_price(raw: str) -> Optional[int]:
        if not raw:
            return None
        cleaned = raw.lower().split("/")[0]
        multiplier = 1
        if 'k' in cleaned:
            multiplier = 1000
            cleaned = cleaned.replace('k', '')
        cleaned = re.sub(r"[^\d.]", "", cleaned).strip()
        try:
            if cleaned:
                return int(float(cleaned) * multiplier)
        except (ValueError, TypeError):
            pass
        return None

    @staticmethod
    def _parse_property_type(title: str) -> Optional[str]:
        match = re.search(r"(\d+)\s*BHK", title, re.IGNORECASE)
        if match:
            return f"{match.group(1)}BHK"
        return title.split()[0] if title else None
