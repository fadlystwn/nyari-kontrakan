from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, SmallInteger, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from .database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(64), nullable=False, index=True)
    external_id = Column(String(255), unique=True, nullable=False)
    title = Column(Text, nullable=False)
    price = Column(BigInteger, index=True)
    location = Column(Text)
    city = Column(String(128), index=True)
    property_type = Column(String(64), index=True)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    land_area_sqm = Column(Integer)
    building_area_sqm = Column(Integer)
    url = Column(Text, nullable=False)
    photos = Column(ARRAY(Text))
    raw_data = Column(JSONB)
    scraped_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Curation Fields
    curated = Column(Boolean, nullable=False, default=False, index=True)
    quality_score = Column(SmallInteger, index=True)
    tags = Column(ARRAY(Text))
    summary = Column(Text)
    normalized_data = Column(JSONB)
    curation_model = Column(String(64))
    curated_at = Column(DateTime(timezone=True))
