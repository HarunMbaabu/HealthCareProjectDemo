import logging
from pathlib import Path

from data.ingestion import DataIngestion
from data.preprocessing import DataPreprocessor
from data.storage import DataStorage
from utils.db import get_engine
from utils.logger import setup_logging


def run(csv_path: str | Path = "healthcare_dataset.csv") -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    engine = get_engine()
    ingestion = DataIngestion(engine)
    preprocessor = DataPreprocessor()
    storage = DataStorage(engine)

    df = ingestion.load_csv(csv_path)
    ingestion.store_raw_data(df)

    cleaned = preprocessor.clean(df)
    storage.upsert_processed_data(cleaned)
    logger.info("Ingestion + processing pipeline completed")


if __name__ == "__main__":
    run()
