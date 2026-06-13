import logging
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from config import settings  # noqa: E402
from curation import GeminiClient, CurationService  # noqa: E402

logger = logging.getLogger(__name__)

async def run_curation_worker():
    """
    Worker function to run curation batch on uncurated listings.
    """
    logger.info("Starting scheduled curation job...")
    try:
        gemini_client = GeminiClient(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model
        )
        service = CurationService(gemini_client)
        
        curated_count = await service.curate_batch()
        logger.info(f"Completed curation job. Curated {curated_count} listings.")
    except Exception as e:
        logger.error(f"Curation job failed: {e}")
