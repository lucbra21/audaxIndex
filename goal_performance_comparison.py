import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from math import pi
import os
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from mplsoccer.utils import add_image
from PIL import Image

def app():
    st.title("Goal Performance Team Comparison")
    
    try:
        # --- RUTAS ---
        ESCUDOS_PATH = "AUDAX/Chile Primeradivision/"
        DATA_PATH = "AUDAX/df_final.csv"

        # --- CARGA DE DATOS ---
        df = pd.read_csv(DATA_PATH)
        match_df = df[df["match_id"] != "AVG"].copy()
        match_df["match_id"] = match_df["match_id"].astype(str)
        match_df["x_label"] = match_df.apply(lambda row: f"J{row['match_week']}: {row['match_score']}", axis=1)

        # --- MÉTRICAS ---
        metrics_dict = {
            'np_xg': 'npXG',
            'np_shots': 'Shots',
            'obv_shot': 'OBV Shots',
            'xgchain': 'xG Chance',
            'goals': 'Goals',
            'Goal Envolvement Index (norm)': 'Goal Envolvement',
            'Goal Conversion Index (norm)': 'Goal Conversion',
            'Possession GoalChance Index (norm)': 'Poss. GoalChance',
            'Goal Performance Index': 'Goal Performance'
        }
        metrics = list(metrics_dict.keys())
        clean_labels = [metrics_dict[m] for m in metrics]

        # Añadir columnas percentil
        for col in metrics:
            if col + "_pctl" not in df.columns:
                df[col + "_pctl"] = df[col].rank(pct=True) * 100
        pctl_metrics = [m + "_pctl" for m in metrics]

        # --- KPIs Evolutivos ---
        kpi_list = [
            "Goal Envolvement Index (norm)",
            "Goal Conversion Index (norm)",
            "Possession GoalChance Index (norm)",
            "Goal Performance Index"
        ]

        # --- FUNCIONES ---
        def get_jornada_options(equipo):
            sub = df[df["team_name"] == equipo][["match_week", "match_id"]].drop_duplicates()
            opts = []
            for _, r in sub.iterrows():
                mw, mid = r["match_week"], r["match_id"]
                mdf = df[df["match_id"] == mid]
                if mdf.shape[0] != 2: continue
                t1, t2 = mdf.iloc[0], mdf.iloc[1]
                local, visita = (t1, t2) if t1["team_name"] == t1["home_team"] else (t2, t1)
                marcador = f"{int(local['goals'])}-{int(visita['goals'])}"
                label = f"J{mw} - {local['team_name']} {marcador} {visita['team_name']}"
                opts.append((label, mw))
            return opts

        # --- SELECCIÓN DE EQUIPO Y JORNADA ---
        available_teams = sorted([t for t in df["team_name"].unique() if t != "ALL_TEAMS_AVG"])
        equipo = st.selectbox("Equipo:", available_teams)
        
        # Obtener opciones de jornadas
        jornada_options = get_jornada_options(equipo)
        if jornada_options:
            jornada_labels = [label for label, _ in jornada_options]
            jornada_values = [value for _, value in jornada_options]
            selected_index = st.selectbox("Jornada:", range(len(jornada_labels)), format_func=lambda i: jornada_labels[i])
            jornada = jornada_values[selected_index]
            
            if st.button("Generar análisis"):
                # Filtrar datos
                md = df[(df["team_name"] == equipo) & (df["match_week"] == jornada)]
                if md.empty:
                    st.error("No se encontró ese equipo en esa jornada.")
                else:
                    mid = md.iloc[0]["match_id"]
                    mdf = df[df["match_id"] == mid]
                    if mdf.shape[0] != 2:
                        st.error("Datos incompletos.")
                    else:
                        team_row = mdf[mdf["team_name"] == equipo].iloc[0]
                        rival_row = mdf[mdf["team_name"] != equipo].iloc[0]

                        team_vals = [team_row[m] for m in pctl_metrics] + [team_row[pctl_metrics[0]]]
                        rival_vals = [rival_row[m] for m in pctl_metrics] + [rival_row[pctl_metrics[0]]]
                        angles = [n / float(len(metrics)) * 2 * pi for n in range(len(metrics))] + [0]

                        local, visita = (team_row, rival_row) if team_row["team_name"] == team_row["home_team"] else (rival_row, team_row)
                        marcador = f"{int(local['goals'])}-{int(visita['goals'])}"
                        title = f"{local['team_name']} {marcador} {visita['team_name']} - Jornada {jornada}"

                        fig = plt.figure(figsize=(20, 30), facecolor="#0E3F5C")
                        gs = gridspec.GridSpec(3, 1, height_ratios=[1.6, 0.6, 1.4], figure=fig)

                        # Subtítulo
                        fig.text(0.5, 0.91, "GoalPerformance Team Comparison", ha='center', va='center', color='lightgray', fontsize=26, fontweight='bold')

                        # --- RADAR ---
                        radar_ax = fig.add_subplot(gs[0], polar=True, facecolor="#0E3F5C")

                        radar_ax.spines['polar'].set_color((0.8, 0.8, 0.8, 0.2))
                        radar_ax.spines['polar'].set_linewidth(1.5)

                        radar_ax.plot(angles, team_vals, linewidth=3, label=equipo, color='gold')
                        radar_ax.fill(angles, team_vals, color='gold', alpha=0.4)
                        radar_ax.plot(angles, rival_vals, linewidth=3, label=rival_row["team_name"], color='lightgray')
                        radar_ax.fill(angles, rival_vals, color='lightgray', alpha=0.4)
                        radar_ax.set_xticks(angles[:-1])
                        radar_ax.set_xticklabels(clean_labels, color='white', size=15)
                        radar_ax.set_yticklabels([])
                        radar_ax.grid(True, color="white", linestyle='--', alpha=0.3)
                        radar_ax.set_title(title, color="white", fontsize=20, pad=30)

                        legend = radar_ax.legend(loc='lower left', fontsize=20, frameon=False, bbox_to_anchor=(-0.3, -0.1))
                        for text in legend.get_texts():
                            text.set_color('white')
                        
                        fig.text(0.97, 0.5, "Data StatsBomb Teams GoalPerformance | code by: @Sevi", color='lightgray', fontsize=12, ha='right', va='bottom')
                        
                        try:
                            local_badge_path = os.path.join(ESCUDOS_PATH, f"{local['team_name']}.png")
                            visita_badge_path = os.path.join(ESCUDOS_PATH, f"{visita['team_name']}.png")
                            
                            if os.path.exists(local_badge_path):
                                local_badge = Image.open(local_badge_path)
                                add_image(local_badge, fig, 0.05, 0.82, 0.12, 0.12)
                                
                            if os.path.exists(visita_badge_path):
                                visita_badge = Image.open(visita_badge_path)
                                add_image(visita_badge, fig, 0.83, 0.82, 0.12, 0.12)
                        except Exception as e:
                            st.warning(f"No se pudieron cargar algunas imágenes: {e}")

                        # --- TABLA ---
                        tabla_ax = fig.add_subplot(gs[1])
                        tabla_ax.axis("off")
                        df_tabla = pd.DataFrame(
                            [[equipo] + [round(team_row[m], 2) for m in pctl_metrics],
                             [rival_row["team_name"]] + [round(rival_row[m], 2) for m in pctl_metrics]],
                            columns=["Equipo"] + clean_labels
                        )

                        def color_cells(value):
                            if value < 40: return '#f4d03f'
                            elif 40 <= value < 65: return '#82e0aa'
                            elif 65 <= value < 85: return '#28b463'
                            else: return '#196f3d'

                        def text_color(name): return 'gold' if name == equipo else '#E0E0E0'
                        colores = [[color_cells(val) for val in row] for row in df_tabla.iloc[:, 1:].values]
                        colores_final = [['#0E3F5C'] + row for row in colores]

                        tabla = tabla_ax.table(
                            cellText=df_tabla.values,
                            colLabels=df_tabla.columns,
                            cellColours=colores_final,
                            cellLoc='center',
                            loc='center'
                        )
                        tabla.auto_set_font_size(False)
                        tabla.set_fontsize(11)
                        tabla.scale(1.3, 2)

                        for (i, j), cell in tabla.get_celld().items():
                            cell.set_edgecolor('white')
                            if i == 0:
                                cell.set_text_props(color='white', weight='bold')
                                cell.set_facecolor('#0E3F5C')
                            else:
                                if j == 0:
                                    cell.set_text_props(color=text_color(df_tabla.iloc[i-1, 0]), weight='bold')
                                    cell.set_facecolor('#0E3F5C')
                                else:
                                    cell.set_text_props(color='white', weight='bold')

                        # --- KPIs EVOLUTIVOS ---
                        team_df = match_df[match_df["team_name"] == equipo].sort_values("match_week")
                        kpi_ax = fig.add_subplot(gs[2])
                        kpi_ax.axis("off")

                        legend_lines = []

                        fig.text(0.5, 0.43, "Evolución de KPIs", ha='center', va='center', color='lightgray', fontsize=26, fontweight='bold')

                        for i, kpi in enumerate(kpi_list):
                            sub_ax = fig.add_axes([0.07 + (i % 2) * 0.46, 0.04 + (1 - i // 2) * 0.2, 0.4, 0.15], facecolor="#0E3F5C")
                            team_avg = team_df[kpi].mean()
                            all_avg = match_df[kpi].mean()

                            # Graficar todos los puntos normales
                            sub_ax.plot(team_df["x_label"], team_df[kpi], marker='o', color='lime', label=equipo, markersize=6)

                            # Resaltar nodo de la jornada seleccionada
                            if jornada in team_df["match_week"].values:
                                idx = team_df[team_df["match_week"] == jornada].index[0]
                                x = team_df.loc[idx, "x_label"]
                                y = team_df.loc[idx, kpi]
                                sub_ax.plot(x, y, marker='o', markersize=13, markeredgewidth=2, markeredgecolor='black', markerfacecolor='greenyellow', zorder=5)

                            # Líneas promedio
                            sub_ax.axhline(team_avg, color='palegreen', linestyle='--', label=f'Prom. {equipo}')
                            sub_ax.axhline(all_avg, color='lightgray', linestyle=':', label='Prom. Liga')

                            if i == 0:
                                 legend_lines = [
                                     Line2D([0], [0], color='lime', marker='o', label=equipo),
                                     Line2D([0], [0], color='palegreen', linestyle='--', label=f'Prom. {equipo}'),
                                     Line2D([0], [0], color='lightgray', linestyle=':', label='Prom. Liga')
                                ]

                            sub_ax.set_title(kpi.replace(" (norm)", ""), color="white", fontsize=14)
                            sub_ax.tick_params(colors='white', labelsize=10)

                            jornadas_labels = team_df["match_week"].apply(lambda x: f"J{x}").tolist()
                            sub_ax.set_xticks(team_df["x_label"])
                            sub_ax.set_xticklabels(jornadas_labels, rotation=30, ha='right')
                            sub_ax.grid(color='white', linestyle='--', alpha=0.2)

                        fig.legend(handles=legend_lines, loc='upper center', bbox_to_anchor=(0.5, 0.42), ncol=3, fontsize=18, frameon=False)

                        output_path = "AUDAX/Radar_Comparativo.png"
                        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
                        
                        # Mostrar imagen en Streamlit
                        st.image(output_path)
        else:
            st.warning(f"No hay jornadas disponibles para el equipo {equipo}")
    
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        st.info("Asegúrate de que el archivo 'AUDAX/df_final.csv' exista y tenga el formato correcto.")
