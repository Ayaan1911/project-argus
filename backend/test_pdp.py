import asyncio
from playwright.async_api import async_playwright

async def get_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.99acres.com/3-bhk-bedroom-apartment-flat-for-rent-in-total-environment-pursuit-of-a-radical-rhapsody-hoodi-bangalore-east-4303-sq-ft-spid-H89314277", wait_until="domcontentloaded")
        title = await page.title()
        desc = await page.evaluate("document.querySelector('meta[name=\"description\"]').content")
        price = await page.evaluate("document.body.innerText.match(/₹\s*[\d,]+/g) || []")
        print("TITLE:", title)
        print("DESC_META:", desc)
        print("PRICES:", price)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_page())
