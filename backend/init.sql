CREATE TABLE IF NOT EXISTS listings (
    id              SERIAL PRIMARY KEY,
    source          VARCHAR(64)     NOT NULL,
    external_id     VARCHAR(255)    UNIQUE NOT NULL,
    title           TEXT            NOT NULL,
    price           BIGINT,
    location        TEXT,
    city            VARCHAR(128),
    property_type   VARCHAR(64),
    bedrooms        INTEGER,
    bathrooms       INTEGER,
    land_area_sqm   INTEGER,
    building_area_sqm INTEGER,
    url             TEXT            NOT NULL,
    photos          TEXT[],
    raw_data        JSONB,
    scraped_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    
    curated          BOOLEAN         NOT NULL DEFAULT FALSE,
    quality_score    SMALLINT,
    tags             TEXT[],
    summary          TEXT,
    normalized_data  JSONB,
    curation_model   VARCHAR(64),
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
