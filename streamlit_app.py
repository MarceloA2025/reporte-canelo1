# === LIBRERIAS NECESARIAS ===
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# === CONFIGURACION DE PAGINA ===
st.set_page_config(page_title="Reporte Mensual", layout="wide")  # Titulo y formato ancho para reuniones ejecutivas

# === ENCABEZADO CON LOGO Y TITULO ===
col_logo, col_title = st.columns([1, 9])  # Definir dos columnas: logo y título
with col_logo:
    st.image("logo.jpg", width=180)  # Mostrar logo corporativo
with col_title:
    # Mostrar título principal en fuente grande y moderna
    st.markdown("<h1 style='font-size: 48px; margin-bottom: 0;'>REPORTE MENSUAL - \U0001F4C5</h1>", unsafe_allow_html=True)

# === SIDEBAR: SELECCION DE MES ===
meses = {
    "Enero": 0, "Febrero": 1, "Marzo": 2, "Abril": 3,
    "Mayo": 4, "Junio": 5, "Julio": 6, "Agosto": 7,
    "Septiembre": 8, "Octubre": 9, "Noviembre": 10, "Diciembre": 11
}
st.sidebar.header("\U0001F4C5 Seleccionar mes")
mes_seleccionado = st.sidebar.selectbox("Mes", list(meses.keys()))
idx_mes = meses[mes_seleccionado]  # Obtener el índice del mes seleccionado

# === CARGA Y PROCESAMIENTO DE DATOS ===
archivo_excel = "HEC mensuales 2025.xlsx"
df_raw = pd.read_excel(archivo_excel, sheet_name="Pluviometria", skiprows=127, usecols="C:D")

# Renombrar columnas para mayor claridad
df = df_raw.rename(columns={df_raw.columns[0]: "Fecha", df_raw.columns[1]: "Precipitacion"})
df["Fecha"] = pd.to_datetime(df["Fecha"])
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month

# Subconjuntos por año para el análisis
# Se asume que hay datos por cada año en la serie

# Datos de precipitación mensual para 2025 y 2024
df_2025 = df[df["Año"] == 2025].reset_index(drop=True)
df_2024 = df[df["Año"] == 2024].reset_index(drop=True)

# Promedio mensual de los últimos 5 años (2020-2024)
df_ult_5 = df[df["Año"].between(2020, 2024)].groupby("Mes")["Precipitacion"].mean()

# === VALORES PARA EL MES SELECCIONADO ===
prec_2025_mes = df_2025.iloc[idx_mes]["Precipitacion"] if idx_mes < len(df_2025) else 0
prec_2024_mes = df_2024.iloc[idx_mes]["Precipitacion"] if idx_mes < len(df_2024) else 0
prom_ult_5_mes = df_ult_5.iloc[idx_mes] if idx_mes < len(df_ult_5) else 0

# === COMPARATIVAS ===
delta_2025_vs_24 = prec_2025_mes - prec_2024_mes
delta_2025_vs_prom = prec_2025_mes - prom_ult_5_mes

# === INDICADORES KPI ===
st.markdown(f"## \U0001F4CA Indicadores de {mes_seleccionado}")
col1, col2, col3 = st.columns(3)
col1.metric("Precipitaciones 2025", f"{prec_2025_mes:.1f} mm", f"{delta_2025_vs_24:+.1f} mm vs 2024")
col2.metric("Precipitaciones 2024", f"{prec_2024_mes:.1f} mm")
col3.metric("Promedio 2020-2024", f"{prom_ult_5_mes:.1f} mm", f"{delta_2025_vs_prom:+.1f} mm vs promedio")

# === GRAFICO DE BARRAS COMPARATIVAS ===
st.markdown(f"### \U0001F4CA Precipitaciones - {mes_seleccionado}")
fig_bar, ax_bar = plt.subplots(figsize=(6, 3))
labels = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025_mes, prec_2024_mes, prom_ult_5_mes]
colores = ['green' if prec_2025_mes >= x else 'red' for x in [prec_2024_mes, prom_ult_5_mes, prom_ult_5_mes]]
ax_bar.bar(labels, valores, color=colores)
ax_bar.set_ylabel("mm")
ax_bar.set_title(f"Comparación mensual ({mes_seleccionado})")
ax_bar.grid(axis='y', linestyle='--', alpha=0.5)
for i, v in enumerate(valores):
    ax_bar.text(i, v + 1, f"{v:.1f}", ha='center')
st.pyplot(fig_bar)

# === GRAFICO DE LINEAS SUAVIZADAS ===
st.markdown("### \U0001F4C8 Evolución mensual de precipitaciones")
fig_line, ax_line = plt.subplots(figsize=(10, 4))
meses_etiquetas = df_2025["Fecha"].dt.strftime('%b')

# Graficar cada línea con estilo distinto
ax_line.plot(meses_etiquetas, df_2025["Precipitacion"], label="2025", linestyle='-', marker='o')
ax_line.plot(meses_etiquetas, df_2024["Precipitacion"], label="2024", linestyle='--', marker='o')
ax_line.plot(meses_etiquetas, df_ult_5.values, label="Prom. 2020-2024", linestyle='-.', marker='o')

ax_line.set_title("Precipitaciones mensuales (mm)", fontsize=16)
ax_line.set_ylabel("mm", fontsize=12)
ax_line.grid(True, linestyle='--', alpha=0.5)
ax_line.legend()
ax_line.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
st.pyplot(fig_line)

# === SECCIONES FUTURAS ===
st.markdown("---")
st.markdown("## \U0001F527 Secciones en desarrollo")
with st.expander("\u26a1 Generación de energía"):
    st.write("Sección de generación en desarrollo...")
with st.expander("💰 Ingresos y ventas"):
    st.write("Sección de ingresos en desarrollo...")
with st.expander("\ud83d\udd12 Cumplimiento normativo y seguridad"):
    st.write("Sección de cumplimiento en desarrollo...")

# === PIE DE PAGINA ===
st.markdown("---")
st.markdown("© 2025 Hidroeléctrica El Canelo S.A. | Marcelo Arriagada")
