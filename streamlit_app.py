import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Configurar página
st.set_page_config(page_title="Reporte Mensual", layout="wide")

# --- ENCABEZADO CON LOGO Y TÍTULO ---
col_logo, col_titulo = st.columns([1, 8])
with col_logo:
    st.image("logo.jpg", width=180)
with col_titulo:
    st.markdown("<h1 style='font-size: 42px; margin-bottom: 0;'>REPORTE MENSUAL</h1>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR: Selección de mes ---
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

# --- Preparar datos por año ---
df = df_raw.rename(columns={df_raw.columns[0]: "Fecha", df_raw.columns[1]: "Precipitacion"})
df["Fecha"] = pd.to_datetime(df["Fecha"])
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month_name()

# Filtrar datos
df_2025 = df[df["Año"] == 2025]
df_2024 = df[df["Año"] == 2024]
df_ult_5 = df[df["Año"].between(2020, 2024)].groupby(df["Fecha"].dt.month)["Precipitacion"].mean()

# Obtener datos del mes seleccionado
prec_2025_mes = df_2025.iloc[idx_mes]["Precipitacion"] if idx_mes < len(df_2025) else 0
prec_2024_mes = df_2024.iloc[idx_mes]["Precipitacion"] if idx_mes < len(df_2024) else 0
prom_ult_5_mes = df_ult_5.iloc[idx_mes] if idx_mes < len(df_ult_5) else 0

# Calcular variaciones
delta_2025_vs_24 = prec_2025_mes - prec_2024_mes
delta_2025_vs_prom = prec_2025_mes - prom_ult_5_mes

# --- Mostrar KPIs ---
st.markdown(f"## 📊 Indicadores del mes de {mes_seleccionado}")
col1, col2, col3 = st.columns(3)
col1.metric("Precipitaciones 2025", f"{prec_2025_mes:.1f} mm", f"{delta_2025_vs_24:+.1f} mm vs 2024")
col2.metric("Precipitaciones 2024", f"{prec_2024_mes:.1f} mm")
col3.metric("Promedio últimos 5 años", f"{prom_ult_5_mes:.1f} mm", f"{delta_2025_vs_prom:+.1f} mm vs promedio")

# --- Gráfico de línea suavizada ---
st.markdown("### 📈 Comparación mensual de precipitaciones (línea suavizada)")

fig_linea, ax = plt.subplots(figsize=(10, 4))
meses_grafico = df_2025["Fecha"].dt.strftime('%b')

ax.plot(meses_grafico, df_2025["Precipitacion"], label="2025", linestyle='-', marker='o')
ax.plot(meses_grafico, df_2024["Precipitacion"], label="2024", linestyle='--', marker='o')
ax.plot(meses_grafico, df_ult_5.values, label="Prom. últimos 5 años", linestyle='-.', marker='o')

ax.set_title("Precipitaciones mensuales (mm)", fontsize=16)
ax.set_ylabel("mm", fontsize=12)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

st.pyplot(fig_linea)

# --- Gráfico de barras para el mes seleccionado ---
st.markdown(f"### 📊 Comparación del mes de {mes_seleccionado} en barra")

fig_barras, ax2 = plt.subplots(figsize=(6, 4))
categorias = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025_mes, prec_2024_mes, prom_ult_5_mes]
colores = ['green' if prec_2025_mes
