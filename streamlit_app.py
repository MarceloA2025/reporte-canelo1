import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image

matplotlib.use('Agg')

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(page_title="Reporte Mensual", layout="centered")

# ---------------- ESTILO GENERAL ----------------
st.markdown("""
    <style>
        body {
            background-color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
        }
        .logo {
            display: flex;
            justify-content: center;
            margin-bottom: 10px;
        }
        .titulo {
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            color: #003366;
            margin-top: -10px;
            letter-spacing: 1px;
        }
        .metric-container .stMetric {
            text-align: center;
        }
        .metric-label {
            font-size: 16px;
            font-weight: 500;
            color: #666;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
        }
        .delta-positive {
            color: green;
            font-weight: bold;
        }
        .delta-negative {
            color: red;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- LOGO Y TÍTULO ----------------
logo = Image.open("logo.jpg")
st.image(logo, use_column_width=False, width=180)
st.markdown('<div class="titulo">REPORTE MENSUAL - HIDROELÉCTRICA EL CANELO</div>', unsafe_allow_html=True)
st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📅 Selecciona Mes")
meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}
mes_nombre = st.sidebar.selectbox("Mes", list(meses.keys()))
mes_numero = meses[mes_nombre] - 1  # índice para listas (0-based)

# ---------------- CARGA Y PROCESAMIENTO DE DATOS ----------------
archivo = "HEC mensuales 2025.xlsx"
df_raw = pd.read_excel(archivo, sheet_name="Pluviometria", header=127, usecols="C:D")

# Renombra columnas para facilitar el trabajo
df_raw.columns = ["Fecha", "Precipitacion"]

# Filtra los años requeridos
df_raw['Fecha'] = pd.to_datetime(df_raw['Fecha'])
df_raw['Año'] = df_raw['Fecha'].dt.year
df_raw['Mes'] = df_raw['Fecha'].dt.month

df_2025 = df_raw[df_raw["Año"] == 2025]
df_2024 = df_raw[df_raw["Año"] == 2024]
df_5anios = df_raw[df_raw["Año"].between(2020, 2024)]

# Calcular promedio 5 años por mes
promedio_5a = df_5anios.groupby("Mes")["Precipitacion"].mean()

# Extrae valores para el mes seleccionado
prec_2025_mes = df_2025[df_2025["Mes"] == meses[mes_nombre]]["Precipitacion"].sum()
prec_2024_mes = df_2024[df_2024["Mes"] == meses[mes_nombre]]["Precipitacion"].sum()
prec_prom_mes = promedio_5a.loc[meses[mes_nombre]]

delta_2025_vs_24 = prec_2025_mes - prec_2024_mes
delta_2025_vs_prom = prec_2025_mes - prec_prom_mes

# ---------------- KPIs ----------------
st.subheader("📊 Precipitaciones Mensuales")

col1, col2, col3 = st.columns(3)

col1.metric(label="Año 2025", value=f"{prec_2025_mes:.1f} mm", delta=f"{delta_2025_vs_24:+.1f} mm")
col2.metric(label="Año 2024", value=f"{prec_2024_mes:.1f} mm")
col3.metric(label="Prom. 2020–2024", value=f"{prec_prom_mes:.1f} mm", delta=f"{delta_2025_vs_prom:+.1f} mm")

# ---------------- GRÁFICO ----------------
st.markdown("### 📈 Comparación de Precipitaciones Acumuladas")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_2025["Mes"], df_2025["Precipitacion"].groupby(df_2025["Mes"]).sum(), label="2025", linestyle='--', linewidth=2)
ax.plot(df_2024["Mes"], df_2024["Precipitacion"].groupby(df_2024["Mes"]).sum(), label="2024", linestyle='--', linewidth=2)
ax.plot(promedio_5a.index, promedio_5a.values, label="Prom. 2020–2024", linestyle='--', linewidth=2)

ax.set_xticks(range(1, 13))
ax.set_xticklabels(list(meses.keys()), rotation=45)
ax.set_ylabel("Precipitación (mm)")
ax.set_xlabel("Mes")
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_facecolor("white")
fig.patch.set_facecolor("white")

st.pyplot(fig)

# ---------------- ESPACIOS PARA FUTURAS SECCIONES ----------------
st.markdown("---")
with st.expander("⚡ Generación Eléctrica (Próximamente)"):
    st.write("Se mostrará información de generación mensual y comparaciones.")

with st.expander("💰 Ingresos y Mercado (Próximamente)"):
    st.write("Análisis de ingresos mensuales y precios de mercado.")

with st.expander("🔒 Seguridad y Normativa (Próximamente)"):
    st.write("Indicadores de cumplimiento y novedades regulatorias.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("Reporte generado automáticamente | © 2025 Hidroeléctrica El Canelo", unsafe_allow_html=True)
