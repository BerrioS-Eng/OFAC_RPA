# OFAC RPA

Automated pipeline that queries persons from a PostgreSQL database, searches each candidate against the [OFAC sanctions list](https://sanctionssearch.ofac.treas.gov/), and persists the results back to the database.

## Flow

```
PostgreSQL → Classify → Insert non-candidates → Scrape OFAC → Insert results
                                ↓
                        Export Excel report
```

1. **Query** — fetches all persons with address detail via LEFT JOIN
2. **Classify** — splits records into four groups:
   - `candidates` → have full address data and `aConsultar = Yes`
   - `incompletes` → missing `direccion` or `pais`
   - `not_consult` → `aConsultar = No`
   - `not_cross` → no match in `MaestraDetallePersonas`
3. **Insert classified** — bulk inserts non-candidate groups with their status
4. **Export report** — generates a `.xlsx` report for incomplete records
5. **Scrape** — fills the OFAC search form per candidate, extracts result count, and takes a screenshot if matches are found
6. **Insert results** — bulk inserts scraping outcomes

## Requirements

- Python 3.12+
- PostgreSQL
- Playwright (Chromium)

```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuration

Copy `.env.example` to `.env` and fill in the values:

```env
# Database
DATABASE_URL=postgres://user:password@host:5432/db?schema=public
TABLE_PERSONAS=Personas
TABLE_MAESTRA_DETALLE_PERSONAS=MaestraDetallePersonas
TABLE_RESULTADOS=Resultados

# Platform
APP_URL=https://sanctionssearch.ofac.treas.gov/

# Bot behavior (optional)
HEADLESS=true
SCREENSHOTS_DIR=output_screenshots
REPORTS_DIR=output_reports
```

## Usage

```bash
# Dry run — validates inserts without committing to the database
PYTHONPATH=. python3 main.py --dry-run

# Production
PYTHONPATH=. python3 main.py
```

## Project structure

```
├── config/
│   ├── settings.py       # Environment-based configuration
│   └── database.py       # Connection pool and context managers
├── services/
│   ├── query_all_persons.py   # Fetch persons with detail
│   ├── classify_persons.py    # Classification logic
│   ├── insert_results.py      # Bulk insert helpers
│   └── export_report.py       # Excel report generation
├── browser/
│   ├── session.py        # Playwright lifecycle
│   └── scraper.py        # OFAC form scraper
├── main.py               # Pipeline orchestrator
└── requirements.txt
```

## Outputs

| Path | Content |
|---|---|
| `output_screenshots/` | Screenshots of OFAC matches |
| `output_reports/` | Excel reports per run |
| `pipeline.log` | Execution log |
