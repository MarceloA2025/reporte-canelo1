# Importación de librerías
import streamlit as st  # Para la interfaz web
import pandas as pd     # Para manejo de datos
import matplotlib.pyplot as plt  # Para gráficos
from pathlib import Path  # Para manejo de rutas multiplataforma
import os  # Para operaciones del sistema

# ==============================================
# CONFIGURACIÓN INICIAL DE LA PÁGINA
# ==============================================
st.set_page_config(
    page_title="Reporte Mensual", 
    layout="wide",  # Usar todo el ancho disponible
    page_icon="📊"  # Icono opcional para la pestaña
)

# ==============================================
# FUNCIÓN PARA CALCULAR Y FORMATEAR DELTAS (EDITABLE)
# ==============================================
def calcular_delta(valor_2025, valor_2024, unidad):
    """
    Calcula la diferencia entre valores y devuelve texto formateado con color
    Args:
        valor_2025: Valor del año actual
        valor_2024: Valor del año anterior
        unidad: Unidad de medida (mm, kWh, USD)
    Returns:
        Texto HTML formateado con color
    """
    if valor_2024 == 0:
        delta_abs = valor_2025
        delta_pct = 0.0
    else:
        delta_abs = valor_2025 - valor_2024
        delta_pct = (delta_abs / valor_2024) * 100
    
    # EDITABLE: Colores y formato del texto
    color = "green" if delta_abs >= 0 else "red"
    formato_numero = f"<span style='color:{color}; font-size:14px;'>{delta_abs:+,.0f} {unidad} ({delta_pct:+.1f}%)</span> vs 2024"
    return formato_numero

# ==============================================
# INTERFAZ DE USUARIO - SELECTOR DE MES (EDITABLE)
# ==============================================
st.markdown("<h2 style='text-align:center; font-family:Arial; color:#333333;'>📅 Seleccione el Mes</h2>", 
            unsafe_allow_html=True)

meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

# Selector de mes (puedes cambiar el index para mes predeterminado)
mes_seleccionado = st.selectbox(
    "",  # Texto vacío porque usamos el markdown de arriba
    list(meses.keys()), 
    index=5,  # Mes predeterminado (0=Enero, 5=Junio)
    label_visibility="collapsed"  # Oculta la etiqueta
)
mes_num = meses[mes_seleccionado]

# ==============================================
# ENCABEZADO CON LOGO Y TÍTULO (EDITABLE)
# ==============================================
col_logo, col_title = st.columns([1, 9])  # Proporción de columnas

with col_logo:
    # EDITABLE: Ruta y tamaño del logo
    logo_path = Path("logo.jpg")  # Cambiar por tu ruta correcta
    if logo_path.exists():
        st.image(str(logo_path), width=180)  # Ajustar ancho
    else:
        st.warning("Logo no encontrado en la ruta especificada")

with col_title:
    # EDITABLE: Estilo del título principal
    st.markdown(
        f"<h1 style='font-size: 48px; margin-bottom: 0; font-family:Arial; color:#2c3e50;'>"
        f"Reporte Mensual {mes_seleccionado} 2025</h1>",
        unsafe_allow_html=True
    )

# ==============================================
# CARGA DE DATOS (EDITABLE - RUTAS Y COLUMNAS)
# ==============================================
try:
    # EDITABLE: Ruta exacta de tu archivo Excel
    archivo_excel = Path(r"C:\One Drive Hotmail\OneDrive\Documentos\Python VSCode\REPORTE WEB\HEC mensuales 2025.xlsx")
    
    # Carga datos de pluviometría - EDITABLE: skiprows y usecols según tu archivo
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

    # Carga datos históricos - EDITABLE: skiprows y usecols según tu archivo
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
    st.stop()  # Detiene la ejecución si hay error

# ==============================================
# FILTRADO DE DATOS POR AÑO
# ==============================================
df_2025 = df_pluv_raw[df_pluv_raw["Año"] == 2025]
df_2024 = df_pluv_raw[df_pluv_raw["Año"] == 2024]
df_5y = df_pluv_raw[df_pluv_raw["Año"].between(2020, 2024)]
df_5y_avg = df_5y.groupby("Mes")["Precipitacion"].mean().reset_index()

dfh_2025 = df_hist_raw[df_hist_raw["Año"] == 2025]
dfh_2024 = df_hist_raw[df_hist_raw["Año"] == 2024]
dfh_5y = df_hist_raw[df_hist_raw["Año"].between(2020, 2024)]

# ==============================================
# FUNCIONES PARA OBTENER VALORES (EDITABLE)
# ==============================================
def get_monthly_value(df, year_col, month_col, value_col, target_year, target_month):
    """Obtiene el valor mensual de una métrica específica"""
    try:
        return df[(df[year_col] == target_year) & (df[month_col] == target_month)][value_col].sum()
    except:
        return 0  # Devuelve 0 si no hay datos

def get_accumulated_value(df, year_col, month_col, value_col, target_year, max_month):
    """Obtiene el valor acumulado hasta un mes específico"""
    try:
        return df[(df[year_col] == target_year) & (df[month_col] <= max_month)][value_col].sum()
    except:
        return 0  # Devuelve 0 si no hay datos

# ==============================================
# CÁLCULO DE KPIs MENSUALES Y ACUMULADOS
# ==============================================
# KPIs mensuales
prec_2025 = get_monthly_value(df_pluv_raw, "Año", "Mes", "Precipitacion", 2025, mes_num)
prec_2024 = get_monthly_value(df_pluv_raw, "Año", "Mes", "Precipitacion", 2024, mes_num)
prec_5y = df_5y_avg[df_5y_avg["Mes"] == mes_num]["Precipitacion"].values[0] if mes_num in df_5y_avg["Mes"].values else 0

gen_2025 = get_monthly_value(df_hist_raw, "Año", "Mes", "Generación Bornes (kWh)", 2025, mes_num)
gen_2024 = get_monthly_value(df_hist_raw, "Año", "Mes", "Generación Bornes (kWh)", 2024, mes_num)

venta_2025 = get_monthly_value(df_hist_raw, "Año", "Mes", "Facturacion (USD$)", 2025, mes_num)
venta_2024 = get_monthly_value(df_hist_raw, "Año", "Mes", "Facturacion (USD$)", 2024, mes_num)

# KPIs acumulados
prec_acum_2025 = get_accumulated_value(df_pluv_raw, "Año", "Mes", "Precipitacion", 2025, mes_num)
prec_acum_2024 = get_accumulated_value(df_pluv_raw, "Año", "Mes", "Precipitacion", 2024, mes_num)
gen_acum_2025 = get_accumulated_value(df_hist_raw, "Año", "Mes", "Generación Bornes (kWh)", 2025, mes_num)
gen_acum_2024 = get_accumulated_value(df_hist_raw, "Año", "Mes", "Generación Bornes (kWh)", 2024, mes_num)
venta_acum_2025 = get_accumulated_value(df_hist_raw, "Año", "Mes", "Facturacion (USD$)", 2025, mes_num)
venta_acum_2024 = get_accumulated_value(df_hist_raw, "Año", "Mes", "Facturacion (USD$)", 2024, mes_num)

# ==============================================
# VISUALIZACIÓN DE KPIs (EDITABLE - ESTILOS)
# ==============================================
st.markdown(f"## 📊 Indicadores de {mes_seleccionado}")

def display_metric(col, title, value_2025, value_2024, unit):
    """Muestra una métrica con su delta comparativo"""
    # EDITABLE: Formato del valor principal
    col.markdown(
        f"<div style='font-size:18px; margin-bottom:5px;'>{title}</div>",
        unsafe_allow_html=True
    )
    
    # EDITABLE: Formato del número (tamaño, negrita, etc.)
    col.markdown(
        f"<div style='font-size:32px; font-weight:bold; margin-bottom:5px;'>{value_2025:,.1f} {unit}</div>",
        unsafe_allow_html=True
    )
    
    # Delta comparativo (usa la función calcular_delta)
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

# ==============================================
# GRÁFICOS (SECCIÓN COMPLETAMENTE EDITABLE)
# ==============================================
# Configuración común para todos los gráficos
plt.style.use('seaborn')  # Estilo base (prueba también 'ggplot' o 'fivethirtyeight')
mes_labels = list(meses.keys())  # Etiquetas de los meses

# Función para crear gráficos de línea consistentes
def create_line_plot(data_2025, data_2024, data_5y, title, ylabel):
    """Crea un gráfico de línea comparativo"""
    fig, ax = plt.subplots(figsize=(10, 4))  # EDITABLE: Tamaño del gráfico
    
    # EDITABLE: Estilo de las líneas (color, grosor, marcadores)
    ax.plot(
        mes_labels[:len(data_2025)], 
        data_2025, 
        label="2025", 
        marker="o", 
        linewidth=2.5,
        color="#3498db"  # Azul
    )
    ax.plot(
        mes_labels[:len(data_2024)], 
        data_2024, 
        label="2024", 
        marker="o", 
        linewidth=2.5,
        color="#e74c3c"  # Rojo
    )
    ax.plot(
        mes_labels[:len(data_5y)], 
        data_5y, 
        label="Prom. 2020-2024", 
        linestyle="--", 
        marker="o", 
        linewidth=2,
        color="#2ecc71"  # Verde
    )
    
    # EDITABLE: Estilo del título y ejes
    ax.set_title(
        title, 
        fontsize=16,  # Tamaño título
        pad=20,       # Espaciado
        fontweight='bold'  # Negrita
    )
    ax.set_ylabel(
        ylabel, 
        fontsize=12  # Tamaño etiqueta eje Y
    )
    
    # EDITABLE: Estilo de la leyenda
    ax.legend(
        frameon=True, 
        facecolor='white', 
        fontsize=10,  # Tamaño letra leyenda
        loc='upper right'
    )
    
    # EDITABLE: Estilo de la cuadrícula
    ax.grid(
        True, 
        linestyle='--', 
        alpha=0.4,  # Transparencia
        axis='y'    # Solo líneas horizontales
    )
    
    # EDITABLE: Rotación de etiquetas del eje X
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()  # Ajusta el layout automáticamente
    return fig

# Gráfico de barras para precipitaciones mensuales
st.markdown("### 🌧️ Comparación Mensual de Precipitaciones")
fig_bar, ax_bar = plt.subplots(figsize=(8, 4))  # EDITABLE: Tamaño del gráfico

labels = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025, prec_2024, prec_5y]
colores = ["#3498db", "#e74c3c", "#2ecc71"]  # EDITABLE: Colores de las barras

bars = ax_bar.bar(
    labels, 
    valores, 
    color=colores,
    width=0.6  # EDITABLE: Ancho de las barras
)

# EDITABLE: Estilo de los valores sobre las barras
for bar, valor in zip(bars, valores):
    ax_bar.text(
        bar.get_x() + bar.get_width()/2, 
        valor, 
        f"{valor:.1f}", 
        ha='center', 
        va='bottom', 
        fontweight='bold',
        fontsize=12  # Tamaño del texto
    )

ax_bar.set_ylabel("mm", fontsize=12)
ax_bar.set_ylim(0, max(valores)*1.2)  # EDITABLE: Límites del eje Y
ax_bar.grid(axis="y", linestyle="--", alpha=0.3)
plt.tight_layout()
st.pyplot(fig_bar)

# Gráficos de línea para series temporales
st.markdown("### 📈 Precipitaciones Anuales")
prec_serie_2025 = df_2025.groupby("Mes")["Precipitacion"].sum()
prec_serie_2024 = df_2024.groupby("Mes")["Precipitacion"].sum()
prec_serie_5y = df_5y.groupby("Mes")["Precipitacion"].mean()
st.pyplot(create_line_plot(
    prec_serie_2025, 
    prec_serie_2024, 
    prec_serie_5y, 
    "Precipitaciones por Mes", 
    "mm"
))

st.markdown("### 🔌 Energía Generada Mensual")
gen_serie_2025 = dfh_2025.groupby("Mes")["Generación Bornes (kWh)"].sum()
gen_serie_2024 = dfh_2024.groupby("Mes")["Generación Bornes (kWh)"].sum()
gen_serie_5y = dfh_5y.groupby("Mes")["Generación Bornes (kWh)"].mean()
st.pyplot(create_line_plot(
    gen_serie_2025, 
    gen_serie_2024, 
    gen_serie_5y,
    "Energía Generada por Mes", 
    "kWh"
))

st.markdown("### 💰 Ventas Mensuales")
venta_serie_2025 = dfh_2025.groupby("Mes")["Facturacion (USD$)"].sum()
venta_serie_2024 = dfh_2024.groupby("Mes")["Facturacion (USD$)"].sum()
venta_serie_5y = dfh_5y.groupby("Mes")["Facturacion (USD$)"].mean()
st.pyplot(create_line_plot(
    venta_serie_2025, 
    venta_serie_2024, 
    venta_serie_5y,
    "Ventas por Mes", 
    "USD"
))

# ==============================================
# PIE DE PÁGINA (EDITABLE)
# ==============================================
st.markdown("---")  # Línea divisoria
st.markdown(
    "<div style='text-align:center; color:gray; font-size:14px; margin-top:30px;'>"
    "Preparado por Ecoener - Marcelo Arriagada<br>"
    "Última actualización: Julio 2023"
    "</div>", 
    unsafe_allow_html=True
)