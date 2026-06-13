import sys
from pathlib import Path

# Add parent directory to path for backend modules
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from database import DatabaseConnectionFactory
from config import settings

async def get_db_connection():
    """
    Establish and return a connection to the PostgreSQL database using asyncpg.
    """
    return await DatabaseConnectionFactory.get_asyncpg_connection(settings.database_url)
