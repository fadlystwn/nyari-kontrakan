from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import sys
from pathlib import Path

# Add parent directory to path for backend modules
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from ..dependencies import get_db
from schemas import HealthCheckResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Execute simple query to test DB connection
        await db.execute(select(1))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Health check failed for database: {e}")
    
    return HealthCheckResponse(status="ok", database=db_status)
