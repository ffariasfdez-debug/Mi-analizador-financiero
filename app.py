import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Terminal Quant Pro", layout="wide")

# 2. Memoria para tus listas personalizadas
if 'mis_listas' not in st.session_state:
    st.session_state.mis_listas = {
        "Tecnología": ["NVDA", "AAPL", "MSFT", "TSM"],
        "Favoritas": ["TSLA", "BTC-USD"]
    }

# --- BARRA LATERAL ---
st.sidebar.title("🚀 Menú Principal")
modo = st.sidebar.radio("Ir a:", ["🔍 Análisis Individual", "📂 Mis Listas", "⚙️ Gestionar Listas"])

# --- FUNCIÓN MAESTRA DE CÁLCULO ---
def obtener_datos(ticker):
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df.empty or len(df) < 50: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Indicadores Técnicos
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    except: return None

# --- MODO 1: ANÁLISIS INDIVIDUAL (ESTÉTICA ORIGINAL) ---
if modo == "🔍 Análisis Individual":
    st.title("📈 Análisis de Mercado Detallado")
    ticker = st.sidebar.text_input("Ticker:", "NVDA").upper()
    
    if st.sidebar.button("Analizar Ahora"):
        df = obtener_datos(ticker)
        if df is not None:
            precio_act = float(df['Close'].iloc[-1])
            sma50_act = float(df['SMA50'].iloc[-1])
            rsi_act = float(df['RSI'].iloc[-1])

            # Métricas visuales
            c1, c2, c3 = st.columns(3)
            c1.metric("Precio Actual", f"${precio_act:.2f}")
            c2.metric("Media 50d", f"${sma50_act:.2f}")
            c3.metric("RSI (Fuerza)", f"{rsi_act:.2f}")

            # Veredicto de Actuación (Lo que te gustaba)
            st.markdown("### 📋 Veredicto de Actuación")
            if precio_act > sma50_act:
                if rsi_act > 70:
                    st.warning("🟡 MANTENER / PRECAUCIÓN: El activo está muy caliente (RSI alto).")
                else:
                    st.success("🟢 COMPRA / MANTENER: Tendencia alcista sana y con fuerza.")
            else:
                st.error("🔴 ESPERAR: El activo está en tendencia bajista (por debajo de la media).")

            # Gráficos
            st.markdown("### 📈 Evolución y Volumen")
            st.line_chart(df[['Close', 'SMA50']])
            st.bar_chart(df['Volume'])
        else:
            st.error("No se pudo analizar este Ticker. Revisa el nombre.")

# --- MODO 2: MIS LISTAS ---
elif modo == "📂 Mis Listas":
    st.title("📂 Scanner de Mis Listas")
    sel = st.sidebar.selectbox("Selecciona Lista:", list(st.session_state.mis_listas.keys()))
    if st.button("Escanear Todo"):
        resultados = []
        for t in st.session_state.mis_listas[sel]:
            df = obtener_datos(t)
            if df is not None:
                p = df['Close'].iloc[-1]
                s = df['SMA50'].iloc[-1]
                v = "🟢 COMPRA" if p > s else "🔴 ESPERAR"
                resultados.append({"Activo": t, "Precio": f"${p:.2f}", "Veredicto": v})
        st.table(pd.DataFrame(resultados))

# --- MODO 3: GESTIONAR ---
else:
    st.title("⚙️ Gestionar mis Activos")
    lista_edit = st.selectbox("Editar lista:", list(st.session_state.mis_listas.keys()))
    nuevo_t = st.text_input("Añadir nuevo Ticker:").upper()
    if st.button("Añadir"):
        if nuevo_t and nuevo_t not in st.session_state.mis_listas[lista_edit]:
            st.session_state.mis_listas[lista_edit].append(nuevo_t)
            st.success(f"{nuevo_t} añadido.")
