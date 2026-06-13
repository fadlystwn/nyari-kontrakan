import os
import asyncio
import logging
import json
from .gemini_client import GeminiClient
from ..database import get_db_connection

logger = logging.getLogger(__name__)

async def run_curation():
    """
    Fetch uncurated listings in batches, enrich via Gemini API, and persist back to PostgreSQL.
    Safe to run concurrently with scraping jobs.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set. Skipping curation job run.")
        return

    batch_size = int(os.getenv("CURATION_BATCH_SIZE", "10"))
    rate_limit_delay = float(os.getenv("CURATION_RATE_LIMIT_DELAY", "1.0"))
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    try:
        client = GeminiClient()
    except Exception as init_err:
        logger.error(f"Failed to initialize Gemini Client: {init_err}")
        return

    conn = await get_db_connection()

    try:
        # Fetch uncurated listings
        rows = await conn.fetch(
            """SELECT id, title, price, location, bedrooms, bathrooms,
                      land_area_sqm, building_area_sqm, photos,
                      source, raw_data
               FROM listings
               WHERE curated = FALSE
               ORDER BY scraped_at DESC
               LIMIT $1""",
            batch_size
        )

        if not rows:
            logger.info("No uncurated listings to process.")
            return

        logger.info(f"Curating {len(rows)} listings using model {model_name}...")

        for row in rows:
            listing = dict(row)
            try:
                result = await client.curate_listing(listing)
                
                await conn.execute(
                    """UPDATE listings SET
                         curated         = TRUE,
                         quality_score   = $1,
                         tags            = $2,
                         summary         = $3,
                         normalized_data = $4,
                         curation_model  = $5,
                         curated_at      = NOW()
                       WHERE id = $6""",
                    result.get("quality_score"),
                    result.get("tags", []),
                    result.get("summary"),
                    json.dumps(result.get("normalized", {})),
                    model_name,
                    listing["id"]
                )
                logger.info(f"Curated listing ID={listing['id']} with quality score={result.get('quality_score')}")
            except Exception as e:
                logger.error(f"Curation failed for listing ID={listing['id']}: {e}")

            await asyncio.sleep(rate_limit_delay)

    finally:
        await conn.close()
