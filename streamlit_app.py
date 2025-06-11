from PIL import Image
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargar logo
logo = Image.open("logo.jpg")  # Reemplaza con tu ruta exacta

# Configurar página
st.set_page_config(
    page_title="REPORTE MENSUAL - HIDROELÉCTRICA EL CANELO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
        .main-title {
            font-size:40px !important;
            font-weight: bold;
            color: #1E3D58;
            text-align: center;
            margin-bottom: 10px;
        }
        .kpi-container {
            display: flex;
            justify-content: space-around;
            margin-top: 30px;
            margin-bottom: 30px;
        }
        .kpi {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            width: 30%;
            text-align: center;
            box-shadow: 2px 2px 12px #ddd;
        }
        .kpi-title {
            font-size: 16px;
            color: #6c757d;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 36px;
            font-weight: bold;
        }
        .positive { color: green; }
        .negative { color: red; }
        .section-title {
            font-size: 24px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 10px;
            color: #0c4a6e;
        }
    </style>
""", unsafe_allow_html=True)

# Título con logo
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(logo, width=120)
with col2:
    st.markdown('<div class="main-title">REPORTE MENSUAL - HIDROELÉCTRICA EL CANELO</div>', unsafe_allow_html=True)

# KPIs de ejemplo
kpis = {
    "Precipitación mensual (mm)": {"valor": 89, "variación": -5},
    "Generación eléctrica (MWh)": {"valor": 1025, "variación": 12},
    "Ingresos netos (MM$)": {"valor": 75, "variación": -8}
}

# KPIs
st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
for titulo, datos in kpis.items():
    variacion = datos["variación"]
    color = "positive" if variacion >= 0 else "negative"
    st.markdown(f"""
        <div class="kpi">
            <div class="kpi-title">{titulo}</div>
            <div class="kpi-value {color}">{datos["valor"]}</div>
            <div class="{color}">{'▲' if variacion >= 0 else '▼'} {abs(variacion)}%</div>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Datos desde Excel
excel_path = "HEC mensuales 2025.xlsx"  # asegúrate de que esté en el repositorio
df = pd.read_excel(excel_path, sheet_name="Datos_Resumen")

# Tabla de datos
st.markdown('<div class="section-title">Datos Resumen</div>', unsafe_allow_html=True)
st.dataframe(df)

# Gráfico
st.markdown('<div class="section-title">Generación mensual (MWh)</div>', unsafe_allow_html=True)
fig, ax = plt.subplots()
ax.plot(df["Mes"], df["Generación (MWh)"], marker='o')
ax.set_ylabel("MWh")
ax.set_xlabel("Mes")
ax.grid(True)
st.pyplot(fig)
