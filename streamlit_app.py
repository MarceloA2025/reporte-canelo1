import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(page_title="Reporte Mensual", layout="wide")

# === FUNCIÓN PARA FORMATO DE DELTA ===
def calcular_delta(valor_2025, valor_2024, unidad):
    if valor_2024 == 0:
        delta_abs = valor_2025
        delta_pct = 0.0
    else:
        delta_abs = valor_2025 - valor_2024
        delta_pct = (delta_abs / valor_2024) * 100
    color = "green" if delta_abs >= 0 else "red"
    return f"<span style='color:{color}'>{delta_abs:+,.0f} {unidad} ({delta_pct:+.1f}%)</span> vs 2024"

# === SELECCIÓN DE MES EN CENTRO ===
st.markdown("<h2 style='text-align:center;'>📅 Seleccione el Mes</h2>", unsafe_allow_html=True)
meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}
mes_seleccionado = st.selectbox("", list(meses.keys()), index=3)
mes_num = meses[mes_seleccionado]

# === ENCABEZADO CON LOGO Y TÍTULO ===
col_logo, col_title = st.columns([1, 9])
with col_logo:
    st.image("logo.jpg", width=180)
with col_title:
    st.markdown(f"<h1 style='font-size: 48px; margin-bottom: 0;'>Reporte Mensual {mes_seleccionado} 2025</h1>", unsafe_allow_html=True)

# === CARGA DE DATOS ===
archivo_excel = "C:\One Drive Hotmail\OneDrive\Documentos\Python VSCode\REPORTE WEB\HEC mensuales 2025.xlsx"
df_pluv_raw = pd.read_excel(archivo_excel, sheet_name="Pluviometria", skiprows=127, usecols="C:D")
df_pluv_raw.columns = ["Fecha", "Precipitacion"]
df_pluv_raw["Fecha"] = pd.to_datetime(df_pluv_raw["Fecha"])
df_pluv_raw["Año"] = df_pluv_raw["Fecha"].dt.year
df_pluv_raw["Mes"] = df_pluv_raw["Fecha"].dt.month

df_hist_raw = pd.read_excel(archivo_excel, sheet_name="Datos Historicos", skiprows=195, usecols="C:G")
df_hist_raw.columns = ["Fecha", "Generación Bornes (kWh)", "Generacion Ref (kWh)", "Potencia Media (MW)", "Facturacion (USD$)"]
df_hist_raw["Fecha"] = pd.to_datetime(df_hist_raw["Fecha"], errors='coerce')
df_hist_raw = df_hist_raw.dropna(subset=["Fecha"])
df_hist_raw["Año"] = df_hist_raw["Fecha"].dt.year
df_hist_raw["Mes"] = df_hist_raw["Fecha"].dt.month

# === FILTROS POR AÑO ===
df_2025 = df_pluv_raw[df_pluv_raw["Año"] == 2025]
df_2024 = df_pluv_raw[df_pluv_raw["Año"] == 2024]
df_5y = df_pluv_raw[df_pluv_raw["Año"].between(2020, 2024)]
df_5y_avg = df_5y.groupby("Mes")["Precipitacion"].mean()

dfh_2025 = df_hist_raw[df_hist_raw["Año"] == 2025]
dfh_2024 = df_hist_raw[df_hist_raw["Año"] == 2024]
dfh_5y = df_hist_raw[df_hist_raw["Año"].between(2020, 2024)]

# === KPI MENSUALES ===
prec_2025 = df_2025[df_2025["Mes"] == mes_num]["Precipitacion"].sum()
prec_2024 = df_2024[df_2024["Mes"] == mes_num]["Precipitacion"].sum()
prec_5y = df_5y_avg.loc[mes_num] if mes_num in df_5y_avg.index else 0

gen_2025 = dfh_2025[dfh_2025["Mes"] == mes_num]["Generación Bornes (kWh)"].sum()
gen_2024 = dfh_2024[dfh_2024["Mes"] == mes_num]["Generación Bornes (kWh)"].sum()

venta_2025 = dfh_2025[dfh_2025["Mes"] == mes_num]["Facturacion (USD$)"].sum()
venta_2024 = dfh_2024[dfh_2024["Mes"] == mes_num]["Facturacion (USD$)"].sum()

# === KPI ACUMULADOS ===
prec_acum_2025 = df_2025[df_2025["Mes"] <= mes_num]["Precipitacion"].sum()
prec_acum_2024 = df_2024[df_2024["Mes"] <= mes_num]["Precipitacion"].sum()
gen_acum_2025 = dfh_2025[dfh_2025["Mes"] <= mes_num]["Generación Bornes (kWh)"].sum()
gen_acum_2024 = dfh_2024[dfh_2024["Mes"] <= mes_num]["Generación Bornes (kWh)"].sum()
venta_acum_2025 = dfh_2025[dfh_2025["Mes"] <= mes_num]["Facturacion (USD$)"].sum()
venta_acum_2024 = dfh_2024[dfh_2024["Mes"] <= mes_num]["Facturacion (USD$)"].sum()

# === VISUALIZACIÓN DE KPIs ===
st.markdown(f"## 📊 Indicadores de {mes_seleccionado}")

col1, col2, col3 = st.columns(3)
col1.metric("Precipitaciones Mensuales 2025", f"{prec_2025:.1f} mm", None)
col1.markdown(calcular_delta(prec_2025, prec_2024, "mm"), unsafe_allow_html=True)

col2.metric("Generación Mensual 2025", f"{gen_2025:,.0f} kWh", None)
col2.markdown(calcular_delta(gen_2025, gen_2024, "kWh"), unsafe_allow_html=True)

col3.metric("Ventas Mensuales 2025", f"${venta_2025:,.0f}", None)
col3.markdown(calcular_delta(venta_2025, venta_2024, "USD"), unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)
col4.metric("Precipitaciones Acumuladas 2025", f"{prec_acum_2025:.1f} mm", None)
col4.markdown(calcular_delta(prec_acum_2025, prec_acum_2024, "mm"), unsafe_allow_html=True)

col5.metric("Generación Acumulada 2025", f"{gen_acum_2025:,.0f} kWh", None)
col5.markdown(calcular_delta(gen_acum_2025, gen_acum_2024, "kWh"), unsafe_allow_html=True)

col6.metric("Ventas Acumuladas 2025", f"${venta_acum_2025:,.0f}", None)
col6.markdown(calcular_delta(venta_acum_2025, venta_acum_2024, "USD"), unsafe_allow_html=True)

# === GRAFICO BARRAS PRECIPITACIONES MENSUALES ===
st.markdown("### 🌧️ Comparación Mensual de Precipitaciones")
fig_bar, ax_bar = plt.subplots(figsize=(4, 2))
labels = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025, prec_2024, prec_5y]
colores = ["#1f77b4", "#ff7f0e", "#2ca02c"]
bars = ax_bar.bar(labels, valores, color=colores)
for bar, valor in zip(bars, valores):
    ax_bar.text(bar.get_x() + bar.get_width()/2, valor, f"{valor:.1f}", ha='center', va='bottom')
ax_bar.set_ylabel("mm")
ax_bar.set_ylim(0, max(valores)*1.2)
ax_bar.grid(axis="y", linestyle="--", alpha=0.3)
st.pyplot(fig_bar)

# === GRAFICO LINEA PRECIPITACIONES ANUALES ===
st.markdown("### 📈 Precipitaciones Anuales")
prec_serie_2025 = df_2025.groupby("Mes")["Precipitacion"].sum()
prec_serie_2024 = df_2024.groupby("Mes")["Precipitacion"].sum()
prec_serie_5y = df_5y.groupby("Mes")["Precipitacion"].mean()
mes_labels = list(meses.keys())

fig_prec, ax_prec = plt.subplots(figsize=(5, 2))
ax_prec.plot(mes_labels[:len(prec_serie_2025)], prec_serie_2025, label="2025", marker="o")
ax_prec.plot(mes_labels[:len(prec_serie_2024)], prec_serie_2024, label="2024", marker="o")
ax_prec.plot(mes_labels[:len(prec_serie_5y)], prec_serie_5y, label="Prom. 2020-2024", linestyle='--', marker="o")
ax_prec.set_title("Precipitaciones por Mes", fontsize=7)
ax_prec.set_ylabel("mm")
ax_prec.legend()
ax_prec.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig_prec)

# === GRAFICO LINEA GENERACION ===
st.markdown("### 🔌 Energía Generada Mensual")
gen_serie_2025 = dfh_2025.groupby("Mes")["Generación Bornes (kWh)"].sum()
gen_serie_2024 = dfh_2024.groupby("Mes")["Generación Bornes (kWh)"].sum()
gen_serie_5y = dfh_5y.groupby("Mes")["Generación Bornes (kWh)"].mean()

fig_gen, ax_gen = plt.subplots(figsize=(5, 2))
ax_gen.plot(mes_labels[:len(gen_serie_2025)], gen_serie_2025, label="2025", marker='o')
ax_gen.plot(mes_labels[:len(gen_serie_2024)], gen_serie_2024, label="2024", marker='o')
ax_gen.plot(mes_labels[:len(gen_serie_5y)], gen_serie_5y, label="Prom. 2020-2024", linestyle='--', marker='o')
ax_gen.set_title("Energía Generada por Mes", fontsize=7)
ax_gen.set_ylabel("kWh")
ax_gen.legend()
ax_gen.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig_gen)

# === GRAFICO LINEA VENTAS ===
st.markdown("### 💰 Ventas Mensuales")
venta_serie_2025 = dfh_2025.groupby("Mes")["Facturacion (USD$)"].sum()
venta_serie_2024 = dfh_2024.groupby("Mes")["Facturacion (USD$)"].sum()
venta_serie_5y = dfh_5y.groupby("Mes")["Facturacion (USD$)"].mean()

fig_venta, ax_venta = plt.subplots(figsize=(5, 2))
ax_venta.plot(mes_labels[:len(venta_serie_2025)], venta_serie_2025, label="2025", marker='o')
ax_venta.plot(mes_labels[:len(venta_serie_2024)], venta_serie_2024, label="2024", marker='o')
ax_venta.plot(mes_labels[:len(venta_serie_5y)], venta_serie_5y, label="Prom. 2020-2024", linestyle='--', marker='o')
ax_venta.set_title("Ventas por Mes", fontsize=7)
ax_venta.set_ylabel("USD")
ax_venta.legend()
ax_venta.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig_venta)

# === PIE DE PÁGINA ===
st.markdown("---")
st.markdown("<div style='text-align:center; color:gray;'>Preparado por Ecoener - Marcelo Arriagada</div>", unsafe_allow_html=True)



