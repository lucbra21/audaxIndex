# AUDAX GoalKPIs - Aplicación Streamlit

Esta aplicación Streamlit implementa el análisis de KPIs de fútbol del notebook "AUDAX GoalKPIs.ipynb".

## Características

- Visualización de métricas clave de equipos de fútbol
- Análisis de rendimiento ofensivo y defensivo
- Gráficos de radar para perfiles de equipo
- Análisis de balones parados
- Índice de Creación de Gol (GCI)
- Visualización de datos detallados por partido

## Requisitos

Los requisitos están especificados en el archivo `requirements.txt`. Las principales dependencias son:

- streamlit
- pandas
- numpy
- matplotlib
- scikit-learn
- pillow
- mplsoccer
- ipywidgets

## Estructura de archivos

- `app.py`: Aplicación principal de Streamlit
- `radar_charts.py`: Funciones para crear gráficos de radar
- `requirements.txt`: Dependencias necesarias

## Datos necesarios

La aplicación espera encontrar los siguientes archivos de datos en la carpeta `AUDAX`:

- `sb_team_match_stats_2025.xlsx`: Estadísticas de equipos por partido
- `sb_matches_2025.xlsx`: Información de partidos

## Ejecución

Para ejecutar la aplicación, usa el siguiente comando:

```bash
streamlit run app.py
```

## Navegación

1. Usa el panel lateral para seleccionar el equipo, temporada y competición
2. Explora las diferentes secciones de análisis
3. Visualiza los gráficos y métricas generadas automáticamente
