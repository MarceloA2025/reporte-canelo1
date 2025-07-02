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

# === PARÁMETROS DE ESTILO ===

## → KPIs
KPI_LABEL_FONT_SIZE       = 14        # tamaño de la letra de la etiqueta (p.ej. "Generación")
KPI_VALUE_FONT_SIZE       = 24        # tamaño de la letra del valor principal (p.ej. "1,234 MWh")
KPI_DELTA_FONT_SIZE       = 16        # tamaño de la letra de los deltas porcentuales
KPI_COLOR_POSITIVE        = PALETTE[2]  # color cuando el delta es positivo
KPI_COLOR_NEGATIVE        = PALETTE[3]  # color cuando el delta es negativo

## → Gráficos plotly
CHART_HEIGHT              = 450       # altura por defecto de los gráficos
BAR_COLOR_CURRENT_YEAR    = PALETTE[0]
LINE_COLOR_HISTORICO      = PALETTE[1]
LEGEND_FONT_SIZE          = 12        # tamaño de fuente de las leyendas
AXIS_TITLE_FONT_SIZE      = 14        # tamaño de fuente de títulos de ejes
AXIS_TICK_FONT_SIZE       = 12        # tamaño de fuente de ticks (números en ejes)

## → Matplotlib (si se usa)
MATPLOT_FONT_FAMILY       = "Arial"
MATPLOT_GRID_COLOR        = "#CCCCCC"
MATPLOT_GRID_STYLE        = "--"
MATPLOT_GRID_ALPHA        = 0.6

# === FIN PARÁMETROS DE ESTILO ===

# === FUNCIONES AUXILIARES ===
def calcular_delta(actual, anterior):
    """Calcula diferencia absoluta y porcentual, y la formatea con color y tamaño de letra."""
    if anterior and abs(anterior) > 1e-9:
        delta = actual - anterior
        pct   = (delta / anterior) * 100
        color = KPI_COLOR_POSITIVE if delta >= 0 else KPI_COLOR_NEGATIVE
        return (
            f"<span style='font-size:{KPI_DELTA_FONT_SIZE}px; color:{color};'>"
            f"{delta:+,.0f} ({pct:+.1f}%)</span>"
        )
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
        df_mayor["AÑO"]  = df_mayor["FECHA"].dt.year
        df_mayor["MES"]  = df_mayor["FECHA"].dt.month
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
    margen  = (utilidad / ingresos) * 100 if ingresos else 0
    return utilidad, margen

# === GRÁFICOS ===
def crear_grafico_tendencias(df_hist, año_actual, mes_actual, kpi):
    meses_str = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    df_mes_actual      = df_hist[df_hist["Año"] == año_actual]
    df_hist_anteriores = df_hist[df_hist["Año"] < año_actual]

    fig = go.Figure()
    # Barras año actual
    fig.add_trace(go.Bar(
        x=meses_str,
        y=[df_mes_actual[df_mes_actual["Mes"] == i][kpi].sum() for i in range(1,13)],
        name=f"{año_actual}",
        marker_color=BAR_COLOR_CURRENT_YEAR
    ))
    # Línea histórico
    años    = sorted(df_hist_anteriores["Año"].unique())
    valores = [df_hist_anteriores[(df_hist_anteriores["Año"] == a) & (df_hist_anteriores["Mes"] == mes_actual)][kpi].sum() for a in años]
    fig.add_trace(go.Scatter(
        x=años,
        y=valores,
        mode='lines+markers',
        name="Histórico",
        line=dict(color=LINE_COLOR_HISTORICO, width=3)
    ))

    fig.update_layout(
        title=f"Tendencias de {kpi}",
        xaxis_title="Mes / Año",
        yaxis_title=f"{kpi} {'(MWh)' if kpi=='Generacion' else ''}",
        barmode='group',
        template="plotly_white",
        height=CHART_HEIGHT,
        legend=dict(
            y=0.99,
            x=0.01,
            font=dict(size=LEGEND_FONT_SIZE)
        ),
        xaxis=dict(
            title_font=dict(size=AXIS_TITLE_FONT_SIZE),
            tickfont=dict(size=AXIS_TICK_FONT_SIZE)
        ),
        yaxis=dict(
            title_font=dict(size=AXIS_TITLE_FONT_SIZE),
            tickfont=dict(size=AXIS_TICK_FONT_SIZE)
        )
    )
    return fig

def grafico_generacion_anual(df_hist):
    df_anual = df_hist.groupby("Año")["Generacion"].sum().reset_index()
    if 2025 not in df_anual["Año"].values:
        df_anual = pd.concat([df_anual, pd.DataFrame({"Año":[2025], "Generacion":[0]})], ignore_index=True)
    df_anual = df_anual.sort_values("Año")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_anual["Año"],
        y=df_anual["Generacion"],
        mode='lines+markers',
        line=dict(color=BAR_COLOR_CURRENT_YEAR, width=3),
        name="Generación Anual (MWh)"
    ))
    fig.update_layout(
        title="Generación Anual de Energía",
        xaxis_title="Año",
        yaxis_title="Generación (MWh)",
        template="plotly_white",
        height=CHART_HEIGHT,
        legend=dict(font=dict(size=LEGEND_FONT_SIZE)),
        xaxis=dict(
            title_font=dict(size=AXIS_TITLE_FONT_SIZE),
            tickfont=dict(size=AXIS_TICK_FONT_SIZE)
        ),
        yaxis=dict(
            title_font=dict(size=AXIS_TITLE_FONT_SIZE),
            tickfont=dict(size=AXIS_TICK_FONT_SIZE)
        )
    )
    return fig

# === RECOMENDACIONES ===
def generar_recomendaciones(analisis):
    recs = []
    margen = analisis['Financiero']['margen_operativo']
    if margen < 15:
        recs.append("🔧 Optimizar costos para mejorar márgenes operativos.")
    elif margen > 30:
        recs.append("📈 Considerar reinversión estratégica en infraestructura.")
    return recs

# === MAIN ===
def main():
    df_pluv, df_hist, df_mayor = cargar_datos(EXCEL_PATH)

    st.sidebar.title("Parámetros del Reporte")
    empresa = st.sidebar.text_input("Nombre de la Empresa", "Hidroeléctrica El Canelo")
    meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    mes = st.sidebar.selectbox("📅 Seleccione Mes", meses, index=4)
    m = meses.index(mes) + 1
    año_actual = 2025

    st.title(f"Reporte Operativo y Financiero - {empresa}")
    st.header(f"Período: {mes} {año_actual}")

    # === KPIs MENSUALES ===
    gen25_mes   = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] == m)]["Generacion"].sum()
    gen24_mes   = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] == m)]["Generacion"].sum()
    genavg_mes  = df_hist[(df_hist["Año"].between(año_actual-5, año_actual-1)) & (df_hist["Mes"] == m)]["Generacion"].mean()
    vent25_mes  = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] == m)]["Ventas"].sum()
    vent24_mes  = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] == m)]["Ventas"].sum()
    ventavg_mes = df_hist[(df_hist["Año"].between(año_actual-5, año_actual-1)) & (df_hist["Mes"] == m)]["Ventas"].mean()
    prec25_mes  = df_pluv[(df_pluv["Año"] == año_actual) & (df_pluv["Mes"] == m)]["Precipitacion"].sum()
    prec24_mes  = df_pluv[(df_pluv["Año"] == año_actual-1) & (df_pluv["Mes"] == m)]["Precipitacion"].sum()
    precavg_mes = df_pluv[(df_pluv["Año"].between(año_actual-5, año_actual-1)) & (df_pluv["Mes"] == m)]["Precipitacion"].mean()

    st.subheader("KPIs Mensuales (solo mes seleccionado)")
    col1, col2, col3 = st.columns(3)
    col1.markdown(
        f"<div>"
        f"<span style='font-size:{KPI_LABEL_FONT_SIZE}px; font-weight:bold;'>Generación</span><br>"
        f"<span style='font-size:{KPI_VALUE_FONT_SIZE}px;'>{format_MWh(gen25_mes)}</span><br>"
        f"Δ vs {año_actual-1}: {calcular_delta(gen25_mes, gen24_mes)}<br>"
        f"Δ vs Prom 5A: {calcular_delta(gen25_mes, genavg_mes)}"
        f"</div>", unsafe_allow_html=True
    )
    col2.markdown(
        f"<div>"
        f"<span style='font-size:{KPI_LABEL_FONT_SIZE}px; font-weight:bold;'>Ventas</span><br>"
        f"<span style='font-size:{KPI_VALUE_FONT_SIZE}px;'>{format_currency(vent25_mes)}</span><br>"
        f"Δ vs {año_actual-1}: {calcular_delta(vent25_mes, vent24_mes)}<br>"
        f"Δ vs Prom 5A: {calcular_delta(vent25_mes, ventavg_mes)}"
        f"</div>", unsafe_allow_html=True
    )
    col3.markdown(
        f"<div>"
        f"<span style='font-size:{KPI_LABEL_FONT_SIZE}px; font-weight:bold;'>Precipitaciones</span><br>"
        f"<span style='font-size:{KPI_VALUE_FONT_SIZE}px;'>{prec25_mes:,.1f} mm</span><br>"
        f"Δ vs {año_actual-1}: {calcular_delta(prec25_mes, prec24_mes)}<br>"
        f"Δ vs Prom 5A: {calcular_delta(prec25_mes, precavg_mes)}"
        f"</div>", unsafe_allow_html=True
    )

    # === Tendencias y anual ===
    st.subheader("Tendencias Operativas")
    st.plotly_chart(crear_grafico_tendencias(df_hist, año_actual, m, "Generacion"), use_container_width=True)
    st.plotly_chart(crear_grafico_tendencias(df_hist, año_actual, m, "Ventas"), use_container_width=True)

    st.subheader("Generación Anual de Energía")
    st.plotly_chart(grafico_generacion_anual(df_hist), use_container_width=True)

    # === Análisis Financiero ===
    st.subheader("Análisis Financiero Detallado")
    estado = procesar_estado_resultado(df_mayor, año_actual, m)
    ingresos = estado[estado["Cuenta"] == "Ingresos"]["HABER"].sum()
    costos   = estado[estado["Cuenta"] == "Costos"]["DEBE"].sum()
    utilidad, margen = calcular_margenes(ingresos, costos)

    display = estado.copy()
    display["DEBE"]  = display["DEBE"].apply(format_currency)
    display["HABER"] = display["HABER"].apply(format_currency)
    display["SALDO"] = display["SALDO"].apply(format_currency)
    st.table(display)

    colf1, colf2, colf3 = st.columns(3)
    colf1.metric("Ingresos Totales", format_currency(ingresos))
    colf2.metric("Costos Totales", format_currency(costos))
    colf3.metric("Utilidad Operativa", format_currency(utilidad), f"{margen:.1f}%")

    # === Recomendaciones ===
    st.subheader("Recomendaciones Estratégicas")
    recs = generar_recomendaciones({'Financiero': {'margen_operativo': margen}})
    if recs:
        for r in recs:
            st.markdown(f"- {r}")
    else:
        st.info("✅ El desempeño operativo y financiero está dentro de parámetros esperados.")

    st.caption(f"Reporte generado el {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')} | © 2025")

if __name__ == "__main__":
    main()
