"""
ai_layer/config.py
==================
Central configuration for the Argus AI Layer.

All modules should import constants from here rather than hardcoding values.
Changing a value here propagates it across the entire pipeline automatically.

Example usage:
    from ai_layer.config import CITIES, MAX_PAGES, DATASET_PATH
"""

import pathlib
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ---------------------------------------------------------------------------
# Target cities (lowercase, used to build search URLs)
# ---------------------------------------------------------------------------
CITIES: list[str] = ["mumbai", "delhi", "bangalore"]

# ---------------------------------------------------------------------------
# Scraper targets
# Key   = platform slug (must match the platform_source field in the dataset)
# Value = URL template — use {city} placeholder, replaced at runtime
# ---------------------------------------------------------------------------
SCRAPER_TARGETS: dict[str, str] = {
    "99acres": "https://www.99acres.com/property-in-{city}-ffid",
    "magicbricks": "https://www.magicbricks.com/property-for-rent-in-{city}",
    "housing": "https://housing.com/rent/flats-in-{city}",
}

# ---------------------------------------------------------------------------
# Scraper behaviour
# ---------------------------------------------------------------------------
MAX_PAGES: int = 5          # Maximum listing pages to visit per city per platform
HEADLESS: bool = True       # Run Playwright in headless mode (set False to debug)

# Polite rate limiting — random pause (seconds) between page loads
RATE_LIMIT_MIN: float = 1.0
RATE_LIMIT_MAX: float = 3.0

# HTTP request timeout for BeautifulSoup fallback (seconds)
REQUEST_TIMEOUT: int = 15

# User-agent sent with every request
USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
# Path is relative to the backend/ directory where scripts are executed from.
# DatasetManager resolves this to an absolute path automatically.
DATASET_PATH: str = "ai_layer/datasets/listings_dataset.json"
MAX_DATASET_SIZE: int = 10000  # Protection against runaway scrapes

# Every listing record MUST contain these keys.
# DatasetManager enforces this and fills missing keys with safe defaults.
REQUIRED_KEYS: dict[str, object] = {
    "listing_id": None,  # SHA256 hash of URL for stable tracking
    "city": None,
    "locality": None,
    "price": None,
    "property_type": None,
    "description": None,
    "image_urls": [],
    "image_count": 0,
    "phone_number": None,
    "listing_url": None,
    "platform_source": None,
    "timestamp": None,
}

# ---------------------------------------------------------------------------
# Logging prefix
# ---------------------------------------------------------------------------
LOG_PREFIX: str = "[Argus Scraper]"
