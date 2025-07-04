import streamlit as st
import pandas as pd
import plotly.express as px

# --- Cargar datos ---
@st.cache_data
def load_data():
    return pd.read_csv("/Users/sevi/Documents/Documentos - MacBook Pro de Miguel/AUDAX/df_final.csv")


df = load_data()

# --- Filtrar datos promedio (AVG) ---
avg_df = df[df["match_id"] == "AVG"]

# --- Título ---
st.title("Evolución de KPIs por equipo (promedios)")

# --- Selector múltiple de equipos ---
teams = st.multiselect("Selecciona uno o más equipos:", avg_df["team_name"].unique(), default=["ALL_TEAMS_AVG"])

# --- KPIs disponibles ---
kpi_options = [
    "Goal Envolvement Index (norm)",
    "Goal Conversion Index (norm)",
    "Possession GoalChance Index (norm)",
    "Goal Performance Index"
]
kpi = st.selectbox("Selecciona el KPI que quieres visualizar:", kpi_options)

# --- Filtrar por equipos seleccionados ---
filtered_df = avg_df[avg_df["team_name"].isin(teams)]

# --- Graficar ---
fig = px.bar(
    filtered_df,
    x="team_name",
    y=kpi,
    color="team_name",
    title=f"{kpi} promedio por equipo"
)
st.plotly_chart(fig)
