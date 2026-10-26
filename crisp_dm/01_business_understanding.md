# CRISP-DM: Entendimento de Negócio (Previsão de Capacidade Hospitalar)

## 1. Problema de Gestão de Leitos Hospitalares
A falta de previsibilidade de leitos de internação e terapia intensiva causa dois problemas financeiros e assistenciais graves:
1. **Superlotação (Overflow)**: Pacientes graves retidos nos corredores do pronto-socorro aguardando leito de UTI.
2. **Capacidade Ociosa Improdutiva**: Custos fixos elevados com equipes de enfermagem em períodos de baixa demanda.

## 2. Abordagem de Séries Temporais Probabilísticas
- Decomposição aditiva: Tendência de longo prazo + Sazonalidade Semanal (efeito fim de semana) + Sazonalidade Anual (doenças respiratórias no inverno).
- Intervalos de confiança paramétricos (P10/P50/P90) para gestão de risco e gatilho de contingência.
