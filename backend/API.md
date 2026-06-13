# API Documentation - Property Data Scraper System

Complete API reference for the Property Data Scraper REST API.

## Base URL

- **Local Development:** `http://localhost:8000`
- **Production:** `https://yourdomain.com/api`

## Interactive Documentation

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

---

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

> **Note:** For production deployments, consider adding API key authentication or OAuth2.

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/listings` | Get paginated listings with filters |
| GET | `/listings/{id}` | Get single listing by ID |
| GET | `/listings/stats` | Get aggregate statistics |
| GET | `/listings/curated` | Get curated listings sorted by quality |
| GET | `/listings/{id}/curation` | Get curation details for a listing |
| POST | `/curation/trigger` | Manually trigger curation batch |

---

## Health Check

### `GET /health`

Check API and database connectivity status.

**Response:**
```json
{
  "status": "ok",
  "database": "healthy"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

## Listings Endpoints

### `GET /listings`

Get paginated property listings with optional filters.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (min: 1) |
| `limit` | integer | No | 20 | Items per page (min: 1, max: 100) |
| `city` | string | No | - | Filter by city (case-insensitive) |
| `property_type` | string | No | - | Filter by property type |
| `min_price` | integer | No | - | Minimum price in IDR |
| `max_price` | integer | No | - | Maximum price in IDR |
| `source` | string | No | - | Filter by source (olx, rumah123) |
| `min_quality` | integer | No | - | Minimum quality score (0-100) |
| `tags` | string | No | - | Comma-separated tags to filter by |

#### Response Schema

```json
{
  "total": 150,
  "page": 1,
  "limit": 20,
  "listings": [
    {
      "id": 1,
      "source": "olx",
      "external_id": "olx-123456",
      "title": "Rumah Minimalis 2 Lantai di Jakarta Selatan",
      "price": 1500000000,
      "location": "Kebayoran Baru, Jakarta Selatan",
      "city": "Jakarta",
      "property_type": "house",
      "bedrooms": 3,
      "bathrooms": 2,
      "land_area_sqm": 120,
      "building_area_sqm": 150,
      "url": "https://www.olx.co.id/item/...",
      "photos": [
        "https://cdn.olx.co.id/photo1.jpg",
        "https://cdn.olx.co.id/photo2.jpg"
      ],
      "raw_data": { ... },
      "scraped_at": "2026-06-12T10:30:00Z",
      "updated_at": "2026-06-12T10:30:00Z",
      "curated": true,
      "quality_score": 85,
      "tags": ["furnished", "near-toll", "strategic"],
      "summary": "Rumah minimalis 2 lantai dengan 3 kamar tidur di lokasi strategis Kebayoran Baru. Dekat dengan akses tol dan fasilitas umum.",
      "normalized_data": {
        "bedrooms": 3,
        "bathrooms": 2,
        "land_area_sqm": 120,
        "building_area_sqm": 150,
        "furnishing": "furnished",
        "condition": "good"
      },
      "curation_model": "gemini-2.5-flash",
      "curated_at": "2026-06-12T11:00:00Z"
    }
  ]
}
```

#### Examples

**Basic pagination:**
```bash
curl "http://localhost:8000/listings?page=1&limit=20"
```

**Filter by city:**
```bash
curl "http://localhost:8000/listings?city=jakarta"
```

**Filter by property type:**
```bash
curl "http://localhost:8000/listings?property_type=house"
```

**Price range filter:**
```bash
curl "http://localhost:8000/listings?min_price=500000000&max_price=2000000000"
```

**Multiple filters:**
```bash
curl "http://localhost:8000/listings?city=jakarta&property_type=house&min_price=1000000000&max_price=3000000000&min_quality=70"
```

**Filter by tags:**
```bash
curl "http://localhost:8000/listings?tags=furnished,near-toll"
```

**Filter by source:**
```bash
curl "http://localhost:8000/listings?source=olx"
```

---

### `GET /listings/{id}`

Get detailed information for a single listing.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Listing ID |

#### Response Schema

```json
{
  "id": 1,
  "source": "olx",
  "external_id": "olx-123456",
  "title": "Rumah Minimalis 2 Lantai di Jakarta Selatan",
  "price": 1500000000,
  "location": "Kebayoran Baru, Jakarta Selatan",
  "city": "Jakarta",
  "property_type": "house",
  "bedrooms": 3,
  "bathrooms": 2,
  "land_area_sqm": 120,
  "building_area_sqm": 150,
  "url": "https://www.olx.co.id/item/...",
  "photos": ["https://cdn.olx.co.id/photo1.jpg"],
  "raw_data": {
    "description": "Full listing description...",
    "seller": "John Doe",
    "posted_date": "2026-06-10"
  },
  "scraped_at": "2026-06-12T10:30:00Z",
  "updated_at": "2026-06-12T10:30:00Z",
  "curated": true,
  "quality_score": 85,
  "tags": ["furnished", "near-toll"],
  "summary": "Rumah minimalis 2 lantai...",
  "normalized_data": { ... },
  "curation_model": "gemini-2.5-flash",
  "curated_at": "2026-06-12T11:00:00Z"
}
```

#### Error Responses

**404 Not Found:**
```json
{
  "detail": "Listing not found"
}
```

#### Examples

```bash
curl "http://localhost:8000/listings/1"
```

---

### `GET /listings/stats`

Get aggregate statistics about listings.

#### Response Schema

```json
{
  "count_by_city": [
    {
      "city": "Jakarta",
      "count": 450
    },
    {
      "city": "Bandung",
      "count": 120
    },
    {
      "city": "Surabaya",
      "count": 85
    }
  ],
  "avg_price_by_type": [
    {
      "property_type": "house",
      "avg_price": 1850000000.50
    },
    {
      "property_type": "apartment",
      "avg_price": 950000000.25
    },
    {
      "property_type": "land",
      "avg_price": 2500000000.00
    }
  ]
}
```

#### Examples

```bash
curl "http://localhost:8000/listings/stats"
```

---

### `GET /listings/curated`

Get only curated listings, sorted by quality score (highest first).

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number |
| `limit` | integer | No | 20 | Items per page (max: 100) |

#### Response Schema

Same as `/listings` endpoint, but only includes listings where `curated = true`, sorted by `quality_score DESC`.

#### Examples

```bash
curl "http://localhost:8000/listings/curated?page=1&limit=10"
```

---

### `GET /listings/{id}/curation`

Get detailed curation information for a specific listing.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Listing ID |

#### Response Schema

```json
{
  "id": 1,
  "curated": true,
  "quality_score": 85,
  "tags": ["furnished", "near-toll", "strategic"],
  "summary": "Rumah minimalis 2 lantai dengan 3 kamar tidur di lokasi strategis Kebayoran Baru. Dekat dengan akses tol dan fasilitas umum.",
  "normalized_data": {
    "bedrooms": 3,
    "bathrooms": 2,
    "land_area_sqm": 120,
    "building_area_sqm": 150,
    "furnishing": "furnished",
    "condition": "good"
  },
  "curation_model": "gemini-2.5-flash",
  "curated_at": "2026-06-12T11:00:00Z"
}
```

#### Error Responses

**404 Not Found:**
```json
{
  "detail": "Listing not found"
}
```

**400 Bad Request (not curated):**
```json
{
  "detail": "Listing is not curated yet"
}
```

#### Examples

```bash
curl "http://localhost:8000/listings/1/curation"
```

---

## Curation Endpoints

### `POST /curation/trigger`

Manually trigger a curation batch job to process uncurated listings.

#### Request Body

None required.

#### Response Schema

```json
{
  "status": "Curation batch triggered in background"
}
```

#### Examples

```bash
curl -X POST "http://localhost:8000/curation/trigger"
```

**Note:** This endpoint triggers a background task. Check scraper logs to monitor progress:
```bash
docker compose logs -f scraper | grep -i curation
```

---

## Data Models

### Listing Object

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | integer | No | Unique listing ID |
| `source` | string | No | Source platform (olx, rumah123) |
| `external_id` | string | No | Unique ID from source site |
| `title` | string | No | Listing title |
| `price` | integer | Yes | Price in IDR |
| `location` | string | Yes | Full location string |
| `city` | string | Yes | Normalized city name |
| `property_type` | string | Yes | Property type (house, apartment, land) |
| `bedrooms` | integer | Yes | Number of bedrooms |
| `bathrooms` | integer | Yes | Number of bathrooms |
| `land_area_sqm` | integer | Yes | Land area in m² |
| `building_area_sqm` | integer | Yes | Building area in m² |
| `url` | string | No | Source URL |
| `photos` | array[string] | Yes | Array of photo URLs |
| `raw_data` | object | Yes | Full raw data from source |
| `scraped_at` | datetime | No | When listing was scraped |
| `updated_at` | datetime | No | Last update timestamp |
| `curated` | boolean | No | Whether listing has been curated |
| `quality_score` | integer | Yes | Quality score 0-100 |
| `tags` | array[string] | Yes | Auto-generated tags |
| `summary` | string | Yes | LLM-generated summary |
| `normalized_data` | object | Yes | Cleaned/normalized fields |
| `curation_model` | string | Yes | Model used for curation |
| `curated_at` | datetime | Yes | When curation completed |

### Normalized Data Object

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `bedrooms` | integer | - | Normalized bedroom count |
| `bathrooms` | integer | - | Normalized bathroom count |
| `land_area_sqm` | integer | - | Normalized land area |
| `building_area_sqm` | integer | - | Normalized building area |
| `furnishing` | string | unfurnished, semi-furnished, furnished, unknown | Furnishing status |
| `condition` | string | new, good, needs-renovation, unknown | Property condition |

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid request body |
| 500 | Internal Server Error |

### Validation Error Response

```json
{
  "detail": [
    {
      "loc": ["query", "page"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production deployments, consider:

- Implementing API key authentication
- Adding rate limiting middleware
- Using Nginx rate limiting

**Example Nginx rate limiting:**
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://127.0.0.1:8000/;
}
```

---

## CORS Configuration

The API is configured to allow all origins by default:

```python
allow_origins=["*"]
```

For production, restrict to specific domains:

```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

---

## Pagination

All list endpoints support pagination with:
- `page`: Page number (default: 1, min: 1)
- `limit`: Items per page (default: 20, min: 1, max: 100)

**Response includes:**
- `total`: Total number of items
- `page`: Current page number
- `limit`: Items per page
- `listings`: Array of listing objects

**Calculate total pages:**
```
total_pages = ceil(total / limit)
```

---

## Filtering Best Practices

### Combining Filters

Filters are combined with AND logic:

```bash
# Returns houses in Jakarta with price between 1B-3B IDR
curl "http://localhost:8000/listings?city=jakarta&property_type=house&min_price=1000000000&max_price=3000000000"
```

### Case Sensitivity

String filters (city, property_type, source) are **case-insensitive**:

```bash
# These are equivalent
curl "http://localhost:8000/listings?city=jakarta"
curl "http://localhost:8000/listings?city=Jakarta"
curl "http://localhost:8000/listings?city=JAKARTA"
```

### Tag Filtering

Multiple tags use AND logic (listing must have all specified tags):

```bash
# Returns listings with BOTH "furnished" AND "near-toll" tags
curl "http://localhost:8000/listings?tags=furnished,near-toll"
```

---

## Examples with Python

### Using `requests` library

```python
import requests

# Get listings
response = requests.get("http://localhost:8000/listings", params={
    "city": "jakarta",
    "property_type": "house",
    "min_price": 1000000000,
    "max_price": 3000000000,
    "page": 1,
    "limit": 20
})

data = response.json()
print(f"Total: {data['total']}")
for listing in data['listings']:
    print(f"{listing['title']} - Rp {listing['price']:,}")

# Get single listing
listing = requests.get("http://localhost:8000/listings/1").json()
print(listing['title'])

# Trigger curation
response = requests.post("http://localhost:8000/curation/trigger")
print(response.json())
```

### Using `httpx` (async)

```python
import httpx
import asyncio

async def get_listings():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/listings", params={
            "city": "jakarta",
            "limit": 10
        })
        return response.json()

data = asyncio.run(get_listings())
print(data)
```

---

## Examples with JavaScript

### Using `fetch` API

```javascript
// Get listings
async function getListings() {
    const params = new URLSearchParams({
        city: 'jakarta',
        property_type: 'house',
        min_price: 1000000000,
        max_price: 3000000000,
        page: 1,
        limit: 20
    });
    
    const response = await fetch(`http://localhost:8000/listings?${params}`);
    const data = await response.json();
    
    console.log(`Total: ${data.total}`);
    data.listings.forEach(listing => {
        console.log(`${listing.title} - Rp ${listing.price.toLocaleString()}`);
    });
}

// Get single listing
async function getListing(id) {
    const response = await fetch(`http://localhost:8000/listings/${id}`);
    const listing = await response.json();
    return listing;
}

// Trigger curation
async function triggerCuration() {
    const response = await fetch('http://localhost:8000/curation/trigger', {
        method: 'POST'
    });
    const result = await response.json();
    console.log(result.status);
}
```

---

## Monitoring API Usage

### Check API Health

```bash
curl http://localhost:8000/health
```

### View API Logs

```bash
docker compose logs -f api
```

### Monitor Request Count

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/access.log | grep "/api/"
```

---

## Future Enhancements

Planned features for future API versions:

- [ ] API key authentication
- [ ] Rate limiting per API key
- [ ] Webhook notifications for new listings
- [ ] Export endpoints (CSV, JSON)
- [ ] Full-text search on title and description
- [ ] Advanced filtering (distance from location, amenities)
- [ ] Batch operations (bulk update, delete)
- [ ] GraphQL endpoint (alternative to REST)

---

## Support

For API issues:
- Check `/docs` for interactive testing
- Review logs: `docker compose logs -f api`
- Consult README.md for setup instructions
- Check DEPLOYMENT.md for production configuration
