import sqlite3
import logging
from backend.config.settings import settings

logger = logging.getLogger(__name__)

def get_db_connection():
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise e
        
def close_db_connection(conn):
    if conn:
        conn.close()
