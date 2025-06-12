import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
from datetime import datetime
import matplotlib.ticker as ticker

# Configuración visual
st.set_page_config(page_title="Reporte Mensual", layout="wide")
st.markdown("""
    <style>
        .kpi-title {
            font-size: 16px;
            color: #666;
        }
        .kpi-value-pos {
            font-size: 28px;
            color: green;
        }
        .kpi-value-neg {
            font-size: 28px;
            color: red;
        }
    </style>
""", unsafe_allow_html=True)

# Logo
logo = Image.open("logo.jpg")
st.image(logo, width=150)

# Título
st.title("📊 REPORTE MENSUAL - HIDROELÉCTRICA EL CANELO")

# Selección del mes
meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
mes_nombre = st.selectbox("Selecciona el mes:", list(meses.values()))
mes_num = list(meses.keys())[list(meses.values()).index(mes_nombre)]

# Cargar Excel
archivo = "HEC mensuales 2025.xlsx"
df = pd.read_excel(archivo, sheet_name="Pluviometria", skiprows=128, usecols="C:D")
df.columns = ["Fecha", "Precipitaciones"]
df = df.dropna()
df["Fecha"] = pd.to_datetime(df["Fecha"], format="%b-%y", errors="coerce")
df = df.dropna()
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month

# Datos año actual, anterior y promedio últimos 5 años (2020-2024)
actual = df[(df["Año"] == 2025) & (df["Mes"] == mes_num)]["Precipitaciones"].sum()
anterior = df[(df["Año"] == 2024) & (df["Mes"] == mes_num)]["Precipitaciones"].sum()
prom5 = df[(df["Año"] >= 2020) & (df["Año"] <= 2024) & (df["Mes"] == mes_num)]["Precipitaciones"].mean()
diferencia = actual - prom5

# Mostrar KPIs
col1, col2, col3 = st.columns(3)
col1.markdown(f"<div class='kpi-title'>Precipitación {mes_nombre} 2025</div><div class='kpi-value-pos'>{actual:.1f} mm</div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi-title'>Precipitación {mes_nombre} 2024</div><div class='kpi-value-pos'>{anterior:.1f} mm</div>", unsafe_allow_html=True)
color = "kpi-value-pos" if diferencia >= 0 else "kpi-value-neg"
col3.markdown(f"<div class='kpi-title'>Diferencia vs promedio (2020-2024)</div><div class='{color}'>{diferencia:+.1f} mm</div>", unsafe_allow_html=True)

# Generar gráfico línea suavizado
st.subheader("📈 Evolución mensual comparada")
df_2025 = df[df["Año"] == 2025].groupby("Mes")["Precipitaciones"].sum()
df_2024 = df[df["Año"] == 2024].groupby("Mes")["Precipitaciones"].sum()
df_5prom = df[(df["Año"] >= 2020) & (df["Año"] <= 2024)].groupby("Mes")["Precipitaciones"].mean()

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(meses.values(), df_2025, marker='o', label="2025", linewidth=2)
ax.plot(meses.values(), df_2024, marker='o', linestyle='--', label="2024", linewidth=2)
ax.plot(meses.values(), df_5prom, marker='o', linestyle=':', label="Promedio 2020-2024", linewidth=2)
ax.set_ylabel("Precipitaciones (mm)")
ax.set_title("Precipitaciones mensuales")
ax.legend()
ax.grid(True)
st.pyplot(fig)




