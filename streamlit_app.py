import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Configuración inicial de la página
st.set_page_config(page_title="REPORTE MENSUAL", layout="wide", page_icon="📊")

# Cargar el logo
st.image("logo.jpg", width=200)

# Título estilizado
st.markdown("<h1 style='text-align: center; color: #003366;'>REPORTE MENSUAL - HIDROELÉCTRICA EL CANELO</h1>", unsafe_allow_html=True)

# Sidebar con selector de mes
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", 
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_idx = st.sidebar.selectbox("📅 Selecciona un mes", range(12), format_func=lambda x: meses[x])

# Cargar datos
archivo_excel = "HEC mensuales 2025.xlsx"
df = pd.read_excel(archivo_excel, sheet_name="Pluviometria", header=127)
df = df.iloc[:, [0, 1, 2, 3]]
df.columns = ["Mes", "2025", "2024", "Prom_5Anios"]

# Obtener valores de KPIs
prec_2025_mes = df.iloc[mes_idx, 1]
prec_2024_mes = df.iloc[mes_idx, 2]
prom_5anios_mes = df.iloc[mes_idx, 3]

# Delta con colores
delta_2025_vs_24 = prec_2025_mes - prec_2024_mes
delta_2025_vs_prom = prec_2025_mes - prom_5anios_mes

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("2025", f"{prec_2025_mes:.1f} mm", f"{delta_2025_vs_24:+.1f} mm", delta_color="normal")
with col2:
    st.metric("2024", f"{prec_2024_mes:.1f} mm")
with col3:
    st.metric("Promedio 5 años", f"{prom_5anios_mes:.1f} mm", f"{delta_2025_vs_prom:+.1f} mm", delta_color="normal")

# Gráfico
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Mes"], df["2025"], label="2025", linestyle='--', marker='o')
ax.plot(df["Mes"], df["2024"], label="2024", linestyle='--', marker='o')
ax.plot(df["Mes"], df["Prom_5Anios"], label="Prom. últimos 5 años", linestyle='--', marker='o')
ax.set_title("Precipitaciones Mensuales", fontsize=16)
ax.set_xlabel("Mes")
ax.set_ylabel("Precipitaciones (mm)")
ax.grid(True, linestyle='--', alpha=0.3)
ax.legend()
st.pyplot(fig)

# Espacio para futuras secciones
with st.expander("⚡ Generación de energía"):
    st.write("Próximamente...")

with st.expander("💰 Ingresos"):
    st.write("Próximamente...")

with st.expander("🔒 Cumplimiento normativo"):
    st.write("Próximamente...")

# Separador final
st.markdown("---")
st.markdown("<footer style='text-align:center'>© 2025 Hidroeléctrica El Canelo</footer>", unsafe_allow_html=True)

