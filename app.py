import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Portafolio (Estilo Ameba)", page_icon="📈", layout="wide")

# --- ESTILOS CSS PARA REPLICAR EL DISEÑO DEL VIDEO ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #1E2130;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #2D3142;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #E0E6ED; }
    .metric-label { font-size: 14px; color: #8C9BB5; }
    .green-text { color: #00C853; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- DATOS DE EJEMPLO (MOCK DATA) ---
# Simulamos los datos que se ven en la tabla del video
datos_ejemplo = {
    "Ticker": ["AAPL", "GOOGL", "MSFT", "META", "AMZN", "INTC"],
    "Cantidad": [10, 125, 20, 94, 71, 33],
    "Precio Prom. (USD)": [150.0, 139.0, 310.0, 293.0, 130.0, 4.28],
    "Precio Actual (USD)": [170.0, 145.0, 330.0, 320.0, 140.0, 14.0],
    "Rendimiento ARS": ["+120.5%", "+154.3%", "+110.2%", "+42.0%", "+33.1%", "+181.1%"],
    "Rendimiento USD": ["+13.3%", "+4.3%", "+6.4%", "+9.2%", "+7.6%", "+227.1%"],
    "Sector": ["Tecnología", "Comunicación", "Tecnología", "Comunicación", "Consumo Discrecional", "Tecnología"],
    "Etiquetas": ["Largo plazo", "Bull", "Bull", "5 años", "Bull", "Hold"]
}
df_portafolio = pd.DataFrame(datos_ejemplo)

# Calculamos valores para las métricas
ccl_actual = 1250.50
valor_usd = sum(df_portafolio["Cantidad"] * df_portafolio["Precio Actual (USD)"])
valor_ars = valor_usd * ccl_actual

# --- BARRA LATERAL (SIDEBAR TIPO AMEBA) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00C853;'>GM Panel</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.button("📊 Portafolio Pro", use_container_width=True, type="primary")
    st.button("📈 Mi Rendimiento", use_container_width=True)
    st.button("⚖️ Desarbitrajes", use_container_width=True)
    st.button("🔥 Mapa de Calor", use_container_width=True)
    st.markdown("---")
    st.caption("Usuario: admin")

# --- ENCABEZADO Y BOTONES SUPERIORES ---
col_title, col_btn1, col_btn2 = st.columns([2, 1, 1])
with col_title:
    st.title("Portafolio Principal")
with col_btn1:
    st.write("") # Espaciador
    if st.button("➕ Agregar operación", use_container_width=True):
        st.toast("Acá abriremos el popup de carga manual")
with col_btn2:
    st.write("")
    if st.button("📥 Importar broker", use_container_width=True):
        st.toast("Acá abriremos el asistente de Excel")

# --- TARJETAS DE MÉTRICAS (METRIC CARDS) ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Valor actual (ARS)</div>
            <div class='metric-value'>$ {valor_ars:,.2f}</div>
            <div class='green-text'>+44.59%</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Valor actual (USD)</div>
            <div class='metric-value'>$ {valor_usd:,.2f}</div>
            <div class='green-text'>+26.42%</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>CCL (USD/ARS)</div>
            <div class='metric-value'>$ {ccl_actual:,.2f}</div>
            <div class='metric-label'>Última actualización: hace 2 mins</div>
        </div>
    """, unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# --- SISTEMA DE PESTAÑAS (TABS) ---
tab_resumen, tab_historial, tab_graficos, tab_ventas = st.tabs([
    "📋 Resumen", "🕒 Historial", "📊 Gráficos", "💰 Ventas"
])

# 1. PESTAÑA RESUMEN (LA TABLA PRINCIPAL)
with tab_resumen:
    st.subheader("Vista Resumida")
    # Mostramos la tabla interactiva de Streamlit
    st.dataframe(df_portafolio, use_container_width=True, hide_index=True)

# 2. PESTAÑA HISTORIAL
with tab_historial:
    st.subheader("Historial de Operaciones")
    st.info("Aquí irá la tabla cruda con todas las compras y ventas históricas.")

# 3. PESTAÑA GRÁFICOS (REPLICANDO LOS DE LA APP)
with tab_graficos:
    st.subheader("Análisis Gráfico")
    
    g_col1, g_col2 = st.columns(2)
    
    # Gráfico de Dona 1: Resumen de Portafolio
    with g_col1:
        fig_dona1 = px.pie(df_portafolio, values='Cantidad', names='Ticker', hole=0.6, title="Resumen de Portafolio")
        fig_dona1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_dona1, use_container_width=True)
        
    # Gráfico de Dona 2: Distribución por Mercado (Simulado)
    with g_col2:
        df_mercado = pd.DataFrame({"Mercado": ["CEDEAR", "Locales"], "Valor": [85, 15]})
        fig_dona2 = px.pie(df_mercado, values='Valor', names='Mercado', hole=0.6, title="Distribución por Mercado", color_discrete_sequence=['#9B59B6', '#E74C3C'])
        fig_dona2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_dona2, use_container_width=True)

    st.markdown("---")
    
    # Gráfico de Barras: Distribución por Sector
    st.markdown("#### Distribución por Sector")
    df_sector = df_portafolio.groupby("Sector")["Cantidad"].sum().reset_index()
    fig_barras = px.bar(df_sector, x="Cantidad", y="Sector", orientation='h', color="Sector")
    fig_barras.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_barras, use_container_width=True)

# 4. PESTAÑA VENTAS
with tab_ventas:
    st.subheader("Calculadora de Ventas Históricas")
    st.radio("Método de cálculo:", ["FIFO (Primero en entrar, primero en salir)", "PPC (Precio Promedio de Compra)"], horizontal=True)
    st.write("---")
    st.info("Aquí aparecerá el resumen de ganancias realizadas de las ventas.")
