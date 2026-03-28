import logging
from psycopg2 import pool, OperationalError
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config.settings import settings
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

logger = logging.getLogger(__name__)

"""
--- CONNECTION POOL ---
"""

_connection_pool = None

def init_pool():
    """Initialize the pool using the configuration DATABASE_URL."""
    global _connection_pool
    try: 
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            dsn=_clean_dsn(settings.database_url),
            connect_timeout=10
        )
        logger.info("Connection pool successfully initialized")
    except OperationalError as e:
        logger.critical(f"Unable to connect to PostgreSQL: {e}")
        raise

def close_pool():
    """Close all connections to the pool."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        logger.info("Closed connection pool")

"""
--- CONTEXT MANAGER ---
"""

@contextmanager
def get_connection():
    """It lends a connection from the pool and returns it when finished."""
    conn = None
    try: 
        conn = _connection_pool.getconn()
        yield conn
    except OperationalError as e: 
        logger.error(f"Connection error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            _connection_pool.putconn(conn)

@contextmanager
def get_cursor(commit=True):
    """
    Provides a dictionary cursor.

        Args:
            commit: True for write operations (INSERT/UPDATE),
                    False for read-only operations (SELECT).
    """
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Query error, rollback executed: {e}")
            raise
        finally:
            cursor.close()

"""
--- Format Database URL ---
"""
def _clean_dsn(dsn):
    """Removes parameters not supported by psycopg2 (e.g., Prisma schema)."""
    parsed = urlparse(dsn)
    params = parse_qs(parsed.query)

    # Remove parameters that psycopg2 does not recognize
    params.pop("schema", None)

    new_query = urlencode(params, doseq=True)
    dsn_clean = urlunparse(parsed._replace(query=new_query))
    return dsn_clean