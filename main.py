import logging
import argparse
from config.database import init_pool, close_pool
from services.query_all_persons import get_all_persons_with_detail
from services.classify_persons import classify_persons
from services.insert_results import insert_classified, insert_scraping_results
from services.export_report import export_report
from browser.scraper import ensure_screenshots_dir
from browser.worker_pool import process_persons
from checkpoint.checkpoint_manager import load_checkpoint, clear_checkpoint

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

    # Export report
    if classification.incompletes:
        export_report("Información incompleta", classification.incompletes)

    # Scraping
    if not classification.candidates:
        logger.info("No candidates for process. Done.")
        return
    
    ensure_screenshots_dir()
    process_ids = load_checkpoint()

    results = process_persons(classification.candidates, process_ids)
    
    # Persist scraping results
    if results:
        insert_scraping_results(results, dry_run=dry_run)
    
    # Clear checkpoint on success
    clear_checkpoint()


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
