from fastapi import APIRouter, BackgroundTasks
from ..curation_task import run_api_curation

router = APIRouter(prefix="/curation", tags=["curation"])

@router.post("/trigger")
async def trigger_curation(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_api_curation)
    return {"status": "Curation batch triggered in background"}
