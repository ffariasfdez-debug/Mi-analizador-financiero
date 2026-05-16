import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA PÁGINA (ADAPTADA A MÓVIL Y WEB)
st.set_page_config(page_title="Terminal Financiero Integral", layout="wide")

# Estilo para forzar que las tablas se desplieguen enteras sin cortes en pantallas pequeñas
st.markdown("""
    <style>
    .stDataFrame div[data-testid="stTable"] {overflow: visible !important;}
    div[data-testid="stMetricValue"] {font-size: 1.8rem !important;}
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE LA MEMORIA DEL SISTEMA (SESSION STATE)
if "listas_seguimiento" not in st.session_state:
    st.session_state.listas_seguimiento = {
        "Robótica/IA": ["ISRG", "ABB", "6861.T", "SYM", "SERV", "TER", "6954.T", "SYK", "CGNX", "AUR", "MBLY"],
        "Tecnología": ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"],
        "Semicond": ["ASML", "AVGO", "ARM", "SMCI", "MU"]
    }

if "efectivo" not in st.session_state:
    st.session_state.efectivo = 30000.0

if "cartera_bot" not in st.session_state:
    st.session_state.cartera_bot = []

if "manual_tickers" not in st.session_state:
    st.session_state.manual_tickers = []

# UNIVERSO BASE DEL BOT AUTÓNOMO (65 Líderes estructurales)
UNIVERSO_BASE_BOT = [
    "NVDA", "AMD", "QCOM", "INTC", "AVGO", "MRVL", "ADI", "TXN", "MU", "SMCI",
    "ISRG", "SYK", "ZBH", "MDT", "BSX", "GMED", "TFX", "SYM", "ABB", "SIE.DE",
    "ROK", "GWW", "FAST", "AZO", "SNA", "GE", "CGNX", "KEYS", "ROV", "PH",
    "AME", "TDY", "KYCCF", "CDNS", "SNPS", "ANSS", "PTC", "ADSK", "DSY.PA", "SAP.DE",
    "WOLF", "ON", "NXPI", "MPWR", "MCHP", "IFX.DE", "STM", "ASML", "ASM.AS", "AMAT",
    "LRCX", "KLAC", "TER", "ENTG", "MKSI", "COHR", "MBLY", "AUR", "LAZR", "APTIV"
]

# 3. DETECTOR DE HORARIOS INTERNACIONALES (EE. UU. vs EUROPA)
def comprobar_horario_mercado(ticker):
    es_europeo = any(ticker.endswith(sufijo) for sufijo in [".DE", ".PA", ".AS", ".MI", ".MC"])
    
    if es_europeo:
        tz = pytz.timezone('Europe/Madrid')
        hora_local = datetime.now(tz)
        inicio = hora_local.replace(hour=9, minute=0, second=0, microsecond=0)
        cierre = hora_local.replace(hour=17, minute=30, second=0, microsecond=0)
    else:
        tz = pytz.timezone('America/New_York')
        hora_local = datetime.now(tz)
        inicio = hora_local.replace(hour=9, minute=30, second=0, microsecond=0)
        cierre = hora_local.replace(hour=16, minute=0, second=0, microsecond=0)
        
    if hora_local.weekday() >= 5:
        return False, "CERRADO (Fin de semana)"
        
    if inicio <= hora_local <= cierre:
        return True, "ABIERTO"
    else:
        return False, "CERRADO (Fuera de hora)"

# 4. MOTOR TÉCNICO DE ANÁLISIS QUANT (COMÚN)
def analizar_activo(ticker):
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        df = tk.history(period="2y")
        if df.empty or len(df) < 200:
            return None
        
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        precio_actual = df['Close'].iloc[-1]
        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        precio_anterior = df['Close'].iloc[-2]
        variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100
        volumen = df['Volume'].iloc[-1]
        maximo = df['High'].iloc[-1]
        minimo = df['Low'].iloc[-1]
        
        # Filtro fiscal por dividendo
        dividend_yield = info.get('dividendYield', 0) or 0
        broker_optimo = "ING España (0% Div)" if dividend_yield == 0 else "Bolero / Revolut"
        
        se_compra = precio_actual > sma200 and 45 <= rsi <= 55
        
        return {
            "ticker": ticker,
            "precio": precio_actual,
            "var": variacion,
            "max": maximo,
            "min": minimo,
            "vol": volumen,
            "rsi": rsi,
            "sma200": sma200,
            "broker": broker_optimo,
            "decision": "COMPRAR" if se_compra else "ESPERAR",
            "motivo": f"RSI en {rsi:.1f} sobre SMA200." if se_compra else f"RSI en {rsi:.1f} fuera de rango."
        }
    except:
        return None

# =========================================================
# 5. MAQUETACIÓN DE LAS 3 PESTAÑAS DEL CENTRO DE MANDO
# =========================================================
st.title("🎛️ Centro de Mando Financiero")

pestana1, pestana2, pestana3 = st.tabs([
    "🔍 Escáner Manual de Listas", 
    "🤖 Bot Masivo Automático 30k",
    "⚙️ Configuración de Listas"
])

# ---------------------------------------------------------
# PESTAÑA 1: TU APLICACIÓN MANUAL ORIGINAL
# ---------------------------------------------------------
with pestana1:
    st.subheader("🔍 Análisis Técnico Manual de Mercado")
    col_individual, col_listas = st.columns(2)
    
    with col_individual:
        st.markdown("### 📊 Opción 1: Ticker Único")
        ticker_individual = st.text_input("Introduce un Ticker individual:", value="", key="manual_ind").upper().strip()
        if st.button("Analizar Ticker Único", key="btn_ind"):
            if ticker_individual:
                res_ind = analizar_activo(ticker_individual)
                if res_ind:
                    st.success(f"**Análisis de {ticker_individual}:**")
                    c_p, c_r, c_e = st.columns(3)
                    c_p.metric("Precio", f"{res_ind['precio']:.2f} $")
                    c_r.metric("RSI (14)", f"{res_ind['rsi']:.1f}")
                    c_e.metric("Filtro", res_ind['decision'])
                    st.info(f"**Filtro Fiscal:** `{res_ind['broker']}`\n\n**Nota Técnica:** {res_ind['motivo']}")
                else:
                    st.error("No se han encontrado datos para este Ticker.")
                    
    with col_listas:
        st.markdown("### 📋 Opción 2: Escanear Tus Listas")
        lista_sel = st.selectbox("Elige una de tus listas guardadas:", list(st.session_state.listas_seguimiento.keys()), key="manual_lista")
        if st.button("🚀 Iniciar Rastreo de Lista", key="btn_lista"):
            resultados = []
            with st.spinner("Escaneando lista seleccionada..."):
                for t in st.session_state.listas_seguimiento[lista_sel]:
                    res = analizar_activo(t)
                    if res:
                        resultados.append({
                            "Ticker": t, 
                            "Precio": f"{res['precio']:.2f}$", 
                            "RSI": round(res['rsi'], 1), 
                            "Filtro": res['decision'], 
                            "Canal Óptimo": res['broker'], 
                            "Nota Técnica": res['motivo']
                        })
            if resultados:
                st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# PESTAÑA 2: EL BOT EXPERTO 100% AUTÓNOMO
# ---------------------------------------------------------
with pestana2:
    st.subheader("🤖 Algoritmo Autónomo del Universo Expandido")
    
    # Panel de exclusiones por si ya tienes acciones compradas en real
    cartera_real_input = st.text_input("🛡️ Acciones en tu cartera real a excluir del radar (Ej: NVDA):", value="", key="bot_excl_input").upper()
    exclusiones_reales = [t.strip() for t in cartera_real_input.split(",") if t.strip()]
    
    # Combinar listas automáticas
    UNIVERSO_TOTAL = list(set(UNIVERSO_BASE_BOT + st.session_state.manual_tickers))
    UNIVERSO_FILTRADO = [t for t in UNIVERSO_TOTAL if t not in exclusiones_reales]
    
    col_r1, col_r2 = st.columns([4, 1])
    with col_r1:
        st.caption(f"📡 Rastreador en Tiempo Real ({len(UNIVERSO_FILTRADO)} activos monitorizados al instante).")
    with col_r2:
        if st.button("🔄 Refrescar Precios", key="refresh_bot"):
            st.rerun()

    # Procesar mercado
    radar_data = []
    with st.spinner("Sincronizando cotizaciones con los servidores..."):
        for ticker in UNIVERSO_FILTRADO:
            data = analizar_activo(ticker)
            if data:
                abierto, estado_txt = comprobar_horario_mercado(ticker)
                data["mercado_abierto"] = abierto
                data["estado_mercado"] = estado_txt
                radar_data.append(data)

    if radar_data:
        df_radar = pd.DataFrame(radar_data)
        
        # Tabla Formato Investing
        df_investing = pd.DataFrame({
            "Ticker": df_radar["ticker"],
            "Último": df_radar["precio"].map("{:,.2f}".format),
            "Var. %": df_radar["var"].map("{:+.2f}%".format),
            "Máx": df_radar["max"].map("{:,.2f}".format),
            "Mín": df_radar["min"].map("{:,.2f}".format),
            "Volumen": df_radar["vol"].map("{:,.0
