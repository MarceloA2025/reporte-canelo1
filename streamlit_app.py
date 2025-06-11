# --- CABECERA CON LOGO Y TÍTULO ---
col1, col2 = st.columns([1, 6])
with col1:
    st.image("logo.jpg", width=140)  # Tamaño del logo incrementado
with col2:
    st.markdown(f"<div class='titulo-texto'>REPORTE MENSUAL - {mes_seleccionado.upper()} 2025</div>", unsafe_allow_html=True)

# --- KPIs (ya existentes) ---
col3, col4, col5 = st.columns(3)
col3.metric("📘 2025", f"{prec_2025_mes:.1f} mm", f"{delta_2025_vs_24:+.1f} mm vs 2024", delta_color="normal")
col4.metric("📗 2024", f"{prec_2024_mes:.1f} mm")
col5.metric("📙 Promedio 5 años", f"{prec_5anios_mes:.1f} mm", f"{delta_2025_vs_5a:+.1f} mm", delta_color="normal")

# --- GRÁFICO DE LÍNEAS (SUAVIZADO) ---
st.markdown("### 📈 Evolución de precipitaciones anuales")
fig, ax = plt.subplots()
for anio, color in zip([2025, 2024, 'Prom 5 años'], ['green', 'blue', 'gray']):
    if anio == 'Prom 5 años':
        df_prom = df_grouped[df_grouped["Año"].between(2020, 2024)].groupby("Mes")["Precipitacion_mm"].mean().reset_index()
        ax.plot(df_prom["Mes"], df_prom["Precipitacion_mm"], label=anio, linestyle='--')
    else:
        df_anio = df_grouped[df_grouped["Año"] == anio]
        ax.plot(df_anio["Mes"], df_anio["Precipitacion_mm"], label=anio, linestyle='-', marker='o')

ax.set_xticks(range(1, 13))
ax.set_xticklabels(list(mes_nombre.values()), rotation=45)
ax.set_ylabel("Precipitación (mm)")
ax.set_title("Precipitación mensual por año", fontsize=14)
ax.legend()
ax.grid(True, linestyle=':', linewidth=0.5)
st.pyplot(fig)

# --- GRÁFICO DE BARRAS ---
st.markdown("### 📊 Comparación mensual de precipitaciones")
fig_bar, ax_bar = plt.subplots()
categorias = ["2025", "2024", "Prom. 5 años"]
valores = [prec_2025_mes, prec_2024_mes, prec_5anios_mes]
colores = ["green", "blue", "gray"]
ax_bar.bar(categorias, valores, color=colores)
ax_bar.set_ylabel("Precipitación (mm)")
ax_bar.set_title(f"Precipitaciones - {mes_seleccionado}")
st.pyplot(fig_bar)

# --- SECCIONES FUTURAS ---
with st.expander("⚡ Generación eléctrica"):
    st.info("Próximamente se incluirá generación mensual, comparación con meta, y eficiencia hidráulica.")

with st.expander("💰 Ingresos y desempeño financiero"):
    st.info("Ingresos estimados, facturación CEN, y comparación con proyecciones.")

with st.expander("🔒 Seguridad y normativa"):
    st.info("Indicadores de cumplimiento normativo, auditorías o hitos regulatorios.")
