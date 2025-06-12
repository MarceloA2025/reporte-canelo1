# Importamos librerías necesarias
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargamos los datos desde Excel (archivo debe estar en la misma carpeta o subirlo en Streamlit Cloud)
archivo_excel = "HEC mensuales 2025.xlsx"

# --- Cargar datos de precipitaciones desde hoja "Pluviometria"
df_pluv = pd.read_excel(archivo_excel, sheet_name="Pluviometria", skiprows=127, usecols="C:F")
df_pluv.columns = ["Mes", "Año", "Precipitacion", "Estacion"]
df_pluv = df_pluv.dropna(subset=["Mes", "Año", "Precipitacion"])
df_pluv["Mes"] = df_pluv["Mes"].astype(int)
df_pluv["Año"] = df_pluv["Año"].astype(int)
df_pluv["Precipitacion"] = pd.to_numeric(df_pluv["Precipitacion"], errors="coerce")
df_pluv["Precipitacion Acumulada"] = df_pluv.groupby("Año")["Precipitacion"].cumsum()

# --- Cargar datos históricos desde celda C196 de la hoja "Datos Historicos"
df_hist = pd.read_excel(archivo_excel, sheet_name="Datos Historicos", skiprows=195, usecols="C:G")
df_hist.columns = ["Fecha", "Generación Bornes (kWh)", "Generacion Referenciada (kWh)", "Potencia Media (MW)", "Facturacion (USD$)"]
df_hist["Fecha"] = pd.to_datetime(df_hist["Fecha"], errors='coerce')
df_hist["Año"] = df_hist["Fecha"].dt.year
df_hist["Mes"] = df_hist["Fecha"].dt.month

# --- Generamos acumulados por año y mes
df_hist = df_hist.dropna(subset=["Generación Bornes (kWh)", "Facturacion (USD$)"])
df_hist.sort_values(by="Fecha", inplace=True)
df_hist["Generacion Acumulada"] = df_hist.groupby("Año")["Generación Bornes (kWh)"].cumsum()
df_hist["Ventas Acumuladas"] = df_hist.groupby("Año")["Facturacion (USD$)"].cumsum()

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide")

# Título principal con el año dinámico
st.title("📊 Reporte Mensual - Hidroeléctrica El Canelo S.A.")

# Selector de mes y año en el centro
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo",
        6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre",
        10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    mes_seleccionado = st.selectbox("Selecciona el mes del reporte", options=list(meses.keys()), format_func=lambda x: meses[x])
    anio_seleccionado = st.selectbox("Selecciona el año", sorted(df_hist["Año"].unique(), reverse=True))

# Subtítulo del reporte
st.subheader(f"📅 Reporte Mensual {meses[mes_seleccionado]} {anio_seleccionado}")

# --- KPIs ---
df_mes = df_hist[(df_hist["Mes"] == mes_seleccionado) & (df_hist["Año"] == anio_seleccionado)]
df_acum = df_hist[(df_hist["Año"] == anio_seleccionado) & (df_hist["Mes"] <= mes_seleccionado)]
df_pluv_mes = df_pluv[(df_pluv["Mes"] == mes_seleccionado) & (df_pluv["Año"] == anio_seleccionado)]
df_pluv_acum = df_pluv[(df_pluv["Año"] == anio_seleccionado) & (df_pluv["Mes"] <= mes_seleccionado)]

# Valores actuales y acumulados
gen_mes = df_mes["Generación Bornes (kWh)"].sum()
ventas_mes = df_mes["Facturacion (USD$)"].sum()
gen_acum = df_acum["Generación Bornes (kWh)"].sum()
ventas_acum = df_acum["Facturacion (USD$)"].sum()
precip_acum = df_pluv_acum["Precipitacion"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("🌧️ Precipitación Acumulada", f"{precip_acum:,.0f} mm")
col2.metric("⚡ Generación Acumulada", f"{gen_acum:,.0f} kWh")
col3.metric("💰 Ventas Acumuladas", f"USD {ventas_acum:,.0f}")

# --- GRAFICOS DE LÍNEA ACUMULADOS ---
fig, ax = plt.subplots()
df_filtrado = df_hist[df_hist["Año"] == anio_seleccionado]
ax.plot(df_filtrado["Mes"], df_filtrado["Generacion Acumulada"], label="Generación Acum.", marker='o')
ax.plot(df_filtrado["Mes"], df_filtrado["Ventas Acumuladas"], label="Ventas Acum.", marker='s')
ax.set_xticks(range(1, 13))
ax.set_xticklabels([meses[i] for i in range(1, 13)], rotation=45)
ax.set_ylabel("Valor acumulado")
ax.set_title("Evolución Acumulada a lo largo del año")
ax.legend()
st.pyplot(fig)
