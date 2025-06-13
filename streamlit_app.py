# === CONFIGURACION DE PAGINA ===
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

st.set_page_config(page_title="Reporte Mensual", layout="wide")

# === FUNCION PARA FORMATO DE DELTA ===
def calcular_delta(valor_2025, valor_2024, unidad):
    if valor_2024 == 0:
        delta_abs = valor_2025
        delta_pct = 0.0
    else:
        delta_abs = valor_2025 - valor_2024
        delta_pct = (delta_abs / valor_2024) * 100
    return f"{delta_abs:+,.1f} {unidad} ({delta_pct:+.1f}%) vs 2024"

# === SIDEBAR: SELECCION DE MES ===
meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}
st.sidebar.header("📅 Seleccionar mes")
mes_seleccionado = st.sidebar.selectbox("Mes", list(meses.keys()))
mes_num = meses[mes_seleccionado]

# === ENCABEZADO CON LOGO Y TITULO ===
col_logo, col_title = st.columns([1, 9])
with col_logo:
    st.image("logo.jpg", width=180)
with col_title:
    st.markdown(f"<h1 style='font-size: 48px; margin-bottom: 0;'>Reporte Mensual {mes_seleccionado} 2025</h1>", unsafe_allow_html=True)

# === CARGA Y PROCESAMIENTO DE DATOS ===
archivo_excel = "HEC mensuales 2025.xlsx"
df_pluv_raw = pd.read_excel(archivo_excel, sheet_name="Pluviometria", skiprows=127, usecols="C:D")
df_pluv = df_pluv_raw.rename(columns={df_pluv_raw.columns[0]: "Fecha", df_pluv_raw.columns[1]: "Precipitacion"})
df_pluv["Fecha"] = pd.to_datetime(df_pluv["Fecha"])
df_pluv["Año"] = df_pluv["Fecha"].dt.year
df_pluv["Mes"] = df_pluv["Fecha"].dt.month

df_hist_raw = pd.read_excel(archivo_excel, sheet_name="Datos Historicos", skiprows=195, usecols="C:G")
df_hist = df_hist_raw.rename(columns={df_hist_raw.columns[0]: "Fecha"})
df_hist["Fecha"] = pd.to_datetime(df_hist["Fecha"], errors='coerce')
df_hist = df_hist.dropna(subset=["Fecha"])
df_hist["Año"] = df_hist["Fecha"].dt.year
df_hist["Mes"] = df_hist["Fecha"].dt.month

# === FILTROS POR AÑO ===
df_hist_2025 = df_hist[df_hist["Año"] == 2025]
df_hist_2024 = df_hist[df_hist["Año"] == 2024]

df_2025 = df_pluv[df_pluv["Año"] == 2025]
df_2024 = df_pluv[df_pluv["Año"] == 2024]

# === KPI MENSUALES ===
prec_2025 = df_2025[df_2025["Mes"] == mes_num]["Precipitacion"].sum()
prec_2024 = df_2024[df_2024["Mes"] == mes_num]["Precipitacion"].sum()

gen_2025 = df_hist_2025[df_hist_2025["Mes"] == mes_num]["Generación Bornes (kWh)"].sum()
gen_2024 = df_hist_2024[df_hist_2024["Mes"] == mes_num]["Generación Bornes (kWh)"].sum()

venta_2025 = df_hist_2025[df_hist_2025["Mes"] == mes_num]["Facturacion (USD$)"].sum()
venta_2024 = df_hist_2024[df_hist_2024["Mes"] == mes_num]["Facturacion (USD$)"].sum()

# === KPI ACUMULADOS ===
prec_acum_2025 = df_2025[df_2025["Mes"] <= mes_num]["Precipitacion"].sum()
prec_acum_2024 = df_2024[df_2024["Mes"] <= mes_num]["Precipitacion"].sum()

gen_acum_2025 = df_hist_2025[df_hist_2025["Mes"] <= mes_num]["Generación Bornes (kWh)"].sum()
gen_acum_2024 = df_hist_2024[df_hist_2024["Mes"] <= mes_num]["Generación Bornes (kWh)"].sum()

venta_acum_2025 = df_hist_2025[df_hist_2025["Mes"] <= mes_num]["Facturacion (USD$)"].sum()
venta_acum_2024 = df_hist_2024[df_hist_2024["Mes"] <= mes_num]["Facturacion (USD$)"].sum()

# === VISUALIZACIÓN KPIs CON % ===
st.markdown(f"## 📊 Indicadores de {mes_seleccionado}")
col1, col2, col3 = st.columns(3)
col1.metric("Precipitaciones Mensuales 2025", f"{prec_2025:.1f} mm", calcular_delta(prec_2025, prec_2024, "mm"))
col2.metric("Generación Mensual 2025", f"{gen_2025:,.0f} kWh", calcular_delta(gen_2025, gen_2024, "kWh"))
col3.metric("Ventas Mensuales 2025", f"${venta_2025:,.0f}", calcular_delta(venta_2025, venta_2024, "USD"))

col4, col5, col6 = st.columns(3)
col4.metric("Precipitaciones Acumuladas 2025", f"{prec_acum_2025:.1f} mm", calcular_delta(prec_acum_2025, prec_acum_2024, "mm"))
col5.metric("Generación Acumulada 2025", f"{gen_acum_2025:,.0f} kWh", calcular_delta(gen_acum_2025, gen_acum_2024, "kWh"))
col6.metric("Ventas Acumuladas 2025", f"${venta_acum_2025:,.0f}", calcular_delta(venta_acum_2025, venta_acum_2024, "USD"))

# === GRAFICO DE BARRAS PRECIPITACIONES ===
st.markdown(f"### 📊 Precipitaciones - {mes_seleccionado}")
labels = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025, prec_2024, prec_5y]
colores = ["#1f77b4", "#ff7f0e", "#2ca02c"]
y_max = max(valores) * 1.25

fig_bar, ax_bar = plt.subplots(figsize=(6, 2))
bars = ax_bar.bar(labels, valores, color=colores, width=0.4)
for bar, valor in zip(bars, valores):
    ax_bar.text(bar.get_x() + bar.get_width()/2, valor + y_max*0.02, f"{valor:.1f}", ha='center', va='bottom', fontsize=10)
ax_bar.set_ylim(0, y_max)
ax_bar.set_ylabel("mm", fontsize=10)
ax_bar.set_title(f"Comparación mensual de precipitaciones", fontsize=13)
ax_bar.grid(axis='y', linestyle='--', alpha=0.3)
ax_bar.spines["top"].set_visible(False)
ax_bar.spines["right"].set_visible(False)
st.pyplot(fig_bar)

# === GRAFICO DE PRODUCCION ANUAL ===
st.markdown("### 🔌 Producción Anual de Energía")
gen_serie_2025 = df_hist_2025.groupby("Mes")["Generación Bornes (kWh)"].sum()
gen_serie_2024 = df_hist_2024.groupby("Mes")["Generación Bornes (kWh)"].sum()
gen_serie_5y = df_hist_5y.groupby("Mes")["Generación Bornes (kWh)"].mean()

fig_gen, ax_gen = plt.subplots(figsize=(10, 4))
mes_labels = list(meses.keys())
ax_gen.plot(mes_labels[:len(gen_serie_2025)], gen_serie_2025, label="2025", marker='o')
ax_gen.plot(mes_labels[:len(gen_serie_2024)], gen_serie_2024, label="2024", marker='o')
ax_gen.plot(mes_labels[:len(gen_serie_5y)], gen_serie_5y, label="Prom. 2020-2024", linestyle='--', marker='o')
ax_gen.set_title("Energía Generada por Mes", fontsize=14)
ax_gen.set_ylabel("kWh")
ax_gen.legend()
ax_gen.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig_gen)

# === GRAFICO DE VENTAS ===
st.markdown("### 💰 Ventas Anuales")
venta_serie_2025 = df_hist_2025.groupby("Mes")["Facturacion (USD$)"].sum()
venta_serie_2024 = df_hist_2024.groupby("Mes")["Facturacion (USD$)"].sum()
venta_serie_5y = df_hist_5y.groupby("Mes")["Facturacion (USD$)"].mean()

fig_venta, ax_venta = plt.subplots(figsize=(10, 4))
ax_venta.plot(mes_labels[:len(venta_serie_2025)], venta_serie_2025, label="2025", marker='o')
ax_venta.plot(mes_labels[:len(venta_serie_2024)], venta_serie_2024, label="2024", marker='o')
ax_venta.plot(mes_labels[:len(venta_serie_5y)], venta_serie_5y, label="Prom. 2020-2024", linestyle='--', marker='o')
ax_venta.set_title("Ventas por Mes (USD)", fontsize=14)
ax_venta.set_ylabel("USD")
ax_venta.legend()
ax_venta.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig_venta)
