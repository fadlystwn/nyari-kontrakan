import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from database import DatabaseConnectionFactory, SessionManager, Base
from config import settings

session_manager = SessionManager(settings.database_url)
engine = session_manager.engine
AsyncSessionLocal = session_manager.session_factory

async def get_db():
    async with session_manager.get_session() as session:
        yield session
