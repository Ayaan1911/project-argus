"""
ai_layer/scraper/sources/ninety_nine_acres.py
==============================================
Platform-specific parsing logic for 99acres.com.

This module is called by PlaywrightScraper for every search results page.
It isolates all 99acres HTML selectors in one place so that selector
changes only require edits here — not in the scraper orchestration layer.

Exported function:
    async def scrape_page(page, city: str) -> list[dict]
"""

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Page

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Platform identifier (must match the key in config.SCRAPER_TARGETS)
# ---------------------------------------------------------------------------
PLATFORM_SOURCE = "99acres"

# ---------------------------------------------------------------------------
# CSS selectors for 99acres search results pages
# NOTE: These selectors may need updating if 99acres changes its markup.
#       Run the scraper with HEADLESS=False to inspect the live page.
# ---------------------------------------------------------------------------
_CARD_SELECTOR = ".srpTuple, [data-label='srp-tuple']"  # Each listing card
_PRICE_SELECTOR = ".priceWithPreference"               # Rent price text
_TITLE_SELECTOR = ".srpTupleTitle"                     # Property title (type + locality)
_LOCALITY_SELECTOR = ".localityName"                   # Locality span
_DESCRIPTION_SELECTOR = ".tupleDesc"                   # Description text (may be absent)
_IMAGE_SELECTOR = "img.lazyLoad, img[data-src]"        # Listing images inside card
_PHONE_SELECTOR = "[class*='contact'], [data-label*='contact']"  # Contact button
_LINK_SELECTOR = "a.srpTupleLink, a[data-label='srp-tuple-link']"  # Card anchor


async def scrape_page(page: "Page", city: str) -> list[dict]:
    """
    Parse all listing cards on the current 99acres search results page.

    Args:
        page: Playwright Page object, already navigated to the results URL.
        city: City name (lowercase), e.g. "mumbai".

    Returns:
        List of raw listing dicts. Fields that could not be extracted are
        set to None; DatasetManager.enforce_schema() will normalise them.
    """
    listings: list[dict] = []

    try:
        # Wait for at least one listing card to appear (up to 15 s)
        await page.wait_for_selector(_CARD_SELECTOR, timeout=15_000)
    except Exception:
        logger.warning("No listing cards found on this page — may be blocked or empty.")
        return listings

    cards = await page.query_selector_all(_CARD_SELECTOR)
    logger.info(f"  Found {len(cards)} cards on page.")

    for card in cards:
        listing: dict = {"city": city, "platform_source": PLATFORM_SOURCE}

        # --- Price ---
        try:
            price_el = await card.query_selector(_PRICE_SELECTOR)
            if price_el:
                raw_price = (await price_el.inner_text()).strip()
                listing["price"] = _parse_price(raw_price)
        except Exception:
            listing["price"] = None

        # --- Property type + Locality (often combined in title) ---
        try:
            title_el = await card.query_selector(_TITLE_SELECTOR)
            if title_el:
                title_text = (await title_el.inner_text()).strip()
                listing["property_type"] = _parse_property_type(title_text)
        except Exception:
            listing["property_type"] = None

        try:
            loc_el = await card.query_selector(_LOCALITY_SELECTOR)
            if loc_el:
                listing["locality"] = (await loc_el.inner_text()).strip()
        except Exception:
            listing["locality"] = None

        # --- Description ---
        try:
            desc_el = await card.query_selector(_DESCRIPTION_SELECTOR)
            if desc_el:
                listing["description"] = (await desc_el.inner_text()).strip()
        except Exception:
            listing["description"] = None

        # --- Images ---
        try:
            img_els = await card.query_selector_all(_IMAGE_SELECTOR)
            image_urls = []
            for img in img_els:
                src = await img.get_attribute("data-src") or await img.get_attribute("src")
                if src and src.startswith("http"):
                    image_urls.append(src)
            listing["image_urls"] = image_urls
            listing["image_count"] = len(image_urls)
        except Exception:
            listing["image_urls"] = []
            listing["image_count"] = 0

        # --- Phone number ---
        # 99acres typically hides numbers behind a click; we capture whatever
        # is visible in the DOM (often masked). Full number requires JS interaction.
        try:
            phone_el = await card.query_selector(_PHONE_SELECTOR)
            if phone_el:
                phone_text = (await phone_el.inner_text()).strip()
                listing["phone_number"] = _parse_phone(phone_text)
            else:
                listing["phone_number"] = None
        except Exception:
            listing["phone_number"] = None

        # --- Listing URL ---
        try:
            link_el = await card.query_selector(_LINK_SELECTOR)
            if link_el:
                href = await link_el.get_attribute("href")
                if href:
                    listing["listing_url"] = (
                        href if href.startswith("http") else f"https://www.99acres.com{href}"
                    )
            else:
                listing["listing_url"] = page.url
        except Exception:
            listing["listing_url"] = page.url

        listings.append(listing)

    return listings


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _parse_price(raw: str) -> int | None:
    """
    Extract integer rent from strings like '₹25,000/month', '25k', '₹25K/month', or '25000'.
    
    Examples:
        "₹25k" -> 25000
        "₹30,000/month" -> 30000
        "25000 onwards" -> 25000
    """
    if not raw:
        return None
        
    # 1. Lowercase and split by '/' (to remove /month, /day if present)
    cleaned = raw.lower().split("/")[0]
    
    # 2. Handle 'k' notation (e.g. 25k -> 25000)
    multiplier = 1
    if 'k' in cleaned:
        multiplier = 1000
        cleaned = cleaned.replace('k', '')
        
    # 3. Remove non-numeric characters except decimals
    cleaned = re.sub(r"[^\d.]", "", cleaned).strip()
    
    # 4. Convert to float then int to handle cases like "2.5k"
    try:
        if cleaned:
            value = float(cleaned) * multiplier
            return int(value)
    except (ValueError, TypeError):
        pass
        
    return None


def _parse_property_type(title: str) -> str | None:
    """
    Extract BHK / property type from title strings.
    Examples: '2 BHK Flat for Rent in Koramangala' → '2BHK'
    """
    match = re.search(r"(\d+)\s*BHK", title, re.IGNORECASE)
    if match:
        return f"{match.group(1)}BHK"
    for keyword in ["Studio", "1RK", "Penthouse", "Villa", "Independent"]:
        if keyword.lower() in title.lower():
            return keyword
    return title.split()[0] if title else None


def _parse_phone(text: str) -> str | None:
    """Extract a 10-digit phone number from a text string, if present."""
    match = re.search(r"(\d[\d\s\-]{8,}\d)", text)
    if match:
        digits = re.sub(r"\D", "", match.group())
        if len(digits) >= 10:
            return digits[-10:]
    return None
