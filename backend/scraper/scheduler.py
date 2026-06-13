import logging
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .database import get_db_connection
from .scrapers.olx import OlxScraper
from .scrapers.rumah123 import Rumah123Scraper
from .curation.curator import run_curation

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def run_olx_scraper():
    logger.info("Starting scheduled OLX scraping job...")
    scraper = OlxScraper()
    try:
        raw_listings = await scraper.fetch_listings()
        logger.info(f"Fetched {len(raw_listings)} raw listings from OLX. Upserting to database...")
        
        conn = await get_db_connection()
        saved_count = 0
        try:
            for raw in raw_listings:
                parsed = scraper.parse_listing(raw)
                try:
                    await conn.execute(
                        """
                        INSERT INTO listings (
                            source, external_id, title, price, location, city, property_type,
                            bedrooms, bathrooms, land_area_sqm, building_area_sqm, url, photos, raw_data,
                            scraped_at, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NOW(), NOW())
                        ON CONFLICT (external_id) DO UPDATE SET
                            title = EXCLUDED.title,
                            price = EXCLUDED.price,
                            location = EXCLUDED.location,
                            city = EXCLUDED.city,
                            property_type = EXCLUDED.property_type,
                            bedrooms = COALESCE(EXCLUDED.bedrooms, listings.bedrooms),
                            bathrooms = COALESCE(EXCLUDED.bathrooms, listings.bathrooms),
                            land_area_sqm = COALESCE(EXCLUDED.land_area_sqm, listings.land_area_sqm),
                            building_area_sqm = COALESCE(EXCLUDED.building_area_sqm, listings.building_area_sqm),
                            url = EXCLUDED.url,
                            photos = EXCLUDED.photos,
                            raw_data = EXCLUDED.raw_data,
                            updated_at = NOW()
                        """,
                        parsed["source"], parsed["external_id"], parsed["title"], parsed["price"],
                        parsed["location"], parsed["city"], parsed["property_type"],
                        parsed["bedrooms"], parsed["bathrooms"], parsed["land_area_sqm"],
                        parsed["building_area_sqm"], parsed["url"], parsed["photos"],
                        json.dumps(parsed["raw_data"])
                    )
                    saved_count += 1
                except Exception as db_err:
                    logger.error(f"Failed to upsert OLX listing {parsed.get('external_id')}: {db_err}")
            logger.info(f"Completed OLX scraper job. Saved/updated {saved_count} listings.")
        finally:
            await conn.close()
    except Exception as e:
        logger.error(f"OLX scraper job failed: {e}")

async def run_rumah123_scraper():
    logger.info("Starting scheduled Rumah123 scraping job...")
    scraper = Rumah123Scraper()
    try:
        raw_listings = await scraper.fetch_listings()
        logger.info(f"Fetched {len(raw_listings)} raw listings from Rumah123. Upserting to database...")
        
        conn = await get_db_connection()
        saved_count = 0
        try:
            for raw in raw_listings:
                parsed = scraper.parse_listing(raw)
                try:
                    await conn.execute(
                        """
                        INSERT INTO listings (
                            source, external_id, title, price, location, city, property_type,
                            bedrooms, bathrooms, land_area_sqm, building_area_sqm, url, photos, raw_data,
                            scraped_at, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NOW(), NOW())
                        ON CONFLICT (external_id) DO UPDATE SET
                            title = EXCLUDED.title,
                            price = EXCLUDED.price,
                            location = EXCLUDED.location,
                            city = EXCLUDED.city,
                            property_type = EXCLUDED.property_type,
                            bedrooms = COALESCE(EXCLUDED.bedrooms, listings.bedrooms),
                            bathrooms = COALESCE(EXCLUDED.bathrooms, listings.bathrooms),
                            land_area_sqm = COALESCE(EXCLUDED.land_area_sqm, listings.land_area_sqm),
                            building_area_sqm = COALESCE(EXCLUDED.building_area_sqm, listings.building_area_sqm),
                            url = EXCLUDED.url,
                            photos = EXCLUDED.photos,
                            raw_data = EXCLUDED.raw_data,
                            updated_at = NOW()
                        """,
                        parsed["source"], parsed["external_id"], parsed["title"], parsed["price"],
                        parsed["location"], parsed["city"], parsed["property_type"],
                        parsed["bedrooms"], parsed["bathrooms"], parsed["land_area_sqm"],
                        parsed["building_area_sqm"], parsed["url"], parsed["photos"],
                        json.dumps(parsed["raw_data"])
                    )
                    saved_count += 1
                except Exception as db_err:
                    logger.error(f"Failed to upsert Rumah123 listing {parsed.get('external_id')}: {db_err}")
            logger.info(f"Completed Rumah123 scraper job. Saved/updated {saved_count} listings.")
        finally:
            await conn.close()
    except Exception as e:
        logger.error(f"Rumah123 scraper job failed: {e}")

# Wire schedules
# Run OLX scraper every day at 00:00 (midnight) server time
scheduler.add_job(run_olx_scraper, "cron", hour=0, minute=0)

# Run Rumah123 scraper every day at 01:00 server time
scheduler.add_job(run_rumah123_scraper, "cron", hour=1, minute=0)

# Run Curation after scrapers have completed, at 03:00 server time
scheduler.add_job(run_curation, "cron", hour=3, minute=0)
