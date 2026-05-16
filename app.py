import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# Estilo CSS para tablas limpias y visualización móvil
st.markdown("""
    <style>
    .stDataFrame div[data-testid="stTable"] {overflow: visible !important;}
    div[data-testid="stMetricValue"] {font-size: 1.6rem !important;}
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DEL SESSION STATE (MEMORIA COLECTIVA)
if "listas_seguimiento" not in st.session_state:
    st.session_state.listas_seguimiento = {
        "Robótica/IA": ["ISRG", "ABB", "SYM", "SERV", "TER", "SYK", "CGNX", "AUR", "MBLY"],
        "Tecnología": ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"],
        "Semicond": ["ASML", "AVGO", "ARM", "SMCI", "MU"]
    }

if "efectivo" not in st.session_state:
    st.session_state.efectivo = 30000.0

if "cartera_bot" not in st.session_state:
    st.session_state.cartera_bot = []

if "manual_tickers" not in st.session_state:
    st.session_state.manual_tickers = []

# Universo de inversión del Bot (Líderes estructurales)
UNIVERSO_BASE_BOT = [
    "NVDA", "AMD", "QCOM", "INTC", "AVGO", "MRVL", "ADI", "TXN", "MU", "SMCI",
    "ISRG", "SYK", "ZBH", "MDT", "BSX", "GMED", "TFX", "SYM", "ABB", "SIE.DE",
    "ROK", "GWW", "FAST", "AZO", "SNA", "GE", "CGNX", "KEYS", "ROV", "PH",
    "AME", "TDY", "KYCCF", "CDNS", "SNPS", "ANSS", "PTC", "ADSK", "DSY.PA", "SAP.DE",
    "WOLF", "ON", "NXPI", "MPWR", "MCHP", "IFX.DE", "STM", "ASML", "ASM.AS", "AMAT",
    "LRCX", "KLAC", "TER", "ENTG", "MKSI", "COHR", "MBLY", "AUR", "LAZR", "APTIV"
]

# 3. VERIFICADOR DE HORARIOS INTERNACIONALES
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

# 4. MOTOR TÉCNICO ALGORÍTMICO
def analizar_activo(ticker):
    try:
        tk = yf.Ticker(ticker)
        try:
            dividend_yield = tk.info.get('dividendYield', 0) or 0
        except:
            dividend_yield = 0
            
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
            "broker": broker_optimo,
            "decision": "COMPRAR" if se_compra else "ESPERAR"
        }
    except:
        return None

# =========================================================
# 5. ARQUITECTURA DE PESTAÑAS (CENTRO DE MANDO)
# =========================================================
st.title("🎛️ Centro de Mando Financiero")

pestana1, pestana2, pestana3 = st.tabs([
    "🔍 Escáner Manual de Listas", 
    "🤖 Bot Masivo Automático 30k",
    "⚙️ Configuración de Listas"
])

# ---------------------------------------------------------
# PESTAÑA 1: ESCÁNER MANUAL
# ---------------------------------------------------------
with pestana1:
    st.subheader("🔍 Escáner Manual de Mercado")
    col_ind, col_lst = st.columns(2)
    
    with col_ind:
        st.markdown("### 📊 Opción 1: Ticker Individual")
        ticker_individual = st.text_input("Escribe un ticker suelto:", value="", key="txt_ind").upper().strip()
        if st.button("Analizar Activo", key="btn_ind"):
            if ticker_individual:
                res_ind = analizar_activo(ticker_individual)
                if res_ind:
                    st.success(f"**Resultado para {ticker_individual}:**")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Precio", f"{res_ind['precio']:.2f}")
                    c2.metric("RSI (14)", f"{res_ind['rsi']:.1f}")
                    c3.metric("Filtro Técnico", res_ind['decision'])
                    st.info(f"**Estrategia Broker:** {res_ind['broker']}")
                else:
                    st.error("No se han podido cruzar datos para este Ticker
