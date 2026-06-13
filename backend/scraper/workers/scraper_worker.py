import logging
import sys
from pathlib import Path

# Add parent directory to path for backend modules
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from database import SessionManager
from config import settings
from services import ScraperService
from ..scrapers.olx_scraper import OLXScraper
from ..scrapers.rumah123_scraper import Rumah123Scraper

logger = logging.getLogger(__name__)

session_manager = SessionManager(settings.database_url)

async def run_olx_scraper():
    """
    Worker function to run OLX scraper and save listings to database.
    """
    logger.info("Starting scheduled OLX scraping job...")
    scraper = OLXScraper()
    try:
        raw_listings = await scraper.fetch_listings()
        logger.info(f"Fetched {len(raw_listings)} raw listings from OLX. Upserting to database...")
        
        async with session_manager.get_session() as session:
            service = ScraperService(session)
            saved_count = await service.save_listings(raw_listings, scraper)
            logger.info(f"Completed OLX scraper job. Saved/updated {saved_count} listings.")
    except Exception as e:
        logger.error(f"OLX scraper job failed: {e}")

async def run_rumah123_scraper():
    """
    Worker function to run Rumah123 scraper and save listings to database.
    """
    logger.info("Starting scheduled Rumah123 scraping job...")
    scraper = Rumah123Scraper()
    try:
        raw_listings = await scraper.fetch_listings()
        logger.info(f"Fetched {len(raw_listings)} raw listings from Rumah123. Upserting to database...")
        
        async with session_manager.get_session() as session:
            service = ScraperService(session)
            saved_count = await service.save_listings(raw_listings, scraper)
            logger.info(f"Completed Rumah123 scraper job. Saved/updated {saved_count} listings.")
    except Exception as e:
        logger.error(f"Rumah123 scraper job failed: {e}")
