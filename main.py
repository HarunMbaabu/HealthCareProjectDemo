from pipelines.ingest_and_process import run as run_ingestion
from pipelines.train_pipeline import run as run_training


if __name__ == "__main__":
    run_ingestion()
    run_training()
