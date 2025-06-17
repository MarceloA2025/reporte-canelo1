import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# === CONFIGURACIÓN INICIAL ===
st.set_page_config(
    page_title="Reporte Mensual", 
    layout="wide",
    page_icon="📊"
)

# === FUNCIÓN PARA CALCULAR DELTAS ===
def calcular_delta(valor_2025, valor_2024, unidad):
    if valor_2024 == 0:
        delta_abs = valor_2025
        delta_pct = 0.0
    else:
        delta_abs = valor_2025 - valor_2024
        delta_pct = (delta_abs / valor_2024) * 100
    color = "green" if delta_abs >= 0 else "red"
    return f"<span style='color:{color}; font-size:32px;'>{delta_abs:+,.0f} {unidad} ({delta_pct:+.1f}%)</span> vs 2024"

# === INTERFAZ DE USUARIO ===
st.markdown("<h2 style='text-align:center; font-family:Arial; color:#333333;'>📅 Seleccione el Mes</h2>", unsafe_allow_html=True)

meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

mes_seleccionado = st.selectbox(
    "", 
    list(meses.keys()), 
    index=3,  # Abril por defecto
    label_visibility="collapsed"
)
mes_num = meses[mes_seleccionado]

# === ENCABEZADO ===
col_logo, col_title = st.columns([1, 9])

with col_logo:
    logo_path = Path("logo.jpg")
    if logo_path.exists():
        st.image(str(logo_path), width=180)
    else:
        st.warning("Logo no encontrado")

with col_title:
    st.markdown(
        f"<h1 style='font-size: 48px; margin-bottom: 0; font-family:Arial; color:#2c3e50;'>"
        f"Reporte Mensual {mes_seleccionado} 2025</h1>",
        unsafe_allow_html=True
    )

# === CARGA DE DATOS ===
try:
    archivo_excel = Path("HEC mensuales 2025.xlsx")
    if not archivo_excel.exists():
        st.error(f"Archivo no encontrado en: {archivo_excel.absolute()}")
        st.stop()

    df_pluv_raw = pd.read_excel(
        archivo_excel, 
        sheet_name="Pluviometria", 
        skiprows=127, 
        usecols="C:D",
        parse_dates=["Fecha"]
    )
    df_pluv_raw.columns = ["Fecha", "Precipitacion"]
    df_pluv_raw["Año"] = df_pluv_raw["Fecha"].dt.year
    df_pluv_raw["Mes"] = df_pluv_raw["Fecha"].dt.month

    df_hist_raw = pd.read_excel(
        archivo_excel, 
        sheet_name="Datos Historicos", 
        skiprows=195, 
        usecols="C:G",
        parse_dates=["Fecha"]
    )
    df_hist_raw.columns = [
        "Fecha", 
        "Generación Bornes (kWh)", 
        "Generacion Ref (kWh)", 
        "Potencia Media (MW)", 
        "Facturacion (USD$)"
    ]
    df_hist_raw = df_hist_raw.dropna(subset=["Fecha"])
    df_hist_raw["Año"] = df_hist_raw["Fecha"].dt.year
    df_hist_raw["Mes"] = df_hist_raw["Fecha"].dt.month
    st.session_state.datos_cargados = True
except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    st.session_state.datos_cargados = False
    st.stop()

# === PROCESAMIENTO DE DATOS ===
# Filtrado por años
# Usar los mismos DataFrames para KPIs y gráficos
mask_2025 = (df_pluv_raw["Año"] == 2025)
mask_2024 = (df_pluv_raw["Año"] == 2024)
mask_5y = df_pluv_raw["Año"].between(2020, 2024)

# Precipitaciones
pluv_2025 = df_pluv_raw[mask_2025]
pluv_2024 = df_pluv_raw[mask_2024]
pluv_5y = df_pluv_raw[mask_5y]
pluv_5y_avg = pluv_5y.groupby("Mes")["Precipitacion"].mean().reindex(range(1,13), fill_value=0)

# Generación y ventas
maskh_2025 = (df_hist_raw["Año"] == 2025)
maskh_2024 = (df_hist_raw["Año"] == 2024)
maskh_5y = df_hist_raw["Año"].between(2020, 2024)

dfh_2025 = df_hist_raw[maskh_2025]
dfh_2024 = df_hist_raw[maskh_2024]
dfh_5y = df_hist_raw[maskh_5y]

# === FUNCIONES PARA OBTENER VALORES ===
def get_monthly(df, col, month):
    return df[df["Mes"] == month][col].sum()

def get_accumulated(df, col, month):
    return df[df["Mes"] <= month][col].sum()

# === KPIs Y DATOS PARA GRÁFICOS (2025) ===
# Precipitaciones
prec_2025_mes = get_monthly(pluv_2025, "Precipitacion", mes_num)
prec_2024_mes = get_monthly(pluv_2024, "Precipitacion", mes_num)
prec_5y_mes = pluv_5y_avg.loc[mes_num] if mes_num in pluv_5y_avg.index else 0
prec_2025_acum = get_accumulated(pluv_2025, "Precipitacion", mes_num)
prec_2024_acum = get_accumulated(pluv_2024, "Precipitacion", mes_num)

# Generación
gen_2025_mes = get_monthly(dfh_2025, "Generación Bornes (kWh)", mes_num)
gen_2024_mes = get_monthly(dfh_2024, "Generación Bornes (kWh)", mes_num)
gen_2025_acum = get_accumulated(dfh_2025, "Generación Bornes (kWh)", mes_num)
gen_2024_acum = get_accumulated(dfh_2024, "Generación Bornes (kWh)", mes_num)

# Ventas
venta_2025_mes = get_monthly(dfh_2025, "Facturacion (USD$)", mes_num)
venta_2024_mes = get_monthly(dfh_2024, "Facturacion (USD$)", mes_num)
venta_2025_acum = get_accumulated(dfh_2025, "Facturacion (USD$)", mes_num)
venta_2024_acum = get_accumulated(dfh_2024, "Facturacion (USD$)", mes_num)

# === VISUALIZACIÓN DE KPIs ===
st.markdown(f"## 📊 Indicadores de {mes_seleccionado}")

def display_metric(col, title, value_2025, value_2024, unit):
    col.markdown(
        f"<div style='font-size:24px; margin-bottom:8px; font-weight:bold;'>{title}</div>",
        unsafe_allow_html=True
    )
    col.markdown(
        f"<div style='font-size:42px; font-weight:bold; margin-bottom:8px;'>{value_2025:,.1f} {unit}</div>",
        unsafe_allow_html=True
    )
    col.markdown(calcular_delta(value_2025, value_2024, unit), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
display_metric(col1, "Precipitaciones Mensuales 2025", prec_2025_mes, prec_2024_mes, "mm")
display_metric(col2, "Generación Mensual 2025", gen_2025_mes, gen_2024_mes, "kWh")
display_metric(col3, "Ventas Mensuales 2025", venta_2025_mes, venta_2024_mes, "USD")

col4, col5, col6 = st.columns(3)
display_metric(col4, "Precipitaciones Acumuladas 2025", prec_2025_acum, prec_2024_acum, "mm")
display_metric(col5, "Generación Acumulada 2025", gen_2025_acum, gen_2024_acum, "kWh")
display_metric(col6, "Ventas Acumuladas 2025", venta_2025_acum, venta_2024_acum, "USD")

# === GRÁFICOS ===
plt.style.use('seaborn-v0_8')
mes_labels = list(meses.keys())

# Precipitaciones mensuales (barras)
st.markdown("### 🌧️ Comparación Mensual de Precipitaciones")
fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
labels = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025_mes, prec_2024_mes, prec_5y_mes]
colores = ["#3498db", "#e74c3c", "#2ecc71"]
bars = ax_bar.bar(labels, valores, color=colores, width=0.6)
for bar, valor in zip(bars, valores):
    ax_bar.text(
        bar.get_x() + bar.get_width()/2, 
        valor, 
        f"{valor:.1f}", 
        ha='center', 
        va='bottom', 
        fontweight='bold',
        fontsize=12
    )
ax_bar.set_ylabel("mm", fontsize=12)
ax_bar.set_ylim(0, max(valores)*1.2)
ax_bar.grid(axis="y", linestyle="--", alpha=0.3)
plt.tight_layout()
st.pyplot(fig_bar)

# Precipitaciones anuales (línea)
st.markdown("### 📈 Precipitaciones Anuales")
prec_serie_2025 = pluv_2025.groupby("Mes")["Precipitacion"].sum().reindex(range(1,13), fill_value=0)
prec_serie_2024 = pluv_2024.groupby("Mes")["Precipitacion"].sum().reindex(range(1,13), fill_value=0)
prec_serie_5y = pluv_5y.groupby("Mes")["Precipitacion"].mean().reindex(range(1,13), fill_value=0)
fig_line, ax_line = plt.subplots(figsize=(10, 4))
ax_line.plot(mes_labels, prec_serie_2025, label="2025", marker="o", linewidth=2.5, color="#3498db")
ax_line.plot(mes_labels, prec_serie_2024, label="2024", marker="o", linewidth=2.5, color="#e74c3c")
ax_line.plot(mes_labels, prec_serie_5y, label="Prom. 2020-2024", linestyle="--", marker="o", linewidth=2, color="#2ecc71")
ax_line.set_title("Precipitaciones por Mes", fontsize=16, pad=20, fontweight='bold')
ax_line.set_ylabel("mm", fontsize=12)
ax_line.legend(frameon=True, facecolor='white', fontsize=10)
ax_line.grid(True, linestyle='--', alpha=0.4, axis='y')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
st.pyplot(fig_line)

# Generación mensual (línea)
st.markdown("### 🔌 Energía Generada Mensual")
gen_serie_2025 = dfh_2025.groupby("Mes")["Generación Bornes (kWh)"].sum().reindex(range(1,13), fill_value=0)
gen_serie_2024 = dfh_2024.groupby("Mes")["Generación Bornes (kWh)"].sum().reindex(range(1,13), fill_value=0)
gen_serie_5y = dfh_5y.groupby("Mes")["Generación Bornes (kWh)"].mean().reindex(range(1,13), fill_value=0)
fig_gen, ax_gen = plt.subplots(figsize=(10, 4))
ax_gen.plot(mes_labels, gen_serie_2025, label="2025", marker="o", linewidth=2.5, color="#3498db")
ax_gen.plot(mes_labels, gen_serie_2024, label="2024", marker="o", linewidth=2.5, color="#e74c3c")
ax_gen.plot(mes_labels, gen_serie_5y, label="Prom. 2020-2024", linestyle="--", marker="o", linewidth=2, color="#2ecc71")
ax_gen.set_title("Energía Generada por Mes", fontsize=16, pad=20, fontweight='bold')
ax_gen.set_ylabel("kWh", fontsize=12)
ax_gen.legend(frameon=True, facecolor='white', fontsize=10)
ax_gen.grid(True, linestyle='--', alpha=0.4, axis='y')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
st.pyplot(fig_gen)

# Ventas mensuales (línea)
st.markdown("### 💰 Ventas Mensuales")
venta_serie_2025 = dfh_2025.groupby("Mes")["Facturacion (USD$)"].sum().reindex(range(1,13), fill_value=0)
venta_serie_2024 = dfh_2024.groupby("Mes")["Facturacion (USD$)"].sum().reindex(range(1,13), fill_value=0)
venta_serie_5y = dfh_5y.groupby("Mes")["Facturacion (USD$)"].mean().reindex(range(1,13), fill_value=0)
fig_venta, ax_venta = plt.subplots(figsize=(10, 4))
ax_venta.plot(mes_labels, venta_serie_2025, label="2025", marker="o", linewidth=2.5, color="#3498db")
ax_venta.plot(mes_labels, venta_serie_2024, label="2024", marker="o", linewidth=2.5, color="#e74c3c")
ax_venta.plot(mes_labels, venta_serie_5y, label="Prom. 2020-2024", linestyle="--", marker="o", linewidth=2, color="#2ecc71")
ax_venta.set_title("Ventas por Mes", fontsize=16, pad=20, fontweight='bold')
ax_venta.set_ylabel("USD", fontsize=12)
ax_venta.legend(frameon=True, facecolor='white', fontsize=10)
ax_venta.grid(True, linestyle='--', alpha=0.4, axis='y')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
st.pyplot(fig_venta)

# === PIE DE PÁGINA ===
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:14px; margin-top:30px;'>"
    "Preparado por Ecoener - Marcelo Arriagada<br>"
    f"Última actualización: {mes_seleccionado} 2025"
    "</div>", 
    unsafe_allow_html=True
)
