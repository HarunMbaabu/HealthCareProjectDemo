import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from utils.config import get_settings

logger = logging.getLogger(__name__)


class DataIngestion:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.settings = get_settings()

    def load_csv(self, csv_path: Path | str) -> pd.DataFrame:
        logger.info("Loading CSV from %s", csv_path)
        return pd.read_csv(csv_path)

    def store_raw_data(self, df: pd.DataFrame) -> None:
        table = self.settings.raw_table_name
        logger.info("Ensuring raw table exists: %s", table)
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        id BIGSERIAL PRIMARY KEY,
                        row_hash TEXT UNIQUE,
                        payload JSONB NOT NULL,
                        ingested_at TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
            )

        payload_df = pd.DataFrame(
            {
                "row_hash": pd.util.hash_pandas_object(df.astype(str), index=False).astype(str),
                "payload": df.to_dict(orient="records"),
            }
        )
        logger.info("Writing raw records to PostgreSQL with deduplication")
        with self.engine.begin() as conn:
            conn.execute(text(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_row_hash ON {table}(row_hash)"))
            for _, row in payload_df.iterrows():
                conn.execute(
                    text(
                        f"INSERT INTO {table}(row_hash, payload) VALUES (:row_hash, CAST(:payload AS JSONB)) "
                        "ON CONFLICT (row_hash) DO NOTHING"
                    ),
                    {"row_hash": row["row_hash"], "payload": pd.io.json.dumps(row["payload"])},
                )
