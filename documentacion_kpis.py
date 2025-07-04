import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from PIL import Image
from mplsoccer import PyPizza
from mplsoccer.utils import add_image
import os
import numpy as np

def app():
    # Configuración de la página
    st.set_page_config(
        page_title="📊 KPIs Documentation",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Título principal con estilo
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 50%, #1E3A8A 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 3rem;">
            ⚽ DOCUMENTACIÓN DE KPIs
        </h1>
        <p style="color: #E5E7EB; text-align: center; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
            Indicadores de Rendimiento entorno al Gol
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Navegación con tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Juego Abierto", "📊 Goal Envolvement", "⚡ Goal Conversion", 
        "🔄 Possession GoalChance", "🏁 Goal Performance", "⚽ Balón Parado"
    ])

    with tab1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #065F46 0%, #047857 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <h2 style="color: white; margin: 0;">🎯 JUEGO ABIERTO - DINÁMICO (Open Play)</h2>
            <p style="color: #D1FAE5; margin: 0.5rem 0 0 0;">
                Los indicadores de juego abierto evalúan el rendimiento ofensivo en situaciones de juego fluido, 
                sin intervención de jugadas a balón parado.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cards informativas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: #F8FAFC; border-left: 5px solid #10B981; padding: 1rem; border-radius: 5px;">
                <h4 style="color: #065F46; margin-top: 0;">🎯 Características Principales</h4>
                <ul style="color: #374151;">
                    <li><strong>Participación directa:</strong> Contribución en jugadas ofensivas</li>
                    <li><strong>Eficiencia de conversión:</strong> Aprovechamiento de oportunidades</li>
                    <li><strong>Transformación de posesión:</strong> Conversión en peligro</li>
                    <li><strong>Impacto global:</strong> Rendimiento ofensivo integral</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: #FEF7FF; border-left: 5px solid #A855F7; padding: 1rem; border-radius: 5px;">
                <h4 style="color: #7C2D12; margin-top: 0;">📈 Aplicaciones Tácticas</h4>
                <ul style="color: #374151;">
                    <li><strong>Análisis individual:</strong> Rendimiento de jugadores clave</li>
                    <li><strong>Evaluación colectiva:</strong> Efectividad del sistema ofensivo</li>
                    <li><strong>Comparativas:</strong> Benchmarking entre equipos</li>
                    <li><strong>Desarrollo:</strong> Identificación de áreas de mejora</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <h2 style="color: white; margin: 0;">📊 Goal Envolvement Index (GEI)</h2>
            <p style="color: #DBEAFE; margin: 0.5rem 0 0 0;">
                Índice compuesto que mide el impacto ofensivo global, más allá de goles y asistencias
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #FFF7ED; border: 1px solid #FB923C; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
            <h4 style="color: #EA580C; margin-top: 0;">🧮 Fórmula de Cálculo</h4>
            <p style="color: #9A3412; margin: 0;">
                <strong>Normalización:</strong> Se divide por minutos jugados × 0.35 para dar un valor por tiempo en cancha
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Métricas del GEI
        metrics_gei = [
            {"weight": "30%", "color": "#10B981", "title": "Ocasiones Directas", 
             "metrics": "xa + key_passes + assists", 
             "desc": "Capacidad de generar ocasiones directas. Corazón del GEI."},
            
            {"weight": "20%", "color": "#3B82F6", "title": "Pases Incisivos", 
             "metrics": "through_balls + passes_into_box + passes_inside_box + crosses_into_box", 
             "desc": "Pases que acercan al gol en el último tercio."},
            
            {"weight": "15%", "color": "#F59E0B", "title": "Presencia Ofensiva", 
             "metrics": "sp_xa + deep_progressions + touches_inside_box", 
             "desc": "Presencia ofensiva sostenida y estratégica."},
            
            {"weight": "10%", "color": "#EF4444", "title": "Construcción de Jugadas", 
             "metrics": "xgchain + xgbuildup", 
             "desc": "Participación indirecta en jugadas peligrosas."},
            
            {"weight": "10%", "color": "#8B5CF6", "title": "Productividad por Posesión", 
             "metrics": "xgchain_per_possession + xgbuildup_per_possession", 
             "desc": "Productividad normalizada por posesión."},
            
            {"weight": "5%", "color": "#6B7280", "title": "Calidad Individual", 
             "metrics": "obv_pass + obv_dribble_carry", 
             "desc": "Valor ofensivo de jugadas individuales."},
            
            {"weight": "5%", "color": "#374151", "title": "Intención Ofensiva", 
             "metrics": "forward_passes", 
             "desc": "Búsqueda de progresión vertical."}
        ]

        for i, metric in enumerate(metrics_gei):
            st.markdown(f"""
            <div style="background: white; border-left: 6px solid {metric['color']}; 
                        padding: 1rem; margin: 0.5rem 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="color: {metric['color']}; margin: 0;">{i+1}. {metric['title']}</h4>
                    <span style="background: {metric['color']}; color: white; padding: 0.3rem 0.8rem; 
                                 border-radius: 15px; font-weight: bold;">{metric['weight']}</span>
                </div>
                <p style="color: #4B5563; margin: 0.5rem 0 0 0;"><strong>Métricas:</strong> {metric['metrics']}</p>
                <p style="color: #6B7280; margin: 0.5rem 0 0 0; font-style: italic;">{metric['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <h2 style="color: white; margin: 0;">⚡ Goal Conversion Index (GCI)</h2>
            <p style="color: #FEE2E2; margin: 0.5rem 0 0 0;">
                Mide la eficiencia para convertir oportunidades ofensivas en goles reales
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #FEF2F2; border: 1px solid #F87171; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
            <h4 style="color: #DC2626; margin-top: 0;">🧮 Fórmula de Cálculo</h4>
            <p style="color: #B91C1C; margin: 0;">
                <strong>Normalización:</strong> Se divide por número total de disparos (sin penaltis) × 0.45
            </p>
        </div>
        """, unsafe_allow_html=True)

        metrics_gci = [
            {"weight": "30%", "color": "#DC2626", "title": "Goles Marcados", 
             "metrics": "goals", 
             "desc": "Resultado final esperado. Contribución directa al marcador."},
            
            {"weight": "20%", "color": "#EF4444", "title": "Calidad de Ocasiones", 
             "metrics": "np_xg", 
             "desc": "Calidad media de ocasiones generadas mediante tiros."},
            
            {"weight": "20%", "color": "#F87171", "title": "Selección de Tiros", 
             "metrics": "np_xg_per_shot", 
             "desc": "Calidad promedio por disparo. Toma de decisiones ofensivas."},
            
            {"weight": "10%", "color": "#FCA5A5", "title": "Precisión Real", 
             "metrics": "np_shots_on_target", 
             "desc": "Disparos que obligan al portero a intervenir."},
            
            {"weight": "10%", "color": "#FECACA", "title": "Eficiencia Ofensiva", 
             "metrics": "shot_touch_ratio", 
             "desc": "Porcentaje de toques que terminan en disparo."},
            
            {"weight": "5%", "color": "#FED7D7", "title": "Penaltis Provocados", 
             "metrics": "penalties_won", 
             "desc": "Oportunidades de alto valor generadas."},
            
            {"weight": "5%", "color": "#FEE2E2", "title": "Valor de Disparos", 
             "metrics": "obv_shot", 
             "desc": "Valor aportado por los tiros en sí."}
        ]

        for i, metric in enumerate(metrics_gci):
            st.markdown(f"""
            <div style="background: white; border-left: 6px solid {metric['color']}; 
                        padding: 1rem; margin: 0.5rem 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="color: {metric['color']}; margin: 0;">{i+1}. {metric['title']}</h4>
                    <span style="background: {metric['color']}; color: white; padding: 0.3rem 0.8rem; 
                                 border-radius: 15px; font-weight: bold;">{metric['weight']}</span>
                </div>
                <p style="color: #4B5563; margin: 0.5rem 0 0 0;"><strong>Métricas:</strong> {metric['metrics']}</p>
                <p style="color: #6B7280; margin: 0.5rem 0 0 0; font-style: italic;">{metric['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <h2 style="color: white; margin: 0;">🔄 Possession GoalChance Index (PGC)</h2>
            <p style="color: #EDE9FE; margin: 0.5rem 0 0 0;">
                Mide cómo se transforma la posesión del balón en situaciones claras de peligro
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #FAF5FF; border: 1px solid #C084FC; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
            <h4 style="color: #7C3AED; margin-top: 0;">🧮 Fórmula de Cálculo</h4>
            <p style="color: #6B21A8; margin: 0;">
                <strong>Normalización:</strong> Se divide por posesión total × 0.2. Premia eficiencia, no volumen.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: white; border-left: 6px solid #7C3AED; 
                        padding: 1rem; margin: 0.5rem 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="color: #7C3AED; margin: 0;">🎯 Impacto Creativo</h4>
                    <span style="background: #7C3AED; color: white; padding: 0.3rem 0.8rem; 
                                 border-radius: 15px; font-weight: bold;">85%</span>
                </div>
                <p style="color: #4B5563; margin: 0.5rem 0 0 0;">
                    <strong>Métricas:</strong> key_passes + assists + xa + xgchain
                </p>
                <p style="color: #6B7280; margin: 0.5rem 0 0 0; font-style: italic;">
                    Impacto en construcción de jugadas de gol. Capacidad creativa y resolutiva.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: white; border-left: 6px solid #A855F7; 
                        padding: 1rem; margin: 0.5rem 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="color: #A855F7; margin: 0;">🏃 Presencia en Área</h4>
                    <span style="background: #A855F7; color: white; padding: 0.3rem 0.8rem; 
                                 border-radius: 15px; font-weight: bold;">15%</span>
                </div>
                <p style="color: #4B5563; margin: 0.5rem 0 0 0;">
                    <strong>Métricas:</strong> touches_inside_box
                </p>
                <p style="color: #6B7280; margin: 0.5rem 0 0 0; font-style: italic;">
                    Presencia ofensiva directa. Progresión hasta zonas de máximo peligro.
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab5:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #059669 0%, #10B981 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <h2 style="color: white; margin: 0;">🏁 Goal Performance Index (GPI)</h2>
            <p style="color: #D1FAE5; margin: 0.5rem 0 0 0;">
                Índice global que sintetiza las tres dimensiones del rendimiento ofensivo
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Componentes del GPI
        components = [
            {"name": "Goal Envolvement Index (GEI)", "weight": "31.6%", "value": "3/9.5", 
             "color": "#3B82F6", "desc": "Participación directa en jugadas de ataque"},
            {"name": "Goal Conversion Index (GCI)", "weight": "47.4%", "value": "4.5/9.5", 
             "color": "#EF4444", "desc": "Capacidad para convertir ocasiones en goles"},
            {"name": "Possession GoalChance Index (PGC)", "weight": "21.1%", "value": "2/9.5", 
             "color": "#A855F7", "desc": "Transformación de posesión en ocasiones claras"}
        ]

        st.markdown("""
        <div style="background: #F0FDF4; border: 1px solid #22C55E; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
            <h4 style="color: #15803D; margin-top: 0;">🧮 Fórmula del GPI</h4>
            <p style="color: #166534; margin: 0;">
                <code>GPI = (GEI × 3 + GCI × 4.5 + PGC × 2) / 9.5 + 3</code>
            </p>
        </div>
        """, unsafe_allow_html=True)

        for component in components:
            st.markdown(f"""
            <div style="background: white; border-left: 6px solid {component['color']}; 
                        padding: 1rem; margin: 0.5rem 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="color: {component['color']}; margin: 0;">{component['name']}</h4>
                    <div>
                        <span style="background: {component['color']}; color: white; padding: 0.3rem 0.8rem; 
                                     border-radius: 15px; font-weight: bold; margin-right: 0.5rem;">{component['weight']}</span>
                        <span style="background: #F3F4F6; color: #374151; padding: 0.3rem 0.8rem; 
                                     border-radius: 15px; font-weight: bold;">{component['value']}</span>
                    </div>
                </div>
                <p style="color: #6B7280; margin: 0.5rem 0 0 0; font-style: italic;">{component['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab6:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #B45309 0%, #D97706 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <h2 style="color: white; margin: 0;">⚽ BALÓN PARADO (Set Piece)</h2>
            <p style="color: #FED7AA; margin: 0.5rem 0 0 0;">
                Oportunidades estructuradas: corners, tiros libres y saques de banda ofensivos
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Sub-tabs para balón parado
        subtab1, subtab2 = st.tabs(["🎯 SetPiece Efficacy Index", "📊 GoalSetPiece Performance"])

        with subtab1:
            st.markdown("""
            <div style="background: #FFFBEB; border: 1px solid #F59E0B; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <h4 style="color: #D97706; margin-top: 0;">🎯 SetPiece Efficacy Index (SPI)</h4>
                <p style="color: #92400E; margin: 0;">
                    Mide cuánto convierte un equipo las jugadas a balón parado en ocasiones y goles, 
                    con énfasis en la eficacia, no en el volumen bruto.
                </p>
            </div>
            """, unsafe_allow_html=True)

            setpiece_components = [
                {"name": "Corner Subindex", "weight": "50%", "color": "#10B981", 
                 "desc": "Productividad ofensiva en tiros de esquina"},
                {"name": "Free Kick Subindex", "weight": "25%", "color": "#F59E0B", 
                 "desc": "Eficacia en jugadas ensayadas desde faltas indirectas"},
                {"name": "Direct FK Subindex", "weight": "15%", "color": "#3B82F6", 
                 "desc": "Peligro directo de los tiros libres al arco"},
                {"name": "Throw-in Subindex", "weight": "10%", "color": "#EF4444", 
                 "desc": "Capacidad para sacar provecho de saques de banda"}
            ]

            for component in setpiece_components:
                st.markdown(f"""
                <div style="background: white; border-left: 6px solid {component['color']}; 
                            padding: 1rem; margin: 0.5rem 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="color: {component['color']}; margin: 0;">{component['name']}</h4>
                        <span style="background: {component['color']}; color: white; padding: 0.3rem 0.8rem; 
                                     border-radius: 15px; font-weight: bold;">{component['weight']}</span>
                    </div>
                    <p style="color: #6B7280; margin: 0.5rem 0 0 0; font-style: italic;">{component['desc']}</p>
                </div>
                """, unsafe_allow_html=True)

        with subtab2:
            st.markdown("""
            <div style="background: #F0F9FF; border: 1px solid #0EA5E9; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <h4 style="color: #0284C7; margin-top: 0;">📊 GoalSetPiece Performance Index (GSPI)</h4>
                <p style="color: #0369A1; margin: 0;">
                    Rendimiento final ofensivo a balón parado, ponderando conversión, eficiencia xG, 
                    volumen y calidad de las jugadas.
                </p>
            </div>
            """, unsafe_allow_html=True)

            gspi_components = [
                {"name": "Goal Conversion SP", "weight": "35%", "color": "#10B981", 
                 "desc": "Ratio de goles por oportunidades a balón parado"},
                {"name": "xG Efficiency SP", "weight": "25%", "color": "#F59E0B", 
                 "desc": "Calidad esperada promedio por jugada a balón parado"},
                {"name": "Shot Conversion SP", "weight": "20%", "color": "#3B82F6", 
                 "desc": "Ratio de tiros generados por jugada a balón parado"},
                {"name": "Volume/Efficacy Goals SP", "weight": "20%", "color": "#EF4444", 
                 "desc": "Goles por cada jugada a balón parado (eficiencia por volumen)"}
            ]

            for component in gspi_components:
                st.markdown(f"""
                <div style="background: white; border-left: 6px solid {component['color']}; 
                            padding: 1rem; margin: 0.5rem 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="color: {component['color']}; margin: 0;">{component['name']}</h4>
                        <span style="background: {component['color']}; color: white; padding: 0.3rem 0.8rem; 
                                     border-radius: 15px; font-weight: bold;">{component['weight']}</span>
                    </div>
                    <p style="color: #6B7280; margin: 0.5rem 0 0 0; font-style: italic;">{component['desc']}</p>
                </div>
                """, unsafe_allow_html=True)

    # Sidebar con información adicional
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1F2937 0%, #374151 100%); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: white; margin: 0; text-align: center;">📊 Guía Rápida</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #F9FAFB; border: 1px solid #D1D5DB; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
            <h4 style="color: #374151; margin-top: 0;">🎯 Rangos de Interpretación</h4>
            <ul style="color: #6B7280; margin: 0;">
                <li><strong>9.0-9.5:</strong> Excelente</li>
                <li><strong>7.0-8.9:</strong> Muy Bueno</li>
                <li><strong>5.0-6.9:</strong> Promedio</li>
                <li><strong>3.0-4.9:</strong> Por debajo del promedio</li>
                <li><strong>0.5-2.9:</strong> Necesita mejora</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #FEF7FF; border: 1px solid #C084FC; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
            <h4 style="color: #7C3AED; margin-top: 0;">📈 Aplicaciones</h4>
            <ul style="color: #6B7280; margin: 0;">
                <li>Análisis de rendimiento</li>
                <li>Comparativas entre equipos</li>
                <li>Identificación de fortalezas</li>
                <li>Detección de áreas de mejora</li>
                <li>Seguimiento de progreso</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="background: #F3F4F6; padding: 1rem; border-radius: 10px; margin-top: 2rem; text-align: center;">
        <p style="color: #6B7280; margin: 0;">
            📊 <strong>TPAC Methodology</strong> | Data from StatsBomb | Code by @Sevi
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    app()