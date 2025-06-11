import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime

# Configuración general
st.set_page_config(page_title="Reporte Mensual", layout="wide")

# Estilos personalizados
st.markdown("""
    <style>
        .titulo-principal {
            font-size: 32px;
            font-weight: bold;
            color: #003366;
            vertical-align: middle;
        }
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        .kpi-style {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Carga de datos
excel_path = "HEC mensuales 2025.xlsx"
df = pd.read_excel(excel_path, sheet_name="Pluviometria", header=127, usecols="C:D")
df = df.dropna()
df.columns = ["Fecha", "Precipitacion"]
df["Fecha"] = pd.to_datetime(df["Fecha"], format="%d-%m-%Y")
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month

# Diccionario de meses
mes_nombre = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# NUEVO: Selector de mes destacado arriba
st.markdown("### 📅 Selecciona el mes del reporte")
mes_seleccionado = st.selectbox("", list(mes_nombre.values()), index=datetime.now().month - 1)
mes_num = list(mes_nombre.keys())[list(mes_nombre.values()).index(mes_seleccionado)]

# Título dinámico con logo alineado
st.markdown(f"""
    <div class='logo-container'>
        <img src="logo.jpg" width="80">
        <div class='titulo-principal'>REPORTE MENSUAL – {mes_nombre[mes_num].upper()} 2025</div>
    </div>
""", unsafe_allow_html=True)

# Cálculo de precipitaciones
def calcular_precipitacion(mes, año):
    return df[(df["Mes"] == mes) & (df["Año"] == año)]["Precipitacion"].sum()

prec_2025 = calcular_precipitacion(mes_num, 2025)
prec_2024 = calcular_precipitacion(mes_num, 2024)
prec_5anios = df[(df["Mes"] == mes_num) & (df["Año"].between(2020, 2024))]["Precipitacion"].mean()

delta_2025_vs_24 = prec_2025 - prec_2024
delta_2025_vs_5a = prec_2025 - prec_5anios

# KPIs estilizados
col1, col2, col3 = st.columns(3)
col1.metric(label="🌧️ Precipitaciones 2025", value=f"{prec_2025:.1f} mm", delta=f"{delta_2025_vs_24:+.1f} mm")
col2.metric(label="📆 Año 2024", value=f"{prec_2024:.1f} mm")
col3.metric(label="📊 Promedio 2020-2024", value=f"{prec_5anios:.1f} mm", delta=f"{delta_2025_vs_5a:+.1f} mm")

# Gráfico de líneas suavizado
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

# Espacios para futuras secciones
with st.expander("⚡ Generación de energía (próximamente)"):
    st.info("Sección en desarrollo para reportar generación mensual de energía.")

with st.expander("💰 Ingresos y ventas (próximamente)"):
    st.info("Resumen financiero de ingresos y ventas por mes.")

with st.expander("🔒 Cumplimiento normativo (próximamente)"):
    st.info("Registro de cumplimiento con normativa SEC, DS327, etc.")
