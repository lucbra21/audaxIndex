import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import os
from PIL import Image
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import matplotlib.colors as mcolors
import matplotlib.cm as cm

# Importar funciones de gráficos de radar
from radar_charts import display_team_radar

# Importar páginas adicionales
import goal_performance
import goal_performance_comparison
import goal_performance_ranking
import generate_csv_files

# Configuración de la página
st.set_page_config(
    page_title="AUDAX GoalKPIs",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Menú de navegación
st.sidebar.title("Navegación")
choice = st.sidebar.radio("Selecciona una página:", ["KPIs Principal", "Goal Performance", "Goal Performance Team Comparison", "Goal Performance Ranking"])

# Botón para generar archivos CSV
st.sidebar.markdown("---")
st.sidebar.subheader("Generación de datos")
if st.sidebar.button("Generar archivos CSV"):
    generate_csv_files.run_generation()

# Título y descripción
if choice == "KPIs Principal":
    st.title("⚽ AUDAX GoalKPIs")
    st.markdown("Análisis de KPIs de equipos de fútbol")

# Función para normalizar datos
def normalize_to_range(series, new_min=0.5, new_max=9.5):
    if series.max() == series.min():
        return pd.Series([5] * len(series), index=series.index)
    return ((series - series.min()) / (series.max() - series.min())) * (new_max - new_min) + new_min

# Cargar datos
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("AUDAX/sb_team_match_stats_2025.xlsx")
        df_matches = pd.read_excel("AUDAX/sb_matches_2025.xlsx")
        
        # Fusionar datos de partidos
        df = pd.merge(
            df,
            df_matches[['match_id', 'match_date', 'competition', 'season', 'match_week', 'competition_stage', 'home_team', 'away_team']],
            on='match_id',
            how='left'
        )
        
        return df, df_matches
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None, None

df, df_matches = load_data()

if df is not None and df_matches is not None and choice == "KPIs Principal":
    # Sidebar para filtros
    st.sidebar.header("Filtros")
    
    # Filtro de equipo
    teams = sorted(df['team_name'].unique())
    selected_team = st.sidebar.selectbox("Seleccionar Equipo", teams)
    
    # Filtro de temporada
    seasons = sorted(df['season'].unique())
    selected_season = st.sidebar.selectbox("Seleccionar Temporada", seasons)
    
    # Filtro de competición
    competitions = sorted(df['competition'].unique())
    selected_competition = st.sidebar.selectbox("Seleccionar Competición", competitions)
    
    # Filtrar datos
    filtered_df = df[(df['team_name'] == selected_team) & 
                     (df['season'] == selected_season) & 
                     (df['competition'] == selected_competition)]
    
    # Mostrar información general
    st.header(f"Información de {selected_team}")
    
    # Crear columnas para mostrar métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        matches_played = len(filtered_df)
        st.metric("Partidos Jugados", matches_played)
    
    with col2:
        goals_scored = filtered_df['team_match_goals'].sum()
        st.metric("Goles Anotados", goals_scored)
    
    with col3:
        avg_xg = filtered_df['team_match_np_xg'].mean()
        st.metric("Promedio xG", f"{avg_xg:.2f}")
    
    with col4:
        avg_shots = filtered_df['team_match_np_shots'].mean()
        st.metric("Promedio Tiros", f"{avg_shots:.1f}")
    
    # Visualización de goles vs xG por partido
    st.subheader("Goles vs xG por Partido")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Ordenar por fecha
    filtered_df_sorted = filtered_df.sort_values('match_date')
    
    # Crear gráfico
    ax.plot(range(len(filtered_df_sorted)), filtered_df_sorted['team_match_np_xg'], 'o-', label='xG', color='blue')
    ax.plot(range(len(filtered_df_sorted)), filtered_df_sorted['team_match_goals'], 'o-', label='Goles', color='red')
    
    # Configurar etiquetas
    ax.set_xticks(range(len(filtered_df_sorted)))
    ax.set_xticklabels([f"J{w}" for w in filtered_df_sorted['match_week']], rotation=45)
    ax.set_xlabel('Jornada')
    ax.set_ylabel('Valor')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Mostrar gráfico en Streamlit
    st.pyplot(fig)
    
    # Análisis de rendimiento ofensivo
    st.header("Rendimiento Ofensivo")
    
    # Crear columnas para métricas ofensivas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Gráfico de tiros por partido
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(range(len(filtered_df_sorted)), filtered_df_sorted['team_match_np_shots'], color='skyblue')
        ax.set_xticks(range(len(filtered_df_sorted)))
        ax.set_xticklabels([f"J{w}" for w in filtered_df_sorted['match_week']], rotation=45)
        ax.set_xlabel('Jornada')
        ax.set_ylabel('Tiros')
        ax.set_title('Tiros por Partido')
        ax.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)
    
    with col2:
        # Gráfico de xG por tiro
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(range(len(filtered_df_sorted)), filtered_df_sorted['team_match_np_xg_per_shot'], color='orange')
        ax.set_xticks(range(len(filtered_df_sorted)))
        ax.set_xticklabels([f"J{w}" for w in filtered_df_sorted['match_week']], rotation=45)
        ax.set_xlabel('Jornada')
        ax.set_ylabel('xG por Tiro')
        ax.set_title('Calidad de Tiros (xG por Tiro)')
        ax.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)
    
    with col3:
        # Gráfico de asistencias esperadas (xA)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(range(len(filtered_df_sorted)), filtered_df_sorted['team_match_xa'], color='green')
        ax.set_xticks(range(len(filtered_df_sorted)))
        ax.set_xticklabels([f"J{w}" for w in filtered_df_sorted['match_week']], rotation=45)
        ax.set_xlabel('Jornada')
        ax.set_ylabel('xA')
        ax.set_title('Asistencias Esperadas (xA)')
        ax.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)
    
    # Análisis de OBV (On-Ball Value)
    st.header("Análisis de OBV (On-Ball Value)")
    
    # Crear columnas para métricas OBV
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de OBV por componente
        obv_cols = ['team_match_obv_pass', 'team_match_obv_shot', 
                    'team_match_obv_defensive_action', 'team_match_obv_dribble_carry']
        
        obv_data = filtered_df_sorted[obv_cols].mean()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(obv_data.index, obv_data.values, color=['blue', 'red', 'green', 'purple'])
        
        # Cambiar etiquetas para mejor legibilidad
        ax.set_xticklabels(['Pases', 'Tiros', 'Def. Acción', 'Regates'], rotation=45)
        ax.set_ylabel('Valor Promedio')
        ax.set_title('Componentes de OBV')
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{height:.2f}', ha='center', va='bottom')
        
        ax.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)
    
    with col2:
        # Evolución del OBV total por partido
        filtered_df_sorted['total_obv'] = filtered_df_sorted[obv_cols].sum(axis=1)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(range(len(filtered_df_sorted)), filtered_df_sorted['total_obv'], 'o-', color='purple')
        ax.set_xticks(range(len(filtered_df_sorted)))
        ax.set_xticklabels([f"J{w}" for w in filtered_df_sorted['match_week']], rotation=45)
        ax.set_xlabel('Jornada')
        ax.set_ylabel('OBV Total')
        ax.set_title('Evolución del OBV Total por Partido')
        ax.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)
    
    # Gráficos de radar
    st.header("Análisis de Perfil del Equipo")
    st.markdown("Visualización de métricas clave del equipo en gráficos de radar")
    
    # Mostrar gráficos de radar
    display_team_radar(df, selected_team, selected_season, selected_competition)
    
    # Análisis de balones parados
    st.header("Análisis de Balones Parados")
    
    # Crear columnas para métricas de balones parados
    col1, col2 = st.columns(2)
    
    # Calcular métricas de balones parados si están disponibles
    sp_metrics = [col for col in filtered_df.columns if 'sp_' in col]
    
    if sp_metrics:
        with col1:
            # Gráfico de eficiencia en balones parados
            if 'team_match_sp_goal_ratio' in filtered_df.columns:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.bar(range(len(filtered_df_sorted)), filtered_df_sorted['team_match_sp_goal_ratio'], color='gold')
                ax.set_xticks(range(len(filtered_df_sorted)))
                ax.set_xticklabels([f"J{w}" for w in filtered_df_sorted['match_week']], rotation=45)
                ax.set_xlabel('Jornada')
                ax.set_ylabel('Ratio de Gol en Balones Parados')
                ax.set_title('Eficiencia en Balones Parados')
                ax.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig)
            else:
                st.info("No hay datos disponibles sobre eficiencia en balones parados")
        
        with col2:
            # Distribución de tipos de balones parados
            corner_cols = [col for col in filtered_df.columns if 'corner' in col]
            free_kick_cols = [col for col in filtered_df.columns if 'free_kick' in col]
            
            if corner_cols and free_kick_cols:
                # Calcular promedios
                corners = filtered_df[corner_cols].mean().sum()
                free_kicks = filtered_df[free_kick_cols].mean().sum()
                
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.pie([corners, free_kicks], 
                       labels=['Córners', 'Tiros Libres'], 
                       autopct='%1.1f%%',
                       colors=['lightblue', 'lightgreen'],
                       startangle=90)
                ax.set_title('Distribución de Tipos de Balones Parados')
                st.pyplot(fig)
            else:
                st.info("No hay datos suficientes para mostrar la distribución de balones parados")
    else:
        st.info("No hay datos disponibles sobre balones parados")
    
    # Índice de Creación de Gol (GCI)
    st.header("Índice de Creación de Gol (GCI)")
    
    # Calcular componentes del GCI si están disponibles en los datos
    gci_components = {
        'np_xg': {'weight': 0.30, 'column': 'team_match_np_xg'},
        'xa': {'weight': 0.20, 'column': 'team_match_xa'},
        'deep_completions': {'weight': 0.15, 'column': 'team_match_deep_completions'},
        'obv_shot': {'weight': 0.15, 'column': 'team_match_obv_shot'},
        'obv_pass': {'weight': 0.15, 'column': 'team_match_obv_pass'},
        'penalties_won': {'weight': 0.05, 'column': 'team_match_penalties_faced'}
    }
    
    # Verificar si tenemos las columnas necesarias
    available_components = {k: v for k, v in gci_components.items() if v['column'] in filtered_df.columns}
    
    if available_components:
        # Normalizar cada componente
        normalized_df = pd.DataFrame()
        for name, info in available_components.items():
            col = info['column']
            normalized_df[name] = normalize_to_range(filtered_df[col])
        
        # Calcular GCI ponderado
        gci_values = pd.Series(0, index=filtered_df.index)
        for name, info in available_components.items():
            gci_values += normalized_df[name] * info['weight']
        
        # Añadir GCI al DataFrame
        filtered_df_sorted['GCI'] = gci_values
        
        # Mostrar gráfico de evolución del GCI
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(range(len(filtered_df_sorted)), filtered_df_sorted['GCI'], 'o-', color='darkred', linewidth=2)
        ax.set_xticks(range(len(filtered_df_sorted)))
        ax.set_xticklabels([f"J{w}" for w in filtered_df_sorted['match_week']], rotation=45)
        ax.set_xlabel('Jornada')
        ax.set_ylabel('GCI')
        ax.set_title('Evolución del Índice de Creación de Gol (GCI)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Añadir línea de promedio
        avg_gci = filtered_df_sorted['GCI'].mean()
        ax.axhline(y=avg_gci, color='gray', linestyle='--', alpha=0.7)
        ax.text(len(filtered_df_sorted)-1, avg_gci, f' Promedio: {avg_gci:.2f}', 
                verticalalignment='center')
        
        st.pyplot(fig)
        
        # Mostrar componentes del GCI
        st.subheader("Componentes del GCI")
        
        component_values = []
        component_names = []
        
        for name, info in available_components.items():
            col = info['column']
            avg_value = filtered_df[col].mean()
            component_values.append(avg_value)
            component_names.append(name)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(component_names, component_values, color='maroon')
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.2f}', ha='center', va='bottom')
        
        ax.set_xlabel('Componente')
        ax.set_ylabel('Valor Promedio')
        ax.set_title('Componentes del Índice de Creación de Gol')
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
    else:
        st.info("No hay datos suficientes para calcular el Índice de Creación de Gol (GCI)")
    
    # Tabla de datos detallados
    st.header("Datos Detallados")
    
    # Seleccionar columnas relevantes para mostrar
    cols_to_show = ['match_date', 'match_week', 'team_match_goals', 'team_match_np_xg', 
                    'team_match_np_shots', 'team_match_xa', 'team_match_deep_completions']
    
    # Renombrar columnas para mejor legibilidad
    renamed_cols = {
        'match_date': 'Fecha',
        'match_week': 'Jornada',
        'team_match_goals': 'Goles',
        'team_match_np_xg': 'xG',
        'team_match_np_shots': 'Tiros',
        'team_match_xa': 'xA',
        'team_match_deep_completions': 'Pases Profundos'
    }
    
    display_df = filtered_df_sorted[cols_to_show].copy()
    display_df = display_df.rename(columns=renamed_cols)
    
    # Formatear valores numéricos
    for col in ['xG', 'xA']:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(2)
    
    st.dataframe(display_df, use_container_width=True)

elif choice == "Goal Performance":
    goal_performance.app()
    
elif choice == "Goal Performance Team Comparison":
    goal_performance_comparison.app()

elif choice == "Goal Performance Ranking":
    goal_performance_ranking.app()

elif df is None or df_matches is None:
    st.error("No se pudieron cargar los datos. Por favor verifica que los archivos existan en la carpeta AUDAX.")
    
    # Instrucciones para el usuario
    st.info("""
    Para usar esta aplicación, necesitas los siguientes archivos en la carpeta AUDAX:
    - sb_team_match_stats_2025.xlsx
    - sb_matches_2025.xlsx
    
    Estos archivos deben contener los datos de equipos y partidos para el análisis.
    """)
