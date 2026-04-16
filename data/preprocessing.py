import logging

import pandas as pd

logger = logging.getLogger(__name__)

DATE_COLS = ["Date of Admission", "Discharge Date"]
DROP_COLS = ["Name", "Doctor", "Hospital", "Room Number"]
CATEGORY_STANDARDIZATION = {
    "Gender": {"male": "Male", "female": "Female"},
    "Admission Type": {
        "urgent": "Urgent",
        "emergency": "Emergency",
        "elective": "Elective",
    },
}


class DataPreprocessor:
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting preprocessing pipeline")
        clean_df = df.copy()

        clean_df = clean_df.drop_duplicates()

        for col in DATE_COLS:
            clean_df[col] = pd.to_datetime(clean_df[col], errors="coerce")

        for col, mapping in CATEGORY_STANDARDIZATION.items():
            clean_df[col] = (
                clean_df[col].astype(str).str.strip().str.lower().map(mapping).fillna(clean_df[col])
            )

        # missing values: numeric -> median, categorical -> mode
        for col in clean_df.columns:
            if clean_df[col].dtype.kind in "biufc":
                clean_df[col] = clean_df[col].fillna(clean_df[col].median())
            else:
                mode_value = clean_df[col].mode(dropna=True)
                fill_value = mode_value.iloc[0] if not mode_value.empty else "Unknown"
                clean_df[col] = clean_df[col].fillna(fill_value)

        clean_df["Length of Stay"] = (
            clean_df["Discharge Date"] - clean_df["Date of Admission"]
        ).dt.days.clip(lower=0)

        clean_df = clean_df.drop(columns=DROP_COLS, errors="ignore")

        clean_df["Billing Amount"] = pd.to_numeric(clean_df["Billing Amount"], errors="coerce")
        clean_df["Age"] = pd.to_numeric(clean_df["Age"], errors="coerce")
        clean_df["Billing Amount"] = clean_df["Billing Amount"].fillna(clean_df["Billing Amount"].median())
        clean_df["Age"] = clean_df["Age"].fillna(clean_df["Age"].median())

        for col in ["Date of Admission", "Discharge Date"]:
            clean_df[col] = clean_df[col].dt.strftime("%Y-%m-%d")

        logger.info("Preprocessing complete. Rows=%s Cols=%s", *clean_df.shape)
        return clean_df
