from datetime import datetime
import logging
import asyncio
from typing import Dict, Any, List
from sqlalchemy import select, update, func

from config import settings
from database import SessionManager, Listing as ListingDB
from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class CurationService:
    def __init__(self, gemini_client: GeminiClient, session_manager: SessionManager = None):
        self.client = gemini_client
        self.session_manager = session_manager or SessionManager(settings.database_url)

    async def curate_listing(self, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Curate a single listing using Gemini API.
        """
        try:
            result = await self.client.curate_listing(listing_data)
            logger.info(f"Curated listing ID={listing_data.get('id')} with score={result.get('quality_score')}")
            return result
        except Exception as e:
            logger.error(f"Curation failed for listing ID={listing_data.get('id')}: {e}")
            raise

    async def curate_batch(self, batch_size: int = None, rate_limit_delay: float = None) -> int:
        """
        Fetch uncurated listings, curate them using Gemini, and save to the database.
        """
        batch_size = batch_size or settings.curation_batch_size
        rate_limit_delay = rate_limit_delay or settings.curation_rate_limit_delay
        
        async with self.session_manager.get_session() as session:
            stmt = (
                select(ListingDB)
                .where(ListingDB.curated == False)
                .order_by(ListingDB.scraped_at.desc())
                .limit(batch_size)
            )
            result = await session.execute(stmt)
            listings = result.scalars().all()

            if not listings:
                logger.info("No uncurated listings found.")
                return 0

            logger.info(f"Starting curation batch of {len(listings)} listings...")
            curated_count = 0

            for listing in listings:
                listing_data = {
                    "id": listing.id,
                    "title": listing.title,
                    "price": listing.price,
                    "location": listing.location,
                    "bedrooms": listing.bedrooms,
                    "bathrooms": listing.bathrooms,
                    "land_area_sqm": listing.land_area_sqm,
                    "building_area_sqm": listing.building_area_sqm,
                    "photos": listing.photos,
                    "source": listing.source,
                    "raw_data": listing.raw_data
                }

                try:
                    curation_result = await self.curate_listing(listing_data)
                    curation_result["curation_model"] = self.client.model
                    
                    update_stmt = (
                        update(ListingDB)
                        .where(ListingDB.id == listing.id)
                        .values(
                            curated=True,
                            quality_score=curation_result.get("quality_score"),
                            tags=curation_result.get("tags", []),
                            summary=curation_result.get("summary"),
                            normalized_data=curation_result.get("normalized", {}),
                            curation_model=curation_result.get("curation_model"),
                            curated_at=func.now()
                        )
                    )
                    await session.execute(update_stmt)
                    await session.commit()
                    
                    curated_count += 1
                    logger.info(f"Successfully curated listing ID {listing.id} with score {curation_result.get('quality_score')}")
                except Exception as e:
                    logger.error(f"Failed to curate listing ID {listing.id}: {e}")
                    await session.rollback()

                await asyncio.sleep(rate_limit_delay)
                
            return curated_count
