from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image

# CONFIGURACIÓN INICIAL
st.set_page_config(layout="wide")
logo = Image.open("logo.jpg")
st.image(logo, width=200)
st.title("📊 REPORTE MENSUAL - HIDROELÉCTRICA EL CANELO")

# CARGA DE DATOS
excel_path = "HEC mensuales 2025.xlsx"
sheet_name = "Pluviometria"
df_raw = pd.read_excel(excel_path, sheet_name=sheet_name, header=127, usecols="C:D")

# PROCESAMIENTO
df_raw = df_raw.rename(columns={df_raw.columns[0]: "Fecha", df_raw.columns[1]: "Precipitaciones"})
df_raw.dropna(inplace=True)
df_raw["Fecha"] = pd.to_datetime(df_raw["Fecha"], errors="coerce")
df_raw.dropna(subset=["Fecha"], inplace=True)
df_raw["Año"] = df_raw["Fecha"].dt.year
df_raw["Mes"] = df_raw["Fecha"].dt.strftime("%B")

# FILTROS
df_2025 = df_raw[df_raw["Año"] == 2025]
df_2024 = df_raw[df_raw["Año"] == 2024]
df_5y = df_raw[df_raw["Año"].between(2020, 2024)]

# PROMEDIOS
df_avg = df_5y.groupby(df_5y["Fecha"].dt.strftime("%B"))["Precipitaciones"].mean().reset_index()
df_avg.columns = ["Mes", "Promedio_5_Años"]

# AGRUPAR POR MES
prec_2025 = df_2025.groupby(df_2025["Fecha"].dt.strftime("%B"))["Precipitaciones"].sum()
prec_2024 = df_2024.groupby(df_2024["Fecha"].dt.strftime("%B"))["Precipitaciones"].sum()

# ORDENAR MESES
meses_orden = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
               "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
prec_2025 = prec_2025.reindex(meses_orden)
prec_2024 = prec_2024.reindex(meses_orden)
df_avg = df_avg.set_index("Mes").reindex([m.capitalize() for m in meses_orden])

# GRAFICO
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(meses_orden, prec_2025, label="2025", linestyle="-", marker="o")
ax.plot(meses_orden, prec_2024, label="2024", linestyle="--", marker="o")
ax.plot(meses_orden, df_avg["Promedio_5_Años"], label="Promedio 2020-2024", linestyle="-.", marker="o")

ax.set_title("Precipitaciones mensuales (mm)", fontsize=16)
ax.set_xlabel("Mes")
ax.set_ylabel("Precipitaciones (mm)")
ax.legend()
ax.grid(True)
plt.xticks(rotation=45)

# MOSTRAR EN STREAMLIT
st.pyplot(fig)
st.caption("Datos provenientes de hoja 'Pluviometria', archivo HEC mensuales 2025.xlsx")
