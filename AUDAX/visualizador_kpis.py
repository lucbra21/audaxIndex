import pandas as pd
import plotly.graph_objects as go
import panel as pn

pn.extension('plotly')

# --- Cargar datos ---
df = pd.read_csv("/Users/sevi/Documents/Documentos - MacBook Pro de Miguel/AUDAX/df_final.csv")

# --- Limpiar y preparar ---
df = df[df["match_id"] != "AVG"].copy()
df["match_id"] = df["match_id"].astype(str)
df["match_order"] = df["match_id"].str[-3:].astype(int)

# --- Detectar KPIs disponibles ---
kpi_cols = df.select_dtypes(include='number').columns.tolist()
kpi_cols = [col for col in kpi_cols if col not in ["match_order", "team_id", "account_id"]]

# --- Widgets ---
equipos = sorted(df["team_name"].unique())
equipo_selector = pn.widgets.MultiChoice(name="Selecciona equipos", options=equipos, value=equipos[:2])
kpi_selector = pn.widgets.Select(name="Selecciona KPI", options=kpi_cols, value=kpi_cols[0])

# --- Función dinámica ---
@pn.depends(equipo_selector, kpi_selector)
def plot_kpi(equipos_seleccionados, kpi):
    fig = go.Figure()
    df_filtrado = df[df["team_name"].isin(equipos_seleccionados)].copy()

    for equipo in equipos_seleccionados:
        datos_equipo = df_filtrado[df_filtrado["team_name"] == equipo].sort_values("match_order")
        fig.add_trace(go.Scatter(x=datos_equipo["match_order"], y=datos_equipo[kpi], mode="lines+markers", name=equipo))
        fig.add_trace(go.Scatter(x=datos_equipo["match_order"], y=[datos_equipo[kpi].mean()] * len(datos_equipo),
                                 mode="lines", line=dict(dash="dash"), name=f"Promedio {equipo}"))

    prom_todos = df[kpi].mean()
    fig.add_trace(go.Scatter(x=sorted(df["match_order"].unique()), y=[prom_todos] * len(df["match_order"].unique()),
                             mode="lines", line=dict(color="black", dash="dot", width=3), name="Promedio Todos"))

    fig.update_layout(title=f"Evolución de {kpi} por Partido",
                      xaxis_title="Match ID (ultimos 3 dígitos)",
                      yaxis_title=kpi,
                      xaxis=dict(tickmode="linear"),
                      hovermode="x unified")
    return fig

# --- Layout ---
dashboard = pn.Column(
    "# Visualizador de KPI por Equipo y Partido",
    equipo_selector,
    kpi_selector,
    plot_kpi
)

dashboard.servable()


