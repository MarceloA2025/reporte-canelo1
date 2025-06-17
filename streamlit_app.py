# Importación de librerías
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os

# === CONFIGURACIÓN INICIAL ===
st.set_page_config(
    page_title="Reporte Mensual", 
    layout="wide",
    page_icon="📊"
)

# === FUNCIÓN PARA CALCULAR DELTAS ===
def calcular_delta(valor_2025, valor_2024, unidad):
    """Calcula la variación entre valores y devuelve texto formateado"""
    if valor_2024 == 0:
        delta_abs = valor_2025
        delta_pct = 0.0
    else:
        delta_abs = valor_2025 - valor_2024
        delta_pct = (delta_abs / valor_2024) * 100
    
    color = "green" if delta_abs >= 0 else "red"
    return f"<span style='color:{color}; font-size:14px;'>{delta_abs:+,.0f} {unidad} ({delta_pct:+.1f}%)</span> vs 2024"

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
    index=5,
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

# === CARGA DE DATOS - VERSIÓN CORREGIDA ===
try:
    # SOLUCIÓN 1: Ruta relativa (coloca el Excel en la misma carpeta que el script)
    archivo_excel = "HEC mensuales 2025.xlsx"
    
    # SOLUCIÓN 2: Ruta absoluta alternativa (descomenta y ajusta)
    # archivo_excel = r"C:\Users\TuUsuario\OneDrive\Documentos\Python VSCode\REPORTE WEB\HEC mensuales 2025.xlsx"
    
    # SOLUCIÓN 3: Usar pathlib (recomendado)
    # from pathlib import Path
    # archivo_excel = Path.home() / "OneDrive" / "Documentos" / "Python VSCode" / "REPORTE WEB" / "HEC mensuales 2025.xlsx"
    
    # Verificar existencia del archivo
    if not os.path.exists(archivo_excel):
        st.error(f"Archivo no encontrado en: {os.path.abspath(archivo_excel)}")
        st.stop()

    # Carga datos de pluviometría
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

    # Carga datos históricos
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

except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    st.stop()

# === PROCESAMIENTO DE DATOS ===
# Filtrado por años
df_2025 = df_pluv_raw[df_pluv_raw["Año"] == 2025]
df_2024 = df_pluv_raw[df_pluv_raw["Año"] == 2024]
df_5y = df_pluv_raw[df_pluv_raw["Año"].between(2020, 2024)]
df_5y_avg = df_5y.groupby("Mes")["Precipitacion"].mean().reset_index()

dfh_2025 = df_hist_raw[df_hist_raw["Año"] == 2025]
dfh_2024 = df_hist_raw[df_hist_raw["Año"] == 2024]
dfh_5y = df_hist_raw[df_hist_raw["Año"].between(2020, 2024)]

# === FUNCIONES PARA OBTENER VALORES ===
def get_monthly_value(df, year_col, month_col, value_col, target_year, target_month):
    try:
        return df[(df[year_col] == target_year) & (df[month_col] == target_month)][value_col].sum()
    except:
        return 0

def get_accumulated_value(df, year_col, month_col, value_col, target_year, max_month):
    try:
        return df[(df[year_col] == target_year) & (df[month_col] <= max_month)][value_col].sum()
    except:
        return 0

# === CÁLCULO DE KPIs ===
# Mensuales
prec_2025 = get_monthly_value(df_pluv_raw, "Año", "Mes", "Precipitacion", 2025, mes_num)
prec_2024 = get_monthly_value(df_pluv_raw, "Año", "Mes", "Precipitacion", 2024, mes_num)
prec_5y = df_5y_avg[df_5y_avg["Mes"] == mes_num]["Precipitacion"].values[0] if mes_num in df_5y_avg["Mes"].values else 0

gen_2025 = get_monthly_value(df_hist_raw, "Año", "Mes", "Generación Bornes (kWh)", 2025, mes_num)
gen_2024 = get_monthly_value(df_hist_raw, "Año", "Mes", "Generación Bornes (kWh)", 2024, mes_num)

venta_2025 = get_monthly_value(df_hist_raw, "Año", "Mes", "Facturacion (USD$)", 2025, mes_num)
venta_2024 = get_monthly_value(df_hist_raw, "Año", "Mes", "Facturacion (USD$)", 2024, mes_num)

# Acumulados
prec_acum_2025 = get_accumulated_value(df_pluv_raw, "Año", "Mes", "Precipitacion", 2025, mes_num)
prec_acum_2024 = get_accumulated_value(df_pluv_raw, "Año", "Mes", "Precipitacion", 2024, mes_num)
gen_acum_2025 = get_accumulated_value(df_hist_raw, "Año", "Mes", "Generación Bornes (kWh)", 2025, mes_num)
gen_acum_2024 = get_accumulated_value(df_hist_raw, "Año", "Mes", "Generación Bornes (kWh)", 2024, mes_num)
venta_acum_2025 = get_accumulated_value(df_hist_raw, "Año", "Mes", "Facturacion (USD$)", 2025, mes_num)
venta_acum_2024 = get_accumulated_value(df_hist_raw, "Año", "Mes", "Facturacion (USD$)", 2024, mes_num)

# === VISUALIZACIÓN DE KPIs ===
st.markdown(f"## 📊 Indicadores de {mes_seleccionado}")

def display_metric(col, title, value_2025, value_2024, unit):
    col.markdown(
        f"<div style='font-size:18px; margin-bottom:5px;'>{title}</div>",
        unsafe_allow_html=True
    )
    col.markdown(
        f"<div style='font-size:32px; font-weight:bold; margin-bottom:5px;'>{value_2025:,.1f} {unit}</div>",
        unsafe_allow_html=True
    )
    col.markdown(calcular_delta(value_2025, value_2024, unit), unsafe_allow_html=True)

# Métricas mensuales
col1, col2, col3 = st.columns(3)
display_metric(col1, "Precipitaciones Mensuales 2025", prec_2025, prec_2024, "mm")
display_metric(col2, "Generación Mensual 2025", gen_2025, gen_2024, "kWh")
display_metric(col3, "Ventas Mensuales 2025", venta_2025, venta_2024, "USD")

# Métricas acumuladas
col4, col5, col6 = st.columns(3)
display_metric(col4, "Precipitaciones Acumuladas 2025", prec_acum_2025, prec_acum_2024, "mm")
display_metric(col5, "Generación Acumulada 2025", gen_acum_2025, gen_acum_2024, "kWh")
display_metric(col6, "Ventas Acumuladas 2025", venta_acum_2025, venta_acum_2024, "USD")

# === GRÁFICOS ===
plt.style.use('seaborn')
mes_labels = list(meses.keys())

def create_line_plot(data_2025, data_2024, data_5y, title, ylabel):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(
        mes_labels[:len(data_2025)], 
        data_2025, 
        label="2025", 
        marker="o", 
        linewidth=2.5,
        color="#3498db"
    )
    ax.plot(
        mes_labels[:len(data_2024)], 
        data_2024, 
        label="2024", 
        marker="o", 
        linewidth=2.5,
        color="#e74c3c"
    )
    ax.plot(
        mes_labels[:len(data_5y)], 
        data_5y, 
        label="Prom. 2020-2024", 
        linestyle="--", 
        marker="o", 
        linewidth=2,
        color="#2ecc71"
    )
    
    ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(frameon=True, facecolor='white', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.4, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

# Gráfico de barras
st.markdown("### 🌧️ Comparación Mensual de Precipitaciones")
fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
labels = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025, prec_2024, prec_5y]
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

# Gráficos de línea
st.markdown("### 📈 Precipitaciones Anuales")
prec_serie_2025 = df_2025.groupby("Mes")["Precipitacion"].sum()
prec_serie_2024 = df_2024.groupby("Mes")["Precipitacion"].sum()
prec_serie_5y = df_5y.groupby("Mes")["Precipitacion"].mean()
st.pyplot(create_line_plot(prec_serie_2025, prec_serie_2024, prec_serie_5y, "Precipitaciones por Mes", "mm"))

st.markdown("### 🔌 Energía Generada Mensual")
gen_serie_2025 = dfh_2025.groupby("Mes")["Generación Bornes (kWh)"].sum()
gen_serie_2024 = dfh_2024.groupby("Mes")["Generación Bornes (kWh)"].sum()
gen_serie_5y = dfh_5y.groupby("Mes")["Generación Bornes (kWh)"].mean()
st.pyplot(create_line_plot(gen_serie_2025, gen_serie_2024, gen_serie_5y, "Energía Generada por Mes", "kWh"))

st.markdown("### 💰 Ventas Mensuales")
venta_serie_2025 = dfh_2025.groupby("Mes")["Facturacion (USD$)"].sum()
venta_serie_2024 = dfh_2024.groupby("Mes")["Facturacion (USD$)"].sum()
venta_serie_5y = dfh_5y.groupby("Mes")["Facturacion (USD$)"].mean()
st.pyplot(create_line_plot(venta_serie_2025, venta_serie_2024, venta_serie_5y, "Ventas por Mes", "USD"))

# === PIE DE PÁGINA ===
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:14px; margin-top:30px;'>"
    "Preparado por Ecoener - Marcelo Arriagada<br>"
    "Última actualización: Julio 2023"
    "</div>", 
    unsafe_allow_html=True
)