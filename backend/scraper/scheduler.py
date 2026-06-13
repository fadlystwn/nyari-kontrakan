import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .workers import run_olx_scraper, run_rumah123_scraper, run_curation_worker

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# Wire schedules
# Run OLX scraper every day at 00:00 (midnight) server time
scheduler.add_job(run_olx_scraper, "cron", hour=0, minute=0)

# Run Rumah123 scraper every day at 01:00 server time
scheduler.add_job(run_rumah123_scraper, "cron", hour=1, minute=0)

# Run Curation after scrapers have completed, at 03:00 server time
scheduler.add_job(run_curation_worker, "cron", hour=3, minute=0)
