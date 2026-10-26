import pytest
from src.schemas import CapacityForecastRequest
from src.forecast_engine import HospitalForecastingEngine

def test_hospital_forecast_uti():
    req = CapacityForecastRequest(
        hospital_unit="UTI_GERAL",
        forecast_horizon_days=30,
        include_seasonal_winter_surge=True
    )
    report = HospitalForecastingEngine.run_forecast(req)
    assert report.total_nominal_beds == 45
    assert len(report.daily_points) == 30
    assert 0.50 <= report.projected_mean_occupancy_rate <= 1.20
    assert report.peak_census > 0

def test_forecast_bounds_logic():
    req = CapacityForecastRequest(
        hospital_unit="ENFERMARIA_CLINICA",
        forecast_horizon_days=14,
        include_seasonal_winter_surge=False
    )
    report = HospitalForecastingEngine.run_forecast(req)
    for pt in report.daily_points:
        assert pt.lower_bound_p10 <= pt.predicted_census_p50 <= pt.upper_bound_p90
