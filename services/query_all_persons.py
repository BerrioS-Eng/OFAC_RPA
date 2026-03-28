import logging
from psycopg2 import sql
from config.settings import settings
from config.database import get_cursor

logger = logging.getLogger(__name__)

def get_all_persons_with_detail():
    """
    Retrieve all persons with address and country.
    LEFT JOIN: if the person has no match in "MaestraDetallePersonas",
    their detail fields will be null → classified as "No cruza con maestra."
    """
    query = sql.SQL("""
        SELECT 
                    p."idPersona", 
                    p."nombrePersona", 
                    p."aConsultar", 
                    mdp.direccion, 
                    mdp.pais,
                    mdp."idPersona" IS NOT NULL AS "cruzaConMaestra"
        FROM {tabla_personas} p 
        LEFT JOIN {tabla_detalle} mdp 
            ON p."idPersona"  = mdp."idPersona" 
    """).format(
        tabla_personas = sql.Identifier(settings.table_personas),
        tabla_detalle = sql.Identifier(settings.table_maestra_detalle_personas),
    )
    with get_cursor(commit=False) as cursor:
        cursor.execute(query)
        registers = cursor.fetchall()
        logger.info(f"Persons obtained: {len(registers)}")
        return registers
