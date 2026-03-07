"""
ai_layer/scraper/base_scraper.py
=================================
Abstract base class for all Argus scrapers.

Every scraper (Playwright, BeautifulSoup, or any future driver) must
inherit from BaseScraper and implement the `scrape_page` coroutine.

The contract guarantees:
    - Returned dicts always include REQUIRED_KEYS from ai_layer.config
    - Missing fields are filled with safe defaults (enforced by DatasetManager)
    - platform_source and timestamp are always set at the scraper level
"""

import abc
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from ai_layer.config import REQUIRED_KEYS, LOG_PREFIX

logger = logging.getLogger(__name__)

# IST offset (+05:30)
_IST = timezone(timedelta(hours=5, minutes=30))


class BaseScraper(abc.ABC):
    """
    Abstract scraper interface.

    Subclasses must implement:
        - scrape_page(page_url, city) -> list[dict]

    Subclasses may optionally override:
        - build_search_url(city, page_num) -> str
    """

    #: Override in each subclass to identify the data source
    platform_source: str = "unknown"

    def now_iso(self) -> str:
        """Return the current IST time in ISO 8601 format."""
        return datetime.now(_IST).isoformat()

    def _generate_listing_id(self, listing_url: str) -> str:
        """Generates a stable SHA256 hash based on the listing URL."""
        if not listing_url:
            return "unknown"
        return hashlib.sha256(listing_url.encode()).hexdigest()

    def enforce_schema(self, listing: dict[str, Any]) -> dict[str, Any]:
        """
        Ensure every listing has exactly the required keys.

        Missing keys are filled with safe defaults from REQUIRED_KEYS.
        Extra keys are preserved (they do no harm and may be useful later).

        Args:
            listing: Raw listing dict from a scraper.

        Returns:
            Dict guaranteed to contain all keys in REQUIRED_KEYS.
        """
        complete = {}
        for key, default in REQUIRED_KEYS.items():
            # Lists are mutable defaults — always copy to avoid aliasing
            complete[key] = listing.get(key, list(default) if isinstance(default, list) else default)

        # Carry over any extra fields the individual scraper may have captured
        for key, value in listing.items():
            if key not in complete:
                complete[key] = value

        # Always stamp platform_source and timestamp
        complete.setdefault("platform_source", self.platform_source)
        complete.setdefault("timestamp", self.now_iso())

        # --- PART 2: Stable Listing ID ---
        url = complete.get("listing_url")
        if not url or url == "Unknown":
            # Part 2 rule: If listing_url is missing -> reject the listing (signal by returning None or raising)
            # We'll return None here and let the caller handle it.
            logger.warning("Rejecting listing — missing listing_url")
            return None

        if not complete.get("listing_id") or complete["listing_id"] == "Unknown":
            complete["listing_id"] = self._generate_listing_id(url)

        return complete

    @abc.abstractmethod
    async def scrape_page(self, page_url: str, city: str) -> list[dict]:
        """
        Scrape a single listing results page.

        Args:
            page_url: Full URL of the search results page.
            city:     City name (lowercase), e.g. "mumbai".

        Returns:
            List of listing dicts, each containing the fields defined in
            REQUIRED_KEYS (enforced by enforce_schema before returning).
        """
        ...

    def build_search_url(self, city: str, page_num: int = 1) -> str:
        """
        Build a paginated search URL for the given city.

        Default implementation raises NotImplementedError.
        Subclasses that support pagination should override this.

        Args:
            city:     City name (lowercase).
            page_num: 1-indexed page number.

        Returns:
            Full URL string.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement build_search_url(). "
            "Override this method to enable pagination."
        )
