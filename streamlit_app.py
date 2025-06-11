import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import numpy as np
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Reporte Mensual Hidroeléctrica El Canelo", layout="wide")

# Logo y título
col1, col2 = st.columns([1, 8])
with col1:
    st.image("logo.jpg", width=120)
with col2:
    st.markdown("### REPORTE MENSUAL - HIDROELÉCTRICA EL CANELO")

# Selección de mes
meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}
mes_seleccionado = st.selectbox("Selecciona el mes para el análisis", list(meses.keys()))
mes_num = meses[mes_seleccionado]

# Leer archivo Excel
excel_path = "HEC mensuales 2025.xlsx"
df = pd.read_excel(excel_path, sheet_name="Pluviometria", skiprows=127, usecols="C:D")

# Renombrar columnas
df.columns = ["Fecha", "Precipitaciones"]

# Procesar fechas
df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
df = df.dropna(subset=["Fecha", "Precipitaciones"])
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month

# Filtrar datos
df_2025 = df[df["Año"] == 2025].groupby("Mes")["Precipitaciones"].sum()
df_2024 = df[df["Año"] == 2024].groupby("Mes")["Precipitaciones"].sum()
df_5y = df[df["Año"].between(2020, 2024)].groupby("Mes")["Precipitaciones"].mean()

# Asegurar índices de 1 a 12 para todos
index_meses = range(1, 13)
df_2025 = df_2025.reindex(index_meses, fill_value=0)
df_2024 = df_2024.reindex(index_meses, fill_value=0)
df_5y = df_5y.reindex(index_meses, fill_value=0)

# Función de suavizado
def suavizar_linea(x, y):
    x_suave = np.linspace(x.min(), x.max(), 300)
    spl = make_interp_spline(x, y, k=3)
    y_suave = spl(x_suave)
    return x_suave, y_suave

# Plot
fig, ax = plt.subplots(figsize=(10, 5))
x = np.array(list(index_meses))

for serie, datos, color, label in zip(
    ["2025", "2024", "Prom. 2020–2024"],
    [df_2025, df_2024, df_5y],
    ['blue', 'orange', 'green'],
    ['Año 2025', 'Año 2024', 'Prom. 5 años']
):
    x_suave, y_suave = suavizar_linea(x, datos.values)
    ax.plot(x_suave, y_suave, label=label, linewidth=2.5, color=color)

ax.set_xticks(x)
ax.set_xticklabels(
    ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
)
ax.set_ylabel("Precipitaciones (mm)")
ax.set_title("Comparativo mensual de precipitaciones")
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()
st.pyplot(fig)

# Indicador mensual
prec_2025_mes = df_2025[mes_num]
prec_2024_mes = df_2024[mes_num]
prom_5y_mes = df_5y[mes_num]
variacion = prec_2025_mes - prom_5y_mes
color_kpi = "green" if variacion >= 0 else "red"

st.markdown(f"""
### Precipitaciones acumuladas en **{mes_seleccionado.upper()}**:
- **2025**: `{prec_2025_mes:.1f} mm`
- **2024**: `{prec_2024_mes:.1f} mm`
- **Prom. 2020–2024**: `{prom_5y_mes:.1f} mm`
""")

st.markdown(f"""
<div style='font-size:18px; color:{color_kpi}; font-weight:bold;'>
    Diferencia 2025 vs. Promedio: <br><span style='font-size:30px'>{variacion:+.1f} mm</span>
</div>
""", unsafe_allow_html=True)
