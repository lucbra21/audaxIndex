import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def app():
    st.title("Goal Performance Ranking")
    
    try:
        # Cargar datos
        ranking_df = pd.read_csv('AUDAX/df_GoalKPIs_TopValues.csv')
        
        # Lista de KPIs disponibles
        kpi_options = [
            "Goal Performance Index",
            "Goal Envolvement Index",
            "Goal Conversion Index",
            "Possession GoalChance Index",
            "corner Efficiency",
            "freekick Efficiency",
            "directfk Efficiency",
            "throw in Efficiency",
            "SetPiece Eficcacy Index",
            "GoalSetPiece Performance Index"
        ]
        
        # Filtrar equipos (excluir TopValues)
        ranking_df = ranking_df[~ranking_df["team_name"].str.contains("TopValues")]
        
        # Selector de KPI
        selected_kpi = st.selectbox("Selecciona KPI para ranking:", kpi_options)
        
        if st.button("Generar ranking"):
            # Crear copia para no modificar el original
            df_plot = ranking_df.copy()
            
            # Calcular Rank dinámicamente según KPI seleccionado
            df_plot["Rank"] = df_plot[selected_kpi].rank(ascending=False, method='min').astype(int)
            
            # Ordenar según nuevo ranking
            df_plot = df_plot.sort_values("Rank").copy()
            
            # Redondear valores numéricos a 3 decimales
            numeric_cols = df_plot.select_dtypes(include='number').columns
            df_plot[numeric_cols] = df_plot[numeric_cols].round(3)
            
            # Seleccionar columnas a mostrar
            display_df = df_plot[[
                "Rank", "team_name", 
                "Goal Performance Index",
                "Goal Envolvement Index",
                "Goal Conversion Index",
                "Possession GoalChance Index",
                "SetPiece Eficcacy Index",
                "GoalSetPiece Performance Index"
            ]]
            
            # Crear figura para Streamlit
            fig, ax = plt.subplots(figsize=(18, 12))
            ax.set_facecolor("#0E3F5C")
            fig.patch.set_facecolor("#0E3F5C")
            
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
            table.set_fontsize(14)
            
            for (row, col), cell in table.get_celld().items():
                if row == 0:
                    # Encabezado
                    cell.set_fontsize(16)
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
                        if isinstance(value, (int, float)):
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
                if col_name in ["Rank"]:
                    cell.set_width(0.18)
                else:
                    cell.set_width(0.45)
            
            ax.axis("off")
            
            # Título
            plt.title(f"Ranking por {selected_kpi}", color="white", fontsize=20, pad=20)
            
            # Guardar y mostrar la figura
            ranking_path = f"AUDAX/Ranking_{selected_kpi.replace(' ', '_')}.png"
            plt.savefig(ranking_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
            
            st.image(ranking_path)
            
            # Mostrar también como tabla interactiva
            st.subheader("Tabla de Ranking")
            st.dataframe(
                display_df,
                column_config={
                    "Rank": st.column_config.NumberColumn(format="%d"),
                    selected_kpi: st.column_config.NumberColumn(format="%.3f", background="greens")
                },
                hide_index=True,
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        st.info("Asegúrate de que el archivo 'AUDAX/df_GoalKPIs_TopValues.csv' exista y tenga el formato correcto.")
