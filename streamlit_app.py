import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime
from PIL import Image

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(
    page_title="Reporte Mensual - Hidroeléctrica El Canelo S.A. - 2025",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LOGO ---
logo = "logo.jpg"
col1, col2 = st.columns([1, 10])
with col1:
    st.image(logo, width=80)
with col2:
    st.markdown("### 📊 Reporte Mensual - Hidroeléctrica El Canelo S.A. - 2025")

# --- SELECCIÓN DE MES ---
meses_dict = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}
mes_seleccionado = st.selectbox("Selecciona el mes del informe", list(meses_dict.values()))
numero_mes = list(meses_dict.values()).index(mes_seleccionado) + 1

# --- LECTURA DE DATOS ---
archivo_excel = "HEC mensuales 2025.xlsx"
df = pd.read_excel(archivo_excel, sheet_name="Pluviometria", header=None, skiprows=128, usecols="C:D")
df.columns = ["Fecha", "Precipitaciones"]
df = df.dropna()
df = df[df["Fecha"] != "Fecha"]  # remover encabezado repetido
df["Fecha"] = pd.to_datetime(df["Fecha"], format="%b-%y", errors="coerce")
df = df.dropna(subset=["Fecha"])
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month
df = df.sort_values("Fecha")

# --- AÑOS DE COMPARACIÓN ---
anio_actual = 2025
anio_anterior = 2024
ultimos_5 = list(range(2020, 2025))

# --- EXTRACCIÓN DE DATOS ---
actual = df[(df["Año"] == anio_actual) & (df["Mes"] == numero_mes)]["Precipitaciones"].values
anterior = df[(df["Año"] == anio_anterior) & (df["Mes"] == numero_mes)]["Precipitaciones"].values
promedio_5 = df[(df["Año"].isin(ultimos_5)) & (df["Mes"] == numero_mes)]["Precipitaciones"].mean()

# --- MÉTRICAS PRINCIPALES ---
st.markdown("### 📌 Resumen del mes")
if len(actual) > 0:
    val_act = actual[0]
    val_ant = anterior[0] if len(anterior) > 0 else None
    variacion = ((val_act - val_ant) / val_ant * 100) if val_ant else None

    st.markdown(f"**Precipitaciones {mes_seleccionado} 2025:** {val_act:.1f} mm")
    if val_ant is not None:
        color_var = "green" if variacion >= 0 else "red"
        st.markdown(f"**Precipitaciones {mes_seleccionado} 2024:** {val_ant:.1f} mm")
        st.markdown(f"<span style='color:{color_var}; font-size: 22px; font-weight: bold;'>"
                    f"Variación interanual:<br>{variacion:+.1f}%</span>", unsafe_allow_html=True)
    st.markdown(f"**Promedio últimos 5 años:** {promedio_5:.1f} mm")
else:
    st.warning("No hay datos para este mes de 2025.")

# --- GRÁFICO DE BARRAS ---
st.markdown("### 📉 Comparación gráfica")
fig_bar, ax = plt.subplots(figsize=(6, 4))
labels = ["2025", "2024", "Prom. 5 años"]
values = [val_act, val_ant if val_ant else 0, promedio_5]
bars = ax.bar(labels, values, color=["#4a90e2", "#f5a623", "#7ed321"])
ax.set_ylabel("Precipitaciones (mm)")
ax.set_title(f"Precipitaciones en {mes_seleccionado.capitalize()}")
st.pyplot(fig_bar)

# --- GRÁFICO DE LÍNEAS ANUAL COMPARADO ---
st.markdown("### 📈 Evolución anual comparada")

# Preparar estructura de meses
df_mes = df[df["Año"].isin(ultimos_5 + [anio_actual, anio_anterior])]
pivot = df_mes.pivot_table(index="Mes", columns="Año", values="Precipitaciones")

# Agregar promedio 5 años
pivot["Prom_5"] = pivot[ultimos_5].mean(axis=1)

fig_line, ax2 = plt.subplots(figsize=(7, 4))
meses = list(meses_dict.values())

ax2.plot(meses, pivot[anio_actual], marker="o", label="2025", color="#4a90e2")
ax2.plot(meses, pivot[anio_anterior], marker="o", label="2024", color="#f5a623", linestyle="--")
ax2.plot(meses, pivot["Prom_5"], marker="o", label="Prom. 2020-2024", color="#7ed321", linestyle="dotted")

ax2.set_title("Precipitaciones enero - diciembre")
ax2.set_ylabel("Precipitaciones (mm)")
ax2.legend()
ax2.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig_line)

