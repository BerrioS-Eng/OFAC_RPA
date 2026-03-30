import logging
from psycopg2 import sql
from psycopg2.extras import execute_values
from config.database import get_connection
from config.settings import settings

logger = logging.getLogger(__name__)

def _build_values(registers, state):
    """Construct tuples of values for a ranked group."""
    return [
        (
            reg["idPersona"],
            reg["nombrePersona"],
            reg["pais"],
            0,
            state,
        )
        for reg in registers
    ]

def _bulk_insert(values, dry_run, log_lable):
    query = sql.SQL("""
                INSERT INTO {tabla} ("idPersona", "nombrePersona", "pais", "cantidadDeResultados", "estadoTransaccion")
                VALUES %s
            """).format(tabla=sql.Identifier(settings.table_resultados))
    
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            execute_values(cursor, query, values, page_size=1000)
            if dry_run:
                conn.rollback()
                logger.info(f"[DRY RUN] {len(values)} {log_lable}, rollback executed.")
            else:
                conn.commit()
                logger.info(f"{len(values)} {log_lable} inserted.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error inserting {log_lable}: {e}")
            raise
        finally:
            cursor.close()

def insert_classified(not_cross, not_consult, incompletes, dry_run=False):
    """
    Bulk Insert.
    Inserts groups in a single transaction.
    """
    values = [
        *_build_values(not_cross, "No cruza con maestra"),
        *_build_values(not_consult, "No consultado"),
        *_build_values(incompletes, "Información incompleta"),
    ]

    if not values:
        logger.info("No classified registers to insert.")
        return

    _bulk_insert(values, dry_run, "classified records")

def insert_scraping_results(results, dry_run=False):
    """Insert the scraped results."""

    if not results:
        logger.info("No scraping results to insert.")
        return
    
    values = [
        (res["idPersona"], res["nombrePersona"], res["pais"], res["cantidadDeResultados"], res["estadoTransaccion"])
        for res in results
    ]
    
    _bulk_insert(values, dry_run, "scraped records")

