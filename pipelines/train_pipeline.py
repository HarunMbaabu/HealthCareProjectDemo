import json
import logging
from pathlib import Path

from data.storage import DataStorage
from models.trainer import ModelTrainer
from utils.config import get_settings
from utils.db import get_engine
from utils.logger import setup_logging


def run() -> Path:
    setup_logging()
    logger = logging.getLogger(__name__)
    settings = get_settings()

    engine = get_engine()
    storage = DataStorage(engine)
    trainer = ModelTrainer(settings.random_state)

    processed = storage.fetch_processed_data()
    best_name, best_model, results = trainer.train(processed)
    model_path = trainer.save_model(best_model, settings.model_dir, settings.model_file_name)

    metrics_path = settings.model_dir / "metrics.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump({"best_model": best_name, "all_metrics": results}, f, indent=2)

    logger.info("Training complete. Best model=%s", best_name)
    logger.info("Metrics saved to %s", metrics_path)
    return model_path


if __name__ == "__main__":
    run()
