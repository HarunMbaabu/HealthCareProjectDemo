### **Project Overview**
This repository now contains a complete **production-style healthcare data platform**:
- CSV ingestion with reproducible logging
- Raw and processed storage in PostgreSQL
- Professional cleaning and transformation pipeline
- Multi-model ML training with mandatory XGBoost + Logistic Regression
- Weekly retraining scheduler (Saturday, 12:00 UTC)
- FastAPI inference service (`POST /predict`)
- Browser UI page similar to your screenshot
- Deployment setup for Vercel

### **Architecture**
1. **Ingestion layer** (`data/ingestion.py`)
   - Reads `healthcare_dataset.csv` with Pandas
   - Stores raw payloads in `healthcare_raw` as JSONB
   - Uses row-level hash + unique index to avoid duplicate inserts

2. **Transformation layer** (`data/preprocessing.py`)
   - Removes duplicates
   - Parses date columns
   - Standardizes categorical values (Gender, Admission Type)
   - Handles missing values (median for numeric, mode for categorical)
   - Drops irrelevant columns (`Name`, `Doctor`, `Hospital`, `Room Number`)
   - Engineers `Length of Stay`

3. **Curated storage layer** (`data/storage.py`)
   - Creates `healthcare_processed` with constraints and indexing
   - Performs idempotent upsert using `row_hash`

4. **ML layer** (`models/trainer.py`, `pipelines/train_pipeline.py`)
   - Trains XGBoost and Logistic Regression pipelines
   - Uses `ColumnTransformer + OneHotEncoder`
   - Computes accuracy, precision, recall, F1, confusion matrix
   - Selects best model by weighted F1
   - Saves model artifact with joblib and writes metrics JSON

5. **Serving layer** (`api/main.py`)
   - FastAPI app with Pydantic validation
   - `/predict` endpoint with robust error handling
   - `/health` endpoint
   - `/` serves lightweight front-end form (`web/index.html`)

6. **Orchestration layer** (`pipelines/scheduler.py`)
   - APScheduler cron job every Saturday at 12:00 UTC
   - Runs ingestion + processing + training

### **Project Structure**
```text
.
├── api/
├── artifacts/
├── data/
├── models/
├── pipelines/
├── utils/
├── web/
├── healthcare_dataset.csv
├── main.py
├── pyproject.toml
├── vercel.json
└── .env.example
```

### **Setup (UV, not pip)**
1. Install uv (if needed):
   - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Create environment + install dependencies:
   - `uv sync`
3. Copy env template:
   - `cp .env.example .env`
4. Ensure PostgreSQL is running and create your DB (`healthcare_db` by default).

### **.env Configuration**
```bash
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare_db
RAW_TABLE_NAME=healthcare_raw
PROCESSED_TABLE_NAME=healthcare_processed
MODEL_DIR=artifacts
MODEL_FILE_NAME=best_model.joblib
RANDOM_STATE=42
```

### **Run the Data Pipeline**
Ingest + clean + store + train once:
```bash
uv run python main.py
```

Run ingestion only:
```bash
uv run python -m pipelines.ingest_and_process
```

Run training only:
```bash
uv run python -m pipelines.train_pipeline
```

### **Run Weekly Retraining Scheduler**
```bash
uv run python -m pipelines.scheduler
```
Schedule configured to run every **Saturday at 12:00 (UTC)**.

### **Run the API**
```bash
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
Open:
- UI: `http://localhost:8000/`
- Swagger docs: `http://localhost:8000/docs`

### **API Request / Response Example**
**POST** `/predict`

Request body:
```json
{
  "Age": 45,
  "Gender": "Male",
  "Blood Type": "O+",
  "Medical Condition": "Diabetes",
  "Billing Amount": 2000.5,
  "Admission Type": "Emergency",
  "Insurance Provider": "Cigna",
  "Medication": "Aspirin"
}
```

Example response:
```json
{
  "predicted_test_result": "Abnormal"
}
```

### **Deployment (Vercel)**
Included `vercel.json` routes:
- `/` serves static front-end form
- `/predict`, `/health`, `/docs`, `/openapi.json` route to FastAPI serverless app

Deploy steps:
1. Push this repo to GitHub.
2. Import project in Vercel.
3. Set environment variables from `.env`.
4. Deploy.
5. Test `https://<your-app>.vercel.app/predict`.

### **Production Notes**
- Add CI/CD (lint/test/deploy checks) before go-live.
- Configure monitoring (Sentry/Datadog/OpenTelemetry).
- Consider model registry and feature store for larger scale.
- Add auth/rate limiting for public APIs.
