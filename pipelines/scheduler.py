import logging
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from pipelines.ingest_and_process import run as run_ingestion
from pipelines.train_pipeline import run as run_training
from utils.logger import setup_logging


def _job() -> None:
    logger = logging.getLogger(__name__)
    logger.info("Scheduled retraining job started")
    run_ingestion()
    run_training()
    logger.info("Scheduled retraining job finished")


def start_scheduler() -> None:
    setup_logging()
    scheduler = BlockingScheduler(timezone="UTC")
    # Every Saturday at 12:00 UTC
    scheduler.add_job(_job, "cron", day_of_week="sat", hour=12, minute=0, id="weekly_retrain")
    logging.getLogger(__name__).info("Scheduler started: Saturdays at 12:00 UTC")
    scheduler.start()


if __name__ == "__main__":
    start_scheduler()
