import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.schemas import CapacityForecastRequest
from src.forecast_engine import HospitalForecastingEngine

st.set_page_config(
    page_title="Hospital Capacity & Bed Forecasting",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hospital Bed & ICU Capacity Forecasting (Prophet-style)")
st.markdown("""
Previsão probabilística de demanda de leitos de enfermaria e terapia intensiva (UTI) com modelagem de **sazonalidade anual (surtos de inverno)** e **efeito de dias da semana** para prevenção de superlotação.
""")

col_param, col_chart = st.columns([1, 2])

with col_param:
    st.subheader("⚙️ Parâmetros do Modelo Preditivo")
    unit = st.selectbox("Unidade Hospitalar:", ["UTI_GERAL", "ENFERMARIA_CLINICA", "PEDIATRIA", "EMERGENCIA"])
    horizon = st.slider("Horizonte de Previsão (Dias)", 14, 90, 45, 1)
    winter_surge = st.checkbox("Incluir Surto Sazonal de Inverno", value=True)

    req = CapacityForecastRequest(
        hospital_unit=unit,
        forecast_horizon_days=horizon,
        include_seasonal_winter_surge=winter_surge
    )
    report = HospitalForecastingEngine.run_forecast(req)

    st.markdown("### 📊 Indicadores Chave de Gestão")
    st.metric("Leitos Operacionais Nominais", f"{report.total_nominal_beds} leitos")
    st.metric("Taxa de Ocupação Média Projetada", f"{report.projected_mean_occupancy_rate:.1%}")
    st.metric("Dias com Risco Crítico de Superlotação", f"{report.critical_overflow_days_count} dias")
    st.metric("Pico de Ocupação Previsto", f"{report.peak_census} leitos ({report.peak_demand_date})")

    st.markdown("### 📋 Plano de Contingência")
    st.info(report.action_plan)

with col_chart:
    st.subheader("Curva de Projeção de Demanda e Intervalos de Incerteza (P10 - P90)")
    df_pts = pd.DataFrame([p.model_dump() for p in report.daily_points])

    fig = go.Figure()
    # Intervalo de incerteza P10 a P90 (banda sombreada)
    fig.add_trace(go.Scatter(
        x=df_pts["date"],
        y=df_pts["upper_bound_p90"],
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=df_pts["date"],
        y=df_pts["lower_bound_p10"],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(31, 119, 180, 0.2)',
        name='Intervalo de Incerteza (P10 - P90)'
    ))
    # Previsão mediana P50
    fig.add_trace(go.Scatter(
        x=df_pts["date"],
        y=df_pts["predicted_census_p50"],
        mode='lines',
        name='Censo Projetado (Mediana P50)',
        line=dict(color='#1f77b4', width=2.5)
    ))
    # Linha de capacidade nominal
    fig.add_trace(go.Scatter(
        x=df_pts["date"],
        y=df_pts["capacity_limit"],
        mode='lines',
        name='Capacidade Máxima Instalada',
        line=dict(color='#d62728', width=2, dash='dash')
    ))

    fig.update_layout(
        title=f"Previsão de Ocupação Diária - {report.hospital_unit}",
        xaxis_title="Data",
        yaxis_title="Pacientes Internados (Leitos Ocupados)",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
