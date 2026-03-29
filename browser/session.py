from playwright.sync_api import sync_playwright
from config.settings import settings

_playwright = None
_browser = None

def init_browser():
    """Start Playwright and the browser. It's called ONCE."""
    global _playwright, _browser
    _playwright = sync_playwright().start()
    _browser = _playwright.chromium.launch(headless=settings.headless)
    return _browser

def close_browser():
    """Cierra navegador y Playwright. Se llama al finalizar."""
    global _playwright, _browser
    if _browser:
        _browser.close()
    if _playwright:
        _playwright.stop()