import logging
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Listing

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_listings(self, raw_listings: List[Dict[str, Any]], scraper) -> int:
        """
        Parse raw listings from a scraper and upsert them to the database.
        """
        saved_count = 0
        for raw in raw_listings:
            parsed = scraper.parse_listing(raw)
            try:
                # Find if already exists in DB
                stmt = select(Listing).where(Listing.external_id == parsed["external_id"])
                result = await self.session.execute(stmt)
                db_model = result.scalar_one_or_none()

                if db_model:
                    # Update fields
                    for key, val in parsed.items():
                        if key not in {"id", "scraped_at", "updated_at"}:
                            setattr(db_model, key, val)
                else:
                    # Create new row
                    db_model = Listing(**parsed)
                    self.session.add(db_model)

                await self.session.flush()
                saved_count += 1
            except Exception as e:
                logger.error(f"Failed to save listing from {scraper.source} with external ID {parsed.get('external_id')}: {e}")
        
        return saved_count
