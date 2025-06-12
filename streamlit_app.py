# === LIBRERIAS NECESARIAS ===
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np  # Para suavizar datos con np.polyfit si se requiere

# === CONFIGURACION DE PAGINA ===
st.set_page_config(page_title="Reporte Mensual", layout="wide")

# === SIDEBAR: SELECCION DE MES ===
meses = {
    "Enero": 0, "Febrero": 1, "Marzo": 2, "Abril": 3,
    "Mayo": 4, "Junio": 5, "Julio": 6, "Agosto": 7,
    "Septiembre": 8, "Octubre": 9, "Noviembre": 10, "Diciembre": 11
}
st.sidebar.header("📅 Seleccionar mes")
mes_seleccionado = st.sidebar.selectbox("Mes", list(meses.keys()))
idx_mes = meses[mes_seleccionado]

# === ENCABEZADO CON LOGO Y TITULO ===
col_logo, col_title = st.columns([1, 9])
with col_logo:
    st.image("logo.jpg", width=180)
with col_title:
    st.markdown(f"<h1 style='font-size: 48px; margin-bottom: 0;'>REPORTE MENSUAL {mes_seleccionado.upper()} 2025</h1>", unsafe_allow_html=True)

# === CARGA Y PROCESAMIENTO DE DATOS ===
archivo_excel = "HEC mensuales 2025.xlsx"
df_raw = pd.read_excel(archivo_excel, sheet_name="Pluviometria", skiprows=127, usecols="C:D")
df = df_raw.rename(columns={df_raw.columns[0]: "Fecha", df_raw.columns[1]: "Precipitacion"})
df["Fecha"] = pd.to_datetime(df["Fecha"])
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month

# Subconjuntos por año para precipitaciones
df_2025 = df[df["Año"] == 2025].reset_index(drop=True)
df_2024 = df[df["Año"] == 2024].reset_index(drop=True)
df_ult_5 = df[df["Año"].between(2020, 2024)].groupby("Mes")["Precipitacion"].mean()

# === VALORES PARA EL MES SELECCIONADO ===
prec_2025_mes = df_2025.iloc[idx_mes]["Precipitacion"] if idx_mes < len(df_2025) else 0
prec_2024_mes = df_2024.iloc[idx_mes]["Precipitacion"] if idx_mes < len(df_2024) else 0
prom_ult_5_mes = df_ult_5.iloc[idx_mes] if idx_mes < len(df_ult_5) else 0

# === COMPARATIVAS ===
delta_2025_vs_24 = prec_2025_mes - prec_2024_mes
delta_2025_vs_prom = prec_2025_mes - prom_ult_5_mes

# === INDICADORES KPI ===
st.markdown(f"## 📊 Indicadores de {mes_seleccionado}")
col1, col2, col3 = st.columns(3)
col1.metric("Precipitaciones 2025", f"{prec_2025_mes:.1f} mm", f"{delta_2025_vs_24:+.1f} mm vs 2024")
col2.metric("Precipitaciones 2024", f"{prec_2024_mes:.1f} mm")
col3.metric("Promedio 2020-2024", f"{prom_ult_5_mes:.1f} mm", f"{delta_2025_vs_prom:+.1f} mm vs promedio")

# === GRAFICO DE BARRAS COMPARATIVAS ===
st.markdown(f"### 📊 Precipitaciones - {mes_seleccionado}")
fig_bar, ax_bar = plt.subplots(figsize=(6, 3))
labels = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025_mes, prec_2024_mes, prom_ult_5_mes]
colores = ["#1f77b4", "#ff7f0e", "#2ca02c"]
ax_bar.bar(labels, valores, color=colores, width=0.5)
ax_bar.set_ylabel("mm")
ax_bar.set_title(f"Comparación mensual ({mes_seleccionado})")
ax_bar.grid(axis='y', linestyle='--', alpha=0.5)
for i, v in enumerate(valores):
    ax_bar.text(i, v + 1, f"{v:.1f}", ha='center')
st.pyplot(fig_bar)

# === GRAFICO DE LINEAS SUAVIZADAS ===
st.markdown("### 📈 Evolución mensual de precipitaciones")
fig_line, ax_line = plt.subplots(figsize=(10, 4))
meses_etiquetas = df_2025["Fecha"].dt.strftime('%b')

serie_2025 = df_2025["Precipitacion"].rolling(window=2, min_periods=1).mean()
serie_2024 = df_2024["Precipitacion"].rolling(window=2, min_periods=1).mean()
serie_5 = pd.Series(df_ult_5.values).rolling(window=2, min_periods=1).mean()

ax_line.plot(meses_etiquetas, serie_2025, label="2025", linestyle='-', marker='o')
ax_line.plot(meses_etiquetas, serie_2024, label="2024", linestyle='--', marker='o')
ax_line.plot(meses_etiquetas[:len(serie_5)], serie_5, label="Prom. 2020-2024", linestyle='-.', marker='o')

ax_line.set_title("Precipitaciones mensuales (mm)", fontsize=16)
ax_line.set_ylabel("mm", fontsize=12)
ax_line.grid(True, linestyle='--', alpha=0.5)
ax_line.legend()
ax_line.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
st.pyplot(fig_line)

# === SECCIONES FUTURAS ===
st.markdown("---")
st.markdown("## 🔧 Secciones en desarrollo")
with st.expander("⚡ Generación de energía"):
    st.write("Sección de generación en desarrollo...")
with st.expander("💰 Ingresos y ventas"):
    st.write("Sección de ingresos en desarrollo...")
with st.expander("🔒 Cumplimiento normativo y seguridad"):
    st.write("Sección de cumplimiento en desarrollo...")

# === PIE DE PAGINA ===
st.markdown("---")
st.markdown("© 2025 Hidroeléctrica El Canelo S.A. | Marcelo Arriagada")


