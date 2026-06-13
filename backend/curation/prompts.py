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
