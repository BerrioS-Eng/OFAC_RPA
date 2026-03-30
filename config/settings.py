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
    # Default bot behavior
    headless: bool = True
    screenshot_dir: str = "output_screenshots"
    reports_dir: str = "output_reports"

    # Database
    database_url: str = field(default_factory= lambda: _require("DATABASE_URL"))
    table_personas: str = field(default_factory= lambda: _require("TABLE_PERSONAS"))
    table_maestra_detalle_personas: str = field(default_factory= lambda: _require("TABLE_MAESTRA_DETALLE_PERSONAS"))
    table_resultados: str = field(default_factory= lambda: _require("TABLE_RESULTADOS"))

    # Platform Web
    app_url: str = field(default_factory= lambda: _require("APP_URL"))

    # Configurable bot behavior
    def __post_init__(self):
        self.headless = os.getenv("HEADLESS", "true").lower() == "true"
        self.screenshot_dir = os.getenv("SCREENSHOTS_DIR", self.screenshot_dir)
        self.reports_dir = os.getenv("REPORTS_DIR", self.reports_dir)

settings = Settings()