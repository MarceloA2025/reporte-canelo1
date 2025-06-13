import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configurar la página de Streamlit
st.set_page_config(page_title="Reporte Mensual", layout="wide")
st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

# Encabezado con logo y título dinámico
col_logo, col_title = st.columns([1, 9])
with col_logo:
    st.image("logo.jpg", width=160)
with col_title:
    meses = {
        "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
        "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
        "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }
    mes_nombre = st.sidebar.selectbox("📅 Seleccionar mes", list(meses.keys()))
    mes_numero = meses[mes_nombre]
    st.markdown(f"<h1 style='font-size: 40px;'>Reporte Mensual {mes_nombre} 2025</h1>", unsafe_allow_html=True)

# Cargar archivo Excel
archivo_excel = "HEC mensuales 2025.xlsx"

# --- Carga de Pluviometría ---
df_pluv = pd.read_excel(archivo_excel, sheet_name="Pluviometria", skiprows=127, usecols="C:D", nrows=24)
df_pluv.columns = ["Fecha", "Precipitacion"]
df_pluv["Fecha"] = pd.to_datetime(df_pluv["Fecha"])
df_pluv["Mes"] = df_pluv["Fecha"].dt.month
df_pluv["Año"] = df_pluv["Fecha"].dt.year

prec_2025 = df_pluv[(df_pluv["Año"] == 2025) & (df_pluv["Mes"] == mes_numero)]["Precipitacion"].sum()
prec_2024 = df_pluv[(df_pluv["Año"] == 2024) & (df_pluv["Mes"] == mes_numero)]["Precipitacion"].sum()
prec_acum_2025 = df_pluv[(df_pluv["Año"] == 2025) & (df_pluv["Mes"] <= mes_numero)]["Precipitacion"].sum()
prec_acum_2024 = df_pluv[(df_pluv["Año"] == 2024) & (df_pluv["Mes"] <= mes_numero)]["Precipitacion"].sum()

# --- Carga de Generación y Ventas ---
df_hist = pd.read_excel(archivo_excel, sheet_name="Datos Historicos", skiprows=195, usecols="C:G")
df_hist.columns = ["Fecha", "Generacion_Bornes", "Generacion_Ref", "Potencia_Media", "Facturacion"]
df_hist.dropna(subset=["Fecha"], inplace=True)
df_hist["Fecha"] = pd.to_datetime(df_hist["Fecha"])
df_hist["Mes"] = df_hist["Fecha"].dt.month
df_hist["Año"] = df_hist["Fecha"].dt.year

gen_2025 = df_hist[(df_hist["Año"] == 2025) & (df_hist["Mes"] == mes_numero)]["Generacion_Bornes"].sum()
gen_2024 = df_hist[(df_hist["Año"] == 2024) & (df_hist["Mes"] == mes_numero)]["Generacion_Bornes"].sum()
gen_acum_2025 = df_hist[(df_hist["Año"] == 2025) & (df_hist["Mes"] <= mes_numero)]["Generacion_Bornes"].sum()
gen_acum_2024 = df_hist[(df_hist["Año"] == 2024) & (df_hist["Mes"] <= mes_numero)]["Generacion_Bornes"].sum()

ventas_2025 = df_hist[(df_hist["Año"] == 2025) & (df_hist["Mes"] == mes_numero)]["Facturacion"].sum()
ventas_2024 = df_hist[(df_hist["Año"] == 2024) & (df_hist["Mes"] == mes_numero)]["Facturacion"].sum()
ventas_acum_2025 = df_hist[(df_hist["Año"] == 2025) & (df_hist["Mes"] <= mes_numero)]["Facturacion"].sum()
ventas_acum_2024 = df_hist[(df_hist["Año"] == 2024) & (df_hist["Mes"] <= mes_numero)]["Facturacion"].sum()

# --- Mostrar KPIs en tabla ---
st.markdown("## 📊 Indicadores Clave del Mes")
kpi_df = pd.DataFrame({
    "Indicador": [
        "Precipitaciones Mensuales (mm)",
        "Precipitaciones Acumuladas (mm)",
        "Generación Mensual (kWh)",
        "Generación Acumulada (kWh)",
        "Ventas Mensuales (USD$)",
        "Ventas Acumuladas (USD$)"
    ],
    "2025": [
        prec_2025, prec_acum_2025,
        gen_2025, gen_acum_2025,
        ventas_2025, ventas_acum_2025
    ],
    "2024": [
        prec_2024, prec_acum_2024,
        gen_2024, gen_acum_2024,
        ventas_2024, ventas_acum_2024
    ],
    "Diferencia": [
        prec_2025 - prec_2024,
        prec_acum_2025 - prec_acum_2024,
        gen_2025 - gen_2024,
        gen_acum_2025 - gen_acum_2024,
        ventas_2025 - ventas_2024,
        ventas_acum_2025 - ventas_acum_2024
    ]
})
st.dataframe(kpi_df.style.format({
    "2025": "{:,.0f}",
    "2024": "{:,.0f}",
    "Diferencia": "{:+,.0f}"
}), use_container_width=True)
