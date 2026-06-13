from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class NormalizedData(BaseModel):
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    land_area_sqm: Optional[int] = None
    building_area_sqm: Optional[int] = None
    furnishing: Optional[str] = None
    condition: Optional[str] = None

class ListingBase(BaseModel):
    source: str
    external_id: str
    title: str
    price: Optional[int] = None
    location: Optional[str] = None
    city: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    land_area_sqm: Optional[int] = None
    building_area_sqm: Optional[int] = None
    url: str
    photos: Optional[List[str]] = []

class ListingResponse(ListingBase):
    id: int
    raw_data: Optional[Dict[str, Any]] = None
    scraped_at: datetime
    updated_at: datetime
    curated: bool
    quality_score: Optional[int] = None
    tags: Optional[List[str]] = []
    summary: Optional[str] = None
    normalized_data: Optional[NormalizedData] = None
    curation_model: Optional[str] = None
    curated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaginatedListingsResponse(BaseModel):
    total: int
    page: int
    limit: int
    listings: List[ListingResponse]

class CityStats(BaseModel):
    city: Optional[str] = None
    count: int

class TypeStats(BaseModel):
    property_type: Optional[str] = None
    avg_price: float

class StatsResponse(BaseModel):
    count_by_city: List[CityStats]
    avg_price_by_type: List[TypeStats]

class HealthCheckResponse(BaseModel):
    status: str
    database: str
