import sys
from pathlib import Path

# Add parent directory to path for backend modules
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from database import SessionManager
from config import settings

session_manager = SessionManager(settings.database_url)

async def get_db():
    async with session_manager.get_session() as session:
        yield session
