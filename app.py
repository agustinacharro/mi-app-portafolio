import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io

# Configuración básica de la página
st.set_page_config(page_title="Mi Panel de Inversiones", page_icon="📈", layout="wide")

# Estilos visuales
st.markdown("""
    <style>
    .main { background-color: #fafbfc; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; }
    .form-container { background-color: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# Credenciales de Acceso
USUARIO_CORRECTO = st.secrets["credentials"]["usuario"]
CLAVE_CORRECTA = st.secrets["credentials"]["clave"]

# Inicialización de la base de datos interna en memoria
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "db_transacciones" not in st.session_state:
    st.session_state["db_transacciones"] = pd.DataFrame(columns=[
        "Fecha", "Tipo Activo", "Ticker", "Operacion", "Cantidad", "Precio Unitario", "Comision", "Total", "Dolar MEP"
    ])

# --- LOGICA DE LOGIN ---
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        st.write("")
        st.markdown("<div style='text-align: center;'><h2>🔐 Acceso Protegido</h2></div>", unsafe_allow_html=True)
        usuario = st.text_input("Usuario", placeholder="Ingresá tu usuario")
        clave = st.text_input("Contraseña", type="password", placeholder="Ingresá tu contraseña")
        
        if st.button("Ingresar al Panel"):
            if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

# --- SISTEMA CENTRAL (LOGUEADO) ---
else:
    # Barra lateral
    with st.sidebar:
        st.markdown("### 👤 Sesión Activa")
        st.caption(f"Usuario: {USUARIO_CORRECTO}")
        if st.button("Cerrar Sesión"):
            st.session_state["autenticado"] = False
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📥 Importar Historial desde Excel")
        st.write("Subí tu planilla histórica para unificarla con la app.")
        uploaded_file = st.file_uploader("Elegir archivo Excel o CSV", type=["xlsx", "csv"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    df_imported = pd.read_excel(uploaded_file)
                else:
                    df_imported = pd.read_csv(uploaded_file)
                
                st.success("¡Archivo leído correctamente!")
                if st.button("Fusionar datos históricos"):
                    st.session_state["db_transacciones"] = pd.concat([st.session_state["db_transacciones"], df_imported], ignore_index=True)
                    st.toast("Historial unificado de forma exitosa")
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

    # Panel Principal
    st.title("📈 Mi Panel Privado de Inversiones")
    
    tab1, tab2, tab3 = st.tabs(["📝 Cargar Operación", "📊 Rendimientos y TIR", "📋 Base de Datos"])
    
    # PESTAÑA 1: CARGA MANUAL DETALLADA
    with tab1:
        st.subheader("Registrar Movimiento Manual")
        
        with st.form("form_registro", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            
            with col_a:
                fecha_op = st.date_input("Fecha de Operación", value=date.today())
                tipo_activo = st.selectbox("Tipo de Activo", ["Cedear", "FCI Pesos", "FCI Dólar", "ON", "Cripto"])
                ticker = st.text_input("Ticker / Símbolo", placeholder="Ej: AAPL, GGAL, AL30, BTC").upper()
                operacion = st.radio("Operación", ["Compra", "Venta"])
            
            with col_b:
                cantidad = st.number_input("Cantidad", min_value=0.0, step=1.0, value=0.0)
                precio_unitario = st.number_input("Precio Unitario", min_value=0.0, step=0.01, value=0.0)
                
                # Regla de automatización pedida por el usuario
                modo_calculo = st.radio(
                    "¿Cómo querés ingresar los costos?",
                    ["Cargar Comisión (Autocalcular Total Total)", "Cargar Total Total (Autocalcular Comisión)"]
                )
                valor_costo = st.number_input("Ingresar Monto ($ / USD)", min_value=0.0, step=0.01, value=0.0)
            
            st.markdown("---")
            col_c, _ = st.columns([1, 1])
            with col_c:
                # Sugerencia inteligente de dólar MEP (Simulado o editable)
                mep_sugerido = 1245.50 if tipo_activo in ["Cedear", "FCI Pesos", "ON"] else 1.0
                dolar_mep = st.number_input("Valor Dólar MEP de la fecha (Modificable)", min_value=1.0, value=mep_sugerido, step=0.5)
            
            guardar = st.form_submit_with_name("Guardar en Historial")
            
            if guardar:
                if cantidad <= 0 or precio_unitario <= 0:
                    st.error("La cantidad y el precio unitario deben ser mayores a cero.")
                else:
                    subtotal = cantidad * precio_unitario
                    
                    # Aplicación de las reglas dinámicas de cálculo del usuario
                    if modo_calculo == "Cargar Comisión (Autocalcular Total Total)":
                        comision = valor_costo
                        if operacion == "Compra":
                            total = subtotal + comision
                        else:
                            total = subtotal - comision
                    else:
                        total = valor_costo
                        comision = abs(total - subtotal)
                    
                    # Estructura del nuevo registro
                    nuevo_registro = {
                        "Fecha": fecha_op.strftime('%Y-%m-%d'),
                        "Tipo Activo": tipo_activo,
                        "Ticker": ticker,
                        "Operacion": operacion,
                        "Cantidad": cantidad,
                        "Precio Unitario": precio_unitario,
                        "Comision": comision,
                        "Total": total,
                        "Dolar MEP": dolar_mep
                    }
                    
                    st.session_state["db_transacciones"] = pd.concat([st.session_state["db_transacciones"], pd.DataFrame([nuevo_registro])], ignore_index=True)
                    st.success(f"¡Operación registrada con éxito! Total: ${total:,.2f} | Comisión calculada: ${comision:,.2f}")

    # PESTAÑA 2: VISUALIZACIÓN ANALÍTICA DE LA TIR
    with tab2:
        st.subheader("Análisis de Portafolio Activo")
        df_actual = st.session_state["db_transacciones"]
        
        if df_actual.empty:
            st.info("No hay datos en la base de datos para procesar rendimientos. Cargá una operación manual o importá un Excel.")
        else:
            tipos = df_actual["Tipo Activo"].unique()
            for t in tipos:
                df_t = df_actual[df_actual["Tipo Activo"] == t]
                st.markdown(f"#### 📦 {t}")
                st.dataframe(df_t, use_container_width=True)
                
                compras = df_t[df_t["Operacion"] == "Compra"]["Total"].sum()
                ventas = df_t[df_t["Operacion"] == "Venta"]["Total"].sum()
                neto = compras - ventas
                st.metric(label=f"Capital Neto Invertido en {t}", value=f"$ {neto:,.2f}")
                st.markdown("---")

    # PESTAÑA 3: LA BASE DE DATOS CRUDA
    with tab3:
        st.subheader("Historial Completo consolidado")
        if not st.session_state["db_transacciones"].empty:
            st.dataframe(st.session_state["db_transacciones"], use_container_width=True)
            
            # Botón para descargar todo en CSV y resguardar datos
            csv_data = io.StringIO()
            st.session_state["db_transacciones"].to_csv(csv_data, index=False)
            st.download_button(
                label="📥 Respaldar / Descargar base de datos actual en CSV",
                data=csv_data.getvalue(),
                file_name="base_inversiones_total.csv",
                mime="text/csv"
            )
        else:
            st.write("Sin registros almacenados.")
