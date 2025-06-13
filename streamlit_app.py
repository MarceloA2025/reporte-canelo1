import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Reporte Mensual", layout="wide")

# --- HEADER ---
col_logo, col_title = st.columns([1, 9])
with col_logo:
    st.image("logo.jpg", width=180)
with col_title:
    st.markdown("<h1 style='font-size: 44px; margin-bottom: 0;'>REPORTE MENSUAL - 📅</h1>", unsafe_allow_html=True)

# --- SIDEBAR: Selector de mes ---
meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}
st.sidebar.header("📅 Seleccionar mes")
mes_nombre = st.sidebar.selectbox("Mes", list(meses.keys()))
mes_num = meses[mes_nombre]

# --- Cargar archivo Excel ---
archivo_excel = "HEC mensuales 2025.xlsx"

# --- Datos de precipitaciones (hoja Pluviometria desde celda C128) ---
df_lluvia = pd.read_excel(archivo_excel, sheet_name="Pluviometria", skiprows=127, usecols="C:D")
df_lluvia.columns = ["Fecha", "Precipitacion"]
df_lluvia["Fecha"] = pd.to_datetime(df_lluvia["Fecha"])
df_lluvia["Año"] = df_lluvia["Fecha"].dt.year
df_lluvia["Mes"] = df_lluvia["Fecha"].dt.month

df_lluvia_2025 = df_lluvia[df_lluvia["Año"] == 2025]
df_lluvia_2024 = df_lluvia[df_lluvia["Año"] == 2024]

prec_2025_mes = df_lluvia_2025[df_lluvia_2025["Mes"] == mes_num]["Precipitacion"].values[0] if not df_lluvia_2025[df_lluvia_2025["Mes"] == mes_num].empty else 0
prec_2024_mes = df_lluvia_2024[df_lluvia_2024["Mes"] == mes_num]["Precipitacion"].values[0] if not df_lluvia_2024[df_lluvia_2024["Mes"] == mes_num].empty else 0
delta_prec_mes = prec_2025_mes - prec_2024_mes

acum_prec_2025 = df_lluvia_2025[df_lluvia_2025["Mes"] <= mes_num]["Precipitacion"].sum()
acum_prec_2024 = df_lluvia_2024[df_lluvia_2024["Mes"] <= mes_num]["Precipitacion"].sum()
delta_acum_prec = acum_prec_2025 - acum_prec_2024

# --- Datos de generación y ventas (hoja Datos Historicos desde celda C196) ---
df_hist = pd.read_excel(archivo_excel, sheet_name="Datos Historicos", skiprows=195)
df_hist.columns = ["Fecha", "Generacion_kWh", "Generacion_Ref_kWh", "Potencia_MW", "Facturacion_USD"]
df_hist["Fecha"] = pd.to_datetime(df_hist["Fecha"], errors="coerce")
df_hist.dropna(subset=["Fecha"], inplace=True)
df_hist["Año"] = df_hist["Fecha"].dt.year
df_hist["Mes"] = df_hist["Fecha"].dt.month

df_hist_2025 = df_hist[df_hist["Año"] == 2025]
df_hist_2024 = df_hist[df_hist["Año"] == 2024]

# Generación mensual y acumulada
gen_2025_mes = df_hist_2025[df_hist_2025["Mes"] == mes_num]["Generacion_kWh"].sum()
gen_2024_mes = df_hist_2024[df_hist_2024["Mes"] == mes_num]["Generacion_kWh"].sum()
delta_gen_mes = gen_2025_mes - gen_2024_mes

acum_gen_2025 = df_hist_2025[df_hist_2025["Mes"] <= mes_num]["Generacion_kWh"].sum()
acum_gen_2024 = df_hist_2024[df_hist_2024["Mes"] <= mes_num]["Generacion_kWh"].sum()
delta_acum_gen = acum_gen_2025 - acum_gen_2024

# Ventas mensual y acumulada
ventas_2025_mes = df_hist_2025[df_hist_2025["Mes"] == mes_num]["Facturacion_USD"].sum()
ventas_2024_mes = df_hist_2024[df_hist_2024["Mes"] == mes_num]["Facturacion_USD"].sum()
delta_ventas_mes = ventas_2025_mes - ventas_2024_mes

acum_ventas_2025 = df_hist_2025[df_hist_2025["Mes"] <= mes_num]["Facturacion_USD"].sum()
acum_ventas_2024 = df_hist_2024[df_hist_2024["Mes"] <= mes_num]["Facturacion_USD"].sum()
delta_acum_ventas = acum_ventas_2025 - acum_ventas_2024

# --- KPIs ---
st.markdown(f"## 📊 Indicadores Clave - {mes_nombre}")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("🌧️ Precipitación mensual (mm)", f"{prec_2025_mes:.1f}", f"{delta_prec_mes:+.1f} vs 2024")
kpi2.metric("⚡ Generación mensual (kWh)", f"{gen_2025_mes:,.0f}", f"{delta_gen_mes:+,.0f} vs 2024")
kpi3.metric("💵 Ventas mensuales (USD)", f"${ventas_2025_mes:,.0f}", f"{delta_ventas_mes:+,.0f} vs 2024")

kpi4, kpi5, kpi6 = st.columns(3)
kpi4.metric("🌧️ Precipitación acumulada", f"{acum_prec_2025:.1f} mm", f"{delta_acum_prec:+.1f} vs 2024")
kpi5.metric("⚡ Generación acumulada", f"{acum_gen_2025:,.0f} kWh", f"{delta_acum_gen:+,.0f} vs 2024")
kpi6.metric("💵 Ventas acumuladas", f"${acum_ventas_2025:,.0f}", f"{delta_acum_ventas:+,.0f} vs 2024")
