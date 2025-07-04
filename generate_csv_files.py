import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os
import matplotlib.pyplot as plt
import streamlit as st

def normalize_to_range(series, new_min=0.5, new_max=9.5):
    old_min = series.min()
    old_max = series.max()
    if old_max == old_min:
        return pd.Series(np.full_like(series, (new_min + new_max) / 2), index=series.index)
    normalized = (series - old_min) / (old_max - old_min)
    scaled = normalized * (new_max - new_min) + new_min
    return scaled

def generate_all_csvs():
    try:
        """
        Función que procesa los datos de fútbol y genera todos los DataFrames como archivos CSV
        en el directorio 'data/'.
        """

        # Crear directorio 'data' si no existe
        os.makedirs('data', exist_ok=True)
        
        print("📊 Iniciando procesamiento de datos...")
        
        # --- 1. LEER ARCHIVOS EXCEL ---
        print("📖 Leyendo archivos Excel...")
        excel_path = "AUDAX/sb_team_match_stats_2025.xlsx"
        df = pd.read_excel(excel_path)
        
        excel_path_matches = "AUDAX/sb_matches_2025.xlsx"
        df_matches = pd.read_excel(excel_path_matches)
        
        # Selecciona solo las columnas deseadas de df_matches
        df_matches_filtered = df_matches[['match_id', 'match_date', 'competition', 'season', 'match_week',  'competition_stage', 'home_team', 'away_team']]

        # Haz el merge (unión) por match_id, manteniendo todas las columnas de df
        df = pd.merge(df, df_matches_filtered, on='match_id', how='left')

        df.columns = df.columns.str.replace("^team_match_", "", regex=True)

        # --- Calcular Goal Envolvement Index (GEI) ---
        df["Goal Envolvement Index"] = (
            (df["xa"] + df["key_passes"] + df["assists"]) * (10 * 0.3) / 3 +
            (df["through_balls"] + df["passes_into_box"] + df["passes_inside_box"] + df["crosses_into_box"]) * (10 * 0.2) / 4 +
            df["box_cross_ratio"] * (10 * 0.05) +
            (df["sp_xa"] + df["deep_progressions"] + df["touches_inside_box"]) * (10 * 0.15) / 3 +
            (df["xgchain"] + df["xgbuildup"]) * (10 * 0.1) / 2 +
            (df["xgchain_per_possession"] + df["xgbuildup_per_possession"]) * (10 * 0.1) / 2 +
            (df["obv_pass"] + df["obv_dribble_carry"]) * (10 * 0.05) / 2 +
            df["forward_passes"] * (10 * 0.05)
        ) / df["minutes"]

        # --- Calcular Goal Conversion Index (GCI) ---
        df["Goal Conversion Index"] = (
            df["goals"] * (10 * 0.3) +
            df["np_xg"] * (10 * 0.2) +
            df["np_xg_per_shot"] * (10 * 0.2) +
            df["np_shots_on_target"] * (10 * 0.1) +
            df["shot_touch_ratio"] * (10 * 0.1) +
            df["penalties_won"] * (10 * 0.05) +
            df["obv_shot"] * (10 * 0.05)
        ) / df["np_shots"]

        # --- Calcular Possession GoalChance Index (PGC) ---
        df["Possession GoalChance Index"] = (
            (df["key_passes"] + df["assists"] + df["xa"] + df["xgchain"]) * (10 * 0.85) / 4 +
            df["touches_inside_box"] * (10 * 0.15)
        ) / df["possession"]

        # --- KPI Compuesto ponderado sin normalización ---
        df["Goal Performance Index"] = (
            df["Goal Envolvement Index"] +
            df["Goal Conversion Index"] +
            df["Possession GoalChance Index"] 
        ) 

        # Sustituir NaN por 0.01
        df = df.fillna(0.01) 

        # --- Mostrar resultado ---
        df[[
            'match_id', 'team_name', 'team_id', 'account_id', 'match_date', 'competition',
            'season', 'match_week', 'competition_stage', 'home_team', 'away_team', 'np_xg', 'np_shots', 'obv_shot', 'xgchain', 'goals',
            "Goal Envolvement Index", "Goal Conversion Index",
            "Possession GoalChance Index", "Goal Performance Index"
        ]]

        # --- Calcular Goal Envolvement Index (GEI) ---
        # Ponderaciones ajustadas para que sumen 10
        df["Goal Envolvement Index"] = (
            (df["xa"] + df["key_passes"] + df["assists"]) * (10 * 0.3) / 3 +  # 3 métricas, 30%
            (df["through_balls"] + df["passes_into_box"] + df["passes_inside_box"] + df["crosses_into_box"]) * (10 * 0.2) / 4 +  # 4 métricas, 20%
            df["box_cross_ratio"] * (10 * 0.05) +  # 5%
            (df["sp_xa"] + df["deep_progressions"] + df["touches_inside_box"]) * (10 * 0.15) / 3 +  # 15%
            (df["xgchain"] + df["xgbuildup"]) * (10 * 0.1) / 2 +  # 10%
            (df["xgchain_per_possession"] + df["xgbuildup_per_possession"]) * (10 * 0.1) / 2 +  # 10%
            (df["obv_pass"] + df["obv_dribble_carry"]) * (10 * 0.05) / 2 +  # 5%
            df["forward_passes"] * (10 * 0.05)  # 5%
        ) / ((df["minutes"])*0.35)

        # --- Calcular Goal Conversion Index (GCI) ---
        df["Goal Conversion Index"] = (
            df["goals"] * (10 * 0.3) +  # 30%
            df["np_xg"] * (10 * 0.2) +  # 20%
            df["np_xg_per_shot"] * (10 * 0.2) +  # 20%
            df["np_shots_on_target"] * (10 * 0.1) +  # 10%
            df["shot_touch_ratio"] * (10 * 0.1) +  # 10%
            df["penalties_won"] * (10 * 0.05) +  # 5%
            df["obv_shot"] * (10 * 0.05)  # 5%
        ) / ((df["np_shots"])*0.45)

        # --- Calcular Possession GoalChance Index (PGC) ---
        df["Possession GoalChance Index"] = (
            (df["key_passes"] + df["assists"] + df["xa"] + df["xgchain"]) * (10 * 0.85) / 4 +  # 85%
            df["touches_inside_box"] * (10 * 0.15)  # 15%
        ) / ((df["possession"])* 0.2)

        # --- Normalizar KPIs entre 0 y 10 ---
        kpi_columns = ["Goal Envolvement Index", "Goal Conversion Index", "Possession GoalChance Index"]

        # Sustituir NaN por 0.01
        df[kpi_columns] = df[kpi_columns].fillna(0.01) 

        # Escalar valores
        scaler = MinMaxScaler(feature_range=(0.5, 9.5))
        df[[col + " (norm)" for col in kpi_columns]] = scaler.fit_transform(df[kpi_columns])

        # --- KPI Compuesto promedio ---
        df["Goal Performance Index"] = df[[col + " (norm)" for col in kpi_columns]].mean(axis=1)

        # --- Mostrar resultado (opcional) ---
        df[['match_id', 'team_name', 'team_id', 'account_id', 'match_date', 'competition',
            'season', 'match_week', 'competition_stage', 'home_team', 'away_team', 'np_xg', 'np_shots', 'obv_shot', 'xgchain', 'goals',
            "Goal Envolvement Index", "Goal Conversion Index",
            "Possession GoalChance Index", "Goal Performance Index"]]

        # --- Calcular Goal Envolvement Index (GEI) ---
        df["Goal Envolvement Index"] = (
            (df["xa"] + df["key_passes"] + df["assists"]) * (10 * 0.3) / 3 +
            (df["through_balls"] + df["passes_into_box"] + df["passes_inside_box"] + df["crosses_into_box"]) * (10 * 0.2) / 4 +
            df["box_cross_ratio"] * (10 * 0.05) +
            (df["sp_xa"] + df["deep_progressions"] + df["touches_inside_box"]) * (10 * 0.15) / 3 +
            (df["xgchain"] + df["xgbuildup"]) * (10 * 0.1) / 2 +
            (df["xgchain_per_possession"] + df["xgbuildup_per_possession"]) * (10 * 0.1) / 2 +
            (df["obv_pass"] + df["obv_dribble_carry"]) * (10 * 0.05) / 2 +
            df["forward_passes"] * (10 * 0.05)
        ) / df["minutes"]

        # --- Calcular Goal Conversion Index (GCI) ---
        df["Goal Conversion Index"] = (
            df["goals"] * (10 * 0.3) +
            df["np_xg"] * (10 * 0.2) +
            df["np_xg_per_shot"] * (10 * 0.2) +
            df["np_shots_on_target"] * (10 * 0.1) +
            df["shot_touch_ratio"] * (10 * 0.1) +
            df["penalties_won"] * (10 * 0.05) +
            df["obv_shot"] * (10 * 0.05)
        ) / df["np_shots"]

        # --- Calcular Possession GoalChance Index (PGC) ---
        df["Possession GoalChance Index"] = (
            (df["key_passes"] + df["assists"] + df["xa"] + df["xgchain"]) * (10 * 0.85) / 4 +
            df["touches_inside_box"] * (10 * 0.15)
        ) / df["possession"]

        # --- Normalizar KPIs entre 0 y 9.5 ---
        kpi_columns = ["Goal Envolvement Index", "Goal Conversion Index", "Possession GoalChance Index"]

        # Sustituir NaN por 0.01
        df[kpi_columns] = df[kpi_columns].fillna(0.01) 

        # Escalar valores
        scaler = MinMaxScaler(feature_range=(0.5, 9.5))
        df[[col + " (norm)" for col in kpi_columns]] = scaler.fit_transform(df[kpi_columns])

        # --- KPI Compuesto ponderado ---
        df["Goal Performance Index"] = ((
            df["Goal Envolvement Index (norm)"] * 3 +
            df["Goal Conversion Index (norm)"] * 4.5 +
            df["Possession GoalChance Index (norm)"] * 2
        ) / (9.5)+ 3)  

        # Tope de 9.7
        df["Goal Performance Index"] = df["Goal Performance Index"].clip(upper=9.75)

        # --- Mostrar resultado ---
        df[[
            'match_id', 'team_name', 'team_id', 'account_id', 'match_date', 'competition', 'season', 'match_week', 'competition_stage', 
            'home_team', 'away_team',  'np_xg', 'np_shots', 'obv_shot', 'xgchain', 'goals',
            "Goal Envolvement Index (norm)", "Goal Conversion Index (norm)",
            "Possession GoalChance Index (norm)", "Goal Performance Index"
        ]]

        # --- Calcular promedio por equipo (incluyendo team_id) ---
        avg_kpis = df.groupby(["team_name", "team_id"])[[
            "np_xg", "np_shots", "obv_shot", "xgchain", "goals",
            "Goal Envolvement Index (norm)",
            "Goal Conversion Index (norm)",
            "Possession GoalChance Index (norm)",
            "Goal Performance Index"
        ]].mean().reset_index()

        # --- Añadir columnas identificadoras de promedio ---
        avg_kpis["match_id"] = "AVG"
        avg_kpis["match_date"] = 2005
        avg_kpis["account_id"] = 7336
        avg_kpis["competition"] = "Chile - Primera División"
        avg_kpis["season"] = 2005
        avg_kpis["match_week"] = df['match_week'].dropna().max()  # jornada máxima jugada
        avg_kpis["competition_stage"] = "Regular Season"
        avg_kpis["home_team"] = "AVG"
        avg_kpis["away_team"] = "AVG"

        # --- Reordenar columnas para que coincidan con df original ---
        avg_kpis = avg_kpis[[
            "match_id", "team_name", "team_id", "account_id", "match_date", "competition", "season", "match_week",
            "competition_stage", "home_team", "away_team", "np_xg", "np_shots", "obv_shot", "xgchain", "goals",
            "Goal Envolvement Index (norm)", "Goal Conversion Index (norm)",
            "Possession GoalChance Index (norm)", "Goal Performance Index"
        ]]

        # --- Calcular promedio general (ALL_TEAMS_AVG) ---
        all_teams_avg = avg_kpis[[
            "np_xg", "np_shots", "goals",
            "Goal Envolvement Index (norm)", "Goal Conversion Index (norm)",
            "Possession GoalChance Index (norm)", "Goal Performance Index"
        ]].mean()

        # --- Crear fila para ALL_TEAMS_AVG ---
        all_teams_avg_row = {
            "match_id": "AVG",
            "team_name": "ALL_TEAMS_AVG",
            "team_id": 1,
            "account_id": 7336,
            "match_date": 2005,
            "competition": "Chile - Primera División",
            "season": 2005 ,
            "match_week": df['match_week'].dropna().max(),
            "competition_stage": "Regular Season",
            "home_team": "AVG",
            "away_team": "AVG",
            **all_teams_avg.to_dict()
        }

        # --- Añadir fila de promedio general a avg_kpis ---
        avg_kpis = pd.concat([avg_kpis, pd.DataFrame([all_teams_avg_row])], ignore_index=True)

        # --- Concatenar el dataframe original con los promedios ---
        df_final = pd.concat([df[[
            "match_id", "team_name", "team_id", "account_id", "match_date", "competition", "season", "match_week",
            "competition_stage", "home_team", "away_team", "np_xg", "np_shots", "obv_shot", "xgchain", "goals",
            "Goal Envolvement Index (norm)", "Goal Conversion Index (norm)",
            "Possession GoalChance Index (norm)", "Goal Performance Index"
        ]], avg_kpis], ignore_index=True)

        # --- Crear columna 'match_score' tipo "home(goals) - away(goals)" ---
        # Obtener goles por equipo por partido
        goals_pivot = df.pivot_table(index="match_id", columns="team_name", values="goals", aggfunc="first")

        # Obtener combinaciones únicas de partidos
        df_scores = df[["match_id", "home_team", "away_team"]].drop_duplicates()

        # Crear columna con formato deseado
        def get_score(row):
            try:
                home_goals = goals_pivot.loc[row["match_id"], row["home_team"]]
                away_goals = goals_pivot.loc[row["match_id"], row["away_team"]]
                return f'{row["home_team"]}({int(home_goals)}) - {row["away_team"]}({int(away_goals)})'
            except:
                return None  # En caso de partidos incompletos o filas "AVG"

        df_scores["match_score"] = df_scores.apply(get_score, axis=1)

        # Unir con df_final
        df_final = df_final.merge(df_scores[["match_id", "match_score"]], on="match_id", how="left")
        # 8. Rellenar NaN
        df_final = df_final.fillna({
            "match_score": "AVG"
        })

        df_final.to_csv("data/df_final.csv", index=False)

        # --- Filtrar solo filas de promedio por equipo (excluyendo ALL_TEAMS_AVG) ---
        avg_only = df_final[
            (df_final["match_id"] == "AVG") & (df_final["team_name"] != "ALL_TEAMS_AVG")
        ].copy()

        # --- Crear columna de ranking según Goal Conversion Index (norm) (descendente) ---
        avg_only["Rank (avg)"] = avg_only["Goal Conversion Index (norm)"].rank(
            ascending=False, method="min"
        ).astype(int)

        # --- Ordenar por ranking ---
        ranking_avg = avg_only.sort_values(by="Rank (avg)").reset_index(drop=True)

        # --- Obtener valor máximo de jornadas jugadas ---
        max_jornada = df_final[df_final["match_id"] != "AVG"]["match_week"].max()

        # --- Crear columna 'match_week' con ese valor constante ---
        ranking_avg["match_week"] = max_jornada

        # --- Renombrar columnas (quitar '(norm)') ---
        ranking_avg = ranking_avg.rename(columns={
            "Goal Performance Index": "Goal Performance Index",
            "Goal Envolvement Index (norm)": "Goal Envolvement Index",
            "Goal Conversion Index (norm)": "Goal Conversion Index",
            "Possession GoalChance Index (norm)": "Possession GoalChance Index"
        })

        # --- Seleccionar columnas finales ---
        ranking_avg_display_GCI = ranking_avg[[
            "Rank (avg)", "team_name", "team_id", "match_week",
            "Goal Performance Index", 
            "Goal Envolvement Index", 
            "Goal Conversion Index", 
            "Possession GoalChance Index"
        ]]

        ranking_avg_display_GCI.to_csv("data/df_ranking_avg_display_GCI.csv", index=False)

        # --- Filtrar solo filas de promedio por equipo (excluyendo ALL_TEAMS_AVG) ---
        avg_only = df_final[
            (df_final["match_id"] == "AVG") & (df_final["team_name"] != "ALL_TEAMS_AVG")
        ].copy()

        # --- Crear columna de ranking según Goal Performance Index (descendente) ---
        avg_only["Rank (avg)"] = avg_only["Goal Envolvement Index (norm)"].rank(ascending=False, method="min").astype(int)

        # --- Ordenar por ranking ---
        ranking_avg = avg_only.sort_values(by="Rank (avg)").reset_index(drop=True)

        # --- Obtener valor máximo de jornadas jugadas ---
        max_jornada = df_final[df_final["match_id"] != "AVG"]["match_week"].max()

        # --- Crear columna 'match_week' con ese valor constante ---
        ranking_avg["match_week"] = max_jornada

        # --- Renombrar columnas (quitar '(norm)') ---
        ranking_avg = ranking_avg.rename(columns={
            "Goal Performance Index": "Goal Performance Index",
            "Goal Envolvement Index (norm)": "Goal Envolvement Index",
            "Goal Conversion Index (norm)": "Goal Conversion Index",
            "Possession GoalChance Index (norm)": "Possession GoalChance Index"
        })

        # --- Seleccionar columnas finales ---
        ranking_avg_display_GEI = ranking_avg[[
            "Rank (avg)", "team_name", "team_id", "match_week",
            "Goal Performance Index", 
            "Goal Envolvement Index", 
            "Goal Conversion Index",  
            "Possession GoalChance Index"
        ]]

        ranking_avg_display_GEI.to_csv("data/df_ranking_avg_display_GEI.csv", index=False)

        # --- Filtrar solo filas de promedio por equipo (excluyendo ALL_TEAMS_AVG) ---
        avg_only = df_final[
            (df_final["match_id"] == "AVG") & (df_final["team_name"] != "ALL_TEAMS_AVG")
        ].copy()

        # --- Crear columna de ranking según Goal Performance Index (descendente) ---
        avg_only["Rank (avg)"] = avg_only[ "Possession GoalChance Index (norm)"].rank(ascending=False, method="min").astype(int)

        # --- Ordenar por ranking ---
        ranking_avg = avg_only.sort_values(by="Rank (avg)").reset_index(drop=True)

        # --- Obtener valor máximo de jornadas jugadas ---
        max_jornada = df_final[df_final["match_id"] != "AVG"]["match_week"].max()

        # --- Crear columna 'match_week' con ese valor constante ---
        ranking_avg["match_week"] = max_jornada

        # --- Renombrar columnas (quitar '(norm)') ---
        ranking_avg = ranking_avg.rename(columns={
            "Goal Performance Index": "Goal Performance Index",
            "Goal Envolvement Index (norm)": "Goal Envolvement Index",
            "Goal Conversion Index (norm)": "Goal Conversion Index",
            "Possession GoalChance Index (norm)": "Possession GoalChance Index"
        })

        # --- Seleccionar columnas finales ---
        ranking_avg_display_PGI = ranking_avg[[
            "Rank (avg)", "team_name", "team_id", "match_week",
            "Goal Performance Index", 
            "Goal Envolvement Index", 
            "Goal Conversion Index",  
            "Possession GoalChance Index"
        ]]
        
        ranking_avg_display_PGI.to_csv("data/df_ranking_avg_display_PGI.csv", index=False)

        # --- Filtrar solo filas de promedio por equipo (excluyendo ALL_TEAMS_AVG) ---
        avg_only = df_final[
            (df_final["match_id"] == "AVG") & (df_final["team_name"] != "ALL_TEAMS_AVG")
        ].copy()

        # --- Crear columna de ranking según Goal Performance Index (descendente) ---
        avg_only["Rank (avg)"] = avg_only["Goal Performance Index"].rank(ascending=False, method="min").astype(int)

        # --- Ordenar por ranking ---
        ranking_avg = avg_only.sort_values(by="Rank (avg)").reset_index(drop=True)

        # --- Obtener valor máximo de jornadas jugadas ---
        max_jornada = df_final[df_final["match_id"] != "AVG"]["match_week"].max()

        # --- Crear columna 'match_week' con ese valor constante ---
        ranking_avg["match_week"] = max_jornada

        # --- Renombrar columnas (quitar '(norm)') ---
        ranking_avg = ranking_avg.rename(columns={
            "Goal Performance Index": "Goal Performance Index",
            "Goal Envolvement Index (norm)": "Goal Envolvement Index",
            "Goal Conversion Index (norm)": "Goal Conversion Index",
            "Possession GoalChance Index (norm)": "Possession GoalChance Index"
        })

        # --- Seleccionar columnas finales ---
        ranking_avg_display_GPI = ranking_avg[[
            "Rank (avg)", "team_name", "team_id", "match_week",
            "Goal Performance Index", 
            "Goal Envolvement Index", 
            "Goal Conversion Index",  
            "Possession GoalChance Index"
        ]]

        ranking_avg_display_GPI.to_csv("data/df_ranking_avg_display_GPI.csv", index=False)
        
        excel_path = "AUDAX/sb_team_season_stats_2025.xlsx"
        df = pd.read_excel(excel_path)

        def normalize_series_min_max(s, new_min=0.5, new_max=9.5):
            old_min = s.min()
            old_max = s.max()
            if old_max == old_min:
                return pd.Series(np.full_like(s, (new_min + new_max) / 2), index=s.index)
            normalized = (s - old_min) / (old_max - old_min)
            scaled = normalized * (new_max - new_min) + new_min
            return scaled

        # Cálculo de eficiencias a balón parado
        df['corner_shot_efficiency'] = df['team_season_shots_from_corners_pg'] / df['team_season_corners_pg']
        df['corner_goal_efficiency'] = df['team_season_goals_from_corners_pg'] / df['team_season_corners_pg']
        df['corner_xg_efficiency'] = df['team_season_corner_xg_pg'] / df['team_season_corners_pg']

        df['free_kick_shot_efficiency'] = df['team_season_shots_from_free_kicks_pg'] / df['team_season_free_kicks_pg']
        df['free_kick_goal_efficiency'] = df['team_season_goals_from_free_kicks_pg'] / df['team_season_free_kicks_pg']
        df['free_kick_xg_efficiency'] = df['team_season_free_kick_xg_pg'] / df['team_season_free_kicks_pg']

        df['dfk_goal_efficiency'] = df['team_season_direct_free_kick_goals_pg'] / df['team_season_direct_free_kicks_pg']
        df['dfk_xg_efficiency'] = df['team_season_direct_free_kick_xg_pg'] / df['team_season_direct_free_kicks_pg']
        df['direct_free_kick_shot_efficiency'] = df['team_season_shots_from_direct_free_kicks_pg'] / df['team_season_direct_free_kicks_pg']

        df['throw_in_shot_efficiency'] = df['team_season_shots_from_throw_ins_pg'] / df['team_season_throw_ins_pg']
        df['throw_in_goal_efficiency'] = df['team_season_goals_from_throw_ins_pg'] / df['team_season_throw_ins_pg']
        df['throw_in_xg_efficiency'] = df['team_season_throw_in_xg_pg'] / df['team_season_throw_ins_pg']

        # Subíndices ponderados
        df['corner_subindex'] = (
            df['corner_goal_efficiency'] * 0.15 +
            df['corner_xg_efficiency'] * 0.10 +
            df['corner_shot_efficiency'] * 0.10
        )

        df['free_kick_subindex'] = (
            df['free_kick_goal_efficiency'] * 0.15 +
            df['free_kick_xg_efficiency'] * 0.10 +
            df['free_kick_shot_efficiency'] * 0.10
        )

        df['directfk_subindex'] = (
            df['dfk_goal_efficiency'] * 0.10 +
            df['dfk_xg_efficiency'] * 0.05 +
            df['direct_free_kick_shot_efficiency'] * 0.05
        )

        df['throw_in_subindex'] = (
            df['throw_in_goal_efficiency'] * 0.10 +
            df['throw_in_xg_efficiency'] * 0.05 +
            df['throw_in_shot_efficiency'] * 0.05
        )

        # Normalizar subíndices
        df['corner_subindex_norm'] = normalize_series_min_max(df['corner_subindex'], 0.5, 9.5)
        df['free_kick_subindex_norm'] = normalize_series_min_max(df['free_kick_subindex'], 0.5, 9.5)
        df['directfk_subindex_norm'] = normalize_series_min_max(df['directfk_subindex'], 0.5, 9.5)
        df['throw_in_subindex_norm'] = normalize_series_min_max(df['throw_in_subindex'], 0.5, 9.5)

        # DataFrame final con columnas normalizadas
        df_setpiece = df[['team_name', 'team_id',
                        'corner_subindex_norm',
                        'free_kick_subindex_norm',
                        'directfk_subindex_norm',
                        'throw_in_subindex_norm']].copy()

        # Eliminar filas con NaNs
        df_setpiece.dropna(inplace=True)


        # KPI global de balón parado con pesos
        df_setpiece['SetPiece Eficcacy Index'] = (
            df_setpiece['corner_subindex_norm'] * 0.50 +
            df_setpiece['free_kick_subindex_norm'] * 0.25 +
            df_setpiece['directfk_subindex_norm'] * 0.15 +
            df_setpiece['throw_in_subindex_norm'] * 0.10
        )

        # Eliminar (norm() de emcabezado)
        df_setpiece.rename(columns=lambda x: x.replace('_norm', ''), inplace=True)

        df_setpiece.to_csv("data/df_setpiece.csv", index=False)

        # Verificar columnas
        required_columns = [
            "team_season_sp_goal_ratio",
            "team_season_xg_per_sp",
            "team_season_sp_shot_ratio",
            "team_season_sp_goals_pg",
            "team_season_sp_pg",
            
        ]

        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Faltan columnas necesarias: {missing}")

        # Calcular volumen eficacia
        volume_efficacy = df["team_season_sp_goals_pg"] / df["team_season_sp_pg"]

        # Normalizar función
        def normalize(s):
            return (s - s.min()) / (s.max() - s.min())

        # Normalizar variables
        goal_conversion_norm = normalize(df["team_season_sp_goal_ratio"])
        xg_efficiency_norm = normalize(df["team_season_xg_per_sp"])
        shot_conversion_norm = normalize(df["team_season_sp_shot_ratio"])
        volume_efficacy_norm = normalize(volume_efficacy)

        # Calcular KPI combinado
        df["GoalSetPiece Performance Index"] = (
            0.35 * goal_conversion_norm +
            0.25 * xg_efficiency_norm +
            0.20 * shot_conversion_norm +
            0.20 * volume_efficacy_norm
        )* 9.5 + 0.5

        # DataFrame reducido para análisis
        df_setpiece_efficiency = df[["team_name", "team_id", "GoalSetPiece Performance Index"]].copy()

        df_setpiece_efficiency  = df_setpiece.merge(
            df_setpiece_efficiency.drop(columns=["team_name"]),
            on='team_id',
            how='inner'
        )

        df_setpiece_efficiency.sort_values("GoalSetPiece Performance Index", ascending=False)

        df_setpiece_efficiency.to_csv("data/df_setpiece_efficiency.csv", index=False)

        df_GoalKPIs = ranking_avg_display_GPI.merge(
            df_setpiece_efficiency.drop(columns=["team_name"]),
            on='team_id',
            how='inner'
        )

        # --- Normalizar subíndices entre 0.5 y 9.5 ---
        def normalize_to_range(series, new_min=0.5, new_max=9.5):
            old_min = series.min()
            old_max = series.max()
            if old_max == old_min:
                return pd.Series([new_min] * len(series), index=series.index)
            return ((series - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

        cols_to_norm = [
            "Goal Envolvement Index",
            "Goal Conversion Index",
            "Possession GoalChance Index",
            
        ]
        df_GoalKPIs.rename(columns={
            "corner_subindex": "corner Efficiency",
            "free_kick_subindex": "freekick Efficiency",
            "directfk_subindex": "directfk Efficiency",
            "throw_in_subindex": "throw in Efficiency"
        }, inplace=True)

        for col in cols_to_norm:
            df_GoalKPIs[col] = normalize_to_range(df_GoalKPIs[col], 0.500, 9.500)

        df_GoalKPIs.to_csv("data/df_GoalKPIs.csv", index=False)
        
        df = df_GoalKPIs.copy()

        kpis = [
            "Goal Performance Index", "Goal Envolvement Index",
            "Goal Conversion Index", "Possession GoalChance Index",
            "corner Efficiency", "freekick Efficiency",
            "directfk Efficiency", "throw in Efficiency",
            "SetPiece Eficcacy Index", "GoalSetPiece Performance Index"
        ]

        # Crear DataFrame con índice y ahora columna 'team_name'
        df_KPIs_TopValues = pd.DataFrame(
            {
                "team_name": ["TopValues (min)", "TopValues (max)"],
            },
            index=["TopValues (min)", "TopValues (max)"]
        )

        # Rellenar los valores min y max por KPI
        for idx_label in ["TopValues (min)", "TopValues (max)"]:
            row = {}
            for kpi in kpis:
                top7 = df.nlargest(7, columns=kpi)[kpi]
                val = top7.min() if idx_label.endswith("(min)") else top7.max()
                row[kpi] = round(val, 3)
            df_KPIs_TopValues.loc[idx_label, kpis] = pd.Series(row)

        # Asegúrate de que 'team_name' es la primera columna
        df_KPIs_TopValues = df_KPIs_TopValues.reset_index(drop=True)


        # 1. Eliminar la columna team_id de ambos (si está presente)
        if "team_id" in df_GoalKPIs.columns:
            df_GoalKPIs = df_GoalKPIs.drop(columns=["team_id"])
        if "team_id" in df_KPIs_TopValues.columns:
            df_KPIs_TopValues = df_KPIs_TopValues.drop(columns=["team_id"])

        # 2. Asegurar que 'Rank (avg)' y 'match_week' están en df_KPIs_TopValues
        match_week_val = df_GoalKPIs["match_week"].iloc[0]
        df_KPIs_TopValues["match_week"] = match_week_val
        df_KPIs_TopValues["Rank (avg)"] = 0  # o cualquier valor placeholder


        # 3. Reordenar columnas para que coincidan con df_GoalKPIs
        cols = df_GoalKPIs.columns.tolist()
        # Es importante que coincidan exactamente, de lo contrario concat() rellenará con NaN :contentReference[oaicite:1]{index=1}
        df_KPIs_TopValues = df_KPIs_TopValues[cols]

        # 4. Concatenar verticalmente
        df_GoalKPIs_TopValues= pd.concat([df_KPIs_TopValues, df_GoalKPIs], ignore_index=True).round(2)


        df_GoalKPIs_TopValues.to_csv("data/df_GoalKPIs_TopValues.csv", index=False)

        return True, "Archivos CSV generados correctamente en la carpeta AUDAX."
        
    except Exception as e:
        return False, f"Error al generar archivos CSV: {str(e)}"

# Función para ejecutar desde la aplicación principal
def run_generation():
    with st.spinner('Generando archivos CSV...'):
        success, message = generate_all_csvs()
        if success:
            st.success(message)
        else:
            st.error(message)

# Si se ejecuta directamente este script
if __name__ == "__main__":
    success, message = generate_csv_files()
    print(message)
