from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
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

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Conditionally enable docs based on environment
docs_url = "/docs" if settings.enable_docs else None
redoc_url = "/redoc" if settings.enable_docs else None

app = FastAPI(
    title="Property Data Scraper API",
    description="REST API for accessing scraped and curated Indonesian property listing data",
    version="1.0.0",
    docs_url=docs_url,
    redoc_url=redoc_url
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Configure CORS to allow frontend connections
# Get allowed origins from environment or use localhost for development
allowed_origins = settings.allowed_origins if hasattr(settings, 'allowed_origins') else [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
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
