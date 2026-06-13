from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from pathlib import Path

# Add parent directory to path for backend modules
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from database import SessionManager
from models import Base
from config import settings
from .controllers import listing_controller, curation_controller, health_controller

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
        session_manager = SessionManager(settings.database_url)
        async with session_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database connection and tables verified.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

# Register routers
app.include_router(listing_controller.router)
app.include_router(curation_controller.router)
app.include_router(health_controller.router)
