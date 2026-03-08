"""
ai_layer/scraper/sources/magicbricks.py
======================================
Platform-specific parsing logic for MagicBricks.
"""

import logging
import re
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from playwright.async_api import Page

logger = logging.getLogger(__name__)

PLATFORM_SOURCE = "magicbricks"

_CARD_SELECTOR = ".mb-srp__card"
_PRICE_SELECTOR = ".mb-srp__card__price--amount"
_TITLE_SELECTOR = ".mb-srp__card--title"
_LOCALITY_SELECTOR = ".mb-srp__card__summary-title"
_DESCRIPTION_SELECTOR = ".mb-srp__card--desc"
_IMAGE_SELECTOR = ".mb-srp__card__photo img"
_PHONE_SELECTOR = ".mb-srp__card__developer--name, .mb-srp__card__contact--phone"
_LINK_SELECTOR = "a.mb-srp__card__link"

def _parse_price(raw: str) -> int | None:
    if not raw:
        return None
    cleaned = raw.lower().split("/")[0]
    multiplier = 1
    if 'k' in cleaned:
        multiplier = 1000
        cleaned = cleaned.replace('k', '')
    if 'lac' in cleaned or 'lakh' in cleaned:
        multiplier = 100000
        cleaned = cleaned.replace('lac', '').replace('lakh', '')
    if 'cr' in cleaned or 'crore' in cleaned:
        multiplier = 10000000
        cleaned = cleaned.replace('cr', '').replace('crore', '')
        
    cleaned = re.sub(r"[^\d.]", "", cleaned).strip()
    try:
        if cleaned:
            return int(float(cleaned) * multiplier)
    except (ValueError, TypeError):
        pass
    return None

def _parse_phone(text: str) -> str | None:
    match = re.search(r"(\d[\d\s\-]{8,}\d)", text)
    if match:
        digits = re.sub(r"\D", "", match.group())
        if len(digits) >= 10:
            return digits[-10:]
    return None

def _parse_property_type(title: str) -> str | None:
    match = re.search(r"(\d+)\s*BHK", title, re.IGNORECASE)
    if match:
        return f"{match.group(1)}BHK"
    for keyword in ["Studio", "1RK", "Penthouse", "Villa", "Independent"]:
        if keyword.lower() in title.lower():
            return keyword
    return title.split()[0] if title else None

async def scrape_page(page: "Page", city: str) -> list[dict]:
    listings: list[dict] = []

    try:
        await page.wait_for_selector(_CARD_SELECTOR, timeout=15_000)
    except Exception:
        logger.warning(f"No {PLATFORM_SOURCE} listing cards found on this page.")
        return listings

    cards = await page.query_selector_all(_CARD_SELECTOR)
    logger.info(f"  Found {len(cards)} cards on page.")

    for card in cards:
        listing: dict = {
            "city": city, 
            "platform_source": PLATFORM_SOURCE,
            "timestamp": datetime.now().isoformat()
        }

        try:
            price_el = await card.query_selector(_PRICE_SELECTOR)
            if price_el:
                listing["price"] = _parse_price((await price_el.inner_text()).strip())
        except Exception:
            listing["price"] = None

        try:
            title_el = await card.query_selector(_TITLE_SELECTOR)
            if title_el:
                title_text = (await title_el.inner_text()).strip()
                listing["property_type"] = _parse_property_type(title_text)
                listing["locality"] = title_text # fallback
        except Exception:
            listing["property_type"] = None

        try:
            loc_el = await card.query_selector(_LOCALITY_SELECTOR)
            if loc_el:
                listing["locality"] = (await loc_el.inner_text()).strip()
        except Exception:
            pass

        try:
            desc_el = await card.query_selector(_DESCRIPTION_SELECTOR)
            if desc_el:
                listing["description"] = (await desc_el.inner_text()).strip()
        except Exception:
            listing["description"] = None

        try:
            img_els = await card.query_selector_all(_IMAGE_SELECTOR)
            image_urls = []
            for img in img_els:
                src = await img.get_attribute("src") or await img.get_attribute("data-src")
                if src and src.startswith("http"):
                    image_urls.append(src)
            listing["image_urls"] = image_urls
            listing["image_count"] = len(image_urls)
        except Exception:
            listing["image_urls"] = []
            listing["image_count"] = 0

        try:
            phone_el = await card.query_selector(_PHONE_SELECTOR)
            if phone_el:
                listing["phone_number"] = _parse_phone((await phone_el.inner_text()).strip())
            else:
                listing["phone_number"] = None
        except Exception:
            listing["phone_number"] = None

        try:
            link_el = await card.query_selector(_LINK_SELECTOR)
            if link_el:
                href = await link_el.get_attribute("href")
                if href:
                    listing["listing_url"] = href if href.startswith("http") else f"https://www.magicbricks.com{href}"
            else:
                listing["listing_url"] = page.url
        except Exception:
            listing["listing_url"] = page.url

        listings.append(listing)

    return listings
