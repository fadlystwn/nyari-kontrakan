from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def get_stealth_page(proxy: str = None):
    """
    Launch headless Playwright Chromium browser with stealth configuration,
    custom Indonesian user agent, locale, and timezone.
    Returns:
        tuple: (playwright_instance, browser_instance, page_instance)
    """
    playwright = await async_playwright().start()
    browser_args = {}
    if proxy:
        browser_args["proxy"] = {"server": proxy}
        
    browser = await playwright.chromium.launch(headless=True, **browser_args)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        locale="id-ID",
        timezone_id="Asia/Jakarta",
        viewport={"width": 1280, "height": 800}
    )
    page = await context.new_page()
    await stealth_async(page)
    return playwright, browser, page
