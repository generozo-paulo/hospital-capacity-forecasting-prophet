from pydantic import BaseModel, Field
from typing import List, Literal

class CapacityForecastRequest(BaseModel):
    hospital_unit: Literal["UTI_GERAL", "ENFERMARIA_CLINICA", "PEDIATRIA", "EMERGENCIA"] = "UTI_GERAL"
    forecast_horizon_days: int = Field(default=30, ge=7, le=180)
    confidence_level: float = Field(default=0.90, ge=0.80, le=0.99)
    include_seasonal_winter_surge: bool = True

class DailyForecastPoint(BaseModel):
    date: str
    predicted_census_p50: float
    lower_bound_p10: float
    upper_bound_p90: float
    capacity_limit: float
    overflow_risk_flag: bool

class CapacityPlanningReport(BaseModel):
    hospital_unit: str
    total_nominal_beds: int
    projected_mean_occupancy_rate: float
    critical_overflow_days_count: int
    peak_demand_date: str
    peak_census: float
    action_plan: str
    daily_points: List[DailyForecastPoint]
