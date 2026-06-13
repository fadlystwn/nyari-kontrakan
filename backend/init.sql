-- Initialize schema for Property Scraper System database
CREATE TABLE IF NOT EXISTS listings (
    id              SERIAL PRIMARY KEY,
    source          VARCHAR(64)     NOT NULL,          -- e.g. 'olx', 'rumah123'
    external_id     VARCHAR(255)    UNIQUE NOT NULL,   -- unique ID from source site
    title           TEXT            NOT NULL,
    price           BIGINT,                            -- stored in IDR
    location        TEXT,
    city            VARCHAR(128),
    property_type   VARCHAR(64),                       -- e.g. 'house', 'apartment', 'land'
    bedrooms        INTEGER,
    bathrooms       INTEGER,
    land_area_sqm   INTEGER,
    building_area_sqm INTEGER,
    url             TEXT            NOT NULL,
    photos          TEXT[],                            -- array of image URLs
    raw_data        JSONB,                             -- full raw payload for future use
    scraped_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    
    -- Curation Fields
    curated          BOOLEAN         NOT NULL DEFAULT FALSE,
    quality_score    SMALLINT,                          -- 0–100
    tags             TEXT[],                            -- e.g. ['furnished', 'near-toll']
    summary          TEXT,                              -- LLM-generated 2–3 sentence summary
    normalized_data  JSONB,                             -- cleaned/canonical field values
    curation_model   VARCHAR(64),                       -- e.g. 'gemini-2.5-flash'
    curated_at       TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_listings_city     ON listings(city);
CREATE INDEX IF NOT EXISTS idx_listings_price    ON listings(price);
CREATE INDEX IF NOT EXISTS idx_listings_type     ON listings(property_type);
CREATE INDEX IF NOT EXISTS idx_listings_source   ON listings(source);
CREATE INDEX IF NOT EXISTS idx_listings_scraped  ON listings(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_listings_curated  ON listings(curated);
CREATE INDEX IF NOT EXISTS idx_listings_quality  ON listings(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_listings_tags     ON listings USING GIN(tags);
