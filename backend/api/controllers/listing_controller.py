from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for backend modules
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from ..dependencies import get_db
from schemas import ListingResponse, PaginatedListingsResponse, StatsResponse
from services import ListingService

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
    service = ListingService(db)
    listings, total = await service.get_listings(
        city=city,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        source=source,
        min_quality=min_quality,
        tags=tags,
        curated_only=False,
        limit=limit,
        page=page
    )
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "listings": listings
    }

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    service = ListingService(db)
    stats = await service.get_statistics()
    return stats

@router.get("/curated", response_model=PaginatedListingsResponse)
async def get_curated_listings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    service = ListingService(db)
    listings, total = await service.get_listings(
        curated_only=True,
        limit=limit,
        page=page
    )
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "listings": listings
    }

@router.get("/{id}", response_model=ListingResponse)
async def get_listing(id: int, db: AsyncSession = Depends(get_db)):
    service = ListingService(db)
    listing = await service.get_listing_by_id(id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

@router.get("/{id}/curation")
async def get_listing_curation(id: int, db: AsyncSession = Depends(get_db)):
    service = ListingService(db)
    listing = await service.get_listing_by_id(id)
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
