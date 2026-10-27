import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .workers import run_olx_scraper, run_rumah123_scraper, run_curation_worker

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

scheduler.add_job(run_olx_scraper, "cron", hour=0, minute=0)

scheduler.add_job(run_rumah123_scraper, "cron", hour=1, minute=0)

scheduler.add_job(run_curation_worker, "cron", hour=3, minute=0)
