from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    Age: int = Field(..., ge=0, le=120)
    Gender: str
    Blood_Type: str = Field(..., alias="Blood Type")
    Medical_Condition: str = Field(..., alias="Medical Condition")
    Billing_Amount: float = Field(..., alias="Billing Amount", ge=0)
    Admission_Type: str = Field(..., alias="Admission Type")
    Insurance_Provider: str = Field(..., alias="Insurance Provider")
    Medication: str

    class Config:
        populate_by_name = True


class PredictionResponse(BaseModel):
    predicted_test_result: str
