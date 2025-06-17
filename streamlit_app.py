import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(page_title="Reporte Mensual Hidroeléctrica", layout="wide")

# === CARGA DE ARCHIVO ===
archivo_excel = "C:/One Drive Hotmail/OneDrive/Documentos/Python VSCode/REPORTE WEB/HEC mensuales 2025.xlsx"

# === CARGA DE DATOS ===
df_pluv_raw = pd.read_excel(archivo_excel, sheet_name="Pluviometria", skiprows=127, usecols="C:D")
df_gen_raw = pd.read_excel(archivo_excel, sheet_name="Datos Historicos", skiprows=195, usecols="C:F")
df_ventas_raw = pd.read_excel(archivo_excel, sheet_name="Datos Historicos", skiprows=195, usecols="C:H")

# === PROCESAMIENTO DE DATOS ===
df_pluv_raw.columns = ["Mes", "Precipitacion"]
df_gen_raw.columns = ["Mes", "Gen_2025", "Gen_2024", "Gen_5y"]
df_ventas_raw.columns = ["Mes", "Ventas_2025", "Ventas_2024", "Ventas_5y"]

df_pluv_raw["Mes"] = pd.Categorical(df_pluv_raw["Mes"], categories=[
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", 
    "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], ordered=True)

# === SELECCIÓN DE MES (EN CUERPO) ===
st.title("📊 Reporte Mensual Hidroeléctrica - 2025")
mes_seleccionado = st.selectbox("Selecciona un mes", df_pluv_raw["Mes"].dropna().tolist(), index=5)
mes_num = df_pluv_raw[df_pluv_raw["Mes"] == mes_seleccionado].index[0] + 1

# === EXTRACCIÓN DE DATOS DEL MES SELECCIONADO ===
prec_2025 = df_pluv_raw.loc[mes_num - 1, "Precipitacion"]
prec_2024 = df_gen_raw.loc[mes_num - 1, "Gen_2024"]
gen_2025 = df_gen_raw.loc[mes_num - 1, "Gen_2025"]
gen_2024 = df_gen_raw.loc[mes_num - 1, "Gen_2024"]
venta_2025 = df_ventas_raw.loc[mes_num - 1, "Ventas_2025"]
venta_2024 = df_ventas_raw.loc[mes_num - 1, "Ventas_2024"]

# === ACUMULADOS ===
acum_prec_2025 = df_pluv_raw.iloc[:mes_num]["Precipitacion"].sum()
acum_prec_2024 = df_gen_raw.iloc[:mes_num]["Gen_2024"].sum()
acum_gen_2025 = df_gen_raw.iloc[:mes_num]["Gen_2025"].sum()
acum_gen_2024 = df_gen_raw.iloc[:mes_num]["Gen_2024"].sum()
acum_venta_2025 = df_ventas_raw.iloc[:mes_num]["Ventas_2025"].sum()
acum_venta_2024 = df_ventas_raw.iloc[:mes_num]["Ventas_2024"].sum()

# === FUNCION PARA DELTA ===
def calcular_delta(valor_actual, valor_anterior):
    delta = valor_actual - valor_anterior
    delta_pct = (delta / valor_anterior * 100) if valor_anterior != 0 else 0
    return delta, delta_pct

# === DELTAS ===
delta_prec, delta_prec_pct = calcular_delta(prec_2025, prec_2024)
delta_gen, delta_gen_pct = calcular_delta(gen_2025, gen_2024)
delta_venta, delta_venta_pct = calcular_delta(venta_2025, venta_2024)
delta_acum_prec, delta_acum_prec_pct = calcular_delta(acum_prec_2025, acum_prec_2024)
delta_acum_gen, delta_acum_gen_pct = calcular_delta(acum_gen_2025, acum_gen_2024)
delta_acum_venta, delta_acum_venta_pct = calcular_delta(acum_venta_2025, acum_venta_2024)

# === KPIs ===
st.subheader("📌 Indicadores Clave (KPI)")
kpi1, kpi2, kpi3 = st.columns(3)
kpi4, kpi5, kpi6 = st.columns(3)

kpi1.metric("Precipitación Mensual 2025", f"{prec_2025:.1f} mm", f"{delta_prec:+.1f} mm ({delta_prec_pct:+.1f}%) vs 2024")
kpi2.metric("Generación Mensual 2025", f"{gen_2025:,.0f} kWh", f"{delta_gen:+,.0f} ({delta_gen_pct:+.1f}%) vs 2024")
kpi3.metric("Ventas Mensuales 2025", f"${venta_2025:,.0f}", f"{delta_venta:+,.0f} ({delta_venta_pct:+.1f}%) vs 2024")
kpi4.metric("Precipitación Acumulada 2025", f"{acum_prec_2025:.1f} mm", f"{delta_acum_prec:+.1f} mm ({delta_acum_prec_pct:+.1f}%) vs 2024")
kpi5.metric("Generación Acumulada 2025", f"{acum_gen_2025:,.0f} kWh", f"{delta_acum_gen:+,.0f} ({delta_acum_gen_pct:+.1f}%) vs 2024")
kpi6.metric("Ventas Acumuladas 2025", f"${acum_venta_2025:,.0f}", f"{delta_acum_venta:+,.0f} ({delta_acum_venta_pct:+.1f}%) vs 2024")

# === GRAFICOS ===
st.subheader("📈 Comparación Visual de Datos")

col1, col2 = st.columns(2)

# Barras de Precipitación
with col1:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df_pluv_raw["Mes"], df_pluv_raw["Precipitacion"], color="#4c72b0")
    ax.set_title("Precipitación Mensual 2025")
    ax.set_ylabel("mm")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

# Línea de Precipitación Comparativa
with col2:
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(df_pluv_raw["Mes"], df_pluv_raw["Precipitacion"], label="2025", marker="o")
    ax2.plot(df_gen_raw["Mes"], df_gen_raw["Gen_2024"], label="2024", marker="s")
    ax2.plot(df_gen_raw["Mes"], df_gen_raw["Gen_5y"], label="Promedio 5 años", linestyle="--")
    ax2.set_title("Precipitación Anual Comparativa")
    ax2.legend()
    ax2.tick_params(axis="x", rotation=45)
    st.pyplot(fig2)

# === PIE DE PÁGINA ===
st.divider()
st.caption("🔧 Preparado por Ecoener - Marcelo Arriagada")


