# === CONFIGURACIÓN GENERAL ===
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(page_title="Reporte Mensual", layout="wide")

# === PARÁMETROS ===
archivo_excel = "HEC mensuales 2025.xlsx"
meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

# === SELECCIÓN DE MES ===
st.markdown("## 📅 Selección de mes")
mes_seleccionado = st.selectbox("Mes", list(meses.keys()), index=pd.Timestamp.now().month - 1)
mes_num = meses[mes_seleccionado]

# === ENCABEZADO ===
col_logo, col_title = st.columns([1, 9])
with col_logo:
    st.image("logo.jpg", width=180)
with col_title:
    st.markdown(f"<h1 style='font-size: 48px;'>Reporte Mensual {mes_seleccionado} 2025</h1>", unsafe_allow_html=True)

# === CARGA DE DATOS ===
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

# === FILTROS Y SERIES POR AÑO ===
df_hist_2025 = df_hist[df_hist["Año"] == 2025]
df_hist_2024 = df_hist[df_hist["Año"] == 2024]
df_hist_5y = df_hist[df_hist["Año"].between(2020, 2024)]

df_2025 = df_pluv[df_pluv["Año"] == 2025]
df_2024 = df_pluv[df_pluv["Año"] == 2024]
df_5y_avg = df_pluv[df_pluv["Año"].between(2020, 2024)].groupby("Mes")["Precipitacion"].mean()

# === KPI MENSUALES ===
prec_2025 = df_2025[df_2025["Mes"] == mes_num]["Precipitacion"].sum()
prec_2024 = df_2024[df_2024["Mes"] == mes_num]["Precipitacion"].sum()
prec_5y = df_5y_avg.loc[mes_num] if mes_num in df_5y_avg.index else 0
gen_2025 = df_hist_2025[df_hist_2025["Mes"] == mes_num]["Generación Bornes (kWh)"].sum()
gen_2024 = df_hist_2024[df_hist_2024["Mes"] == mes_num]["Generación Bornes (kWh)"].sum()
venta_2025 = df_hist_2025[df_hist_2025["Mes"] == mes_num]["Facturacion (USD$)"].sum()
venta_2024 = df_hist_2024[df_hist_2024["Mes"] == mes_num]["Facturacion (USD$)"].sum()

# === ACUMULADOS ===
prec_acum = df_2025[df_2025["Mes"] <= mes_num]["Precipitacion"].sum()
gen_acum = df_hist_2025[df_hist_2025["Mes"] <= mes_num]["Generación Bornes (kWh)"].sum()
venta_acum = df_hist_2025[df_hist_2025["Mes"] <= mes_num]["Facturacion (USD$)"].sum()

# === DELTAS ===
delta_prec_24 = prec_2025 - prec_2024
delta_prec_5y = prec_2025 - prec_5y
delta_gen = gen_2025 - gen_2024
delta_venta = venta_2025 - venta_2024

# === VISUALIZACIÓN KPI ===
st.markdown(f"## 📊 Indicadores de {mes_seleccionado}")
col1, col2, col3 = st.columns(3)
col1.metric("Precipitaciones 2025", f"{prec_2025:.1f} mm", f"{delta_prec_24:+.1f} mm vs 2024")
col2.metric("Precipitaciones 2024", f"{prec_2024:.1f} mm")
col3.metric("Promedio 2020-2024", f"{prec_5y:.1f} mm", f"{delta_prec_5y:+.1f} mm vs promedio")

col4, col5 = st.columns(2)
col4.metric("Generación 2025", f"{gen_2025:,.0f} kWh", f"{delta_gen:+,.0f} kWh vs 2024")
col5.metric("Ventas 2025", f"${venta_2025:,.0f}", f"{delta_venta:+,.0f} USD vs 2024")

st.markdown("### 🔄 Valores Acumulados a la Fecha")
col6, col7, col8 = st.columns(3)
col6.metric("Acumulado Precipitaciones", f"{prec_acum:.1f} mm")
col7.metric("Acumulado Generación", f"{gen_acum:,.0f} kWh")
col8.metric("Acumulado Ventas", f"${venta_acum:,.0f}")

# === GRAFICO DE BARRAS DE PRECIPITACIONES ===
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
ax_bar.set_title("Comparación mensual de precipitaciones", fontsize=13)
ax_bar.grid(axis='y', linestyle='--', alpha=0.3)
ax_bar.spines["top"].set_visible(False)
ax_bar.spines["right"].set_visible(False)
st.pyplot(fig_bar)

# === GRAFICO SUAVIZADO DE PRECIPITACIONES ===
st.markdown("### 🌧️ Evolución de Precipitaciones 2025")
prec_mes_acum = df_2025.groupby("Mes")["Precipitacion"].sum().reindex(range(1,13), fill_value=0)
x = np.arange(1, 13)
z = np.polyfit(x, prec_mes_acum, 3)
p = np.poly1d(z)
x_smooth = np.linspace(1, 12, 300)
y_smooth = p(x_smooth)

fig_smooth, ax_smooth = plt.subplots(figsize=(10, 4))
ax_smooth.plot(x, prec_mes_acum, "o", label="Datos mensuales")
ax_smooth.plot(x_smooth, y_smooth, label="Tendencia suavizada", linewidth=2)
ax_smooth.set_title("Precipitaciones mensuales acumuladas - 2025", fontsize=14)
ax_smooth.set_xticks(x)
ax_smooth.set_xticklabels(list(meses.keys()), rotation=45)
ax_smooth.set_ylabel("mm")
ax_smooth.grid(True, linestyle="--", alpha=0.5)
ax_smooth.legend()
st.pyplot(fig_smooth)

# === GRAFICOS ANUALES: GENERACIÓN ===
st.markdown("### ⚡ Generación Anual")
gen_serie_2025 = df_hist_2025.groupby("Mes")["Generación Bornes (kWh)"].sum()
gen_serie_2024 = df_hist_2024.groupby("Mes")["Generación Bornes (kWh)"].sum()
gen_serie_5y = df_hist_5y.groupby("Mes")["Generación Bornes (kWh)"].mean()

fig_gen, ax_gen = plt.subplots(figsize=(10, 4))
ax_gen.plot(gen_serie_2025.index, gen_serie_2025, marker='o', label="2025")
ax_gen.plot(gen_serie_2024.index, gen_serie_2024, marker='o', label="2024")
ax_gen.plot(gen_serie_5y.index, gen_serie_5y, linestyle='--', marker='o', label="Prom. 2020-2024")
ax_gen.set_xticks(range(1, 13))
ax_gen.set_xticklabels(list(meses.keys()), rotation=45)
ax_gen.set_ylabel("kWh")
ax_gen.set_title("Energía Generada por Mes")
ax_gen.grid(True, linestyle="--", alpha=0.5)
ax_gen.legend()
st.pyplot(fig_gen)

# === GRAFICOS ANUALES: VENTAS ===
st.markdown("### 💰 Ventas Anuales")
venta_serie_2025 = df_hist_2025.groupby("Mes")["Facturacion (USD$)"].sum()
venta_serie_2024 = df_hist_2024.groupby("Mes")["Facturacion (USD$)"].sum()
venta_serie_5y = df_hist_5y.groupby("Mes")["Facturacion (USD$)"].mean()

fig_venta, ax_venta = plt.subplots(figsize=(10, 4))
ax_venta.plot(venta_serie_2025.index, venta_serie_2025, marker='o', label="2025")
ax_venta.plot(venta_serie_2024.index, venta_serie_2024, marker='o', label="2024")
ax_venta.plot(venta_serie_5y.index, venta_serie_5y, linestyle='--', marker='o', label="Prom. 2020-2024")
ax_venta.set_xticks(range(1, 13))
ax_venta.set_xticklabels(list(meses.keys()), rotation=45)
ax_venta.set_ylabel("USD")
ax_venta.set_title("Ventas por Mes")
ax_venta.grid(True, linestyle="--", alpha=0.5)
ax_venta.legend()
st.pyplot(fig_venta)
