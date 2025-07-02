import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from cycler import cycler
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(
    page_title="Reporte Operativo y Financiero",
    layout="wide",
    page_icon=None
)

# === PALETA DE COLORES Y ESTILOS ===
PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
plt.style.use('ggplot')
plt.rcParams.update({
    'axes.prop_cycle': cycler(color=PALETTE),
    'font.family': 'Arial',
    'axes.titleweight': 'bold',
    'font.size': 14,
    'grid.color': '#CCCCCC',
    'grid.linestyle': '--',
    'grid.alpha': 0.6
})

# === FUNCIONES AUXILIARES ===
def calcular_delta(actual, anterior):
    """Calcula diferencia absoluta y porcentual, y la formatea con color."""
    if anterior and abs(anterior) > 1e-9:
        delta = actual - anterior
        pct = (delta / anterior) * 100
        color = PALETTE[2] if delta >= 0 else PALETTE[3]
        return f"<span style='color:{color};'>{delta:+,.0f} ({pct:+.1f}%)</span>"
    return "N/A"

def format_currency(x):
    """Formatea como moneda."""
    return f"${x:,.0f}"

def format_MWh(x):
    """Formatea como MWh."""
    return f"{x:,.0f} MWh"

# === CARGA DE DATOS ===
EXCEL_PATH = Path("HEC mensuales 2025.xlsx")
if not EXCEL_PATH.exists():
    st.error(f"Archivo no encontrado: {EXCEL_PATH}.")
    st.stop()

@st.cache_data(ttl=3600)
def cargar_datos(path):
    df_pluv = pd.read_excel(path, sheet_name="Pluviometria", skiprows=127, usecols="C:D")
    df_pluv.columns = ["Fecha", "Precipitacion"]
    df_pluv["Fecha"] = pd.to_datetime(df_pluv["Fecha"], errors='coerce')
    df_pluv["Año"] = df_pluv["Fecha"].dt.year
    df_pluv["Mes"] = df_pluv["Fecha"].dt.month

    df_hist = pd.read_excel(path, sheet_name="Datos Historicos", skiprows=195, usecols="C:G")
    df_hist.columns = ["Fecha", "Generacion", "Generacion_Ref", "Potencia", "Ventas"]
    df_hist["Fecha"] = pd.to_datetime(df_hist["Fecha"], errors='coerce')
    df_hist.dropna(subset=["Fecha"], inplace=True)
    df_hist["Año"] = df_hist["Fecha"].dt.year
    df_hist["Mes"] = df_hist["Fecha"].dt.month

    df_mayor = pd.read_excel(path, sheet_name="Mayor", skiprows=4)
    df_mayor = df_mayor.loc[:, ~df_mayor.columns.str.contains("^Unnamed")]
    df_mayor.columns = [c.strip().upper() for c in df_mayor.columns]
    if "FECHA" in df_mayor.columns:
        df_mayor["FECHA"] = pd.to_datetime(df_mayor["FECHA"], errors="coerce")
        df_mayor["AÑO"] = df_mayor["FECHA"].dt.year
        df_mayor["MES"] = df_mayor["FECHA"].dt.month
    else:
        df_mayor["AÑO"] = pd.NA
        df_mayor["MES"] = pd.NA

    return df_pluv, df_hist, df_mayor

# === ANÁLISIS FINANCIERO ===
def procesar_estado_resultado(df_mayor, año, mes):
    df_periodo = df_mayor[(df_mayor["AÑO"] == año) & (df_mayor["MES"] == mes)]
    df_periodo["CLASE"] = df_periodo["CUENTA"].astype(str).str[0].astype(int)
    agregado = df_periodo.groupby("CLASE").agg({
        "DEBE": "sum",
        "HABER": "sum",
        "SALDO": "sum"
    }).reset_index()
    clase_nombre = {
        1: "Activos",
        2: "Pasivos",
        3: "Costos",
        4: "Ingresos",
        5: "Gastos",
        6: "Patrimonio"
    }
    agregado["Cuenta"] = agregado["CLASE"].map(clase_nombre)
    return agregado[["Cuenta", "DEBE", "HABER", "SALDO"]]

def calcular_margenes(ingresos, costos):
    utilidad = ingresos - costos
    margen = (utilidad / ingresos) * 100 if ingresos else 0
    return utilidad, margen

# === GRÁFICOS ===
def crear_grafico_tendencias(df_hist, año_actual, mes_actual, kpi, altura=400):
    """Gráfico de barras para año actual y línea para histórico del KPI."""
    meses_str = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    df_mes_actual = df_hist[(df_hist["Año"] == año_actual)]
    df_hist_anteriores = df_hist[(df_hist["Año"] < año_actual)]

    fig = go.Figure()
    # Barras año actual
    fig.add_trace(go.Bar(
        x=meses_str,
        y=[df_mes_actual[df_mes_actual["Mes"] == i][kpi].sum() for i in range(1,13)],
        name=f"{año_actual}",
        marker_color=PALETTE[0]
    ))
    # Línea histórico para el mes seleccionado
    años = sorted(df_hist_anteriores["Año"].unique())
    valores = [df_hist_anteriores[(df_hist_anteriores["Año"] == a) & (df_hist_anteriores["Mes"] == mes_actual)][kpi].sum() for a in años]
    fig.add_trace(go.Scatter(
        x=años,
        y=valores,
        mode='lines+markers',
        name="Histórico",
        line=dict(color=PALETTE[1], width=3)
    ))

    fig.update_layout(
        title=f"Tendencias de {kpi}",
        xaxis_title="Mes / Año",
        yaxis_title=f"{kpi} {'(MWh)' if kpi=='Generacion' else ''}",
        barmode='group',
        template="plotly_white",
        height=altura,
        legend=dict(y=0.99, x=0.01)
    )
    return fig

def grafico_generacion_anual(df_hist):
    df_generacion_anual = df_hist.groupby("Año")["Generacion"].sum().reset_index()
    if 2025 not in df_generacion_anual["Año"].values:
        df_generacion_anual = pd.concat([
            df_generacion_anual,
            pd.DataFrame({"Año": [2025], "Generacion": [0]})
        ], ignore_index=True)
    df_generacion_anual = df_generacion_anual.sort_values("Año")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_generacion_anual["Año"],
        y=df_generacion_anual["Generacion"],
        mode='lines+markers',
        line=dict(color=PALETTE[0], width=3),
        name="Generación Anual (MWh)"
    ))
    fig.update_layout(
        title="Generación Anual de Energía",
        xaxis_title="Año",
        yaxis_title="Generación (MWh)",
        template="plotly_white",
        height=400
    )
    return fig

# === RECOMENDACIONES ===
def generar_recomendaciones(analisis):
    recs = []
    margen = analisis['Financiero']['margen_operativo']
    if margen < 15:
        recs.append("🔧 Optimizar costos para mejorar márgenes operativos.")
    elif margen > 30:
        recs.append("📈 xxxxxxxx")
    return recs

# === MAIN ===
def main():
    # Carga datos
    df_pluv, df_hist, df_mayor = cargar_datos(EXCEL_PATH)

    # Sidebar - selección
    st.sidebar.title("Parámetros del Reporte")
    empresa = st.sidebar.text_input("Nombre de la Empresa", "Hidroeléctrica El Canelo")
    meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    mes = st.sidebar.selectbox("📅 Seleccione Mes", meses, index=4)  # Mayo por defecto
    m = meses.index(mes) + 1
    año_actual = 2025

    st.title(f"Reporte Operativo y Financiero - {empresa}")
    st.header(f"Período: {mes} {año_actual}")

    # === KPIs MENSUALES ===
    # Solo el mes seleccionado
    gen25_mes = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] == m)]["Generacion"].sum()
    gen24_mes = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] == m)]["Generacion"].sum()
    genavg_mes = df_hist[(df_hist["Año"].between(año_actual-5, año_actual-1)) & (df_hist["Mes"] == m)]["Generacion"].mean()

    vent25_mes = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] == m)]["Ventas"].sum()
    vent24_mes = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] == m)]["Ventas"].sum()
    ventavg_mes = df_hist[(df_hist["Año"].between(año_actual-5, año_actual-1)) & (df_hist["Mes"] == m)]["Ventas"].mean()

    prec25_mes = df_pluv[(df_pluv["Año"] == año_actual) & (df_pluv["Mes"] == m)]["Precipitacion"].sum()
    prec24_mes = df_pluv[(df_pluv["Año"] == año_actual-1) & (df_pluv["Mes"] == m)]["Precipitacion"].sum()
    precavg_mes = df_pluv[(df_pluv["Año"].between(año_actual-5, año_actual-1)) & (df_pluv["Mes"] == m)]["Precipitacion"].mean()

    # === KPIs ACUMULADOS ===
    # De enero al mes seleccionado
    gen25_acum = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] <= m)]["Generacion"].sum()
    gen24_acum = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] <= m)]["Generacion"].sum()
    genavg_acum = df_hist[df_hist["Año"].between(año_actual-5, año_actual-1)].groupby("Año").apply(lambda x: x[x["Mes"] <= m]["Generacion"].sum()).mean()

    vent25_acum = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] <= m)]["Ventas"].sum()
    vent24_acum = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] <= m)]["Ventas"].sum()
    ventavg_acum = df_hist[df_hist["Año"].between(año_actual-5, año_actual-1)].groupby("Año").apply(lambda x: x[x["Mes"] <= m]["Ventas"].sum()).mean()

    prec25_acum = df_pluv[(df_pluv["Año"] == año_actual) & (df_pluv["Mes"] <= m)]["Precipitacion"].sum()
    prec24_acum = df_pluv[(df_pluv["Año"] == año_actual-1) & (df_pluv["Mes"] <= m)]["Precipitacion"].sum()
    precavg_acum = df_pluv[df_pluv["Año"].between(año_actual-5, año_actual-1)].groupby("Año").apply(lambda x: x[x["Mes"] <= m]["Precipitacion"].sum()).mean()

    # === VISUALIZACIÓN DE KPIs ===
    st.subheader("KPIs Mensuales (solo mes seleccionado)")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**Generación**<br>{format_MWh(gen25_mes)}<br>Δ vs {año_actual-1}: {calcular_delta(gen25_mes, gen24_mes)}<br>Δ vs Promedio 5A: {calcular_delta(gen25_mes, genavg_mes)}", unsafe_allow_html=True)
    col2.markdown(f"**Ventas**<br>{format_currency(vent25_mes)}<br>Δ vs {año_actual-1}: {calcular_delta(vent25_mes, vent24_mes)}<br>Δ vs Promedio 5A: {calcular_delta(vent25_mes, ventavg_mes)}", unsafe_allow_html=True)
    col3.markdown(f"**Precipitaciones**<br>{prec25_mes:,.1f} mm<br>Δ vs {año_actual-1}: {calcular_delta(prec25_mes, prec24_mes)}<br>Δ vs Promedio 5A: {calcular_delta(prec25_mes, precavg_mes)}", unsafe_allow_html=True)

    st.subheader("KPIs Acumulados (enero a mes seleccionado)")
    col4, col5, col6 = st.columns(3)
    col4.markdown(f"**Generación Acum.**<br>{format_MWh(gen25_acum)}<br>Δ vs {año_actual-1}: {calcular_delta(gen25_acum, gen24_acum)}<br>Δ vs Promedio 5A: {calcular_delta(gen25_acum, genavg_acum)}", unsafe_allow_html=True)
    col5.markdown(f"**Ventas Acum.**<br>{format_currency(vent25_acum)}<br>Δ vs {año_actual-1}: {calcular_delta(vent25_acum, vent24_acum)}<br>Δ vs Promedio 5A: {calcular_delta(vent25_acum, ventavg_acum)}", unsafe_allow_html=True)
    col6.markdown(f"**Precipitaciones Acum.**<br>{prec25_acum:,.1f} mm<br>Δ vs {año_actual-1}: {calcular_delta(prec25_acum, prec24_acum)}<br>Δ vs Promedio 5A: {calcular_delta(prec25_acum, precavg_acum)}", unsafe_allow_html=True)

    # Gráficos tendencias mensuales y anuales
    st.subheader("Tendencias Operativas")
    fig_gen = crear_grafico_tendencias(df_hist, año_actual, m, "Generacion")
    st.plotly_chart(fig_gen, use_container_width=True)

    fig_vent = crear_grafico_tendencias(df_hist, año_actual, m, "Ventas")
    st.plotly_chart(fig_vent, use_container_width=True)

    # Gráfico anual generación con 2025
    st.subheader("Generación Anual de Energía")
    fig_anual = grafico_generacion_anual(df_hist)
    st.plotly_chart(fig_anual, use_container_width=True)

    # Análisis financiero
    st.subheader("Análisis Financiero Detallado")
    estado_resultado = procesar_estado_resultado(df_mayor, año_actual, m)

    ingresos = estado_resultado[estado_resultado["Cuenta"] == "Ingresos"]["HABER"].sum()
    costos = estado_resultado[estado_resultado["Cuenta"] == "Costos"]["DEBE"].sum()
    utilidad, margen = calcular_margenes(ingresos, costos)

    estado_display = estado_resultado.copy()
    estado_display["DEBE"] = estado_display["DEBE"].apply(format_currency)
    estado_display["HABER"] = estado_display["HABER"].apply(format_currency)
    estado_display["SALDO"] = estado_display["SALDO"].apply(format_currency)
    st.table(estado_display)

    colf1, colf2, colf3 = st.columns(3)
    colf1.metric("Ingresos Totales", format_currency(ingresos))
    colf2.metric("Costos Totales", format_currency(costos))
    colf3.metric("Utilidad Operativa", format_currency(utilidad), f"{margen:.1f}%")

    # Recomendaciones
    analisis = {
        'Financiero': {'margen_operativo': margen}
    }
    st.subheader("Recomendaciones Estratégicas")
    recs = generar_recomendaciones(analisis)
    if recs:
        for r in recs:
            st.markdown(f"- {r}")
    else:
        st.info("✅ El desempeño operativo y financiero está dentro de parámetros esperados.")

    st.caption(f"Reporte generado el {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')} | Derechos reservados © 2025")

if __name__ == "__main__":
    main()
