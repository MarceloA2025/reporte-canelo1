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
    
    color = "#4CAF50" if delta_abs >= 0 else "#F44336"  # Verde/Rojo modernos
    return f"<span style='color:{color}; font-size:16px; font-family:Arial;'>{delta_abs:+,.0f} {unidad} ({delta_pct:+.1f}%) vs 2024</span>"

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
    
    # Conversión explícita a numérico y limpieza
    df_hist_raw["Generación Bornes (kWh)"] = pd.to_numeric(df_hist_raw["Generación Bornes (kWh)"], errors='coerce').fillna(0)
    df_hist_raw["Facturacion (USD$)"] = pd.to_numeric(df_hist_raw["Facturacion (USD$)"], errors='coerce').fillna(0)
    
    df_hist_raw = df_hist_raw.dropna(subset=["Fecha"])
    df_hist_raw["Año"] = df_hist_raw["Fecha"].dt.year
    df_hist_raw["Mes"] = df_hist_raw["Fecha"].dt.month

    # Verificación de datos cargados
    st.write("Datos de 2025 cargados correctamente")
    st.write("Muestra de datos:", df_hist_raw[df_hist_raw["Año"] == 2025].head())

except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    st.stop()

# === PROCESAMIENTO DE DATOS ===
# Filtrado por años
df_2025 = df_pluv_raw[df_pluv_raw["Año"] == 2025].copy()
df_2024 = df_pluv_raw[df_pluv_raw["Año"] == 2024].copy()
df_5y = df_pluv_raw[df_pluv_raw["Año"].between(2020, 2024)].copy()
df_5y_avg = df_5y.groupby("Mes")["Precipitacion"].mean().reset_index()

dfh_2025 = df_hist_raw[df_hist_raw["Año"] == 2025].copy()
dfh_2024 = df_hist_raw[df_hist_raw["Año"] == 2024].copy()
dfh_5y = df_hist_raw[df_hist_raw["Año"].between(2020, 2024)].copy()

# === FUNCIÓN ROBUSTA PARA OBTENER VALORES ===
def get_kpi_values(df, month, cols):
    """Obtiene valores mensuales y acumulados para múltiples columnas"""
    results = {}
    for col in cols:
        try:
            # Datos mensuales
            monthly_data = df[df["Mes"] == month]
            monthly = monthly_data[col].sum()
            
            # Datos acumulados
            ytd_data = df[df["Mes"] <= month]
            ytd = ytd_data[col].sum()
            
            results[col] = {
                "mensual": monthly,
                "acumulado": ytd,
                "existe_datos": not monthly_data.empty
            }
            
        except Exception as e:
            st.error(f"Error en {col}: {str(e)}")
            results[col] = {"mensual": 0, "acumulado": 0, "existe_datos": False}
    return results

# === CÁLCULO DE KPIs ===
# Precipitación (se mantiene igual)
prec_2025 = df_2025[df_2025["Mes"] == mes_num]["Precipitacion"].sum()
prec_2024 = df_2024[df_2024["Mes"] == mes_num]["Precipitacion"].sum()
prec_5y = df_5y_avg[df_5y_avg["Mes"] == mes_num]["Precipitacion"].values[0] if mes_num in df_5y_avg["Mes"].values else 0

prec_acum_2025 = df_2025[df_2025["Mes"] <= mes_num]["Precipitacion"].sum()
prec_acum_2024 = df_2024[df_2024["Mes"] <= mes_num]["Precipitacion"].sum()

# Generación y Ventas - Versión corregida
kpi_2025 = get_kpi_values(dfh_2025, mes_num, ["Generación Bornes (kWh)", "Facturacion (USD$)"])
kpi_2024 = get_kpi_values(dfh_2024, mes_num, ["Generación Bornes (kWh)", "Facturacion (USD$)"])

# Extracción de valores
gen_2025 = kpi_2025["Generación Bornes (kWh)"]["mensual"]
gen_2024 = kpi_2024["Generación Bornes (kWh)"]["mensual"]
gen_acum_2025 = kpi_2025["Generación Bornes (kWh)"]["acumulado"]
gen_acum_2024 = kpi_2024["Generación Bornes (kWh)"]["acumulado"]

venta_2025 = kpi_2025["Facturacion (USD$)"]["mensual"]
venta_2024 = kpi_2024["Facturacion (USD$)"]["mensual"]
venta_acum_2025 = kpi_2025["Facturacion (USD$)"]["acumulado"]
venta_acum_2024 = kpi_2024["Facturacion (USD$)"]["acumulado"]

# Verificación de datos
if not kpi_2025["Generación Bornes (kWh)"]["existe_datos"]:
    st.warning(f"No hay datos de generación para {mes_seleccionado} 2025")
if not kpi_2025["Facturacion (USD$)"]["existe_datos"]:
    st.warning(f"No hay datos de ventas para {mes_seleccionado} 2025")

# === VISUALIZACIÓN DE KPIs ===
st.markdown(f"## 📊 Indicadores de {mes_seleccionado}")

def display_metric(col, title, value_2025, value_2024, unit):
    """Muestra una métrica con estilo mejorado"""
    col.markdown(
        f"""
        <div style='padding:15px; border-radius:10px; background-color:#f8f9fa; margin-bottom:20px;'>
            <div style='font-size:24px; font-weight:bold; color:#333333; margin-bottom:8px; font-family:Arial;'>
                {title}
            </div>
            <div style='font-size:42px; font-weight:bold; color:#2c3e50; margin-bottom:8px; font-family:Arial;'>
                {value_2025:,.1f} {unit}
            </div>
            {calcular_delta(value_2025, value_2024, unit)}
        </div>
        """,
        unsafe_allow_html=True
    )

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
try:
    plt.style.use('seaborn-v0_8')
except:
    plt.style.use('seaborn')

mes_labels = list(meses.keys())

def create_line_plot(data_2025, data_2024, data_5y, title, ylabel):
    """Crea gráficos de línea consistentes"""
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Asegurar todos los meses
    meses_completos = range(1, 13)
    data_2025 = data_2025.reindex(meses_completos, fill_value=0)
    data_2024 = data_2024.reindex(meses_completos, fill_value=0)
    data_5y = data_5y.reindex(meses_completos, fill_value=0)
    
    ax.plot(mes_labels, data_2025, label="2025", marker="o", linewidth=2.5, color="#3498db")
    ax.plot(mes_labels, data_2024, label="2024", marker="o", linewidth=2.5, color="#e74c3c")
    ax.plot(mes_labels, data_5y, label="Prom. 2020-2024", linestyle="--", marker="o", linewidth=2, color="#2ecc71")
    
    ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(frameon=True, facecolor='white', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.4, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

# Gráfico de barras de precipitaciones
st.markdown("### 🌧️ Comparación Mensual de Precipitaciones")
fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
valores = [prec_2025, prec_2024, prec_5y]
bars = ax_bar.bar(["2025", "2024", "Prom. 5 años"], valores, color=["#3498db", "#e74c3c", "#2ecc71"], width=0.6)
for bar, valor in zip(bars, valores):
    ax_bar.text(bar.get_x() + bar.get_width()/2, valor, f"{valor:.1f}", ha='center', va='bottom', fontweight='bold', fontsize=12)
ax_bar.set_ylabel("mm", fontsize=12)
ax_bar.set_ylim(0, max(valores)*1.2)
ax_bar.grid(axis="y", linestyle="--", alpha=0.3)
st.pyplot(fig_bar)

# Gráficos de línea temporales
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
    f"Última actualización: {mes_seleccionado} 2025"
    "</div>", 
    unsafe_allow_html=True
)