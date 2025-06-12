import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

# Configuración general
st.set_page_config(
    page_title="Reporte Mensual - Hidroeléctrica El Canelo",
    layout="wide",
    page_icon="📊"
)

# Insertar logo
st.markdown(
    """
    <style>
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .logo-container img {
            max-height: 90px;
        }
        .header-title {
            font-size: 32px;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 8])
with col1:
    st.image("logo.jpg", use_column_width="auto")
with col2:
    st.markdown("<div class='header-title'>REPORTE MENSUAL - HIDROELÉCTRICA EL CANELO</div>", unsafe_allow_html=True)

# Cargar archivo Excel
excel_path = "HEC 0125-Marcelo_A.xlsx"
sheet_name = "Datos_Resumen"

try:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
except Exception as e:
    st.error(f"No se pudo cargar la hoja '{sheet_name}'. Verifica que exista en el archivo Excel.")
    st.stop()

# Conversión de fechas
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df = df.dropna(subset=["Fecha"])
df = df.sort_values("Fecha")

# Gráfico de precipitaciones
st.markdown("## 🌧️ Precipitaciones Mensuales")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["Fecha"], df["Precipitaciones (mm)"], marker="o", linestyle="-", color="#1f77b4")
ax.set_title("Precipitaciones acumuladas por mes", fontsize=14)
ax.set_xlabel("Fecha", fontsize=12)
ax.set_ylabel("Precipitación (mm)", fontsize=12)
ax.grid(True, linestyle="--", alpha=0.5)
fig.patch.set_facecolor('white')
st.pyplot(fig)

# KPI de precipitaciones comparadas
col1, col2, col3 = st.columns(3)
def kpi_box(title, value, diff):
    color = "green" if diff >= 0 else "red"
    return f"""
    <div style='text-align: center; padding: 15px; border-radius: 10px; background-color: #f9f9f9; box-shadow: 1px 1px 5px rgba(0,0,0,0.1);'>
        <div style='font-size: 14px; color: gray;'>{title}</div>
        <div style='font-size: 32px; font-weight: bold;'>{value} mm</div>
        <div style='font-size: 16px; color: {color};'>{'▲' if diff > 0 else '▼'} {abs(diff)} mm</div>
    </div>
    """

last = df.iloc[-1]["Precipitaciones (mm)"]
prev = df.iloc[-2]["Precipitaciones (mm)"]
prom5 = df["Precipitaciones (mm)"].tail(5).mean()

with col1:
    st.markdown(kpi_box("Mes actual", f"{last:.1f}", last - prev), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_box("Mes anterior", f"{prev:.1f}", prev - prom5), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_box("Prom. últimos 5 meses", f"{prom5:.1f}", last - prom5), unsafe_allow_html=True)

# Pie de página
st.markdown("---")
st.caption("Reporte generado automáticamente - Hidroeléctrica El Canelo S.A.")




