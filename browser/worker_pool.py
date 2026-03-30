import asyncio
import logging
from browser.scraper import scrape_person
from browser.session import init_browser, close_browser
from checkpoint.checkpoint_manager import save_checkpoint
from config.settings import settings

logger = logging.getLogger(__name__)

async def _worker(page, persons, processed, lock):
    """Processes a list of persons sequentially on a single browser page."""
    results = []
    for person in persons:
        result = await scrape_person(page, person)
        results.append(result)
        async with lock:
            processed.add(person["idPersona"])
            save_checkpoint(processed)
    return results

async def _process_async(candidates, processed):
    """
    Async pipeline: filters pending candidates, distributes them
    round-robin across N browser pages.
    """
    pending = [c for c in candidates if c["idPersona"] not in processed]
    if not pending:
        logger.info("All candidates already processed. (from checkpoint).")
        return []

    logger.info(
        f"Processing {len(pending)} candidates "
        f"({len(candidates) - len(pending)} skipped from checkpoint)."
    )

    n = min(settings.max_workers, len(pending))
    browser = await init_browser()
    lock = asyncio.Lock()

    buckets = [[] for _ in range(n)]
    for i, person in enumerate(pending):
        buckets[i % n].append(person)
    
    try:
        pages = [await browser.new_page() for _ in range(n)]
        for page in pages:
            await page.goto(settings.app_url)
            await page.wait_for_load_state("networkidle")

        results_nested = await asyncio.gather(
            *[_worker(pages[i], buckets[i], processed, lock) for i in range(n)],
            return_exceptions=True
        )
        results = [r for bucket in results_nested for r in bucket]

        logger.info(f"Processing completed: {len(results)} results "
                f"({sum(1 for r in results if r["estadoTransaccion"] == "OK")} OK, "
                f"{sum(1 for r in results if r["estadoTransaccion"] == "NOK")} NOK)"
                )
        return results
    finally:
        for page in pages:
            await page.close()
        await close_browser()

def process_persons(candidates, processed):
    """Sync entry point — runs the async pipeline."""
    return asyncio.run(_process_async(candidates, processed))