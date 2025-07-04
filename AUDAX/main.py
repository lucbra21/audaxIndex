import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# ---------- CONFIGURACIÓN ----------
pctl_metrics_dict = {
    'np_xg': 'npXG',
    'np_shots': 'Shots',
    'obv_shot': 'OBV Shots',
    'xgchain': 'xG Chance',
    'goals': 'Goals',
    'Goal Envolvement Index (norm)': 'Goal Envolvement',
    'Goal Conversion Index (norm)': 'Goal Conversion',
    'Possession GoalChance Index (norm)': 'Possession GoalChance',
    'Goal Performance Index': 'Goal Performance'
}
metrics = list(pctl_metrics_dict.keys())
pctl_metrics = [col + "_pctl" for col in metrics]
clean_labels = list(pctl_metrics_dict.values())

# ---------- RADAR INDIVIDUAL ----------
def generar_radar(df, equipo, output_path):
    row = df[df["team_name"] == equipo].iloc[0]
    values = [round(row[col], 2) for col in pctl_metrics]
    angles = np.linspace(0, 2 * np.pi, len(values), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    labels = clean_labels + [clean_labels[0]]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color='lime', linewidth=2)
    ax.fill(angles, values, color='lime', alpha=0.3)
    ax.set_facecolor('#0E3F5C')
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 100)
    ax.set_title(equipo, color='white', weight='bold', size=16, pad=20)
    ax.tick_params(colors='white')
    for label in ax.get_xticklabels():
        label.set_color('white')
    for label in ax.get_yticklabels():
        label.set_color('white')

    fig.patch.set_facecolor('#0E3F5C')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

# ---------- TABLA COMPARATIVA ----------
def color_cells(value):
    if value < 40:
        return '#f4d03f'
    elif 40 <= value < 65:
        return '#82e0aa'
    elif 65 <= value < 85:
        return '#28b463'
    else:
        return '#196f3d'

def generar_tabla_comparativa(df, equipo1, equipo2, output_path):
    row1 = df[df["team_name"] == equipo1].iloc[0]
    row2 = df[df["team_name"] == equipo2].iloc[0]

    equipo1_vals = [round(row1[m], 2) for m in pctl_metrics]
    equipo2_vals = [round(row2[m], 2) for m in pctl_metrics]

    table_data = pd.DataFrame(
        [[equipo1] + equipo1_vals, [equipo2] + equipo2_vals],
        columns=["Equipo"] + clean_labels
    )

    def text_color(equipo):
        return 'gold' if equipo == equipo1 else '#E0E0E0'

    cell_colors = [[color_cells(val) for val in row] for row in table_data.iloc[:, 1:].values]
    full_colors = [['#0E3F5C'] + row for row in cell_colors]

    fig, ax_table = plt.subplots(figsize=(15, 2.5), facecolor='#0E3F5C')
    ax_table.axis("off")

    table = ax_table.table(
        cellText=table_data.values,
        colLabels=table_data.columns,
        cellColours=full_colors,
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.8, 2)

    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('white')
        if i == 0:
            cell.set_text_props(color='white', weight='bold')
            cell.set_facecolor('#0E3F5C')
        else:
            if j == 0:
                equipo = table_data.iloc[i - 1, 0]
                cell.set_text_props(color=text_color(equipo), weight='bold')
                cell.set_facecolor('#0E3F5C')
            else:
                cell.set_text_props(color='white', weight='bold')

    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

# ---------- FUNCIONES POR JORNADA ----------
def generar_reporte_jornada(df, jornada, base_dir):
    df = df.copy()
    for col in metrics:
        df[col + "_pctl"] = df[col].rank(pct=True) * 100

    jornada_df = df[df["jornada"] == jornada]
    equipos = jornada_df["team_name"].unique().tolist()

    jornada_folder = os.path.join(base_dir, f"Jornada_{jornada}")
    os.makedirs(jornada_folder, exist_ok=True)
    radar_folder = os.path.join(jornada_folder, "radars")
    tabla_folder = os.path.join(jornada_folder, "tablas")
    os.makedirs(radar_folder, exist_ok=True)
    os.makedirs(tabla_folder, exist_ok=True)

    for equipo in equipos:
        radar_path = os.path.join(radar_folder, f"{equipo.replace(' ', '_')}_radar.png")
        generar_radar(jornada_df, equipo, radar_path)

    if len(equipos) % 2 != 0:
        print("⚠️ Número impar de equipos. Revisa la jornada.")
        return

    for i in range(0, len(equipos), 2):
        equipo1 = equipos[i]
        equipo2 = equipos[i + 1]
        tabla_path = os.path.join(tabla_folder, f"{equipo1.replace(' ', '_')}_vs_{equipo2.replace(' ', '_')}.png")
        generar_tabla_comparativa(jornada_df, equipo1, equipo2, tabla_path)

    print(f"✅ Reporte generado para jornada {jornada} en {jornada_folder}")


# ---------- BLOQUE PRINCIPAL ----------
if __name__ == "__main__":
    # Carga de datos
    df = pd.read_csv("data/tus_datos.csv")

    # Llamada a la función
    generar_reporte_jornada(df, jornada=13, base_dir="reportes")
