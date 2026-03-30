import logging
import re
import os
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)

def ensure_screenshots_dir():
    """Creates screenshots directory if it doesn't exist."""
    os.makedirs(settings.screenshot_dir, exist_ok=True)


def scrape_person(page, person):
    """
    Processes a single person:
    fills form, searches, and extracts results.
    If result_int > 0, screenshot process.
    """
    try:

        # Fill form
        page.locator("#ctl00_MainContent_txtLastName").fill(person["nombrePersona"])
        page.locator("#ctl00_MainContent_txtAddress").fill(person["direccion"])
        page.locator("#ctl00_MainContent_ddlCountry").select_option(person["pais"])

        # Search
        page.locator("#ctl00_MainContent_btnSearch").click()
        page.wait_for_selector("#ctl00_MainContent_lblResults")

        # Extract result
        result_text = page.locator("#ctl00_MainContent_lblResults").inner_text()
        match = re.search(r'\d+', result_text)
        result_int = int(match.group()) if match else 0

        # Screenshot if results found
        if result_int > 0:
            filename = f"{datetime.now().strftime('%Y%m%d')}_{person['idPersona']}.png"
            page.screenshot(path=os.path.join(settings.screenshot_dir, filename), full_page=True)
            logger.info(f"Screenshot taken for {person['nombrePersona']}")

        return {
            "idPersona": person["idPersona"],
            "nombrePersona": person["nombrePersona"],
            "pais": person["pais"],
            "cantidadDeResultados": result_int,
            "estadoTransaccion": "OK",
        }

    except Exception as e:
        logger.warning(f"Error scraping {person['nombrePersona']}: {e}")
        return {
            "idPersona": person["idPersona"],
            "nombrePersona": person["nombrePersona"],
            "pais": person["pais"],
            "cantidadDeResultados": 0,
            "estadoTransaccion": "NOK",
        }