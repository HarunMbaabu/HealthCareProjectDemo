import logging
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.schemas import PredictionRequest, PredictionResponse
from utils.config import get_settings
from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title="Healthcare Test Result Predictor", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = None


def load_model():
    global MODEL
    if MODEL is None:
        model_path = settings.model_dir / settings.model_file_name
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {model_path}. Run training pipeline first."
            )
        MODEL = joblib.load(model_path)
    return MODEL


@app.get("/")
def home():
    html_path = Path("web/index.html")
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "Healthcare API is running", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    try:
        model = load_model()
        frame = pd.DataFrame(
            [
                {
                    "age": payload.Age,
                    "gender": payload.Gender,
                    "blood_type": payload.Blood_Type,
                    "medical_condition": payload.Medical_Condition,
                    "insurance_provider": payload.Insurance_Provider,
                    "billing_amount": payload.Billing_Amount,
                    "admission_type": payload.Admission_Type,
                    "medication": payload.Medication,
                    "length_of_stay": 0,
                }
            ]
        )
        prediction = model.predict(frame)[0]
        return PredictionResponse(predicted_test_result=str(prediction))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc
