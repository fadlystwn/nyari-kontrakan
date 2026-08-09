from fastapi import APIRouter, BackgroundTasks, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..curation_task import run_api_curation
from ..auth import verify_api_key

router = APIRouter(prefix="/curation", tags=["curation"], dependencies=[Depends(verify_api_key)])
limiter = Limiter(key_func=get_remote_address)

@router.post("/trigger")
@limiter.limit("5/minute")  # Limit to 5 triggers per minute per IP
async def trigger_curation(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_api_curation)
    return {"status": "Curation batch triggered in background"}
