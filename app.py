import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Terminal Financiero Autónomo", layout="wide")

# Estilo para forzar que las tablas ocupen todo su espacio sin scrolls internos molestos
st.markdown("""
    <style>
    .stDataFrame div[data-testid="stTable"] {overflow: visible !important;}
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE LA MEMORIA (SESSION STATE)
if "efectivo" not in st.session_state:
    st.session_state.efectivo = 30000.0

if "cartera_bot" not in st.session_state:
    st.session_state.cartera_bot = []

if "manual_tickers" not in st.session_state:
    st.session_state.manual_tickers = []

# UNIVERSO DE INVERSIÓN (65 Líderes estructurales)
UNIVERSO_BASE = [
    "NVDA", "AMD", "QCOM", "INTC", "AVGO", "MRVL", "ADI", "TXN", "MU", "SMCI",
    "ISRG", "SYK", "ZBH", "MDT", "BSX", "GMED", "TFX", "SYM", "ABB", "SIE.DE",
    "ROK", "GWW", "FAST", "AZO", "SNA", "GE", "CGNX", "KEYS", "ROV", "PH",
    "AME", "TDY", "KYCCF", "CDNS", "SNPS", "ANSS", "PTC", "ADSK", "DSY.PA", "SAP.DE",
    "WOLF", "ON", "NXPI", "MPWR", "MCHP", "IFX.DE", "STM", "ASML", "ASM.AS", "AMAT",
    "LRCX", "KLAC", "TER", "ENTG", "MKSI", "COHR", "MBLY", "AUR", "LAZR", "APTIV"
]

# 3. DETECTOR MULTI-HORARIO INTELIGENTE (EE. UU. vs EUROPA)
def comprobar_horario_mercado(ticker):
    # Determinar zona horaria según el sufijo del ticker de yFinance
    es_europeo = any(ticker.endswith(sufijo) for sufijo in [".DE", ".PA", ".AS", ".MI", ".MC"])
    
    if es_europeo:
        tz = pytz.timezone('Europe/Madrid') # Horario Central Europeo (CET/CEST)
        hora_local = datetime.now(tz)
        inicio = hora_local.replace(hour=9, minute=0, second=0, microsecond=0)
        cierre = hora_local.replace(hour=17, minute=30, second=0, microsecond=0)
    else:
        tz = pytz.timezone('America/New_York') # Horario de Wall Street (EST/EDT)
        hora_local = datetime.now(tz)
        inicio = hora_local.replace(hour=9, minute=30, second=0, microsecond=0)
        cierre = hora_local.replace(hour=16, minute=0, second=0, microsecond=0)
        
    # Validar si es fin de semana (Sábado=5, Domingo=6)
    if hora_local.weekday() >= 5:
        return False, "CERRADO (Fin de semana)"
        
    if inicio <= hora_local <= cierre:
        return True, "ABIERTO (Horario Regular)"
    else:
        return False, "CERRADO (Fuera de hora operativa)"

# 4. MOTOR TÉCNICO DE ANÁLISIS
def bot_experto_analisis(ticker):
    try:
        tk = yf.Ticker(ticker)
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
        
        se_compra = precio_actual > sma200 and 45 <= rsi <= 55
        
        return {
            "ticker": ticker,
            "precio": precio_actual,
            "var": variacion,
            "max": maximo,
            "min": minimo,
            "vol": volumen,
            "rsi": rsi,
            "decision": "COMPRAR" if se_compra else "ESPERAR"
        }
    except:
        return None

# 5. INTERFAZ GRÁFICA
st.title("🤖 Terminal de Inversión 100% Algorítmico")
st.caption("Estrategia automatizada orientada a acumulación y crecimiento estructural (Horizonte 4 años).")

# PANEL LATERAL
with st.sidebar:
    st.header("⚙️ Panel de Control")
    cartera_real_input = st.text_input("🛡️ Acciones en tu cartera real (Ej: NVDA, ASML):", value="").upper()
    exclusiones_reales = [t.strip() for t in cartera_real_input.split(",") if t.strip()]
    
    st.markdown("---")
    st.subheader("➕ Forzar Ticker al Radar")
    ticker_manual = st.text_input("Escribe un ticker nuevo:", value="").upper().strip()
    if st.button("Añadir al Radar de Rastreo"):
        if ticker_manual and ticker_manual not in st.session_state.manual_tickers:
            st.session_state.manual_tickers.append(ticker_manual)
            st.success(f"{ticker_manual} añadido.")
            st.rerun()

# Combinación y limpieza de listas
UNIVERSO_TOTAL = list(set(UNIVERSO_BASE + st.session_state.manual_tickers))
UNIVERSO_FILTRADO = [t for t in UNIVERSO_TOTAL if t not in exclusiones_reales]

st.subheader(f"📡 Radar Global de Rastreo ({len(UNIVERSO_FILTRADO)} Activos)")
if st.button("🔄 Refrescar Pantalla y Cotizaciones"):
    st.rerun()

# Analizar mercado y pintar el radar estilo Investing
radar_data = []
with st.spinner("Analizando ecosistema financiero internacional en tiempo real..."):
    for ticker in UNIVERSO_FILTRADO:
        data = bot_experto_analisis(ticker)
        if data:
            # Añadimos al diccionario si el mercado específico de esta acción está abierto ahora mismo
            abierto, estado_txt = comprobar_horario_mercado(ticker)
            data["mercado_abierto"] = abierto
            data["estado_mercado"] = estado_txt
            radar_data.append(data)

if radar_data:
    df_radar = pd.DataFrame(radar_data)
    
    df_investing = pd.DataFrame({
        "Ticker": df_radar["ticker"],
        "Último ($/€)": df_radar["precio"].map("{:,.2f}".format),
        "Var. %": df_radar["var"].map("{:+.2f}%".format),
        "Máx": df_radar["max"].map("{:,.2f}".format),
        "Mín": df_radar["min"].map("{:,.2f}".format),
        "Volumen": df_radar["vol"].map("{:,.0f}".format),
        "RSI (14)": df_radar["rsi"].map("{:,.1f}".format),
        "Mercado": df_radar["estado_mercado"],
        "Filtro Técnico": df_radar["decision"]
    }).sort_values(by="Ticker")
    
    # Despliegue total de la lista en pantalla sin recortes de scroll
    altura_dinamica = min(len(df_investing) * 36 + 40, 2500)
    st.dataframe(df_investing, use_container_width=True, hide_index=True, height=altura_dinamica)
    
    # EJECUCIÓN OPERATIVA CRONOMETRADA INDEPENDIENTE POR ACTIVO
    for operativo in radar_data:
        if operativo["decision"] == "COMPRAR" and operativo["mercado_abierto"]:
            ya_comprada = any(pos["Ticker"] == operativo["ticker"] for pos in st.session_state.cartera_bot)
            
            if not ya_comprada and len(st.session_state.cartera_bot) < 10 and st.session_state.efectivo >= 3000:
                st.session_state.cartera_bot.append({
                    "Fecha/Hora (Local)": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Ticker": operativo["ticker"],
                    "Precio Ejecución": f"{operativo['precio']:.2f}",
                    "Capital Invertido": "3.000 €",
                    "RSI Entrada": round(operativo["rsi"], 1),
                    "Estrategia": "Acumulación 4A"
                })
                st.session_state.efectivo -= 3000
                st.toast(f"🤖 Bot ejecutó COMPRA de {operativo['ticker']} en su mercado abierto.")
                st.rerun()
else:
    st.error("Error al sincronizar con los servidores de datos.")

st.markdown("---")

# EL "EXCEL" DE OPERACIONES
st.subheader("📈 Registro de Operaciones y Cartera del Bot (Tu Excel)")
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Presupuesto Inicial", "30.000 €")
col_m2.metric("Líquido en Caja Ficticia", f"{st.session_state.efectivo:,.2f} €")
col_m3.metric("Posiciones Totales", f"{len(st.session_state.cartera_bot)} / 10")

if st.session_state.cartera_bot:
    df_excel = pd.DataFrame(st.session_state.cartera_bot)
    st.table(df_excel)
    
    if st.button("🗑️ Reiniciar Historial de Operaciones"):
        st.session_state.efectivo = 30000.0
        st.session_state.cartera_bot = []
        st.rerun()
else:
    st.info("El bot monitoriza el mercado global en liquidez, respetando las aperturas oficiales.")
