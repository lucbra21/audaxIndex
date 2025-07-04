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
    st.title("⚽ Goal Performance Analysis")
    st.markdown("---")
    
    # Crear tabs para organizar mejor el contenido
    tab1, tab2, tab3 = st.tabs(["📊 Rankings", "🎯 Análisis Individual", "📈 Comparativas"])
    
    # -------------------------------------------
    # 📌 CARGA DE DATOS
    # -------------------------------------------
    @st.cache_data
    def load_data():
        """Cargar datos desde el CSV"""
        try:
            # Intentar cargar desde diferentes ubicaciones posibles
            possible_paths = [
                "data/df_GoalKPIs_TopValues.csv",
                "data/goal_kpis_with_top_values.csv",
                "goal_kpis_with_top_values.csv",
                "data/goal_kpis.csv",
                "goal_kpis.csv",
                "data/df_GoalKPIs.csv"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    df = pd.read_csv(path)
                    st.success(f"✅ Datos cargados desde: {path}")
                    return df
            
            st.error("❌ No se encontró el archivo CSV. Asegúrate de tener los datos disponibles.")
            return None
            
        except Exception as e:
            st.error(f"❌ Error al cargar los datos: {str(e)}")
            return None
    
    # Cargar datos
    with st.spinner("📊 Cargando datos..."):
        df = load_data()
    
    if df is None:
        st.stop()
    
    # Obtener equipos disponibles
    equipos = df[~df["team_name"].str.contains("TopValues", na=False)]["team_name"].unique()
    
    # -------------------------------------------
    # TAB 1: RANKINGS INTERACTIVOS
    # -------------------------------------------
    with tab1:
        st.header("🏆 Rankings Interactivos por KPI")
        
        # Mostrar información básica
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_teams = len(equipos)
            st.metric("🏆 Total de Equipos", total_teams)
        
        with col2:
            if 'match_week' in df.columns:
                max_week = df[df['match_week'].notna()]['match_week'].max()
                st.metric("📅 Jornada Actual", int(max_week) if max_week else "N/A")
        
        with col3:
            kpi_count = len([col for col in df.columns if 'Index' in col or 'Efficiency' in col])
            st.metric("📊 KPIs Disponibles", kpi_count)
        
        # Lista de KPIs disponibles
        available_kpis = []
        possible_kpis = [
            "Goal Performance Index",
            "Goal Envolvement Index",
            "Goal Conversion Index", 
            "Possession GoalChance Index",
            "SetPiece Eficcacy Index",
            "GoalSetPiece Performance Index",
            "corner Efficiency",
            "freekick Efficiency",
            "directfk Efficiency",
            "throw in Efficiency"
        ]
        
        for kpi in possible_kpis:
            if kpi in df.columns:
                available_kpis.append(kpi)
        
        # Función para crear ranking (EXACTAMENTE tu función original)
        def plot_ranking(selected_kpi):
            # Crear copia para no modificar el original
            # df_plot = ranking_df.copy()
            df_plot = pd.read_csv("data/df_GoalKPIs_TopValues.csv")
            
            # Calcular Rank dinámicamente según KPI seleccionado
            df_plot["Rank (avg)"] = df_plot[selected_kpi].rank(ascending=False, method='min').astype(int)
            
            # Ordenar según nuevo ranking
            df_plot = df_plot.sort_values("Rank (avg)").copy()
            
            # Redondear valores numéricos a 3 decimales
            numeric_cols = df_plot.select_dtypes(include='number').columns
            df_plot[numeric_cols] = df_plot[numeric_cols].round(3)

            # Crear figura
            fig, ax = plt.subplots(figsize=(18, 12))
            ax.set_facecolor("#0E3F5C")
            fig.patch.set_facecolor("#0E3F5C")  # Solo añadido esto para Streamlit

            # Seleccionar columnas a mostrar
            display_df = df_plot[[
                "Rank (avg)", "team_name", "match_week",
                "Goal Performance Index",
                "Goal Envolvement Index",
                "Goal Conversion Index",
                "Possession GoalChance Index",
                "SetPiece Eficcacy Index",
                "GoalSetPiece Performance Index"
            ]]

            # Crear tabla
            table = ax.table(
                cellText=display_df.values,
                colLabels=display_df.columns,
                cellLoc='center',
                loc='center',
                colColours=["#1C5D77"] * display_df.shape[1]
            )

            # Estilo de la tabla
            table.auto_set_font_size(False)
            table.set_fontsize(28)

            for (row, col), cell in table.get_celld().items():
                if row == 0:
                    # Encabezado
                    cell.set_fontsize(22)
                    cell.set_text_props(weight='bold', color='white')
                    cell.set_edgecolor("white")
                    cell.set_facecolor("#1C5D77")
                    cell.set_height(0.08)
                else:
                    # Celdas de datos
                    col_name = display_df.columns[col]
                    value = display_df.iloc[row - 1][col_name]

                    cell.set_text_props(color='white')
                    cell.set_edgecolor("white")
                    cell.set_facecolor("#0E3F5C")
                    cell.set_height(0.1)

                    # Resaltar KPI seleccionado
                    if col_name == selected_kpi:
                        if value >= 7:
                            cell.set_facecolor("darkgreen")
                        elif value >= 6.5:
                            cell.set_facecolor("forestgreen")
                        elif value >= 6:
                            cell.set_facecolor("seagreen")
                        else:
                            cell.set_facecolor("mediumseagreen")

                # Ajustar anchos
                col_name = display_df.columns[col]
                if col_name in ["Rank (avg)", "match_week"]:
                    cell.set_width(0.18)
                else:
                    cell.set_width(0.45)

            ax.axis("off")
            
            return fig  # Cambio: devolver fig en lugar de plt.show()
        
        if available_kpis:
            # Selector de KPI
            selected_kpi = st.selectbox(
                "📈 Selecciona KPI para Ranking:",
                options=available_kpis,
                index=0,
                key="ranking_kpi"
            )
            
            # Generar y mostrar gráfico
            with st.spinner("📊 Generando ranking..."):
                # fig = plot_ranking(df, selected_kpi)
                fig = plot_ranking(selected_kpi)
                
                if fig:
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)
            
            # Mostrar estadísticas del KPI
            teams_df = df[~df['team_name'].str.contains('TopValues', na=False)]
            if selected_kpi in teams_df.columns:
                with st.expander("📊 Estadísticas del KPI seleccionado"):
                    kpi_stats = teams_df[selected_kpi].describe()
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Promedio", f"{kpi_stats['mean']:.2f}")
                    with col2:
                        st.metric("Máximo", f"{kpi_stats['max']:.2f}")
                    with col3:
                        st.metric("Mínimo", f"{kpi_stats['min']:.2f}")
                    with col4:
                        st.metric("Desv. Estándar", f"{kpi_stats['std']:.2f}")
        else:
            st.error("❌ No se encontraron KPIs válidos en los datos")

    # -------------------------------------------
    # TAB 2: ANÁLISIS INDIVIDUAL (TU CÓDIGO ORIGINAL)
    # -------------------------------------------
    with tab2:
        st.header("🎯 Análisis Individual Detallado")
        
        # Selección de equipo
        team_name = st.selectbox('Selecciona equipo:', sorted(equipos), key="individual_team")
        
        if st.button("🔍 Generar Análisis Completo"):
            try:

                
                # Carpetas y rutas
                output_dir = "AUDAX/"
                os.makedirs(output_dir, exist_ok=True)
                badge_path = f"Chile Primeradivision/{team_name}.png"
                ligue_path = f"Chile Primeradivision/Liga de Primera Itaú.png"

                # Columnas para visualización
                display_cols = [
                    "team_name",
                    "Goal Performance Index", "Goal Envolvement Index",
                    "Goal Conversion Index", "Possession GoalChance Index",
                    "corner Efficiency", "freekick Efficiency",
                    "directfk Efficiency", "throw in Efficiency",
                    "SetPiece Eficcacy Index", "GoalSetPiece Performance Index"
                ]
                
                # Filtrar solo columnas que existen
                existing_cols = ["team_name"] + [col for col in display_cols[1:] if col in df.columns]
                
                # Obtener datos del equipo
                team_data = df[df["team_name"] == team_name][existing_cols].iloc[0]
                values = team_data[1:].astype(float).values
                
                # Obtener valores top
                top_min = df[df["team_name"] == "TopValues (min)"][existing_cols[1:]].astype(float).values[0]
                
                # Preparar parámetros para el radar
                params = [c.replace(" Index", "").replace(" Efficiency", "").replace(" Eficcacy", "") for c in existing_cols[1:]]
                min_values = [0.5] * len(params)
                max_values = [9.5] * len(params)
                slice_colors = ["lightgreen" if values[i] < top_min[i] else "darkgreen" for i in range(len(values))]

                bg_color = '#0E3F5C'

                # --------------------- 1. RADAR CHART (MEJORADO) ---------------------
                baker = PyPizza(
                    params=params,
                    min_range=min_values,
                    max_range=max_values,
                    background_color=bg_color,
                    straight_line_color="white",
                    last_circle_color="white",
                    last_circle_lw=1.5,
                    straight_line_lw=1,
                    other_circle_lw=0,
                    other_circle_color="white",
                    inner_circle_size=12,
                )

                fig1, ax = baker.make_pizza(
                    values,
                    figsize=(8, 8),
                    color_blank_space="same",
                    blank_alpha=0.3,
                    param_location=110,
                    slice_colors=slice_colors,
                    kwargs_slices=dict(facecolor="lightgreen", edgecolor="lightgreen", zorder=1, linewidth=1),
                    kwargs_params=dict(color="lightgreen", fontsize=10, va="center"),
                    kwargs_values=dict(color="white", fontsize=12,
                                    bbox=dict(edgecolor="lightgreen", facecolor="green",
                                                boxstyle="round,pad=0.2", lw=1))
                )
                
                fig1.text(0.5, 0.97, team_name, size=18, ha="center", color="white")
                fig1.text(0.5, 0.94,
                        "Chile - Primera División | Tactical SetPiece Profile",
                        size=13, ha="center", color="white")
                fig1.text(0.99, 0.005,
                        "Data from StatsBomb | Code by @Sevi | TPAC Methodology",
                        size=9, color="#F2F2F2", ha="right")
                
                # Añadir logos con posiciones mejoradas
                if os.path.exists(badge_path):
                    badge = Image.open(badge_path)
                    add_image(badge, fig1, left=0.435, bottom=0.43, width=0.15, height=0.15)
                if os.path.exists(ligue_path):
                    ligue = Image.open(ligue_path)
                    add_image(ligue, fig1, left=0.02, bottom=0.01, width=0.15, height=0.15)
                
                radar_path = f"{output_dir}{team_name}_GoalPerformance_Profile.png"
                fig1.savefig(radar_path, dpi=300, bbox_inches='tight', facecolor=fig1.get_facecolor())
                plt.close(fig1)

                # Mostrar métricas numéricas
                # st.subheader("📋 Resumen Numérico")
                # team_metrics = df.loc[df["team_name"] == team_name, existing_cols[1:]].iloc[0]
                # for i, (kpi, value) in enumerate(team_metrics.items()):
                #     if i % 2 == 0:
                #         col_a, col_b = st.columns(2)
                #         col_a.metric(kpi.replace(" Index", "").replace(" Efficiency", ""), f"{value:.2f}")
                #     else:
                #         if i < len(team_metrics) - 1:
                #             next_kpi = list(team_metrics.items())[i][0]
                #             next_value = list(team_metrics.items())[i][1]
                #             col_b.metric(next_kpi.replace(" Index", "").replace(" Efficiency", ""), f"{next_value:.2f}")
                # --------------------- 2. BOXPLOT ---------------------
                kpi_names = existing_cols[1:]
                if "TopValues (min)" in df["team_name"].values and "TopValues (max)" in df["team_name"].values:
                    top_min_vals = df.loc[df["team_name"] == "TopValues (min)", kpi_names].iloc[0].astype(float)
                    top_max_vals = df.loc[df["team_name"] == "TopValues (max)", kpi_names].iloc[0].astype(float)
                    team_vals = df.loc[df["team_name"] == team_name, kpi_names].iloc[0].astype(float)
                    data = [[top_min_vals[kpi], team_vals[kpi], top_max_vals[kpi]] for kpi in kpi_names]

                    def get_color(val, mn, mx):
                        return 'lightgreen' if val < mn else 'darkgreen'

                    fig2, ax = plt.subplots(figsize=(14, 10))
                    fig2.patch.set_facecolor(bg_color)
                    ax.set_facecolor(bg_color)
                    ax.boxplot(data, vert=False, patch_artist=True, widths=0.6,
                            boxprops=dict(color='white'), medianprops=dict(color='white'),
                            whiskerprops=dict(color='white'), capprops=dict(color='white'),
                            flierprops=dict(marker='o', color='white', alpha=0.5))
                    
                    for i, kpi in enumerate(kpi_names):
                        val = team_vals[kpi]
                        color = get_color(val, top_min_vals[kpi], top_max_vals[kpi])
                        ax.plot(val, i+1, 'o', markersize=12, color=color, markeredgecolor='black', markeredgewidth=1.5)
                        ax.text(val, i+1 + 0.2, f'{val:.2f}', ha='center', va='bottom', fontsize=11, color='white', fontweight='bold')
                        ax.text(top_min_vals[kpi] - 0.3, i+1, f'{top_min_vals[kpi]:.2f}', ha='right', va='center', fontsize=9, color='white')
                        ax.text(top_max_vals[kpi] + 0.3, i+1, f'{top_max_vals[kpi]:.2f}', ha='left', va='center', fontsize=9, color='white')
                    
                    ax.set_yticks(range(1, len(kpi_names)+1))
                    ax.set_yticklabels(kpi_names, color='white', fontsize=12, fontweight='bold')
                    ax.set_xlabel("Valor", color='white', fontsize=12)
                    ax.tick_params(axis='x', colors='white')
                    for side in ['top', 'right']:
                        ax.spines[side].set_visible(False)
                    for side in ['bottom', 'left']:
                        ax.spines[side].set_color('white')
                    ax.set_title(f'GoalPerformace {team_name} vs TopValues', color='white', fontsize=16, fontweight='bold')
                    
                    if os.path.exists(badge_path):
                        badge = Image.open(badge_path)
                        add_image(badge, fig2, left=0.25, bottom=0.2, width=0.65, height=0.65, alpha=0.2)
                    
                    boxplot_path = f"{output_dir}GoalPerformance{team_name}_vs_TopValues.png"
                    fig2.savefig(boxplot_path, dpi=300, bbox_inches='tight', facecolor=fig2.get_facecolor())
                    plt.close(fig2)

                    # --------------------- 3. PERFORMANCE BOXES ---------------------
                    top_min = df.loc[df["team_name"] == "TopValues (min)", kpi_names].iloc[0].astype(float)
                    top_max = df.loc[df["team_name"] == "TopValues (max)", kpi_names].iloc[0].astype(float)
                    row = df.loc[df["team_name"] == team_name, kpi_names].iloc[0].astype(float)

                    goal_perf = row.get("Goal Performance Index", 5.0)
                    setpiece_perf = row.get("GoalSetPiece Performance Index", 5.0)
                    below = (row < top_min).sum()
                    improvement_pct = (below / len(kpi_names)) * 100
                    x_perf = (row / top_max).mean() * (9.5 - 0.5) + 0.5

                    metrics = [
                        ("Goal\nPerformance", goal_perf),
                        ("Goal SetPiece\nPerformance", setpiece_perf),
                        ("Improvement\nArea (%)", improvement_pct),
                        ("xPerformance\nPotential", x_perf)
                    ]

                    cmap = cm.get_cmap('Greens')
                    norm = mcolors.Normalize(vmin=0, vmax=10)
                    outline_effect = [path_effects.withStroke(linewidth=2, foreground='black')]
                    spacing = 6
                    box_width, box_height = 3.5, 1

                    fig3, ax = plt.subplots(figsize=(20, 5))
                    fig3.patch.set_facecolor(bg_color)
                    ax.set_facecolor(bg_color)
                    
                    for i, (label, val) in enumerate(metrics):
                        x0 = i * spacing
                        color = cmap(norm(val))
                        box = patches.FancyBboxPatch((x0, 0.5), width=box_width, height=box_height,
                                                boxstyle="round,pad=0.2", edgecolor='black', facecolor=color)
                        ax.add_patch(box)
                        ax.text(x0 + box_width/2, 1.3, label, ha='center', va='center',
                                fontsize=18, fontweight='bold', color='white', path_effects=outline_effect)
                        ax.text(x0 + box_width/2, 0.7, f"{val:.2f}", ha='center', va='center',
                                fontsize=35, fontweight='bold', color='white', path_effects=outline_effect)
                    
                    ax.set_xlim(-2.5, spacing * len(metrics))
                    ax.set_ylim(0, 2.5)
                    ax.axis('off')
                    ax.set_title(f"{team_name}\nAdvanced Performance Keys", color='lightgray', fontsize=30, fontweight='bold', pad=3)
                    
                    if os.path.exists(badge_path):
                        badge = Image.open(badge_path)
                        add_image(badge, fig3, left=0.12, bottom=0.75, width=0.25, height=0.25, alpha=0.8)
                    if os.path.exists(ligue_path):
                        ligue = Image.open(ligue_path)
                        add_image(ligue, fig3, left=0.65, bottom=0.73, width=0.25, height=0.25)
                    
                    box_path = f"{output_dir}GoalPerformance_{team_name}_Advanced_Indexes.png"
                    fig3.savefig(box_path, dpi=300, bbox_inches='tight', facecolor=fig3.get_facecolor())
                    plt.close(fig3)

                    # --------------------- MOSTRAR RESULTADOS ---------------------
                    st.success("✅ Análisis generado exitosamente!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🎯 Perfil de Goal Performance")
                        if os.path.exists(radar_path):
                            st.image(radar_path)
                        
                        
                    
                    with col2:
                        st.subheader("📈 Índices Avanzados")
                        if os.path.exists(box_path):
                            st.image(box_path)
                        
                        st.subheader("📊 Comparativa vs TopValues")
                        if os.path.exists(boxplot_path):
                            st.image(boxplot_path)
                else:
                    st.warning("⚠️ No se encontraron valores TopValues para comparación")
                    
            except Exception as e:
                st.error(f"❌ Error al generar el análisis: {str(e)}")
                st.info("Verifica que todos los archivos necesarios estén disponibles")
    
    # -------------------------------------------
    # TAB 3: COMPARATIVAS
    # -------------------------------------------
    with tab3:
        st.header("📈 Comparativas entre Equipos")
        
        # Selección múltiple de equipos
        selected_teams = st.multiselect(
            "Selecciona equipos para comparar:",
            options=sorted(equipos),
            default=sorted(equipos)[:3] if len(equipos) >= 3 else sorted(equipos),
            key="compare_teams"
        )
        
        if selected_teams and len(selected_teams) >= 2:
            # Seleccionar KPIs para comparar
            available_kpis_compare = [kpi for kpi in available_kpis if kpi in df.columns]
            selected_kpis_compare = st.multiselect(
                "Selecciona KPIs para comparar:",
                options=available_kpis_compare,
                default=available_kpis_compare[:4] if len(available_kpis_compare) >= 4 else available_kpis_compare,
                key="compare_kpis"
            )
            
            if selected_kpis_compare:
                # Filtrar datos para equipos seleccionados
                compare_df = df[df["team_name"].isin(selected_teams)][["team_name"] + selected_kpis_compare]
                
                # Crear gráfico de barras comparativo
                fig, axes = plt.subplots(2, 2, figsize=(15, 10))
                fig.patch.set_facecolor('#0E3F5C')
                axes = axes.flatten()
                
                colors = plt.cm.Set3(np.linspace(0, 1, len(selected_teams)))
                
                for i, kpi in enumerate(selected_kpis_compare[:4]):  # Mostrar máximo 4 KPIs
                    ax = axes[i]
                    ax.set_facecolor('#0E3F5C')
                    
                    values = [compare_df[compare_df["team_name"] == team][kpi].iloc[0] for team in selected_teams]
                    bars = ax.bar(selected_teams, values, color=colors)
                    
                    # Personalizar el gráfico
                    ax.set_title(kpi.replace(" Index", "").replace(" Efficiency", ""), 
                               color='white', fontsize=12, fontweight='bold')
                    ax.set_ylabel("Valor", color='white')
                    ax.tick_params(axis='x', colors='white', rotation=45)
                    ax.tick_params(axis='y', colors='white')
                    ax.spines['bottom'].set_color('white')
                    ax.spines['left'].set_color('white')
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    
                    # Añadir valores encima de las barras
                    for bar, value in zip(bars, values):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                               f'{value:.2f}', ha='center', va='bottom', color='white', fontsize=10)
                
                # Ocultar subplots no utilizados
                for i in range(len(selected_kpis_compare), 4):
                    axes[i].set_visible(False)
                
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
                
                # Mostrar tabla comparativa
                st.subheader("📋 Tabla Comparativa")
                compare_display = compare_df.round(3)
                st.dataframe(compare_display, use_container_width=True, hide_index=True)
                
        else:
            st.info("👆 Selecciona al menos 2 equipos para realizar comparativas")

    # Información adicional en sidebar
    with st.sidebar:
        st.header("📊 Información")
        st.markdown("""
        **🎨 Código de Colores:**
        - 🟢 **Verde Oscuro**: >= 7.0 (Excelente)
        - 🟢 **Verde Bosque**: >= 6.5 (Muy Bueno)  
        - 🟢 **Verde Mar**: >= 6.0 (Bueno)
        - 🟢 **Verde Medio**: < 6.0 (Regular)
        
        **📈 KPIs Principales:**
        - **Goal Performance**: Rendimiento general
        - **Goal Envolvement**: Participación en jugadas
        - **Goal Conversion**: Eficiencia de conversión
        - **Possession GoalChance**: Oportunidades en posesión
        - **SetPiece Efficacy**: Eficacia en balón parado
        """)
        
        if df is not None:
            st.markdown("---")
            st.subheader("📈 Estadísticas Generales")
            teams_df = df[~df['team_name'].str.contains('TopValues', na=False)]
            if not teams_df.empty and 'Goal Performance Index' in teams_df.columns:
                avg_performance = teams_df['Goal Performance Index'].mean()
                st.metric("Promedio Liga", f"{avg_performance:.2f}")

if __name__ == "__main__":
    app()