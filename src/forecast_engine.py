import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, List
from src.schemas import CapacityForecastRequest, DailyForecastPoint, CapacityPlanningReport

class HospitalForecastingEngine:
    """
    Motor aditivo de previsão probabilística de séries temporais para capacidade hospitalar (Prophet-style).
    """

    CAPACITY_MAP = {
        "UTI_GERAL": 45,
        "ENFERMARIA_CLINICA": 120,
        "PEDIATRIA": 60,
        "EMERGENCIA": 80
    }

    @staticmethod
    def run_forecast(request: CapacityForecastRequest) -> CapacityPlanningReport:
        nominal_beds = HospitalForecastingEngine.CAPACITY_MAP.get(request.hospital_unit, 50)
        start_date = datetime(2026, 11, 1)

        points: List[DailyForecastPoint] = []
        overflow_count = 0
        peak_census = 0.0
        peak_date = ""

        # Média basal de ocupação (~82% da capacidade)
        base_census = nominal_beds * 0.82

        for d in range(request.forecast_horizon_days):
            current_date = start_date + timedelta(days=d)
            day_of_week = current_date.weekday() # 0 = Segunda, 6 = Domingo
            day_of_year = current_date.timetuple().tm_yday

            # Sazonalidade semanal: Admissões caem no sábado (5) e domingo (6)
            weekly_effect = - (nominal_beds * 0.08) if day_of_week in [5, 6] else (nominal_beds * 0.03)

            # Sazonalidade anual (Surtos respiratórios de inverno - maio a agosto / hemisfério sul)
            winter_surge = 0.0
            if request.include_seasonal_winter_surge:
                # Efeito cíclico suave usando senoide
                winter_surge = float(nominal_beds * 0.12 * np.sin(2 * np.pi * (day_of_year + 40) / 365.0))

            # Tendência linear suave
            trend = d * 0.04

            p50 = float(base_census + weekly_effect + winter_surge + trend)
            noise_std = nominal_beds * 0.05
            p10 = float(max(p50 - (1.645 * noise_std), 5.0))
            p90 = float(p50 + (1.645 * noise_std))

            is_overflow = bool(p90 >= nominal_beds)
            if is_overflow:
                overflow_count += 1

            if p50 > peak_census:
                peak_census = p50
                peak_date = current_date.strftime("%Y-%m-%d")

            points.append(DailyForecastPoint(
                date=current_date.strftime("%Y-%m-%d"),
                predicted_census_p50=round(p50, 1),
                lower_bound_p10=round(p10, 1),
                upper_bound_p90=round(p90, 1),
                capacity_limit=float(nominal_beds),
                overflow_risk_flag=is_overflow
            ))

        mean_census = np.mean([p.predicted_census_p50 for p in points])
        mean_occupancy = float(mean_census / nominal_beds)

        if overflow_count > 5:
            plan = "🚨 ACIONAR CONTINGÊNCIA: Contratar escala médica extra e postergar procedimentos eletivos."
        elif overflow_count > 0:
            plan = "⚠️ ATENÇÃO OPERACIONAL: Monitorar altas diárias e agilizar desospitalização para leitos de retaguarda."
        else:
            plan = "✅ CAPACIDADE ADEQUADA: Taxa de ocupação equilibrada dentro da faixa de segurança (< 85%)."

        return CapacityPlanningReport(
            hospital_unit=request.hospital_unit,
            total_nominal_beds=nominal_beds,
            projected_mean_occupancy_rate=round(mean_occupancy, 4),
            critical_overflow_days_count=overflow_count,
            peak_demand_date=peak_date,
            peak_census=round(peak_census, 1),
            action_plan=plan,
            daily_points=points
        )
