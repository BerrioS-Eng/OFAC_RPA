from dotenv import load_dotenv
from dataclasses import dataclass, field
import os

load_dotenv()

def _require(var: str) -> str:
    """An explicit failure occurs if a critical variable is not defined."""
    value = os.getenv(var)
    if not value: 
        raise EnvironmentError(f"Required environment variable not found: {var}")
    return value

@dataclass
class Settings:
    # Database
    database_url: str = field(default_factory= lambda: _require("DATABASE_URL"))
    table_personas: str = field(default_factory= lambda: _require("TABLE_PERSONAS"))
    table_maestra_detalle_personas: str = field(default_factory= lambda: _require("TABLE_MAESTRA_DETALLE_PERSONAS"))
    table_resultados: str = field(default_factory= lambda: _require("TABLE_RESULTADOS"))

    # Platform Web
    app_url: str = field(default_factory= lambda: _require("APP_URL"))

    # Bot behavior
    headless: bool = field(default_factory= lambda: os.getenv("HEADLESS", "true").lower() == "true")
    timeout_ms: int = field(default_factory= lambda: int(os.getenv("TIMEOUT_MS", "30000")))

    screenshot_dir: str = field(default_factory= lambda: os.getenv("SCREENSHOTS_DIR", "output_screenshots"))

settings = Settings()