from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from .database import get_db, engine, Base
from .schemas import HealthCheckResponse
from .routers import listings, curation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Property Data Scraper API",
    description="REST API for accessing scraped and curated Indonesian property listing data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up FastAPI application...")
    try:
        # Fallback table creation if not already created by DB initialization script
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database connection and tables verified.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

# Register routers
app.include_router(listings.router)
app.include_router(curation.router)

@app.get("/health", response_model=HealthCheckResponse, tags=["health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Execute simple query to test DB connection
        await db.execute(select(1))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Health check failed for database: {e}")
    
    return HealthCheckResponse(status="ok", database=db_status)
