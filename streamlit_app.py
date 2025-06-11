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
        .titulo {
            font-size: 36px;
            font-weight: 700;
            color: #003366;
            text-align: center;
            margin-bottom: 10px;
        }
        .kpi-label {
            font-size: 16px;
            color: #666666;
        }
        .kpi-value {
            font-size: 30px;
            font-weight: bold;
            line-height: 1.2;
        }
        .metric-green {
            color: green;
        }
        .metric-red {
            color: red;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGO Y TÍTULO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.jpg", width=200)
    st.markdown("<h1 class='titulo'>REPORTE MENSUAL - HIDROELÉCTRICA EL CANELO</h1>", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
excel_path = "HEC mensuales 2025.xlsx"
df = pd.read_excel(excel_path, sheet_name="Pluviometria", header=127, usecols="C:D")

df = df.dropna()
df.columns = ["Fecha", "Precipitacion"]
df["Fecha"] = pd.to_datetime(df["Fecha"], format="%d-%m-%Y")

df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month

# --- SELECTOR DE MES ---
mes_nombre = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
mes_seleccionado = st.sidebar.selectbox("📅 Selecciona el mes", list(mes_nombre.values()))
mes_num = list(mes_nombre.keys())[list(mes_nombre.values()).index(mes_seleccionado)]

# --- CÁLCULOS ---
def calcular_precipitacion(mes, año):
    return df[(df["Mes"] == mes) & (df["Año"] == año)]["Precipitacion"].sum()

prec_2025 = calcular_precipitacion(mes_num, 2025)
prec_2024 = calcular_precipitacion(mes_num, 2024)
prec_5anios = df[(df["Mes"] == mes_num) & (df["Año"].between(2020, 2024))]["Precipitacion"].mean()

delta_2025_vs_24 = prec_2025 - prec_2024
delta_2025_vs_5a = prec_2025 - prec_5anios

# --- KPIs ---
col1, col2, col3 = st.columns(3)

col1.metric(label="🌧️ Precipitaciones 2025", value=f"{prec_2025:.1f} mm", delta=f"{delta_2025_vs_24:+.1f} mm")
col2.metric(label="📆 Año 2024", value=f"{prec_2024:.1f} mm", delta="")
col3.metric(label="📊 Promedio 2020-2024", value=f"{prec_5anios:.1f} mm", delta=f"{delta_2025_vs_5a:+.1f} mm")

# --- GRÁFICO DE LÍNEA SUAVIZADO ---
fig, ax = plt.subplots(figsize=(10, 5))

for año in [2025, 2024]:
    datos = df[df["Año"] == año].groupby("Mes")["Precipitacion"].sum()
    ax.plot(datos.index, datos.values, linestyle='-', marker='o', label=str(año))

promedios = df[df["Año"].between(2020, 2024)].groupby("Mes")["Precipitacion"].mean()
ax.plot(promedios.index, promedios.values, linestyle='--', marker='s', label="Promedio 2020-2024")

ax.set_title("📈 Precipitaciones Mensuales Comparadas", fontsize=14)
ax.set_xlabel("Mes")
ax.set_ylabel("Precipitación (mm)")
ax.set_xticks(range(1, 13))
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: mes_nombre.get(int(x), "")))
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()

st.pyplot(fig)

# --- FUTURAS SECCIONES ---
with st.expander("⚡ Generación de energía (próximamente)"):
    st.info("Sección en desarrollo para reportar generación mensual de energía.")

with st.expander("💰 Ingresos y ventas (próximamente)"):
    st.info("Resumen financiero de ingresos y ventas por mes.")

with st.expander("🔒 Cumplimiento normativo (próximamente)"):
    st.info("Registro de cumplimiento con normativa SEC, DS327, etc.")
