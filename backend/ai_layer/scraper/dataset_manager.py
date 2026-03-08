"""
ai_layer/scraper/dataset_manager.py
=====================================
Manages the lifecycle of the scraped listings dataset.

Responsibilities:
    - Load existing listings from listings_dataset.json on startup
    - Enforce the dataset schema (fills missing keys with safe defaults)
    - Deduplicate listings by listing_url
    - Save incrementally (after each city batch, not just at the end)
    - Emit structured log output after every save

Log format:
    [Argus Scraper] {City}: {N} listings scraped
    [Argus Scraper] {D} duplicates skipped
    [Argus Scraper] Dataset updated: {A} new entries saved

Usage:
    dm = DatasetManager()
    added, skipped = dm.add_listings(city_listings)
    dm.save()
    print(f"Saved {dm.dataset_path}")
"""

import json
import logging
import pathlib
from typing import Any, Optional

from ai_layer.config import DATASET_PATH, LOG_PREFIX, REQUIRED_KEYS, MAX_DATASET_SIZE

logger = logging.getLogger(__name__)


class DatasetManager:
    """
    Persistent, deduplicating store for scraped rental listings.

    All listings are keyed by their listing_url for deduplication.
    Entries missing required fields are automatically normalised on ingest.
    """

    # Mutable default values keyed by field name — used for normalisation
    _SAFE_DEFAULTS: dict[str, Any] = REQUIRED_KEYS

    def __init__(self, path: Optional[pathlib.Path] = None):
        """
        Initialise the DatasetManager and load any existing data.

        Args:
            path: Override the dataset file path (useful for testing).
                  Defaults to ai_layer/config.DATASET_PATH.
        """
        if path is None:
            # Resolve relative to wherever the process is run from (backend/)
            self.dataset_path = pathlib.Path(DATASET_PATH).resolve()
        else:
            self.dataset_path = pathlib.Path(path).resolve()

        # Internal store: listing_url → listing dict
        self._store: dict[str, dict] = {}

        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def listings(self) -> list[dict]:
        """Return all stored listings as a list (order mirrors insertion order)."""
        return list(self._store.values())

    def add_listing(self, listing: dict) -> bool:
        """
        Add a single listing to the store.

        Args:
            listing: Raw listing dict (will be normalised before storing).

        Returns:
            True if the listing was new and added; False if it was a duplicate or invalid.
        """
        # --- PART 5: Dataset Size Protection ---
        if len(self._store) >= MAX_DATASET_SIZE:
            logger.warning(f"{LOG_PREFIX} Dataset size limit reached ({MAX_DATASET_SIZE}) — stopping scrape.")
            return False

        normalised = self._normalise(listing)
        
        # --- PART 4: Listing Validation ---
        if not self.validate_listing(normalised):
            return False

        key = normalised.get("listing_url")
        if not key or key == "Unknown":
            logger.debug(f"{LOG_PREFIX} Listing has no listing_url — skipping.")
            return False

        if key in self._store:
            return False  # Duplicate

        self._store[key] = normalised
        return True

    def validate_listing(self, listing: dict) -> bool:
        """
        Apply Part 4 validation rules:
        - price > 0
        - listing_url exists
        - description length >= 10 characters
        """
        # 1. URL exists (already checked in base_scraper and add_listing, but for safety)
        url = listing.get("listing_url")
        if not url or url == "Unknown":
            logger.warning(f"{LOG_PREFIX} Rejected listing — missing listing_url.")
            return False

        # 2. Price > 0
        price = listing.get("price")
        try:
            if price is None or int(price) <= 0:
                logger.warning(f"{LOG_PREFIX} Rejected listing — invalid price ({price}).")
                return False
        except (ValueError, TypeError):
            logger.warning(f"{LOG_PREFIX} Rejected listing — non-numeric price.")
            return False

        # 3. Description length >= 10
        description = listing.get("description", "")
        if len(description) < 10:
            logger.warning(f"{LOG_PREFIX} Rejected listing — description too short (< 10 chars).")
            return False

        return True

    def add_listings(self, listings: list[dict]) -> tuple[int, int]:
        """
        Add multiple listings and return (added_count, skipped_count).

        Args:
            listings: List of raw listing dicts.

        Returns:
            (added, skipped) tuple.
        """
        added = 0
        skipped = 0
        for listing in listings:
            if self.add_listing(listing):
                added += 1
            else:
                skipped += 1
        return added, skipped

    def save(self) -> None:
        """
        Persist the current dataset to disk as a formatted JSON file.

        Creates parent directories automatically if they don't exist.
        Writes atomically via a temp file to prevent partial writes.
        """
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to a temp file first, then rename (atomic on most OS)
        tmp_path = self.dataset_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self.listings, f, ensure_ascii=False, indent=2)
        tmp_path.replace(self.dataset_path)

        logger.info(f"{LOG_PREFIX} Saved {len(self._store)} total listings → {self.dataset_path}")

    def total(self) -> int:
        """Return the total number of listings currently in the store."""
        return len(self._store)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load existing listings from the dataset file, if it exists."""
        if not self.dataset_path.exists():
            logger.info(f"{LOG_PREFIX} No existing dataset at {self.dataset_path} — starting fresh.")
            return

        try:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                raw_list: list[dict] = json.load(f)

            for item in raw_list:
                normalised = self._normalise(item)
                key = normalised.get("listing_url")
                if key:
                    self._store[key] = normalised

            logger.info(f"{LOG_PREFIX} Loaded {len(self._store)} existing listings from disk.")

        except (json.JSONDecodeError, OSError) as err:
            logger.error(f"{LOG_PREFIX} Failed to load dataset: {err}. Starting with empty store.")
            self._store = {}

    def _normalise(self, listing: dict) -> dict:
        """
        Ensure the listing contains all REQUIRED_KEYS with safe defaults.

        Extra keys (e.g. scrape_method) are preserved.

        Args:
            listing: Raw or partial listing dict.

        Returns:
            Fully normalised listing dict.
        """
        result: dict[str, Any] = {}

        for key, default in self._SAFE_DEFAULTS.items():
            value = listing.get(key)
            if value is None:
                # Use a copy for mutable defaults (lists)
                result[key] = list(default) if isinstance(default, list) else default
            else:
                result[key] = value

        # Derive image_count from image_urls if not explicitly set
        if result.get("image_count") == 0 and result.get("image_urls"):
            result["image_count"] = len(result["image_urls"])

        # Preserve any extra fields
        for key, value in listing.items():
            if key not in result:
                result[key] = value

        return result
