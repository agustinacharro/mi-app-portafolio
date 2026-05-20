import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date
import io

st.set_page_config(page_title="Mi Portafolio", page_icon="📈", layout="wide")

# --- FUNCIONES DE SCRAPING ---
@st.cache_data(ttl=600)
def obtener_dolar_mep():
    url = "https://iol.invertironline.com/mercado/cotizaciones/argentina/monedas"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        dfs = pd.read_html(io.StringIO(r.text))
        df = dfs[0]
        # Buscamos la fila que contiene 'Dólar MEP' o 'Dólar CCL'
        fila = df[df.iloc[:, 0].str.contains("Dólar MEP", case=False, na=False)]
        if not fila.empty:
            precio = float(str(fila.iloc[0, 1]).replace('.', '').replace(',', '.'))
            return precio
    except:
        return 1250.0 # Fallback
    return 1250.0

# --- GESTIÓN DE SESIÓN Y NAVEGACIÓN ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "menu" not in st.session_state: st.session_state["menu"] = "Portafolio"

# --- LOGIN ---
if not st.session_state["autenticado"]:
    st.title("🔐 Acceso")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u == st.secrets["credentials"]["usuario"] and p == st.secrets["credentials"]["clave"]:
            st.session_state["autenticado"] = True
            st.rerun()

else:
    # --- SIDEBAR ---
    with st.sidebar:
        st.title("Panel Control")
        if st.button("📊 Portafolio Pro", use_container_width=True): st.session_state["menu"] = "Portafolio"
        if st.button("➕ Agregar Operación", use_container_width=True): st.session_state["menu"] = "Carga"
        if st.button("📈 Mi Rendimiento", use_container_width=True): st.session_state["menu"] = "Rendimiento"
        st.markdown("---")
        if st.button("Cerrar Sesión"): 
            st.session_state["autenticado"] = False
            st.rerun()

    # --- NAVEGACIÓN ---
    if st.session_state["menu"] == "Portafolio":
        st.header("Vista General")
        st.metric("Cotización Dólar MEP (IOL)", f"$ {obtener_dolar_mep():,.2f}")
        st.info("Aquí verás tus activos una vez cargados.")

    elif st.session_state["menu"] == "Carga":
        st.header("Nueva Transacción")
        dolar_hoy = obtener_dolar_mep()
        
        with st.form("form_carga"):
            col1, col2 = st.columns(2)
            with col1:
                ticker = st.text_input("Ticker").upper()
                cant = st.number_input("Cantidad", step=1.0)
            with col2:
                precio = st.number_input("Precio Unitario", step=0.01)
                mep_input = st.number_input("Dólar MEP de la fecha", value=dolar_hoy)
            
            submit = st.form_submit_button("Guardar")
            if submit:
                st.success(f"Operación registrada con dólar a ${mep_input}")

    elif st.session_state["menu"] == "Rendimiento":
        st.header("Mi Rendimiento")
        st.write("Estamos trabajando en los gráficos...")
