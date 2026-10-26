# Especificação Contratual (SDD) - Hospital Bed & ICU Capacity Forecasting

## 1. Escopo & Objetivos
Previsão probabilística de séries temporais para demanda de internações em enfermaria e leitos de UTI (horizonte de 30 a 90 dias) considerando sazonalidade anual (surtos de vírus sincicial respiratório/gripe no inverno), efeitos de dia da semana (quedas de admissões eletivas no fim de semana) e feriados nacionais.
Gera intervalos de incerteza (P10, P50, P90) para suporte à escala médica e planejamento de compras de insumos.

## 2. Contratos de Entrada (Pydantic)

### 2.1 Requisição de Previsão (`CapacityForecastRequest`)
- `hospital_unit`: Literal["UTI_GERAL", "ENFERMARIA_CLINICA", "PEDIATRIA", "EMERGENCIA"]
- `forecast_horizon_days`: int = Field(default=30, ge=7, le=180)
- `confidence_level`: float = Field(default=0.90, ge=0.80, le=0.99)
- `include_seasonal_winter_surge`: bool = True

## 3. Contratos de Saída (Pydantic)

### 3.1 Ponto de Previsão Diário (`DailyForecastPoint`)
- `date`: str
- `predicted_census_p50`: float
- `lower_bound_p10`: float
- `upper_bound_p90`: float
- `capacity_limit`: float
- `overflow_risk_flag`: bool

### 3.2 Relatório Consolidado de Planejamento de Capacidade (`CapacityPlanningReport`)
- `hospital_unit`: str
- `total_nominal_beds`: int
- `projected_mean_occupancy_rate`: float
- `critical_overflow_days_count`: int
- `peak_demand_date`: str
- `peak_census`: float
- `action_plan`: str
