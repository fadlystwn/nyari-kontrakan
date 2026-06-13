import logging
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models import Listing

logger = logging.getLogger(__name__)

class ListingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_listings(
        self,
        city: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        property_type: Optional[str] = None,
        source: Optional[str] = None,
        min_quality: Optional[int] = None,
        tags: Optional[str] = None,
        curated_only: bool = False,
        limit: int = 20,
        page: int = 1
    ) -> Tuple[List[Listing], int]:
        offset = (page - 1) * limit
        stmt = select(Listing)
        count_stmt = select(func.count()).select_from(Listing)

        filters = []
        if city:
            filters.append(func.lower(Listing.city) == city.lower())
        if property_type:
            filters.append(func.lower(Listing.property_type) == property_type.lower())
        if min_price is not None:
            filters.append(Listing.price >= min_price)
        if max_price is not None:
            filters.append(Listing.price <= max_price)
        if source:
            filters.append(func.lower(Listing.source) == source.lower())
        if min_quality is not None:
            filters.append(Listing.quality_score >= min_quality)
        if tags:
            search_tags = [t.strip() for t in tags.split(",") if t.strip()]
            for tag in search_tags:
                filters.append(Listing.tags.contains([tag]))
        if curated_only:
            filters.append(Listing.curated == True)

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        if curated_only:
            stmt = stmt.order_by(Listing.quality_score.desc())
        else:
            stmt = stmt.order_by(Listing.scraped_at.desc())
            
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        listings = list(result.scalars().all())
        
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        return listings, total_count

    async def get_listing_by_id(self, id: int) -> Optional[Listing]:
        stmt = select(Listing).where(Listing.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_statistics(self) -> Dict[str, Any]:
        # Count by city
        city_stmt = select(Listing.city, func.count(Listing.id)).group_by(Listing.city)
        city_result = await self.session.execute(city_stmt)
        count_by_city = [
            {"city": row[0], "count": row[1]} 
            for row in city_result.all() 
            if row[0] is not None
        ]
        
        # Average price by property type (only where price is valid)
        type_stmt = (
            select(Listing.property_type, func.avg(Listing.price))
            .where(Listing.price > 0)
            .group_by(Listing.property_type)
        )
        type_result = await self.session.execute(type_stmt)
        avg_price_by_type = [
            {"property_type": row[0], "avg_price": float(row[1]) if row[1] is not None else 0.0}
            for row in type_result.all() 
            if row[0] is not None
        ]
        
        return {
            "count_by_city": count_by_city,
            "avg_price_by_type": avg_price_by_type
        }
