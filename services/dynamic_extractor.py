from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def extract_dynamic_page_text(url: str, selector_priority=None) -> str:    
    selector_priority = selector_priority or [
        "article",
        "main",
        "div#content",
        "div.main",
        "section.content"
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, timeout=15000)
            await page.wait_for_load_state("networkidle")
            html = await page.content()
        finally:
            await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    for selector in selector_priority:
        element = soup.select_one(selector)
        if element:
            return element.get_text(separator="\n", strip=True)

    return soup.get_text(separator="\n", strip=True)
