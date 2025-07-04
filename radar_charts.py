import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from mplsoccer import PyPizza
from mplsoccer.utils import add_image
from PIL import Image
import os

def normalize_to_range(series, new_min=0.5, new_max=9.5):
    """Normaliza una serie a un rango específico"""
    if series.max() == series.min():
        return pd.Series([5] * len(series), index=series.index)
    return ((series - series.min()) / (series.max() - series.min())) * (new_max - new_min) + new_min

def create_radar_chart(team_data, metrics, title, team_name, color_scheme='blue'):
    """
    Crea un gráfico de radar (pizza chart) para visualizar métricas de un equipo
    
    Parámetros:
    - team_data: DataFrame con los datos del equipo
    - metrics: Lista de métricas a incluir en el gráfico
    - title: Título del gráfico
    - team_name: Nombre del equipo
    - color_scheme: Esquema de color para el gráfico
    
    Retorna:
    - fig: Figura de matplotlib
    """
    # Preparar datos
    values = []
    for metric in metrics:
        if metric in team_data.columns:
            values.append(team_data[metric].mean())
        else:
            values.append(0)  # Valor por defecto si no existe la métrica
    
    # Normalizar valores al rango 0-100 para el gráfico
    values_norm = normalize_to_range(pd.Series(values), 0, 100).tolist()
    
    # Parámetros para el gráfico
    params = metrics
    
    # Definir colores seguros
    color_map = {
        'red': 'tab:red',
        'blue': 'tab:blue',
        'green': 'tab:green',
        'orange': 'tab:orange',
        'purple': 'tab:purple',
        'brown': 'tab:brown',
        'pink': 'tab:pink',
        'gray': 'tab:gray',
        'olive': 'tab:olive',
        'cyan': 'tab:cyan'
    }
    
    # Obtener color seguro
    slice_color = color_map.get(color_scheme, 'tab:blue')  # Azul por defecto
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Crear instancia de PyPizza
    baker = PyPizza(
        params=params,                  # lista de parámetros
        background_color=None,          # color de fondo
        straight_line_color="black",     # color de las líneas rectas
        straight_line_lw=1,             # grosor de las líneas rectas
        last_circle_lw=1,               # grosor del último círculo
        other_circle_lw=1,              # grosor de los otros círculos
        inner_circle_size=20            # tamaño del círculo interno
    )
    
    # Dibujar gráfico de pizza
    baker.make_pizza(
        values=values_norm,              # valores normalizados
        figsize=(10, 10),                # tamaño de la figura
        param_location=110,              # ubicación de los parámetros
        kwargs_slices=dict(
            facecolor=slice_color, edgecolor="black",
            zorder=2, linewidth=1
        ),                               # personalización de las rebanadas
        kwargs_params=dict(
            color="black", fontsize=12,
            fontweight="bold", va="center"
        ),                               # personalización de los parámetros
        kwargs_values=dict(
            color="black", fontsize=12,
            fontweight="bold", zorder=3,
            bbox=dict(
                edgecolor="black", facecolor="lightblue",
                boxstyle="round,pad=0.2", lw=1
            )
        )                                # personalización de los valores
    )
    
    # Añadir título
    fig.text(
        0.515, 0.97, f"{title}\n{team_name}",
        size=18, ha="center", fontweight="bold"
    )
    
    # Añadir leyenda de métricas
    legend_elements = []
    for i, metric in enumerate(metrics):
        legend_elements.append(f"{i+1}. {metric}")
    
    fig.text(
        0.515, 0.02,
        "\n".join(legend_elements),
        size=10, ha="center"
    )
    
    return fig

def display_team_radar(df, team_name, season, competition):
    """
    Muestra gráficos de radar para un equipo específico
    
    Parámetros:
    - df: DataFrame con todos los datos
    - team_name: Nombre del equipo a analizar
    - season: Temporada seleccionada
    - competition: Competición seleccionada
    """
    # Filtrar datos
    team_data = df[(df['team_name'] == team_name) & 
                   (df['season'] == season) & 
                   (df['competition'] == competition)]
    
    if len(team_data) == 0:
        st.warning(f"No hay datos disponibles para {team_name} en la temporada {season} y competición {competition}")
        return
    
    # Definir métricas para diferentes aspectos del juego
    offensive_metrics = [
        'team_match_np_xg', 
        'team_match_np_shots', 
        'team_match_xa', 
        'team_match_deep_completions',
        'team_match_obv_shot',
        'team_match_obv_pass'
    ]
    
    defensive_metrics = [
        'team_match_ball_recoveries',
        'team_match_obv_defensive_action',
        'team_match_np_psxg',
        'team_match_obv_gk'
    ]
    
    # Crear columnas para mostrar gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Perfil Ofensivo")
        fig_off = create_radar_chart(
            team_data, 
            offensive_metrics, 
            "Perfil Ofensivo", 
            team_name, 
            color_scheme='red'
        )
        st.pyplot(fig_off)
    
    with col2:
        st.subheader("Perfil Defensivo")
        fig_def = create_radar_chart(
            team_data, 
            defensive_metrics, 
            "Perfil Defensivo", 
            team_name, 
            color_scheme='blue'
        )
        st.pyplot(fig_def)
