"""
ai_layer/scraper/sources/nobroker.py
======================================
STUB — NoBroker.in platform scraper.

TODO: Implement this module when NoBroker support is needed.

Expected interface (same contract as ninety_nine_acres.py):

    async def scrape_page(page: "Page", city: str) -> list[dict]:
        \"\"\"
        Parse all listing cards on a NoBroker search results page.

        Args:
            page: Playwright Page already navigated to the results URL.
            city: City name (lowercase).

        Returns:
            List of partial listing dicts. Missing fields will be filled
            by DatasetManager.enforce_schema().
        \"\"\"
        raise NotImplementedError("nobroker scraper not yet implemented")

Search URL pattern (for reference):
    https://www.nobroker.in/property/residential/rent/{city}/

Selectors to investigate:
    - Listing card: .list-card-new or [data-property-id]
    - Price: .price-block
    - Locality: .locality-name
    - Description: .desc-block
    - Phone: Often behind a login wall — capture via click + DOM extraction

Note: NoBroker shows phone numbers only after login.
      Consider using a headless authenticated session or capturing numbers
      from listings where they appear in description text.

PLATFORM_SOURCE = "nobroker"
"""

PLATFORM_SOURCE = "nobroker"


async def scrape_page(page, city: str) -> list[dict]:
    """STUB — NoBroker scraper not yet implemented."""
    raise NotImplementedError(
        "nobroker.scrape_page() is not yet implemented. "
        "See the docstring in this file for the expected interface."
    )
