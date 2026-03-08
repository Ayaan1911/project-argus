"""
ai_layer/scraper/sources/__init__.py
======================================
Platform source registry.

Each module in this package implements the parsing logic for a single platform.
To add a new platform, create a new .py file here with:

    async def scrape_page(page, city: str) -> list[dict]:
        \"\"\"
        Parse the current Playwright page and return a list of listing dicts.
        All dicts will be passed through BaseScraper.enforce_schema() downstream.
        \"\"\"
        ...

Then register it in PlaywrightScraper or BS4Scraper as needed.
"""
