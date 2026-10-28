from pydantic import BaseModel, Field
class ValuationRequest(BaseModel):
    location: str = Field(min_length=2, max_length=160)
    property_type: str = Field(min_length=2, max_length=80)
    area_sqft: float = Field(gt=0, le=10000000)
    rate_per_sqft: float = Field(gt=0, le=10000000)
    age_years: int = Field(ge=0, le=300)
    condition: str = "Good"
class PlanRequest(BaseModel):
    project_name: str = Field(min_length=2, max_length=160)
    project_type: str = "Residential"
    site_area_sqft: float = Field(gt=0)
    floors: int = Field(ge=1, le=150)
    target_months: int = Field(ge=1, le=240)
    budget_inr: float = Field(gt=0)
    notes: str = ""
class DailyRequest(BaseModel):
    question: str = Field(min_length=3, max_length=3000)
    city: str = ""
    weather: str = "Not provided"
    work_stage: str = "General site work"
