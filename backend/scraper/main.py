import asyncio
import os
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from database import SessionManager, Base  # noqa: E402
from config import settings  # noqa: E402
from .scheduler import scheduler, run_olx_scraper, run_rumah123_scraper, run_curation_worker  # noqa: E402

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("scraper_worker")

session_manager = SessionManager(settings.database_url)

async def init_db_schema():
    logger.info("Verifying/creating database schema using shared SQLAlchemy models...")
    try:
        async with session_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema verified and created successfully.")
    except Exception as e:
        logger.error(f"Error checking/initializing database schema: {e}")
        raise e

async def main():
    logger.info("Starting Scraper & Curator worker daemon...")
    
    db_connected = False
    retries = 10
    while not db_connected and retries > 0:
        try:
            await init_db_schema()
            db_connected = True
        except Exception as e:
            logger.warning(f"Database connection failed: {e}. Retrying in 3 seconds... (Retries left: {retries})")
            retries -= 1
            await asyncio.sleep(3)
            
    if not db_connected:
        logger.error("Could not connect to database. Exiting worker.")
        return

    scheduler.start()
    logger.info("APScheduler started successfully.")
    
    if os.getenv("SCRAPE_ON_STARTUP", "false").lower() == "true":
        logger.info("SCRAPE_ON_STARTUP is enabled. Running jobs immediately...")
        await run_olx_scraper()
        await run_rumah123_scraper()
        await run_curation_worker()

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down worker...")
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
