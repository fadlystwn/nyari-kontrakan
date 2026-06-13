import sys
from pathlib import Path
import logging

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from curation import GeminiClient, CurationService  # noqa: E402

logger = logging.getLogger(__name__)

async def run_api_curation():
    try:
        client = GeminiClient()
        service = CurationService(client)
        await service.curate_batch()
    except Exception as e:
        logger.error(f"Error during API background curation task: {e}")
