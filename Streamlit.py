import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import base64

# === CONFIGURACIÓN DE PÁGINA Y ESTILOS ===
st.set_page_config(page_title="Reporte Operativo y Financiero", layout="wide")
PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
KPI_FONT_SIZE = 25
KPI_DELTA_FONT_SIZE = 18
CHART_HEIGHT = 450

EXCEL_PATH = Path("HEC mensuales 2025.xlsx")
GEN_PATH = Path(r"C:\One Drive Hotmail\OneDrive\Documentos\Python VSCode\REPORTE WEB\Generacion Central El Canelo.xlsx")
LOGO_PATH = r"C:\One Drive Hotmail\OneDrive\Documentos\Python VSCode\REPORTE WEB\logo.jpg"

def mostrar_titulo_con_logo(logo_path):
    logo_path_obj = Path(logo_path)
    if logo_path_obj.exists():
        with open(logo_path, "rb") as image_file:
            image_type = "jpeg" if logo_path_obj.suffix.lower() in [".jpg", ".jpeg"] else logo_path_obj.suffix.lower().replace(".", "")
            encoded = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"<div style='display:flex; align-items:center;'>"
            f"<img src='data:image/{image_type};base64,{encoded}' style='height:60px;margin-right:15px;'/>"
            f"<h1 style='display:inline;'>Reporte Operativo y Financiero - Hidroeléctrica El Canelo</h1>"
            f"</div>", unsafe_allow_html=True
        )
    else:
        st.title("Reporte Operativo y Financiero - Hidroeléctrica El Canelo")

@st.cache_data(ttl=3600)
def cargar_datos(path):
    df_pluv = pd.read_excel(path, sheet_name="Pluviometria", skiprows=127, usecols="C:D")
    df_pluv.columns = ["Fecha", "Precipitacion"]
    df_pluv["Fecha"] = pd.to_datetime(df_pluv["Fecha"], errors='coerce')
    df_pluv.dropna(subset=["Fecha", "Precipitacion"], inplace=True)
    df_pluv["Año"] = df_pluv["Fecha"].dt.year
    df_pluv["Mes"] = df_pluv["Fecha"].dt.month

    df_hist = pd.read_excel(path, sheet_name="Datos Historicos", skiprows=195, usecols="C:G")
    df_hist.columns = ["Fecha", "Generacion", "Generacion_Ref", "Potencia", "Ventas"]
    df_hist["Fecha"] = pd.to_datetime(df_hist["Fecha"], errors='coerce')
    df_hist.dropna(subset=["Fecha", "Generacion", "Ventas"], inplace=True)
    df_hist["Año"] = df_hist["Fecha"].dt.year
    df_hist["Mes"] = df_hist["Fecha"].dt.month

    return df_pluv, df_hist

@st.cache_data(ttl=3600)
def cargar_generacion_diaria(path, año, mes):
    df = pd.read_excel(path, sheet_name=0, header=None)
    header_row = None
    for i, row in df.iterrows():
        if ("APORTE.CANELO\nIntervalo de energía activa generada\n(kWh)" in row.values and "Fecha y hora" in row.values):
            header_row = i
            break
    if header_row is None:
        return pd.DataFrame()
    df = pd.read_excel(path, sheet_name=0, header=header_row)
    col_fecha = "Fecha y hora"
    col_gen = "APORTE.CANELO\nIntervalo de energía activa generada\n(kWh)"
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce", dayfirst=True)
    df = df.dropna(subset=[col_fecha, col_gen])
    df = df[(df[col_fecha].dt.year == año) & (df[col_fecha].dt.month == mes)].copy()
    if df.empty:
        return pd.DataFrame()
    df['Dia'] = df[col_fecha].dt.date
    df_dia = df.groupby('Dia')[col_gen].sum().reset_index()
    df_dia['Fecha'] = pd.to_datetime(df_dia['Dia'])
    return df_dia[['Fecha', col_gen]].rename(columns={col_gen: 'AporteCanelo_kWh'})

@st.cache_data(ttl=3600)
def cargar_estado_resultado(path):
    df = pd.read_excel(path, sheet_name="Estado de Resultado", header=None, usecols="A:G", skiprows=5, nrows=39)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    return df

def calcular_delta(actual, anterior):
    if anterior is None or pd.isna(anterior) or abs(anterior) < 1e-9:
        return "N/A"
    delta = actual - anterior
    pct = (delta / anterior) * 100
    color = "green" if delta >= 0 else "red"
    return f"<span style='font-size:{KPI_DELTA_FONT_SIZE}px; color:{color};'>{delta:+,.0f} ({pct:+.1f}%)</span>"

def format_currency(x):
    return f"${x:,.0f}"

def format_MWh(x):
    return f"{x:,.0f} MWh"

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
        legend=dict(font=dict(size=12)),
        margin=dict(t=100),
        xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), fixedrange=True),
        yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), fixedrange=True),
        dragmode=False
    )
    fig.update_traces(hoverinfo="skip", hovertemplate=None)
    fig['layout']['uirevision'] = True
    return fig

def grafico_lineas_tendencia(df, col_fecha, col_valor, año_actual, col_label, meses_labels, nombre, color_actual, color_anterior, color_5a):
    df = df.copy()
    df['Año'] = df[col_fecha].dt.year
    df['Mes'] = df[col_fecha].dt.month
    serie_actual = df[df['Año'] == año_actual].groupby('Mes')[col_valor].sum()
    serie_anterior = df[df['Año'] == año_actual-1].groupby('Mes')[col_valor].sum()
    mask_5a = df['Año'].between(año_actual-5, año_actual-1)
    serie_5a = df[mask_5a].groupby(['Año','Mes'])[col_valor].sum().groupby('Mes').mean()
    serie_actual = [serie_actual.get(i+1, None) for i in range(12)]
    serie_anterior = [serie_anterior.get(i+1, None) for i in range(12)]
    serie_5a = [serie_5a.get(i+1, None) for i in range(12)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=meses_labels, y=serie_actual,
        mode='lines+markers', name=f"{año_actual}", line=dict(color=color_actual, width=3)
    ))
    fig.add_trace(go.Scatter(
        x=meses_labels, y=serie_anterior,
        mode='lines+markers', name=f"{año_actual-1}", line=dict(color=color_anterior, width=2, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=meses_labels, y=serie_5a,
        mode='lines+markers', name="Promedio 5A", line=dict(color=color_5a, width=2, dash='dash')
    ))
    fig.update_layout(
        title=nombre,
        xaxis_title="Mes",
        yaxis_title=col_label,
        template='plotly_white',
        height=CHART_HEIGHT,
        legend=dict(font=dict(size=12)),
        xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), fixedrange=True),
        yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), fixedrange=True),
        dragmode=False
    )
    fig.update_traces(hoverinfo="skip", hovertemplate=None)
    fig['layout']['uirevision'] = True
    return fig

def tabla_estado_resultado_operativa(df):
    palabras_operativas = [
        "Transferencias de Energía", "Transferencias de Potencia", "Servicios de Administrativos",
        "Peajes", "Costos por Energía", "Balance de Potencial", "Transferencia de Energía",
        "Petroleo", "Bencina", "Pasajes", "Electricidad", "Agua", "Gas", "Telefono", "Computacion",
        "Aseo", "Mantenimiento", "Revisión", "Depreciación", "Equipos Hidroelectrica", "Seguros",
        "Rutinaria", "Vehiculos", "Oficina"
    ]
    summary_rubros = ["GANANCIA", "PERDIDA", "TOTAL GENERAL"]
    desc_col = df.columns[0]
    keep_rows_idx = []
    for idx, row in df.iterrows():
        rubro_desc = str(row[desc_col]).strip()
        is_summary = any(s_rubro.lower() in rubro_desc.lower() for s_rubro in summary_rubros)
        is_operative = any(p_key.lower() in rubro_desc.lower() for p_key in palabras_operativas)
        is_heading_or_subtotal = rubro_desc.isupper() and not any(char.isdigit() for char in rubro_desc) and len(rubro_desc) > 3
        if is_summary or is_operative or is_heading_or_subtotal:
            keep_rows_idx.append(idx)
    df_final = df.loc[keep_rows_idx].copy()
    return df_final

def main():
    meses_labels = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    meses_str_for_chart = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

    mostrar_titulo_con_logo(LOGO_PATH)
    mes_idx = st.sidebar.selectbox("Selecciona el mes", list(enumerate(meses_labels)), index=5, format_func=lambda x: x[1])[0]
    mes_nombre = meses_labels[mes_idx]
    año_actual = 2025
    mes_num = mes_idx + 1

    st.header(f"Período: {mes_nombre} {año_actual}")

    df_pluv, df_hist = cargar_datos(EXCEL_PATH)

    # KPIs
    gen25_mes = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] == mes_num)]["Generacion"].sum()
    gen24_mes = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] == mes_num)]["Generacion"].sum()
    genavg_mes = df_hist[(df_hist["Año"].between(año_actual-5, año_actual-1)) & (df_hist["Mes"] == mes_num)]["Generacion"].mean()
    vent25_mes = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] == mes_num)]["Ventas"].sum()
    vent24_mes = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] == mes_num)]["Ventas"].sum()
    ventavg_mes = df_hist[(df_hist["Año"].between(año_actual-5, año_actual-1)) & (df_hist["Mes"] == mes_num)]["Ventas"].mean()
    prec25_mes = df_pluv[(df_pluv["Año"] == año_actual) & (df_pluv["Mes"] == mes_num)]["Precipitacion"].sum()
    prec24_mes = df_pluv[(df_pluv["Año"] == año_actual-1) & (df_pluv["Mes"] == mes_num)]["Precipitacion"].sum()
    precavg_mes = df_pluv[(df_pluv["Año"].between(año_actual-5, año_actual-1)) & (df_pluv["Mes"] == mes_num)]["Precipitacion"].mean()

    gen25_acum = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] <= mes_num)]["Generacion"].sum()
    gen24_acum = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] <= mes_num)]["Generacion"].sum()
    genavg_acum = df_hist[df_hist["Año"].between(año_actual-5, año_actual-1)].groupby("Año").apply(lambda x: x[x["Mes"] <= mes_num]["Generacion"].sum()).mean()
    vent25_acum = df_hist[(df_hist["Año"] == año_actual) & (df_hist["Mes"] <= mes_num)]["Ventas"].sum()
    vent24_acum = df_hist[(df_hist["Año"] == año_actual-1) & (df_hist["Mes"] <= mes_num)]["Ventas"].sum()
    ventavg_acum = df_hist[df_hist["Año"].between(año_actual-5, año_actual-1)].groupby("Año").apply(lambda x: x[x["Mes"] <= mes_num]["Ventas"].sum()).mean()
    prec25_acum = df_pluv[(df_pluv["Año"] == año_actual) & (df_pluv["Mes"] <= mes_num)]["Precipitacion"].sum()
    prec24_acum = df_pluv[(df_pluv["Año"] == año_actual-1) & (df_pluv["Mes"] <= mes_num)]["Precipitacion"].sum()
    precavg_acum = df_pluv[df_pluv["Año"].between(año_actual-5, año_actual-1)].groupby("Año").apply(lambda x: x[x["Mes"] <= mes_num]["Precipitacion"].sum()).mean()

    st.subheader("KPIs Mensuales (solo mes seleccionado)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='font-size:{KPI_FONT_SIZE}px;'><b>Generación</b><br>{format_MWh(gen25_mes)}</div>", unsafe_allow_html=True)
        st.markdown(f"Δ vs {año_actual-1}: {calcular_delta(gen25_mes, gen24_mes)}", unsafe_allow_html=True)
        st.markdown(f"Δ vs Promedio 5A: {calcular_delta(gen25_mes, genavg_mes)}", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='font-size:{KPI_FONT_SIZE}px;'><b>Ventas</b><br>{format_currency(vent25_mes)}</div>", unsafe_allow_html=True)
        st.markdown(f"Δ vs {año_actual-1}: {calcular_delta(vent25_mes, vent24_mes)}", unsafe_allow_html=True)
        st.markdown(f"Δ vs Promedio 5A: {calcular_delta(vent25_mes, ventavg_mes)}", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='font-size:{KPI_FONT_SIZE}px;'><b>Precipitaciones</b><br>{prec25_mes:,.1f} mm</div>", unsafe_allow_html=True)
        st.markdown(f"Δ vs {año_actual-1}: {calcular_delta(prec25_mes, prec24_mes)}", unsafe_allow_html=True)
        st.markdown(f"Δ vs Promedio 5A: {calcular_delta(prec25_mes, precavg_mes)}", unsafe_allow_html=True)

    st.subheader("KPIs Acumulados (enero a mes seleccionado)")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(f"<div style='font-size:{KPI_FONT_SIZE}px;'><b>Generación Acum.</b><br>{format_MWh(gen25_acum)}</div>", unsafe_allow_html=True)
        st.markdown(f"Δ vs {año_actual-1}: {calcular_delta(gen25_acum, gen24_acum)}", unsafe_allow_html=True)
        st.markdown(f"Δ vs Promedio 5A: {calcular_delta(gen25_acum, genavg_acum)}", unsafe_allow_html=True)
    with col5:
        st.markdown(f"<div style='font-size:{KPI_FONT_SIZE}px;'><b>Ventas Acum.</b><br>{format_currency(vent25_acum)}</div>", unsafe_allow_html=True)
        st.markdown(f"Δ vs {año_actual-1}: {calcular_delta(vent25_acum, vent24_acum)}", unsafe_allow_html=True)
        st.markdown(f"Δ vs Promedio 5A: {calcular_delta(vent25_acum, ventavg_acum)}", unsafe_allow_html=True)
    with col6:
        st.markdown(f"<div style='font-size:{KPI_FONT_SIZE}px;'><b>Precipitaciones Acum.</b><br>{prec25_acum:,.1f} mm</div>", unsafe_allow_html=True)
        st.markdown(f"Δ vs {año_actual-1}: {calcular_delta(prec25_acum, prec24_acum)}", unsafe_allow_html=True)
        st.markdown(f"Δ vs Promedio 5A: {calcular_delta(prec25_acum, precavg_acum)}", unsafe_allow_html=True)

    # Gráfico de generación diaria
    df_dia = cargar_generacion_diaria(GEN_PATH, año_actual, mes_num)
    if not df_dia.empty:
        st.plotly_chart(grafico_generacion_diaria(df_dia, mes_nombre, año_actual), use_container_width=True)
    else:
        st.info(f"No hay datos diarios disponibles para {mes_nombre}.")

    # Gráficos de tendencias
    st.subheader("Tendencias Mensuales: Actual, Año Anterior y Promedio 5A")
    st.plotly_chart(
        grafico_lineas_tendencia(
            df_hist, col_fecha="Fecha", col_valor="Generacion", año_actual=año_actual,
            col_label="Generación (MWh)", meses_labels=meses_str_for_chart,
            nombre="Generación Mensual",
            color_actual=PALETTE[0], color_anterior=PALETTE[1], color_5a=PALETTE[2]
        ), use_container_width=True
    )
    st.plotly_chart(
        grafico_lineas_tendencia(
            df_hist, col_fecha="Fecha", col_valor="Ventas", año_actual=año_actual,
            col_label="Ventas ($)", meses_labels=meses_str_for_chart,
            nombre="Ventas Mensuales",
            color_actual=PALETTE[0], color_anterior=PALETTE[1], color_5a=PALETTE[2]
        ), use_container_width=True
    )
    st.plotly_chart(
        grafico_lineas_tendencia(
            df_pluv, col_fecha="Fecha", col_valor="Precipitacion", año_actual=año_actual,
            col_label="Precipitación (mm)", meses_labels=meses_str_for_chart,
            nombre="Precipitaciones Mensuales",
            color_actual=PALETTE[0], color_anterior=PALETTE[1], color_5a=PALETTE[2]
        ), use_container_width=True
    )

    # Estado de Resultado Operativo
    df_estado = cargar_estado_resultado(EXCEL_PATH)
    if not df_estado.empty:
        st.subheader("Estado de Resultado Operativo Perido 2025)")
        df_estado_op = tabla_estado_resultado_operativa(df_estado)
        st.dataframe(df_estado_op, use_container_width=True)
    else:
        st.info("No hay datos de Estado de Resultado para mostrar.")

    # Análisis textual
    st.subheader("Análisis de Partidas Operativas del Estado de Resultado")
    st.markdown("""
**Ingresos Operativos:**  
- Los ingresos provienen principalmente de transferencias de energía y potencia.

**Costos y Gastos Operativos:**  
- Los principales egresos corresponden a servicios administrativos y operacionales, peajes de subtransmisión, costos por energía, balance de potencial, combustibles, servicios básicos, telecomunicaciones, artículos y servicios de computación, seguros, y gastos de mantenimiento y depreciaciones.

**Resultado Operativo:**  
- 
""")

    st.caption(f"Reporte generado el {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')} | Derechos reservados © 2025")

if __name__ == "__main__":
    main()

