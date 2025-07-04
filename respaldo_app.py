import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from cycler import cycler
import base64

# === CONFIGURACIÓN DE PÁGINA Y ESTILOS ===
st.set_page_config(page_title="Reporte Operativo y Financiero", layout="wide")
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
KPI_FONT_SIZE = 25
KPI_DELTA_FONT_SIZE = 18
KPI_COLOR_POSITIVE = PALETTE[2]
KPI_COLOR_NEGATIVE = PALETTE[3]
CHART_HEIGHT = 450
BAR_COLOR_CURRENT_YEAR = PALETTE[0]
LINE_COLOR_HISTORICO = PALETTE[1]
LEGEND_FONT_SIZE = 12
AXIS_TITLE_FONT_SIZE = 14
AXIS_TICK_FONT_SIZE = 12

# === ARCHIVOS ===
EXCEL_PATH = Path("HEC mensuales 2025.xlsx")
RUTA_LOCAL_APORTE = r"C:\One Drive Hotmail\OneDrive\Documentos\Python VSCode\REPORTE WEB\Generacion Central El Canelo.xlsx"
LOGO_PATH = "logo_empresa.png"  # Coloca el logo en el mismo directorio del script

if not Path(RUTA_LOCAL_APORTE).exists():
    st.error(f"No se encontró el archivo local de Generación Central El Canelo en: {RUTA_LOCAL_APORTE}")
    st.stop()
EXCEL_APORTE_PATH = RUTA_LOCAL_APORTE
if not EXCEL_PATH.exists():
    st.error(f"Archivo no encontrado: {EXCEL_PATH}.")
    st.stop()

# === FUNCIONES DE CARGA Y PROCESAMIENTO ===
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

@st.cache_data(ttl=3600)
def cargar_generacion_diaria(path, año, mes):
    df = pd.read_excel(path, sheet_name=0, header=None)
    header_row = None
    for i, row in df.iterrows():
        if (
            "APORTE.CANELO\nIntervalo de energía activa generada\n(kWh)" in row.values
            and "Fecha y hora" in row.values
        ):
            header_row = i
            break
    if header_row is None:
        return None
    df = pd.read_excel(path, sheet_name=0, header=header_row)
    col_fecha = "Fecha y hora"
    col_gen = "APORTE.CANELO\nIntervalo de energía activa generada\n(kWh)"
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce", dayfirst=True)
    df = df.dropna(subset=[col_fecha, col_gen])
    df = df[(df[col_fecha].dt.year == año) & (df[col_fecha].dt.month == mes)].copy()
    df['Dia'] = df[col_fecha].dt.date
    df_dia = df.groupby('Dia')[col_gen].sum().reset_index()
    df_dia['Fecha'] = pd.to_datetime(df_dia['Dia'])
    return df_dia[['Fecha', col_gen]].rename(columns={col_gen: 'AporteCanelo_kWh'})

@st.cache_data(ttl=3600)
def cargar_estado_resultado(path):
    try:
        df = pd.read_excel(path, sheet_name="Estado de Resultado", header=0)
    except ValueError:
        st.warning("No se encontró la hoja 'Estado de Resultado' en el archivo.")
        return pd.DataFrame()
    return df

def calcular_delta(actual, anterior):
    if anterior and abs(anterior) > 1e-9:
        delta = actual - anterior
        pct = (delta / anterior) * 100
        color = KPI_COLOR_POSITIVE if delta >= 0 else KPI_COLOR_NEGATIVE
        return (
            f"<span style='font-size:{KPI_DELTA_FONT_SIZE}px; "
            f"color:{color};'>{delta:+,.0f} ({pct:+.1f}%)</span>"
        )
    return "N/A"

def format_currency(x):
    return f"${x:,.0f}"

def format_MWh(x):
    return f"{x:,.0f} MWh"

def mostrar_titulo_con_logo(logo_path):
    if logo_path and Path(logo_path).exists():
        with open(logo_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"<div style='display:flex; align-items:center;'>"
            f"<img src='data:image/png;base64,{encoded}' style='height:60px;margin-right:15px;'/>"
            f"<h1 style='display:inline;'>Reporte Operativo y Financiero - Hidroeléctrica El Canelo</h1>"
            f"</div>", unsafe_allow_html=True
        )
    else:
        st.title("Reporte Operativo y Financiero - Hidroeléctrica El Canelo")

def grafico_generacion_diaria(df_dia, mes_nombre, año):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_dia['Fecha'],
        y=df_dia['AporteCanelo_kWh'],
        mode='lines+markers',
        name='Energía diaria',
        line=dict(color=PALETTE[1], width=3)
    ))
    title = f"<b>Generación Diaria - Central El Canelo ({mes_nombre} {año})</b>"
    fig.update_layout(
        title=title,
        xaxis_title="Fecha",
        yaxis_title="Energía generada (kWh)",
        template='plotly_white',
        height=CHART_HEIGHT,
        legend=dict(font=dict(size=LEGEND_FONT_SIZE)),
        margin=dict(t=100),
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

def grafico_lineas_tendencia(df, col_fecha, col_valor, año_actual, col_label, meses, nombre, color_actual, color_anterior, color_5a):
    df = df.copy()
    df['Año'] = df[col_fecha].dt.year
    df['Mes'] = df[col_fecha].dt.month
    # Serie actual
    serie_actual = df[df['Año'] == año_actual].groupby('Mes')[col_valor].sum()
    # Serie año anterior
    serie_anterior = df[df['Año'] == año_actual-1].groupby('Mes')[col_valor].sum()
    # Serie promedio 5A
    mask_5a = df['Año'].between(año_actual-5, año_actual-1)
    serie_5a = df[mask_5a].groupby(['Año','Mes'])[col_valor].sum().groupby('Mes').mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=meses, y=[serie_actual.get(i+1, 0) for i in range(12)],
        mode='lines+markers', name=f"{año_actual}", line=dict(color=color_actual, width=3)
    ))
    fig.add_trace(go.Scatter(
        x=meses, y=[serie_anterior.get(i+1, 0) for i in range(12)],
        mode='lines+markers', name=f"{año_actual-1}", line=dict(color=color_anterior, width=2, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=meses, y=[serie_5a.get(i+1, 0) for i in range(12)],
        mode='lines+markers', name="Promedio 5A", line=dict(color=color_5a, width=2, dash='dash')
    ))
    fig.update_layout(
        title=nombre,
        xaxis_title="Mes",
        yaxis_title=col_label,
        template='plotly_white',
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

def tabla_estado_resultado_relevante(df):
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre", "Total general"]
    df = df[df.iloc[:, 0].notna()]
    cols = [df.columns[0]] + [c for c in df.columns if any(m in c.lower() for m in meses)]
    df = df[cols]
    meses_cols = [c for c in df.columns if c != df.columns[0]]
    df = df[df[meses_cols].notna().any(axis=1)]
    return df

def main():
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    mostrar_titulo_con_logo(LOGO_PATH)
    mes_idx = st.sidebar.selectbox("Selecciona el mes", list(enumerate(meses)), index=5, format_func=lambda x: x[1])[0]
    mes_nombre = meses[mes_idx]
    año_actual = 2025
    m = mes_idx + 1

    st.header(f"Período: {mes_nombre} {año_actual}")

    # KPIs primero
    df_pluv, df_hist, df_mayor = cargar_datos(EXCEL_PATH)
    gen25_mes = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] == m)]["Generacion"].sum()
    gen24_mes = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] == m)]["Generacion"].sum()
    genavg_mes = df_hist[(df_hist["Año"].between(año_actual-5, año_actual-1)) & (df_hist["Mes"] == m)]["Generacion"].mean()
    vent25_mes = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] == m)]["Ventas"].sum()
    vent24_mes = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] == m)]["Ventas"].sum()
    ventavg_mes = df_hist[(df_hist["Año"].between(año_actual-5, año_actual-1)) & (df_hist["Mes"] == m)]["Ventas"].mean()
    prec25_mes = df_pluv[(df_pluv["Año"] == año_actual) & (df_pluv["Mes"] == m)]["Precipitacion"].sum()
    prec24_mes = df_pluv[(df_pluv["Año"] == año_actual-1) & (df_pluv["Mes"] == m)]["Precipitacion"].sum()
    precavg_mes = df_pluv[(df_pluv["Año"].between(año_actual-5, año_actual-1)) & (df_pluv["Mes"] == m)]["Precipitacion"].mean()

    gen25_acum = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] <= m)]["Generacion"].sum()
    gen24_acum = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] <= m)]["Generacion"].sum()
    genavg_acum = df_hist[df_hist["Año"].between(año_actual-5, año_actual-1)].groupby("Año").apply(lambda x: x[x["Mes"] <= m]["Generacion"].sum()).mean()
    vent25_acum = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] <= m)]["Ventas"].sum()
    vent24_acum = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] <= m)]["Ventas"].sum()
    ventavg_acum = df_hist[df_hist["Año"].between(año_actual-5, año_actual-1)].groupby("Año").apply(lambda x: x[x["Mes"] <= m]["Ventas"].sum()).mean()
    prec25_acum = df_pluv[(df_pluv["Año"] == año_actual) & (df_pluv["Mes"] <= m)]["Precipitacion"].sum()
    prec24_acum = df_pluv[(df_pluv["Año"] == año_actual-1) & (df_pluv["Mes"] <= m)]["Precipitacion"].sum()
    precavg_acum = df_pluv[df_pluv["Año"].between(año_actual-5, año_actual-1)].groupby("Año").apply(lambda x: x[x["Mes"] <= m]["Precipitacion"].sum()).mean()

    st.subheader("KPIs Mensuales (solo mes seleccionado)")
    col1, col2, col3 = st.columns(3)
    col1.markdown(
        f"<div style='font-size:{KPI_FONT_SIZE}px;'>"
        f"**Generación**<br>{format_MWh(gen25_mes)}<br>"
        f"Δ vs {año_actual-1}: {calcular_delta(gen25_mes, gen24_mes)}<br>"
        f"Δ vs Promedio 5A: {calcular_delta(gen25_mes, genavg_mes)}"
        f"</div>", unsafe_allow_html=True
    )
    col2.markdown(
        f"<div style='font-size:{KPI_FONT_SIZE}px;'>"
        f"**Ventas**<br>{format_currency(vent25_mes)}<br>"
        f"Δ vs {año_actual-1}: {calcular_delta(vent25_mes, vent24_mes)}<br>"
        f"Δ vs Promedio 5A: {calcular_delta(vent25_mes, ventavg_mes)}"
        f"</div>", unsafe_allow_html=True
    )
    col3.markdown(
        f"<div style='font-size:{KPI_FONT_SIZE}px;'>"
        f"**Precipitaciones**<br>{prec25_mes:,.1f} mm<br>"
        f"Δ vs {año_actual-1}: {calcular_delta(prec25_mes, prec24_mes)}<br>"
        f"Δ vs Promedio 5A: {calcular_delta(prec25_mes, precavg_mes)}"
        f"</div>", unsafe_allow_html=True
    )

    st.subheader("KPIs Acumulados (enero a mes seleccionado)")
    col4, col5, col6 = st.columns(3)
    col4.markdown(
        f"<div style='font-size:{KPI_FONT_SIZE}px;'>"
        f"**Generación Acum.**<br>{format_MWh(gen25_acum)}<br>"
        f"Δ vs {año_actual-1}: {calcular_delta(gen25_acum, gen24_acum)}<br>"
        f"Δ vs Promedio 5A: {calcular_delta(gen25_acum, genavg_acum)}"
        f"</div>", unsafe_allow_html=True
    )
    col5.markdown(
        f"<div style='font-size:{KPI_FONT_SIZE}px;'>"
        f"**Ventas Acum.**<br>{format_currency(vent25_acum)}<br>"
        f"Δ vs {año_actual-1}: {calcular_delta(vent25_acum, vent24_acum)}<br>"
        f"Δ vs Promedio 5A: {calcular_delta(vent25_acum, ventavg_acum)}"
        f"</div>", unsafe_allow_html=True
    )
    col6.markdown(
        f"<div style='font-size:{KPI_FONT_SIZE}px;'>"
        f"**Precipitaciones Acum.**<br>{prec25_acum:,.1f} mm<br>"
        f"Δ vs {año_actual-1}: {calcular_delta(prec25_acum, prec24_acum)}<br>"
        f"Δ vs Promedio 5A: {calcular_delta(prec25_acum, precavg_acum)}"
        f"</div>", unsafe_allow_html=True
    )

    # Gráfico de generación diaria (después de KPIs)
    df_dia = cargar_generacion_diaria(EXCEL_APORTE_PATH, año_actual, m)
    if df_dia is not None and not df_dia.empty:
        st.plotly_chart(grafico_generacion_diaria(df_dia, mes_nombre, año_actual), use_container_width=True)
    else:
        st.info("No hay datos diarios disponibles para el mes seleccionado.")

    # Gráficos de tendencias de generación, ventas y precipitaciones
    st.subheader("Tendencias de Generación")
    st.plotly_chart(
        grafico_lineas_tendencia(
            df_hist, col_fecha="Fecha", col_valor="Generacion", año_actual=año_actual,
            col_label="Generación (MWh)", meses=meses,
            nombre="Generación Mensual: Actual, Año Anterior y Promedio 5A",
            color_actual=PALETTE[0], color_anterior=PALETTE[1], color_5a=PALETTE[2]
        ),
        use_container_width=True
    )
    st.subheader("Tendencias de Ventas")
    st.plotly_chart(
        grafico_lineas_tendencia(
            df_hist, col_fecha="Fecha", col_valor="Ventas", año_actual=año_actual,
            col_label="Ventas ($)", meses=meses,
            nombre="Ventas Mensuales: Actual, Año Anterior y Promedio 5A",
            color_actual=PALETTE[0], color_anterior=PALETTE[1], color_5a=PALETTE[2]
        ),
        use_container_width=True
    )
    st.subheader("Tendencias de Precipitaciones")
    st.plotly_chart(
        grafico_lineas_tendencia(
            df_pluv, col_fecha="Fecha", col_valor="Precipitacion", año_actual=año_actual,
            col_label="Precipitación (mm)", meses=meses,
            nombre="Precipitaciones Mensuales: Actual, Año Anterior y Promedio 5A",
            color_actual=PALETTE[0], color_anterior=PALETTE[1], color_5a=PALETTE[2]
        ),
        use_container_width=True
    )

    # Estado de Resultado tabulado y limpio
    df_estado = cargar_estado_resultado(EXCEL_PATH)
    if not df_estado.empty:
        st.subheader("Estado de Resultado (Rubros Relevantes)")
        df_estado_limpia = tabla_estado_resultado_relevante(df_estado)
        st.dataframe(df_estado_limpia, use_container_width=True)
    else:
        st.info("No hay datos de Estado de Resultado para mostrar.")

    st.caption(f"Reporte generado el {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')} | Derechos reservados © 2025")

if __name__ == "__main__":
    main()
