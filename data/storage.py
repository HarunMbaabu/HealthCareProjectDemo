import logging

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from utils.config import get_settings

logger = logging.getLogger(__name__)


class DataStorage:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.settings = get_settings()

    def create_processed_table(self) -> None:
        table = self.settings.processed_table_name
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id BIGSERIAL PRIMARY KEY,
                    age INT NOT NULL CHECK (age >= 0),
                    gender TEXT NOT NULL,
                    blood_type TEXT NOT NULL,
                    medical_condition TEXT NOT NULL,
                    date_of_admission DATE,
                    insurance_provider TEXT,
                    billing_amount NUMERIC(12,2),
                    admission_type TEXT,
                    discharge_date DATE,
                    medication TEXT,
                    test_results TEXT NOT NULL,
                    length_of_stay INT,
                    row_hash TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
                """
                )
            )
            conn.execute(
                text(
                    f"CREATE INDEX IF NOT EXISTS idx_{table}_test_results ON {table}(test_results)"
                )
            )

    def upsert_processed_data(self, df: pd.DataFrame) -> None:
        self.create_processed_table()
        table = self.settings.processed_table_name

        rename_cols = {
            "Age": "age",
            "Gender": "gender",
            "Blood Type": "blood_type",
            "Medical Condition": "medical_condition",
            "Date of Admission": "date_of_admission",
            "Insurance Provider": "insurance_provider",
            "Billing Amount": "billing_amount",
            "Admission Type": "admission_type",
            "Discharge Date": "discharge_date",
            "Medication": "medication",
            "Test Results": "test_results",
            "Length of Stay": "length_of_stay",
        }
        normalized = df.rename(columns=rename_cols).copy()
        normalized["row_hash"] = pd.util.hash_pandas_object(normalized.astype(str), index=False).astype(str)

        with self.engine.begin() as conn:
            for _, row in normalized.iterrows():
                conn.execute(
                    text(
                        f"""
                        INSERT INTO {table}(
                            age, gender, blood_type, medical_condition, date_of_admission,
                            insurance_provider, billing_amount, admission_type, discharge_date,
                            medication, test_results, length_of_stay, row_hash
                        ) VALUES (
                            :age, :gender, :blood_type, :medical_condition, :date_of_admission,
                            :insurance_provider, :billing_amount, :admission_type, :discharge_date,
                            :medication, :test_results, :length_of_stay, :row_hash
                        )
                        ON CONFLICT (row_hash) DO NOTHING
                        """
                    ),
                    row.to_dict(),
                )
        logger.info("Processed data upserted: %s rows attempted", len(normalized))

    def fetch_processed_data(self) -> pd.DataFrame:
        table = self.settings.processed_table_name
        return pd.read_sql(f"SELECT * FROM {table}", self.engine)
