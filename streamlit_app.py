import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Configuración general
st.set_page_config(page_title="Reporte Mensual - Hidroeléctrica El Canelo S.A.", layout="centered")
st.title("📊 Reporte Mensual - Hidroeléctrica El Canelo S.A. - 2025")

# Leer datos desde Excel
archivo = "HEC mensuales 2025.xlsx"
hoja = "Pluviometria"
df = pd.read_excel(archivo, sheet_name=hoja, header=None, skiprows=128, usecols="C:D")
df.columns = ["Fecha", "Precipitaciones"]
df = df.dropna()
df = df[df["Fecha"] != "Fecha"]  # Eliminar encabezado repetido
df["Fecha"] = pd.to_datetime(df["Fecha"], format='mixed', dayfirst=True, errors='coerce')
df = df.dropna(subset=["Fecha"])
df = df.sort_values("Fecha")
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month

# Diccionario de meses
meses_dict = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
              7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}

# Selector de mes
mes_seleccionado = st.selectbox("Selecciona el mes del informe", list(meses_dict.values()))
numero_mes = list(meses_dict.keys())[list(meses_dict.values()).index(mes_seleccionado)]
anio_actual = 2025
anio_anterior = anio_actual - 1

# Datos específicos
val_actual = df[(df["Año"] == anio_actual) & (df["Mes"] == numero_mes)]["Precipitaciones"].values
val_anterior = df[(df["Año"] == anio_anterior) & (df["Mes"] == numero_mes)]["Precipitaciones"].values
val_promedio_5 = df[(df["Año"] >= anio_actual - 5) & (df["Año"] < anio_actual) & (df["Mes"] == numero_mes)]["Precipitaciones"].mean()

# Mostrar métricas si hay datos
if len(val_actual) > 0:
    actual = val_actual[0]
    anterior = val_anterior[0] if len(val_anterior) > 0 else None
    variacion = ((actual - anterior) / anterior) * 100 if anterior else None

    st.subheader("📌 Resumen del mes")
    st.markdown(f"**Precipitaciones {mes_seleccionado} 2025:** {actual:.1f} mm")
    if anterior:
        st.markdown(f"**Precipitaciones {mes_seleccionado} 2024:** {anterior:.1f} mm")
        st.markdown(f"**Variación interanual:** {variacion:+.1f}%")
    if val_promedio_5:
        st.markdown(f"**Promedio últimos 5 años:** {val_promedio_5:.1f} mm")

    # Tabla resumen para exportación
    resumen_df = pd.DataFrame({
        "Año": ["2025", "2024", "Promedio 5 años"],
        "Precipitaciones (mm)": [actual, anterior if anterior else 0, val_promedio_5]
    })

    # Gráfico de barras
    st.subheader("📉 Comparación gráfica")
    fig, ax = plt.subplots(figsize=(6, 2))
    etiquetas = ["2025", "2024", "Prom. 5 años"]
    valores = [actual, anterior if anterior else 0, val_promedio_5]
    ax.bar(etiquetas, valores, color='skyblue')
    ax.set_ylabel("Precipitaciones (mm)")
    ax.set_title(f"Precipitaciones en {mes_seleccionado.capitalize()}")
    fig.patch.set_facecolor('white')
    st.pyplot(fig)

    # Descargar gráfico de barras
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches='tight', facecolor='white')
    st.download_button(
        label="📥 Descargar gráfico de barras (PNG)",
        data=buffer.getvalue(),
        file_name=f"Precipitaciones_{mes_seleccionado}_2025.png",
        mime="image/png"
    )

    # Gráfico de líneas (serie completa enero-diciembre)
    st.subheader("📈 Evolución anual comparada")
    meses_orden = list(range(1, 13))
    data_plot = pd.DataFrame({
        "Mes": meses_orden,
        "2025": [df[(df["Año"] == 2025) & (df["Mes"] == m)]["Precipitaciones"].mean() for m in meses_orden],
        "2024": [df[(df["Año"] == 2024) & (df["Mes"] == m)]["Precipitaciones"].mean() for m in meses_orden],
        "Promedio 5 años": [df[(df["Año"] >= 2020) & (df["Año"] < 2025) & (df["Mes"] == m)]["Precipitaciones"].mean() for m in meses_orden]
    })

    fig2, ax2 = plt.subplots(figsize=(8, 3.4))
    ax2.plot(data_plot["Mes"], data_plot["2025"], label="2025", marker='o')
    ax2.plot(data_plot["Mes"], data_plot["2024"], label="2024", marker='o')
    ax2.plot(data_plot["Mes"], data_plot["Promedio 5 años"], label="Prom. 5 años", linestyle='--', marker='o')
    ax2.set_xticks(meses_orden)
    ax2.set_xticklabels([meses_dict[m].capitalize()[:3] for m in meses_orden], rotation=45)
    ax2.set_ylabel("Precipitaciones (mm)")
    ax2.set_title("Precipitaciones enero - diciembre")
    ax2.legend()
    fig2.patch.set_facecolor('white')
    st.pyplot(fig2)

    # Descargar resumen Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        resumen_df.to_excel(writer, index=False, sheet_name="Resumen")
    st.download_button(
        label="📥 Descargar resumen en Excel",
        data=output.getvalue(),
        file_name=f"Resumen_Pluviometria_{mes_seleccionado}_2025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.warning("⚠️ No hay datos disponibles para ese mes de 2025.")
