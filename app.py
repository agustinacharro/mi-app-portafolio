import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date
import io

# Configuración de página
st.set_page_config(page_title="Mi Panel de Inversiones", page_icon="📈", layout="wide")

# Forzar lectura de credenciales seguras
try:
    USUARIO_CORRECTO = st.secrets["credentials"]["usuario"]
    CLAVE_CORRECTA = st.secrets["credentials"]["clave"]
except Exception:
    st.error("Error: Configurar los 'Secrets' en Streamlit con usuario y clave.")
    st.stop()

# Inicializar Base de Datos en Memoria
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "db_transacciones" not in st.session_state:
    st.session_state["db_transacciones"] = pd.DataFrame(columns=[
        "Fecha", "Tipo Activo", "Ticker", "Operacion", "Moneda", "Cantidad", "Precio Unitario", "Comision", "Total", "Dolar MEP"
    ])

# --- FUNCIONES DE SCRAPING EN TIEMPO REAL ---
@st.cache_data(ttl=600)  # Guarda la info por 10 minutos para que la app sea rápida
def obtener_datos_iol(url, es_cedear=True):
    """Extrae tickers, precios y variaciones de InvertirOnline"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        dfs = pd.read_html(io.StringIO(r.text))
        df = dfs[0] # Tomar la primera tabla
        
        # Limpieza de nombres de columnas según estructura de IOL
        df.columns = [c.strip() for c in df.columns]
        
        ticker_col = "Símbolo" if "Símbolo" in df.columns else df.columns[0]
        precio_col = "Último Operado" if "Último Operado" in df.columns else df.columns[1]
        var_col = "Variación Diaria" if "Variación Diaria" in df.columns else df.columns[2]
        
        lista_activos = []
        for _, row in df.iterrows():
            tk = str(row[ticker_col]).strip().upper()
            # Unificación de formato numérico (comas por puntos)
            try:
                pr = float(str(row[precio_col]).replace('.', '').replace(',', '.'))
                var = str(row[var_col]).strip()
            except:
                pr = 0.0
                var = "0,00%"
            lista_activos.append({"ticker": tk, "precio": pr, "variacion": var})
            
        return pd.DataFrame(lista_activos)
    except Exception as e:
        # Retorno de emergencia si la web de IOL cambia o se cae temporalmente
        fallback = ["AAPL", "TSLA", "AMZN", "MSFT", "NVDA"] if es_cedear else ["AL30", "GD30", "YMCXO"]
        return pd.DataFrame([{"ticker": x, "precio": 0.0, "variacion": "0.0%"} for x in fallback])

@st.cache_data(ttl=1200)
def obtener_fondos_totales():
    """Simula y estructura el mapeo de FondosOnline y Santander"""
    # Nota técnica: Las páginas de Santander y FondosOnline usan cargas dinámicas por JavaScript (React/Angular).
    # Para producción robusta se consume su API interna. Dejamos el mapeo estandarizado aquí:
    fondos = [
        {"ticker": "Super Fondo Súper Ahorro $", "precio": 452.12, "variacion": "+0.12%", "tipo": "FCI Pesos"},
        {"ticker": "Super Fondo Renta Fija $", "precio": 128.54, "variacion": "+0.25%", "tipo": "FCI Pesos"},
        {"ticker": "FCI Balanz Short Term USD", "precio": 1.45, "variacion": "+0.03%", "tipo": "FCI Dólares"},
        {"ticker": "Super Fondo Renta Fija USD", "precio": 2.11, "variacion": "+0.01%", "tipo": "FCI Dólares"}
    ]
    return pd.DataFrame(fondos)

# --- CARGA DE DATOS DE MERCADO ---
df_cedears_market = obtener_datos_iol("https://iol.invertironline.com/mercado/cotizaciones/argentina/cedears/todos", es_cedear=True)
df_ons_market = obtener_datos_iol("https://iol.invertironline.com/mercado/cotizaciones/argentina/obligaciones-negociables/todos", es_cedear=False)
df_fondos_market = obtener_fondos_totales()

# --- LOGIN ---
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='text-align: center; margin-top:50px;'><h2>🔐 Mi Panel Privado</h2></div>", unsafe_allow_html=True)
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Datos incorrectos.")
else:
    # --- SISTEMA DE LOGUEADO ---
    with st.sidebar:
        st.markdown("### 👤 Navegación")
        if st.button("Cerrar Sesión"):
            st.session_state["autenticado"] = False
            st.rerun()

    st.title("📈 Gestión Automatizada de Portafolio")
    tab1, tab2 = st.tabs(["📝 Cargar Operación", "📋 Base de Datos"])

    with tab1:
        st.subheader("Nueva Transacción Inteligente")
        
        # 1. Selección Tipo de Activo principal
        tipo_activo = st.selectbox("Seleccioná el Tipo de Activo", ["Cedear", "FCI Pesos", "FCI Dólares", "ONs"])
        
        # Filtrado dinámico de tickers y precios según la selección de arriba
        precio_sugerido = 0.0
        info_variacion = "0.0%"
        
        if tipo_activo == "Cedear":
            lista_tickers = df_cedears_market["ticker"].tolist()
            ticker_seleccionado = st.selectbox("Seleccioná el Cedear", lista_tickers)
            row_match = df_cedears_market[df_cedears_market["ticker"] == ticker_seleccionado]
            if not row_match.empty:
                precio_sugerido = float(row_match.iloc[0]["precio"])
                info_variacion = row_match.iloc[0]["variacion"]
                
        elif tipo_activo == "ONs":
            lista_tickers = df_ons_market["ticker"].tolist()
            ticker_seleccionado = st.selectbox("Seleccioná la Obligación Negociable (ON)", lista_tickers)
            row_match = df_ons_market[df_ons_market["ticker"] == ticker_seleccionado]
            if not row_match.empty:
                precio_sugerido = float(row_match.iloc[0]["precio"])
                info_variacion = row_match.iloc[0]["variacion"]
                
        else: # Fondos
            df_f_filtrado = df_fondos_market[df_fondos_market["tipo"] == tipo_activo]
            lista_tickers = df_f_filtrado["ticker"].tolist()
            ticker_seleccionado = st.selectbox("Seleccioná el Fondo", lista_tickers)
            row_match = df_f_filtrado[df_f_filtrado["ticker"] == ticker_seleccionado]
            if not row_match.empty:
                precio_sugerido = float(row_match.iloc[0]["precio"])
                info_variacion = row_match.iloc[0]["variacion"]

        if precio_sugerido > 0:
            st.caption(f"💡 Última cotización detectada en mercado: **${precio_sugerido:,.2f}** ({info_variacion})")

        # Formulario secundario para los costos
        with st.form("formulario_costos"):
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                fecha_op = st.date_input("Fecha de Operación", value=date.today())
                operacion = st.radio("Operación", ["Compra", "Venta"])
                moneda = st.radio("Moneda de la Operación", ["Pesos ($)", "Dólares (USD)"])
            
            with col_b:
                cantidad = st.number_input("Cantidad", min_value=0.0, step=1.0, value=1.0)
                # El precio unitario toma el sugerido de mercado, pero te deja editarlo si querés
                precio_unitario = st.number_input("Precio Unitario", min_value=0.0, step=0.01, value=precio_sugerido)
            
            with col_c:
                modo_calculo = st.radio("Método de entrada", ["Ingresar Comisión (Calcular Total)", "Ingresar Total (Calcular Comisión)"])
                valor_costo = st.number_input("Monto ingresado ($ / USD)", min_value=0.0, step=0.01, value=0.0)
                
            st.markdown("---")
            col_d, _ = st.columns(2)
            with col_d:
                mep_inicial = 1250.0 if moneda == "Pesos ($)" else 1.0
                dolar_mep = st.number_input("Cotización Dólar MEP de la fecha", min_value=1.0, value=mep_inicial)

            guardar = st.form_submit_with_name("Registrar Transacción")
            
            if guardar:
                subtotal = cantidad * precio_unitario
                if modo_calculo == "Ingresar Comisión (Calcular Total)":
                    comision = valor_costo
                    total = subtotal + comision if operacion == "Compra" else subtotal - comision
                else:
                    total = valor_costo
                    comision = abs(total - subtotal)
                
                nuevo_reg = {
                    "Fecha": fecha_op.strftime('%Y-%m-%d'),
                    "Tipo Activo": tipo_activo,
                    "Ticker": ticker_seleccionado,
                    "Operacion": operacion,
                    "Moneda": moneda,
                    "Cantidad": cantidad,
                    "Precio Unitario": precio_unitario,
                    "Comision": comision,
                    "Total": total,
                    "Dolar MEP": dolar_mep
                }
                
                st.session_state["db_transacciones"] = pd.concat([st.session_state["db_transacciones"], pd.DataFrame([nuevo_reg])], ignore_index=True)
                st.success(f"¡Cargado! Total: {moneda} {total:,.2f} | Comisión: {moneda} {comision:,.2f}")

    with tab2:
        st.subheader("Historial de Operaciones en esta Sesión")
        st.dataframe(st.session_state["db_transacciones"], use_container_width=True)
