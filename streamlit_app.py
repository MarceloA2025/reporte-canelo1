import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.interpolate import make_interp_spline
import numpy as np

# Configuración de página
st.set_page_config(page_title="Reporte Mensual", layout="wide")

# --- Encabezado con logo y título ---
col_logo, col_titulo = st.columns([1, 9])
with col_logo:
    st.image("logo.jpg", width=180)
with col_titulo:
    st.markdown("<h1 style='font-size: 48px; margin-bottom: 0;'>REPORTE MENSUAL - 📅</h1>", unsafe_allow_html=True)

# --- Sidebar: Selector de mes ---
meses = {
    "Enero": 0, "Febrero": 1, "Marzo": 2, "Abril": 3,
    "Mayo": 4, "Junio": 5, "Julio": 6, "Agosto": 7,
    "Septiembre": 8, "Octubre": 9, "Noviembre": 10, "Diciembre": 11
}
st.sidebar.header("📅 Seleccionar mes")
mes_seleccionado = st.sidebar.selectbox("Mes", list(meses.keys()))
idx_mes = meses[mes_seleccionado]

# --- Cargar datos desde Excel ---
archivo_excel = "HEC mensuales 2025.xlsx"
df_raw = pd.read_excel(archivo_excel, sheet_name="Pluviometria", skiprows=127, usecols="C:D")
df = df_raw.rename(columns={df_raw.columns[0]: "Fecha", df_raw.columns[1]: "Precipitacion"})
df["Fecha"] = pd.to_datetime(df["Fecha"])
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month

# --- Preparación de datos ---
df_2025 = df[df["Año"] == 2025].reset_index(drop=True)
df_2024 = df[df["Año"] == 2024].reset_index(drop=True)
df_ult_5 = df[df["Año"].between(2020, 2024)].groupby("Mes")["Precipitacion"].mean()

# --- Obtener valores del mes seleccionado ---
prec_2025_mes = df_2025.iloc[idx_mes]["Precipitacion"] if idx_mes < len(df_2025) else 0
prec_2024_mes = df_2024.iloc[idx_mes]["Precipitacion"] if idx_mes < len(df_2024) else 0
prom_ult_5_mes = df_ult_5.iloc[idx_mes] if idx_mes < len(df_ult_5) else 0

# --- KPIs principales ---
delta_2025_vs_24 = prec_2025_mes - prec_2024_mes
delta_2025_vs_prom = prec_2025_mes - prom_ult_5_mes

st.markdown(f"## 📊 Indicadores de {mes_seleccionado}")
col1, col2, col3 = st.columns(3)
col1.metric("Precipitaciones 2025", f"{prec_2025_mes:.1f} mm", f"{delta_2025_vs_24:+.1f} mm vs 2024")
col2.metric("Precipitaciones 2024", f"{prec_2024_mes:.1f} mm")
col3.metric("Prom. 2020–2024", f"{prom_ult_5_mes:.1f} mm", f"{delta_2025_vs_prom:+.1f} mm vs promedio")

# --- Gráfico de barras ---
st.markdown(f"### 📊 Comparación del mes de {mes_seleccionado}")
fig_bar, ax_bar = plt.subplots(figsize=(6, 3))
labels = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025_mes, prec_2024_mes, prom_ult_5_mes]
colores = ['green' if prec_2025_mes >= x else 'red' for x in [prec_2024_mes, prom_ult_5_mes, prom_ult_5_mes]]
ax_bar.bar(labels, valores, color=colores)
ax_bar.set_ylabel("mm")
ax_bar.set_title(f"Precipitaciones - {mes_seleccionado}", fontsize=14)
ax_bar.grid(axis='y', linestyle='--', alpha=0.5)
for i, v in enumerate(valores):
    ax_bar.text(i, v + 1, f"{v:.1f}", ha='center', fontsize=10)
st.pyplot(fig_bar)

# --- Gráfico de línea suavizada ---
st.markdown("### 📈 Evolución mensual de precipitaciones (línea suavizada)")

# Suavizado con interpolación
mes_numerico = np.arange(1, len(df_2025["Precipitacion"]) + 1)
mes_labels = df_2025["Fecha"].dt.strftime('%b')

def suavizar(x, y):
    if len(x) >= 4:
        xnew = np.linspace(x.min(), x.max(), 300)
        spl = make_interp_spline(x, y, k=3)
        ynew = spl(xnew)
        return xnew, ynew
    else:
        return x, y

x_2025, y_2025 = suavizar(mes_numerico, df_2025["Precipitacion"].values)
x_2024, y_2024 = suavizar(mes_numerico, df_2024["Precipitacion"].values)
x_prom, y_prom = suavizar(mes_numerico, df_ult_5.values)

fig_line, ax_line = plt.subplots(figsize=(10, 4))
ax_line.plot(x_2025, y_2025, label="2025", linewidth=2.2)
ax_line.plot(x_2024, y_2024, label="2024", linestyle='--', linewidth=2)
ax_line.plot(x_prom, y_prom, label="Prom. 2020–2024", linestyle='-.', linewidth=2)
ax_line.set_xticks(mes_numerico)
ax_line.set_xticklabels(mes_labels, rotation=45)
ax_line.set_title("Tendencia de precipitaciones mensuales", fontsize=16)
ax_line.set_ylabel("mm", fontsize=12)
ax_line.grid(True, linestyle='--', alpha=0.4)
ax_line.legend()
st.pyplot(fig_line)

# --- Secciones futuras ---
st.markdown("---")
st.markdown("## 🔧 Secciones en desarrollo")
with st.expander("⚡ Generación de energía"):
    st.write("Esta sección estará disponible próximamente.")
with st.expander("💰 Ingresos y ventas"):
    st.write("Esta sección estará disponible próximamente.")
with st.expander("🔒 Cumplimiento normativo y seguridad"):
    st.write("Esta sección estará disponible próximamente.")

# --- Pie de página ---
st.markdown("---")
st.markdown("© 2025 Hidroeléctrica El Canelo S.A. | Marcelo Arriagada")




