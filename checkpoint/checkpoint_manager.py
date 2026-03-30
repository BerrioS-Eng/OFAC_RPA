import json
import os
import logging
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)

CHECKPOINT_FILE = os.path.join(settings.checkpoint_dir, "checkpoint.json")

def _ensure_checkpoint_dir():
    """Ensure the checkpoint directory exists."""
    os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)

def load_checkpoint():
    """Loads last checkpoint if exists."""

    if not os.path.exists(CHECKPOINT_FILE):
        logger.info("No checkpoint found. Starting fresh.")
        return set()

    try:
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
            processed = set(data.get("processed", []))
            logger.info(f"Checkpoint loaded: {len(processed)} already processed "
                        f"(from {data.get("last_updated", "unknown")})"
                        )
            return processed
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Corrupted checkpoint, starting fresh: {e}")
        return set()

def save_checkpoint(processed):
    """Saves current progress. Called after each successful scrape."""
    
    _ensure_checkpoint_dir()

    data = {
        "processed": list(processed),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_processed": len(processed),
    }
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def clear_checkpoint():
    """Removes checkpoint file. Called when pipeline completes successfully."""
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        logger.info("Checkpoint cleared.")