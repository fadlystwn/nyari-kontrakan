import asyncio
import os
import logging
from dotenv import load_dotenv
from .database import get_db_connection
from .scheduler import scheduler, run_olx_scraper, run_rumah123_scraper, run_curation

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("scraper_worker")

async def init_db_schema():
    conn = await get_db_connection()
    try:
        # Check if listings table exists
        exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'listings')"
        )
        if not exists:
            logger.info("Listings table not found in database. Initializing table and indexes...")
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id              SERIAL PRIMARY KEY,
                source          VARCHAR(64)     NOT NULL,          -- e.g. 'olx', 'rumah123'
                external_id     VARCHAR(255)    UNIQUE NOT NULL,   -- unique ID from source site
                title           TEXT            NOT NULL,
                price           BIGINT,                            -- stored in IDR
                location        TEXT,
                city            VARCHAR(128),
                property_type   VARCHAR(64),                       -- e.g. 'house', 'apartment', 'land'
                bedrooms        INTEGER,
                bathrooms       INTEGER,
                land_area_sqm   INTEGER,
                building_area_sqm INTEGER,
                url             TEXT            NOT NULL,
                photos          TEXT[],                            -- array of image URLs
                raw_data        JSONB,                             -- full raw payload for future use
                scraped_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
                updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
                
                -- Curation Fields
                curated          BOOLEAN         NOT NULL DEFAULT FALSE,
                quality_score    SMALLINT,                          -- 0–100
                tags             TEXT[],                            -- e.g. ['furnished', 'near-toll']
                summary          TEXT,                              -- LLM-generated 2–3 sentence summary
                normalized_data  JSONB,                             -- cleaned/canonical field values
                curation_model   VARCHAR(64),                       -- e.g. 'gemini-2.5-flash'
                curated_at       TIMESTAMPTZ
            );
            """)
            
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_city     ON listings(city);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_price    ON listings(price);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_type     ON listings(property_type);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_source   ON listings(source);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_scraped  ON listings(scraped_at DESC);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_curated  ON listings(curated);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_quality  ON listings(quality_score DESC);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_tags     ON listings USING GIN(tags);")
            
            logger.info("Database schema initialized successfully.")
        else:
            logger.info("Database schema already exists.")
    except Exception as e:
        logger.error(f"Error checking/initializing database schema: {e}")
        raise e
    finally:
        await conn.close()

async def main():
    logger.info("Starting Scraper & Curator worker daemon...")
    
    # Wait for database to be ready and initialize schema
    db_connected = False
    retries = 10
    while not db_connected and retries > 0:
        try:
            await init_db_schema()
            db_connected = True
        except Exception as e:
            logger.warning(f"Database connection failed, retrying in 3 seconds... (Retries left: {retries})")
            retries -= 1
            await asyncio.sleep(3)
            
    if not db_connected:
        logger.error("Could not connect to database. Exiting worker.")
        return

    # Start the scheduler
    scheduler.start()
    logger.info("APScheduler started successfully.")
    
    # Check if run on startup is requested
    if os.getenv("SCRAPE_ON_STARTUP", "false").lower() == "true":
        logger.info("SCRAPE_ON_STARTUP is enabled. Running jobs immediately...")
        await run_olx_scraper()
        await run_rumah123_scraper()
        await run_curation()

    # Keep daemon running
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down worker...")
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
