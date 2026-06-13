from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from ..database import get_db
from ..models import Listing
from ..schemas import ListingResponse, PaginatedListingsResponse, StatsResponse, CityStats, TypeStats

router = APIRouter(prefix="/listings", tags=["listings"])

@router.get("", response_model=PaginatedListingsResponse)
async def get_listings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    property_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    source: Optional[str] = None,
    min_quality: Optional[int] = None,
    tags: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
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
            
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
        
    stmt = stmt.order_by(Listing.scraped_at.desc())
    
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    listings = result.scalars().all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "listings": listings
    }

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    # Count by city
    city_stmt = select(Listing.city, func.count(Listing.id)).group_by(Listing.city)
    city_result = await db.execute(city_stmt)
    count_by_city = [CityStats(city=row[0], count=row[1]) for row in city_result.all()]
    
    # Average price by property type (only where price is valid)
    type_stmt = (
        select(Listing.property_type, func.avg(Listing.price))
        .where(Listing.price > 0)
        .group_by(Listing.property_type)
    )
    type_result = await db.execute(type_stmt)
    avg_price_by_type = [
        TypeStats(property_type=row[0], avg_price=float(row[1]) if row[1] is not None else 0.0)
        for row in type_result.all()
    ]
    
    return StatsResponse(
        count_by_city=count_by_city,
        avg_price_by_type=avg_price_by_type
    )

@router.get("/curated", response_model=PaginatedListingsResponse)
async def get_curated_listings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Listing).where(Listing.curated == True).order_by(Listing.quality_score.desc())
    count_stmt = select(func.count()).select_from(Listing).where(Listing.curated == True)
    
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    listings = result.scalars().all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "listings": listings
    }

@router.get("/{id}", response_model=ListingResponse)
async def get_listing(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Listing).where(Listing.id == id)
    result = await db.execute(stmt)
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

@router.get("/{id}/curation")
async def get_listing_curation(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Listing).where(Listing.id == id)
    result = await db.execute(stmt)
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not listing.curated:
        raise HTTPException(status_code=400, detail="Listing is not curated yet")
    
    return {
        "id": listing.id,
        "curated": listing.curated,
        "quality_score": listing.quality_score,
        "tags": listing.tags,
        "summary": listing.summary,
        "normalized_data": listing.normalized_data,
        "curation_model": listing.curation_model,
        "curated_at": listing.curated_at
    }
