import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Terminal Quant Pro", layout="wide")

# 2. Gestión de Memoria (Para que la app recuerde tus listas)
if 'mis_listas' not in st.session_state:
    # Estas son tus listas iniciales por defecto
    st.session_state.mis_listas = {
        "Tecnología": ["NVDA", "AAPL", "MSFT"],
        "Cripto": ["BTC-USD", "ETH-USD"]
    }

# --- BARRA LATERAL ---
st.sidebar.title("Configuración")
modo = st.sidebar.radio("Ir a:", ["Análisis Individual", "Mis Listas", "⚙️ Gestionar Listas"])

# --- MODO: GESTIONAR LISTAS (Aquí añades tú las cosas) ---
if modo == "⚙️ Gestionar Listas":
    st.title("⚙️ Panel de Control de Listas")
    
    # Crear nueva lista
    nueva_lista = st.text_input("Nombre de la nueva lista (ej: Dividendos):")
    if st.button("Crear Lista"):
        if nueva_lista and nueva_lista not in st.session_state.mis_listas:
            st.session_state.mis_listas[nueva_lista] = []
            st.success(f"Lista '{nueva_lista}' creada.")

    st.write("---")
    
    # Añadir acciones a una lista existente
    lista_sel = st.selectbox("Selecciona lista para editar:", list(st.session_state.mis_listas.keys()))
    nuevo_ticker = st.text_input("Añadir Ticker (ej: TSLA, SAN.MC):").upper()
    if st.button(f"Añadir a {lista_sel}"):
        if nuevo_ticker and nuevo_ticker not in st.session_state.mis_listas[lista_sel]:
            st.session_state.mis_listas[lista_sel].append(nuevo_ticker)
            st.success(f"{nuevo_ticker} añadido a {lista_sel}")

    st.write("Contenido actual:", st.session_state.mis_listas[lista_sel])

# --- MODO: MIS LISTAS (Análisis) ---
elif modo == "Mis Listas":
    st.title("📂 Scanner de Listas")
    sel = st.sidebar.selectbox("Selecciona Lista:", list(st.session_state.mis_listas.keys()))
    
    if st.button("Escanear Todo"):
        res = []
        for t in st.session_state.mis_listas[sel]:
            d = yf.download(t, period="1y", progress=False)
            if not d.empty:
                d.columns = [col[0] if isinstance(col, tuple) else col for col in d.columns]
                precio = d['Close'].iloc[-1]
                res.append({"Activo": t, "Precio": f"${precio:.2f}"})
        st.table(pd.DataFrame(res))

# --- MODO: INDIVIDUAL ---
else:
    st.title("🔍 Análisis Individual")
    ticker = st.sidebar.text_input("Ticker:", "NVDA").upper()
    if st.sidebar.button("Analizar"):
        df = yf.download(ticker, period="1y")
        if not df.empty:
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
            st.metric("Precio Actual", f"${df['Close'].iloc[-1]:.2f}")
            st.line_chart(df['Close'])
