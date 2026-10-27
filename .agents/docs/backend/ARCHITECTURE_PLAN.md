# Backend Architecture Plan - Best Practice Refactoring

## 📋 Overview

Refactoring backend dari struktur campuran menjadi **Clean Architecture** dengan pola **Controller-Service-Model** yang konsisten dan scalable.

---

## 🎯 Tujuan Refactoring

1. **Separation of Concerns** - Pemisahan jelas antara HTTP handling, business logic, dan data access
2. **Consistency** - Struktur yang konsisten antara API dan Scraper
3. **Testability** - Mudah untuk unit testing dan integration testing
4. **Maintainability** - Kode yang mudah dipahami dan dimodifikasi
5. **Scalability** - Mudah menambah fitur baru tanpa mengubah struktur existing

---

## 🏗️ Proposed Architecture

```
backend/
├── api/                          # FastAPI Application (REST API)
│   ├── controllers/              # HTTP Request/Response handlers
│   │   ├── __init__.py
│   │   ├── listing_controller.py
│   │   ├── curation_controller.py
│   │   └── health_controller.py
│   ├── middlewares/              # Custom middlewares
│   │   ├── __init__.py
│   │   ├── cors.py
│   │   └── error_handler.py
│   ├── dependencies.py           # FastAPI dependencies (DB session, auth, etc)
│   ├── main.py                   # FastAPI app initialization
│   ├── Dockerfile
│   └── requirements.txt
│
├── scraper/                      # Scraper Worker Application
│   ├── scrapers/                 # Scraping logic (BeautifulSoup/Playwright)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── olx_scraper.py
│   │   └── rumah123_scraper.py
│   ├── workers/                  # Background job workers
│   │   ├── __init__.py
│   │   ├── scraper_worker.py
│   │   └── curation_worker.py
│   ├── scheduler.py              # APScheduler configuration
│   ├── main.py                   # Worker daemon entry point
│   ├── Dockerfile
│   └── requirements.txt
│
├── shared/                       # Shared code between API & Scraper
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   └── listing.py
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── listing_service.py
│   │   ├── scraper_service.py
│   │   └── curation_service.py
│   ├── schemas/                  # Pydantic schemas (validation & serialization)
│   │   ├── __init__.py
│   │   ├── listing_schema.py
│   │   └── curation_schema.py
│   ├── database/                 # Database configuration
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── session.py
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── parsers.py           # Price, Location parsers
│   │   └── validators.py
│   └── integrations/             # External service integrations
│       ├── __init__.py
│       └── gemini_client.py
│
├── tests/                        # Test suite
│   ├── unit/
│   │   ├── services/
│   │   └── utils/
│   ├── integration/
│   │   └── api/
│   └── conftest.py
│
├── deployment/                   # Deployment configs
│   └── nginx/
│
├── .env.template
├── .gitignore
├── docker-compose.yml
├── init.sql
└── README.md
```

---

## 📊 Layer Responsibilities

### 1. **Controllers** (HTTP Layer)

**Location:** `api/controllers/`

**Responsibilities:**

- Handle HTTP requests and responses
- Input validation (via Pydantic schemas)
- Call appropriate service methods
- Format responses
- Handle HTTP errors

**Example:**

```python
# api/controllers/listing_controller.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from shared.services import ListingService
from shared.schemas import ListingResponse, PaginatedListingsResponse
from ..dependencies import get_db

router = APIRouter(prefix="/listings", tags=["listings"])

@router.get("", response_model=PaginatedListingsResponse)
async def get_listings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    city: str = None,
    db: AsyncSession = Depends(get_db)
):
    service = ListingService(db)
    listings, total = await service.get_listings(
        city=city, limit=limit, page=page
    )
    return {"total": total, "page": page, "limit": limit, "listings": listings}
```

---

### 2. **Services** (Business Logic Layer)

**Location:** `shared/services/`

**Responsibilities:**

- Business logic implementation
- Data validation and transformation
- Coordinate between multiple data sources
- Transaction management
- Error handling and logging

**Example:**

```python
# shared/services/listing_service.py
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models import Listing

class ListingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_listings(
        self,
        city: Optional[str] = None,
        limit: int = 20,
        page: int = 1
    ) -> Tuple[List[Listing], int]:
        # Business logic here
        pass
```

---

### 3. **Models** (Data Layer)

**Location:** `shared/models/`

**Responsibilities:**

- Define database schema (SQLAlchemy ORM)
- Database relationships
- Table constraints and indexes

**Example:**

```python
# shared/models/listing.py
from sqlalchemy import Column, Integer, String, Text, Boolean
from shared.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    # ... other fields
```

---

### 4. **Schemas** (Validation & Serialization Layer)

**Location:** `shared/schemas/`

**Responsibilities:**

- Request/Response validation (Pydantic)
- Data serialization
- API documentation (OpenAPI)

**Example:**

```python
# shared/schemas/listing_schema.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ListingResponse(BaseModel):
    id: int
    title: str
    price: Optional[int]
    city: Optional[str]

    class Config:
        from_attributes = True
```

---

### 5. **Scrapers** (Data Collection Layer)

**Location:** `scraper/scrapers/`

**Responsibilities:**

- Web scraping logic
- HTML parsing
- Data extraction
- Handle anti-scraping measures

**Example:**

```python
# scraper/scrapers/olx_scraper.py
from .base import BaseScraper

class OLXScraper(BaseScraper):
    source = "olx"
    base_url = "https://www.olx.co.id"

    async def scrape(self, city: str) -> List[dict]:
        # Scraping logic
        pass
```

---

### 6. **Workers** (Background Jobs Layer)

**Location:** `scraper/workers/`

**Responsibilities:**

- Execute scheduled tasks
- Coordinate scraping jobs
- Handle job failures and retries
- Logging and monitoring

**Example:**

```python
# scraper/workers/scraper_worker.py
from shared.services import ScraperService
from shared.database import SessionManager
from ..scrapers import OLXScraper

async def run_olx_scraper():
    async with SessionManager().session() as session:
        service = ScraperService(session)
        scraper = OLXScraper()

        raw_data = await scraper.scrape(city="jakarta")
        count = await service.save_listings(raw_data, scraper)

        await session.commit()
```

---

## 🔄 Migration Strategy

### Phase 1: Preparation (No Breaking Changes)

1. ✅ Create new directory structure
2. ✅ Create `ARCHITECTURE_PLAN.md` (this document)
3. ✅ Setup testing framework

### Phase 2: Move Models & Schemas

1. Move `api/models.py` → `shared/models/listing.py`
2. Move `api/schemas.py` → `shared/schemas/listing_schema.py`
3. Update all imports
4. Test: Ensure API still works

### Phase 3: Refactor Services

1. Split `shared/services.py` into:
   - `shared/services/listing_service.py`
   - `shared/services/scraper_service.py`
2. Move `shared/curation/service.py` → `shared/services/curation_service.py`
3. Update all imports
4. Test: Ensure services work correctly

### Phase 4: Refactor Controllers

1. Rename `api/routers/` → `api/controllers/`
2. Rename files:
   - `listings.py` → `listing_controller.py`
   - `curation.py` → `curation_controller.py`
3. Extract health check to `health_controller.py`
4. Update imports in `main.py`
5. Test: Ensure all endpoints work

### Phase 5: Refactor Scrapers

1. Rename scrapers:
   - `olx.py` → `olx_scraper.py`
   - `rumah123.py` → `rumah123_scraper.py`
2. Create `scraper/workers/` directory
3. Extract worker logic from `scheduler.py` to:
   - `scraper_worker.py`
   - `curation_worker.py`
4. Update `scheduler.py` to use workers
5. Test: Ensure scraping still works

### Phase 6: Organize Utilities

1. Move parsers from `shared/utils.py` to `shared/utils/parsers.py`
2. Move Gemini client to `shared/integrations/gemini_client.py`
3. Move prompts to `shared/integrations/prompts.py`
4. Update all imports
5. Test: Ensure utilities work

### Phase 7: Cleanup & Documentation

1. Remove old files
2. Update README.md
3. Update API.md
4. Add inline documentation
5. Final testing

---

## 📝 File Mapping (Old → New)

### API Module

```
api/routers/listings.py       → api/controllers/listing_controller.py
api/routers/curation.py       → api/controllers/curation_controller.py
api/main.py (health endpoint) → api/controllers/health_controller.py
api/models.py                 → shared/models/listing.py
api/schemas.py                → shared/schemas/listing_schema.py
api/database.py               → api/dependencies.py (refactored)
```

### Scraper Module

```
scraper/scrapers/olx.py       → scraper/scrapers/olx_scraper.py
scraper/scrapers/rumah123.py  → scraper/scrapers/rumah123_scraper.py
scraper/scheduler.py (jobs)   → scraper/workers/scraper_worker.py
scraper/scheduler.py (jobs)   → scraper/workers/curation_worker.py
```

### Shared Module

```
shared/services.py            → shared/services/listing_service.py
                              → shared/services/scraper_service.py
shared/curation/service.py    → shared/services/curation_service.py
shared/curation/gemini_client.py → shared/integrations/gemini_client.py
shared/curation/prompts.py    → shared/integrations/prompts.py
shared/utils.py               → shared/utils/parsers.py
shared/database/models.py     → shared/models/listing.py (merge with api/models.py)
```

---

## ✅ Benefits After Refactoring

### 1. **Clear Separation of Concerns**

- Controllers hanya handle HTTP
- Services hanya handle business logic
- Models hanya handle data structure
- Scrapers hanya handle data collection

### 2. **Easier Testing**

```python
# Test service tanpa HTTP layer
async def test_listing_service():
    service = ListingService(mock_session)
    listings, total = await service.get_listings(city="jakarta")
    assert total > 0
```

### 3. **Reusable Components**

```python
# Service bisa dipakai di API dan Worker
from shared.services import ListingService

# Di API Controller
service = ListingService(db)
listings = await service.get_listings()

# Di Scraper Worker
service = ListingService(db)
listing = await service.get_listing_by_id(123)
```

### 4. **Better Code Organization**

- Mudah menemukan file yang dicari
- Struktur yang predictable
- Konsisten dengan industry standard

### 5. **Scalability**

- Mudah menambah controller baru
- Mudah menambah service baru
- Mudah menambah scraper baru
- Tidak perlu ubah struktur existing

---

## 🚀 Implementation Priority

### High Priority (Core Functionality)

1. ✅ Models & Schemas separation
2. ✅ Services refactoring
3. ✅ Controllers refactoring

### Medium Priority (Code Organization)

4. ✅ Scrapers refactoring
5. ✅ Workers extraction
6. ✅ Utils organization

### Low Priority (Nice to Have)

7. ⏳ Testing framework
8. ⏳ Middleware extraction
9. ⏳ Documentation updates

---

## 📚 Naming Conventions

### Files

- Controllers: `*_controller.py`
- Services: `*_service.py`
- Models: `*.py` (singular, e.g., `listing.py`)
- Schemas: `*_schema.py`
- Scrapers: `*_scraper.py`
- Workers: `*_worker.py`

### Classes

- Controllers: `*Controller` (optional, bisa pakai router saja)
- Services: `*Service` (e.g., `ListingService`)
- Models: Singular noun (e.g., `Listing`)
- Schemas: `*Response`, `*Request`, `*Schema`
- Scrapers: `*Scraper` (e.g., `OLXScraper`)

### Functions

- Controllers: HTTP verbs (e.g., `get_listings`, `create_listing`)
- Services: Business actions (e.g., `find_listings`, `save_listing`)
- Scrapers: `scrape`, `parse_listing`
- Workers: `run_*` (e.g., `run_olx_scraper`)

---

## 🔍 Code Examples

### Before (Current)

```python
# api/routers/listings.py
from ..database import get_db
from ..schemas import ListingResponse
from shared import ListingService

@router.get("/{id}")
async def get_listing(id: int, db: AsyncSession = Depends(get_db)):
    service = ListingService(db)
    listing = await service.get_listing_by_id(id)
    return listing
```

### After (Proposed)

```python
# api/controllers/listing_controller.py
from ..dependencies import get_db
from shared.schemas import ListingResponse
from shared.services import ListingService

@router.get("/{id}", response_model=ListingResponse)
async def get_listing(id: int, db: AsyncSession = Depends(get_db)):
    service = ListingService(db)
    listing = await service.get_listing_by_id(id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing
```

---

## 🎓 Best Practices Applied

1. ✅ **Single Responsibility Principle** - Each layer has one clear purpose
2. ✅ **Dependency Injection** - Services receive dependencies via constructor
3. ✅ **Interface Segregation** - Small, focused interfaces
4. ✅ **DRY (Don't Repeat Yourself)** - Shared code in `shared/`
5. ✅ **Explicit over Implicit** - Clear naming and structure
6. ✅ **Separation of Concerns** - HTTP, Business Logic, Data Access separated
7. ✅ **Testability** - Easy to mock and test each layer
8. ✅ **Scalability** - Easy to add new features

---

## 📖 References

- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SQLAlchemy Best Practices](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 🤝 Next Steps

1. Review this architecture plan
2. Get team approval
3. Start Phase 1 implementation
4. Test each phase before moving to next
5. Update documentation as we go

---

**Last Updated:** 2026-06-13  
**Status:** ✅ Implemented  
**Approved By:** Implemented and Ready for Testing
