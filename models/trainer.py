import logging
from pathlib import Path

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)


class ModelTrainer:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def _build_models(self) -> dict[str, object]:
        return {
            "xgboost": XGBClassifier(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=5,
                subsample=0.9,
                colsample_bytree=0.9,
                objective="multi:softprob",
                eval_metric="mlogloss",
                random_state=self.random_state,
            ),
            "logistic_regression": LogisticRegression(max_iter=2000, random_state=self.random_state),
        }

    def train(self, df):
        target_col = "test_results"
        features = [
            "age",
            "gender",
            "blood_type",
            "medical_condition",
            "insurance_provider",
            "billing_amount",
            "admission_type",
            "medication",
            "length_of_stay",
        ]

        dataset = df[features + [target_col]].dropna().copy()
        X = dataset[features]
        y = dataset[target_col]

        categorical_cols = [
            "gender",
            "blood_type",
            "medical_condition",
            "insurance_provider",
            "admission_type",
            "medication",
        ]
        numeric_cols = ["age", "billing_amount", "length_of_stay"]

        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
                ("num", "passthrough", numeric_cols),
            ]
        )

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=self.random_state
        )

        results = {}
        best_name = None
        best_f1 = -np.inf
        best_pipeline = None

        for name, model in self._build_models().items():
            pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])
            pipeline.fit(X_train, y_train)
            preds = pipeline.predict(X_test)

            metrics = {
                "accuracy": accuracy_score(y_test, preds),
                "precision": precision_score(y_test, preds, average="weighted", zero_division=0),
                "recall": recall_score(y_test, preds, average="weighted", zero_division=0),
                "f1": f1_score(y_test, preds, average="weighted", zero_division=0),
                "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
            }
            results[name] = metrics

            if metrics["f1"] > best_f1:
                best_f1 = metrics["f1"]
                best_name = name
                best_pipeline = pipeline

        return best_name, best_pipeline, results

    @staticmethod
    def save_model(model_pipeline, output_dir: Path, file_name: str) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / file_name
        joblib.dump(model_pipeline, output_path)
        logger.info("Saved best model to %s", output_path)
        return output_path
