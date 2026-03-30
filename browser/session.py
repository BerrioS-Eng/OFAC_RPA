from playwright.async_api import async_playwright
from config.settings import settings

_playwright = None
_browser = None

async def init_browser():
    """Start Playwright and the browser. It's called ONCE."""
    global _playwright, _browser
    _playwright = await async_playwright().start()
    _browser = await _playwright.chromium.launch(headless=settings.headless)
    return _browser

async def close_browser():
    """Cierra navegador y Playwright. Se llama al finalizar."""
    global _playwright, _browser
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()