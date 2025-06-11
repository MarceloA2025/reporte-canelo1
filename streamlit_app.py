import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Reporte Mensual", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
        .titulo-linea {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 10px;
        }
        .titulo-texto {
            font-size: 36px;
            font-weight: 900;
            color: #003366;
            text-transform: uppercase;
        }
        .selector-mes {
            text-align: center;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- MES SELECCIONADO ---
mes_nombre = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
mes_seleccionado = st.selectbox("📅 Selecciona el mes del reporte:", list(mes_nombre.values()), index=datetime.now().month - 1)
mes_num = list(mes_nombre.keys())[list(mes_nombre.values()).index(mes_seleccionado)]

# --- CABECERA CON LOGO Y TÍTULO ---
col1, col2 = st.columns([1, 6])
with col1:
    st.image("logo.jpg", width=70)
with col2:
    st.markdown(f"<div class='titulo-texto'>REPORTE MENSUAL - {mes_seleccionado.upper()} 2025</div>", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
excel_file = "HEC mensuales 2025.xlsx"
df_raw = pd.read_excel(excel_file, sheet_name="Pluviometria", header=127, usecols="C:D")
df_raw.columns = ["Fecha", "Precipitacion_mm"]
df_raw.dropna(inplace=True)
df_raw["Fecha"] = pd.to_datetime(df_raw["Fecha"])
df_raw["Mes"] = df_raw["Fecha"].dt.month
df_raw["Año"] = df_raw["Fecha"].dt.year

# --- CÁLCULO PRECIPITACIONES POR AÑO Y MES ---
df_grouped = df_raw.groupby(["Año", "Mes"])["Precipitacion_mm"].sum().reset_index()
prec_2025_mes = df_grouped.query("Año == 2025 and Mes == @mes_num")["Precipitacion_mm"].sum()
prec_2024_mes = df_grouped.query("Año == 2024 and Mes == @mes_num")["Precipitacion_mm"].sum()
prec_5anios_mes = df_grouped.query("Año >= 2020 and Año <= 2024 and Mes == @mes_num")["Precipitacion_mm"].mean()

# --- KPIs ---
delta_2025_vs_24 = prec_2025_mes - prec_2024_mes
delta_2025_vs_5a = prec_2025_mes - prec_5anios_mes

col3, col4, col5 = st.columns(3)
col3.metric("📘 2025", f"{prec_2025_mes:.1f} mm", f"{delta_2025_vs_24:+.1f} mm vs 2024", delta_color="normal")
col4.metric("📗 2024", f"{prec_2024_mes:.1f} mm")
col5.metric("📙 Promedio 5 años", f"{prec_5anios_mes:.1f} mm", f"{delta_2025_vs_5a:+.1f} mm", delta_color="normal")

# --- GRÁFICO DE BARRAS POR MES ---
st.markdown("### 📊 Comparación mensual de precipitaciones")
fig_bar, ax_bar = plt.subplots()
categorias = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025_mes, prec_2024_mes, prec_5anios_mes]
colores = ["green", "blue", "gray"]
ax_bar.bar(categorias, valores, color=colores)
ax_bar.set_ylabel("Precipitación (mm)")
ax_bar.set_title(f"Precipitaciones - {mes_seleccionado}")
st.pyplot(fig_bar)
