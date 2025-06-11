import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración general
st.set_page_config(page_title="Reporte Mensual - Hidroeléctrica El Canelo", layout="wide")

# Logo superior
st.image("logo.png", width=200)
st.title("📊 REPORTE MENSUAL - Hidroeléctrica El Canelo S.A. - 2025")

# Leer archivo
archivo = "HEC mensuales 2025.xlsx"
hoja = "Pluviometria"
df = pd.read_excel(archivo, sheet_name=hoja, header=None, skiprows=128, usecols="C:D")
df.columns = ["Fecha", "Precipitaciones"]
df = df[df["Fecha"] != "Fecha"]
df = df.dropna()
df["Fecha"] = pd.to_datetime(df["Fecha"], format='mixed', dayfirst=True, errors='coerce')
df = df.dropna(subset=["Fecha"])
df = df.sort_values("Fecha")
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month

# Diccionario de meses
meses_dict = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
              7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}

# Selector
mes_seleccionado = st.selectbox("Selecciona el mes del informe", list(meses_dict.values()))
num_mes = list(meses_dict.keys())[list(meses_dict.values()).index(mes_seleccionado)]
anio_actual = 2025
anio_anterior = anio_actual - 1

# Valores
val_actual = df[(df["Año"] == anio_actual) & (df["Mes"] == num_mes)]["Precipitaciones"].values
val_anterior = df[(df["Año"] == anio_anterior) & (df["Mes"] == num_mes)]["Precipitaciones"].values
prom_5 = df[(df["Año"] >= anio_actual - 5) & (df["Año"] < anio_actual) & (df["Mes"] == num_mes)]["Precipitaciones"].mean()

# Mostrar KPIs
if len(val_actual) > 0:
    actual = val_actual[0]
    anterior = val_anterior[0] if len(val_anterior) > 0 else None
    variacion = ((actual - anterior) / anterior) * 100 if anterior else None
    color_var = "green" if variacion and variacion > 0 else "red"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**2025**")
        st.markdown(f"<h1 style='color:#1f77b4;'>{actual:.1f} mm</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown("**2024**")
        st.markdown(f"<h1 style='color:#ff7f0e;'>{anterior:.1f} mm</h1>" if anterior else "Sin datos", unsafe_allow_html=True)
    with col3:
        st.markdown("**Variación Interanual**")
        if anterior:
            st.markdown(f"<h1 style='color:{color_var};'>{variacion:+.1f}%</h1>", unsafe_allow_html=True)

    st.markdown("---")

    # Promedio últimos 5 años
    st.subheader(f"📌 Promedio últimos 5 años para {mes_seleccionado.capitalize()}: {prom_5:.1f} mm")

    # Gráfico comparativo
    st.subheader("📉 Comparación mensual histórica")
    fig, ax = plt.subplots(figsize=(8, 4))
    etiquetas = ["2025", "2024", "Prom. 5 años"]
    valores = [actual, anterior if anterior else 0, prom_5]
    ax.bar(etiquetas, valores, color=["#1f77b4", "#ff7f0e", "#2ca02c"])
    ax.set_ylabel("Precipitaciones (mm)")
    ax.set_title(f"Precipitaciones en {mes_seleccionado.capitalize()}")
    st.pyplot(fig)

    # Gráfico de líneas anuales
    st.subheader("📈 Tendencia anual comparativa")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    for year in [anio_actual, anio_anterior]:
        data = df[df["Año"] == year].groupby("Mes")["Precipitaciones"].sum()
        ax2.plot(data.index, data.values, marker="o", label=str(year))
    data_avg = df[(df["Año"] >= anio_actual - 5) & (df["Año"] < anio_actual)].groupby("Mes")["Precipitaciones"].mean()
    ax2.plot(data_avg.index, data_avg.values, marker="o", linestyle="--", label="Prom. 5 años", color="gray")
    ax2.set_xticks(list(range(1, 13)))
    ax2.set_xticklabels([meses_dict[m].capitalize()[:3] for m in range(1, 13)])
    ax2.set_ylabel("Precipitaciones (mm)")
    ax2.set_title("Tendencia anual")
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

else:
    st.warning("⚠️ No hay datos disponibles para ese mes de 2025.")
