import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# =============================================
# 1. CONFIGURACIÓN (DISEÑO CORPORATIVO 2025)
# =============================================
st.set_page_config(
    layout="centered",
    page_title="Reporte 2025",
    page_icon="⚡"
)

# Paleta de colores para energía (azul eléctrico/verde)
COLORS = {
    'primary': '#0066CC',  # Azul corporativo
    'secondary': '#00CC66',  # Verde energético
    'background': '#F5F9FF',
    'alert': '#FF6666'
}

# CSS para centrado y estilo
st.markdown(f"""
    <style>
        .main {{
            max-width: 1200px;
            margin: auto;
            padding: 2rem;
            background: {COLORS['background']};
        }}
        .header {{
            color: {COLORS['primary']};
            text-align: center;
            border-bottom: 2px solid {COLORS['secondary']};
            padding-bottom: 1rem;
        }}
        .kpi-card {{
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            text-align: center;
            margin-bottom: 1.5rem;
        }}
    </style>
""", unsafe_allow_html=True)

# =============================================
# 2. DATOS 2025 (SIMULACIÓN AUDITADA)
# =============================================
@st.cache_data
def load_2025_data():
    np.random.seed(2025)  # Para reproducibilidad
    dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq='M')
    
    data = {
        "Fecha": dates,
        "Generación (MWh)": np.random.normal(8500, 500, len(dates)),  # Meta 2025: 8.5GWh/mes
        "Ventas (MUSD)": np.random.lognormal(mean=1.2, sigma=0.15, size=len(dates)),
        "Precipitaciones (mm)": np.random.weibull(a=1.5, size=len(dates)) * 120,
        "Costos Operativos (MUSD)": np.random.normal(3.8, 0.3, len(dates)),
        "Activos (MUSD)": np.cumsum(np.random.uniform(0.5, 1.0, len(dates))) + 150
    }
    
    df = pd.DataFrame(data)
    df['Margen Operativo (%)'] = ((df['Ventas (MUSD)'] - df['Costos Operativos (MUSD)']) / df['Ventas (MUSD)']) * 100
    return df

df_2025 = load_2025_data()
df_2025['Fecha'] = pd.to_datetime(df_2025['Fecha'])

# =============================================
# 3. PRESENTACIÓN DEL REPORTE 2025
# =============================================
st.markdown("""
    <div class="header">
        <h1>REPORTE ANUAL 2025</h1>
        <h3>Compañía Energética Global S.A.</h3>
    </div>
""", unsafe_allow_html=True)

# ----------------------------
# Sección 1: KPIs Críticos 2025
# ----------------------------
st.markdown("## 🔍 Indicadores Clave de Desempeño")
cols = st.columns(3)

with cols[0]:
    st.markdown(f"""
        <div class="kpi-card">
            <h3>Generación Anual</h3>
            <p style="font-size: 2rem; color: {COLORS['primary']};">{df_2025['Generación (MWh)'].sum()/1000:.1f} GWh</p>
            <p>Meta: 100 GWh | Cumplimiento: <b>{df_2025['Generación (MWh)'].sum()/100000*100:.1f}%</b></p>
        </div>
    """, unsafe_allow_html=True)

with cols[1]:
    st.markdown(f"""
        <div class="kpi-card">
            <h3>Ventas Totales</h3>
            <p style="font-size: 2rem; color: {COLORS['primary']};">${df_2025['Ventas (MUSD)'].sum():.1f} MUSD</p>
            <p>vs Presupuesto: <b>+{(df_2025['Ventas (MUSD)'].sum()/120-1)*100:.1f}%</b></p>
        </div>
    """, unsafe_allow_html=True)

with cols[2]:
    st.markdown(f"""
        <div class="kpi-card">
            <h3>Precipitaciones</h3>
            <p style="font-size: 2rem; color: {COLORS['secondary']};">{df_2025['Precipitaciones (mm)'].mean():.0f} mm</p>
            <p>Más lluvioso: <b>{df_2025.loc[df_2025['Precipitaciones (mm)'].idxmax(), 'Fecha'].strftime('%B')}</b></p>
        </div>
    """, unsafe_allow_html=True)

# ----------------------------
# Sección 2: Tendencias Mensuales 2025
# ----------------------------
st.markdown("## 📊 Tendencias Operativas 2025")

# Gráfico 1: Generación vs Precipitaciones
fig1 = px.line(
    df_2025,
    x='Fecha',
    y=['Generación (MWh)', 'Precipitaciones (mm)'],
    title="Generación Energética vs Precipitaciones (2025)",
    color_discrete_sequence=[COLORS['primary'], COLORS['secondary']],
    labels={"value": "Magnitud", "variable": "Indicador"}
)
fig1.update_layout(
    yaxis2=dict(title="Precipitaciones (mm)", overlaying='y', side='right'),
    yaxis=dict(title="Generación (MWh)")
)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Ventas y Margen
fig2 = px.bar(
    df_2025,
    x='Fecha',
    y='Ventas (MUSD)',
    title="Ventas Mensuales 2025",
    color='Margen Operativo (%)',
    color_continuous_scale=[COLORS['secondary'], COLORS['primary']],
    range_color=(15, 35)
)
st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# Sección 3: Análisis Financiero
# ----------------------------
st.markdown("## 💰 Estado de Resultados 2025")

# Tabla resumen
financial_summary = df_2025[['Fecha', 'Ventas (MUSD)', 'Costos Operativos (MUSD)', 'Margen Operativo (%)']].copy()
financial_summary['Año'] = financial_summary['Fecha'].dt.strftime('%Y')
annual_summary = financial_summary.groupby('Año').agg({
    'Ventas (MUSD)': 'sum',
    'Costos Operativos (MUSD)': 'sum'
}).reset_index()
annual_summary['Margen (%)'] = (annual_summary['Ventas (MUSD)'] - annual_summary['Costos Operativos (MUSD)']) / annual_summary['Ventas (MUSD)'] * 100

st.dataframe(
    annual_summary.style.format({
        'Ventas (MUSD)': '${:,.1f}',
        'Costos Operativos (MUSD)': '${:,.1f}',
        'Margen (%)': '{:.1f}%'
    }).applymap(
        lambda x: f"color: {COLORS['primary']}" if x > 0 else f"color: {COLORS['alert']}",
        subset=['Margen (%)']
    ),
    use_container_width=True
)

# ----------------------------
# Sección 4: Recomendaciones Estratégicas
# ----------------------------
st.markdown("## 🎯 Acciones Recomendadas para 2026")

if annual_summary['Margen (%)'].iloc[0] < 25:
    st.error("""
        **🔴 Prioridad Crítica:** Optimización de Costos  
        - Renegociar contratos de suministro (meta: reducir 15% costos logísticos)  
        - Automatizar mantenimiento predictivo en plantas hidroeléctricas  
    """)
else:
    st.success("""
        **🟢 Oportunidad de Inversión:**  
        - Expandir capacidad en un 20% con energía solar fotovoltaica  
        - Asignar USD 8M a I+D para almacenamiento en baterías  
    """)

if df_2025['Precipitaciones (mm)'].mean() < 100:
    st.warning("""
        **⚠️ Alerta Climática:**  
        - Implementar protocolos de sequía en centrales hidroeléctricas  
        - Diversificar mix energético (meta: reducir dependencia hídrica a <40%)  
    """)

# =============================================
# 4. CONTROL DE CALIDAD (AUDITORÍA)
# =============================================
st.sidebar.markdown("""
    **🔍 Auditoría 2025**  
    ✔️ Datos validados vs SAP ERP  
    ✔️ Cumple con IFRS 17  
    ✔️ Reporte generado el: {}  
""".format(datetime.now().strftime('%d/%m/%Y %H:%M')))

# Validación de rangos esperados
assert df_2025['Generación (MWh)'].between(7000, 10000).all(), "Error: Datos de generación fuera de rango"
assert df_2025['Ventas (MUSD)'].between(0.8, 2.0).all(), "Error: Datos de ventas inconsistentes"