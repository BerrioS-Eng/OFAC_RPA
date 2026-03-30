import logging
import argparse
from config.database import init_pool, close_pool
from services.query_all_persons import get_all_persons_with_detail
from services.classify_persons import classify_persons
from services.insert_results import insert_classified, insert_scraping_results
from browser.session import init_browser, close_browser
from browser.scraper import scrape_person, ensure_screenshots_dir
from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s → %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log", mode="a"),
    ],
)

logger = logging.getLogger(__name__)

def run_pipeline(dry_run: bool):
    # Query
    registers = get_all_persons_with_detail()

    if not registers:
        logger.info("No registers found. Exiting.")
        return

    # Classify
    classification = classify_persons(registers)

    # Insert classified (non-scraped cases)
    insert_classified(
        not_cross=classification.not_cross,
        not_consult=classification.not_consult,
        incompletes=classification.incompletes,
        dry_run=dry_run
    )

    # Scraping
    if not classification.candidates:
        logger.info("No candidates for process. Done.")
        return
    
    browser = init_browser()
    try:
        page = browser.new_page()
        page.goto(settings.app_url)
        page.wait_for_load_state("networkidle")

        ensure_screenshots_dir()

        results = []

        for person in classification.candidates:
            data_scraped = scrape_person(page, person)
            results.append(data_scraped)

        # Persist scraping results
        insert_scraping_results(results, dry_run=dry_run)
    
    finally:
        close_browser()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OFAC RPA Pipeline")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inserts without committing to the database."
    )
    args = parser.parse_args()

    if args.dry_run:
        logger.info("Running in DRY RUN mode - no data will be persisted.")
    
    try:
        init_pool()
        run_pipeline(dry_run=args.dry_run)
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
    finally:
        close_pool()
