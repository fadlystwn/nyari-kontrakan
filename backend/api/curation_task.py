import os
import httpx
import json
import asyncio
import logging
from datetime import datetime
from sqlalchemy import select, update
from .database import AsyncSessionLocal
from .models import Listing

logger = logging.getLogger(__name__)

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/gemini-2.5-flash:generateContent"
)

def build_curation_prompt(listing: dict) -> str:
    description = ""
    if listing.get("raw_data") and isinstance(listing["raw_data"], dict):
        description = listing["raw_data"].get("description", "") or ""
    
    return f"""
You are a real estate data curator for an Indonesian property platform.
Analyze the following raw property listing and return a JSON object only.

RAW LISTING:
- Title       : {listing.get('title', '')}
- Price       : {listing.get('price', '')}
- Location    : {listing.get('location', '')}
- Bedrooms    : {listing.get('bedrooms', '')}
- Bathrooms   : {listing.get('bathrooms', '')}
- Land Area   : {listing.get('land_area_sqm', '')} sqm
- Building    : {listing.get('building_area_sqm', '')} sqm
- Description : {description[:800]}
- Photos      : {len(listing.get('photos') or [])} photos
- Source      : {listing.get('source', '')}

Return ONLY a valid JSON object with this exact schema:
{{
  "quality_score": <integer 0-100>,
  "tags": [<list of short English/Indonesian keyword tags, max 8>],
  "summary": "<2-3 sentence Indonesian summary of the listing>",
  "normalized": {{
    "bedrooms": <integer or null>,
    "bathrooms": <integer or null>,
    "land_area_sqm": <integer or null>,
    "building_area_sqm": <integer or null>,
    "furnishing": "<unfurnished|semi-furnished|furnished|unknown>",
    "condition": "<new|good|needs-renovation|unknown>"
  }},
  "is_duplicate_candidate": <true|false>
}}

Quality score guide:
- 80–100 : Complete data, many photos, detailed description, plausible price
- 50–79  : Moderate completeness, some fields missing
- 0–49   : Sparse data, no photos, suspicious price, or very short description
"""

async def curate_single_listing(client: httpx.AsyncClient, api_key: str, listing_dict: dict) -> dict:
    prompt = build_curation_prompt(listing_dict)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 1024,
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }
    
    resp = await client.post(
        f"{GEMINI_API_URL}?key={api_key}",
        json=payload,
        timeout=30.0
    )
    resp.raise_for_status()
    data = resp.json()
    
    # Extract response text
    text_content = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text_content)

async def run_api_curation():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set. Skipping curation trigger.")
        return

    batch_size = int(os.getenv("CURATION_BATCH_SIZE", "10"))
    rate_limit_delay = float(os.getenv("CURATION_RATE_LIMIT_DELAY", "1.0"))

    async with AsyncSessionLocal() as session:
        # Fetch uncurated listings
        stmt = (
            select(Listing)
            .where(Listing.curated == False)
            .order_by(Listing.scraped_at.desc())
            .limit(batch_size)
        )
        result = await session.execute(stmt)
        listings = result.scalars().all()

        if not listings:
            logger.info("No uncurated listings found.")
            return

        logger.info(f"Triggered curation for {len(listings)} listings...")

        async with httpx.AsyncClient() as client:
            for listing in listings:
                listing_dict = {
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
                    curation_result = await curate_single_listing(client, api_key, listing_dict)
                    
                    listing.curated = True
                    listing.quality_score = curation_result.get("quality_score")
                    listing.tags = curation_result.get("tags", [])
                    listing.summary = curation_result.get("summary")
                    listing.normalized_data = curation_result.get("normalized", {})
                    listing.curation_model = "gemini-2.5-flash"
                    listing.curated_at = datetime.utcnow()
                    
                    await session.commit()
                    logger.info(f"Successfully curated listing ID {listing.id} with score {listing.quality_score}")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Failed to curate listing ID {listing.id}: {e}")

                await asyncio.sleep(rate_limit_delay)
