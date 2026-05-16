import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Terminal Financiero Autónomo", layout="wide")

# 2. INICIALIZACIÓN DE LA MEMORIA DEL BOT (Simula la persistencia)
if "efectivo" not in st.session_state:
    st.session_state.efectivo = 30000.0  # Presupuesto inicial

if "cartera_bot" not in st.session_state:
    st.session_state.cartera_bot = []  # Tu "Excel" de operaciones ejecutadas

if "radar_historico" not in st.session_state:
    st.session_state.radar_historico = {}

if "manual_tickers" not in st.session_state:
    st.session_state.manual_tickers = []

# UNIVERSO DE INVERSIÓN (65 Líderes del sector tecnológico y robótica)
UNIVERSO_BASE = [
    "NVDA", "AMD", "QCOM", "INTC", "AVGO", "MRVL", "ADI", "TXN", "MU", "SMCI",
    "ISRG", "SYK", "ZBH", "MDT", "BSX", "GMED", "TFX", "SYM", "ABB", "SIE.DE",
    "ROK", "GWW", "FAST", "AZO", "SNA", "GE", "CGNX", "KEYS", "ROV", "PH",
    "AME", "TDY", "KYCCF", "CDNS", "SNPS", "ANSS", "PTC", "ADSK", "DSY.PA", "SAP.DE",
    "WOLF", "ON", "NXPI", "MPWR", "MCHP", "IFX.DE", "STM", "ASML", "ASM.AS", "AMAT",
    "LRCX", "KLAC", "TER", "ENTG", "MKSI", "COHR", "MBLY", "AUR", "LAZR", "APTIV"
]

# 3. MOTOR TÉCNICO DE DECISIÓN AUTÓNOMA (Estilo Bot Experto)
def bot_experto_analisis(ticker):
    try:
        tk = yf.Ticker(ticker)
        df = tk.history(period="2y")
        if df.empty or len(df) < 200:
            return None
        
        # Limpieza de columnas de yfinance
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        precio_actual = df['Close'].iloc[-1]
        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # Cálculo de RSI de 14 días
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        # Datos del día para el modo "Investing"
        precio_anterior = df['Close'].iloc[-2]
        variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100
        volumen = df['Volume'].iloc[-1]
        maximo = df['High'].iloc[-1]
        minimo = df['Low'].iloc[-1]
        
        # CONDICIÓN MATEMÁTICA DE COMPRA (Filtro de acumulación estricto)
        # El bot busca activos sobre su SMA200 (tendencia alcista de largo plazo) y RSI controlado
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
            "decision": "COMPRAR" if se_compra else "ESPERAR"
        }
    except:
        return None

# 4. INTERFAZ DE USUARIO
st.title("🤖 Terminal de Inversión 100% Algorítmico")
st.caption("Estrategia automatizada orientada a acumulación y crecimiento estructural (Horizonte 4 años).")

# =========================================================
# BLOQUE DE CONFIGURACIÓN (Tus reglas y exclusiones)
# =========================================================
with st.sidebar:
    st.header("⚙️ Panel de Control")
    
    # 1. Filtro para meter acciones que YA tienes en cartera (para sacarlas del radar)
    cartera_real_input = st.text_input(
        "🛡️ Acciones en tu cartera real (Ej: NVDA, ASML):", 
        value=""
    ).upper()
    exclusiones_reales = [t.strip() for t in cartera_real_input.split(",") if t.strip()]
    
    st.markdown("---")
    
    # 2. Inyectar manualmente una acción al radar que el bot no tenga listada
    st.subheader("➕ Forzar Ticker al Radar")
    ticker_manual = st.text_input("Escribe un ticker nuevo:", value="").upper().strip()
    if st.button("Añadir al Radar de Rastreo"):
        if ticker_manual and ticker_manual not in st.session_state.manual_tickers:
            st.session_state.manual_tickers.append(ticker_manual)
            st.success(f"{ticker_manual} inyectado al radar.")
            st.rerun()

# Combinar universo base con tus tickers manuales y limpiar los que tienes en cartera real
UNIVERSO_TOTAL = list(set(UNIVERSO_BASE + st.session_state.manual_tickers))
UNIVERSO_FILTRADO = [t for t in UNIVERSO_TOTAL if t not in exclusiones_reales]

# =========================================================
# CUADRO 1: EL RADAR EN TIEMPO REAL (ESTILO INVESTING)
# =========================================================
st.subheader("📡 Acciones en el Radar Global del Bot")
st.caption("Los datos se actualizan con las cotizaciones del momento preciso en el que abres o refrescas la aplicación.")

# Botón para forzar actualización manual si se desea
if st.button("🔄 Refrescar Cotizaciones del Momento"):
    st.rerun()

# Rastrear y analizar el mercado en segundo plano
radar_data = []
with st.spinner("Bot analizando métricas de mercado en tiempo real..."):
    for ticker in UNIVERSO_FILTRADO:
        data = bot_experto_analisis(ticker)
        if data:
            radar_data.append(data)
            st.session_state.radar_historico[ticker] = data

if radar_data:
    df_radar = pd.DataFrame(radar_data)
    
    # Transformamos el DataFrame para que muestre exactamente los campos clásicos de Investing
    df_investing = pd.DataFrame({
        "Ticker": df_radar["ticker"],
        "Último ($)": df_radar["precio"].map("{:,.2f}".format),
        "Var. %": df_radar["var"].map("{:+.2f}%".format),
        "Máx": df_radar["max"].map("{:,.2f}".format),
        "Mín": df_radar["min"].map("{:,.2f}".format),
        "Volumen": df_radar["vol"].map("{:,.0f}".format),
        "RSI (14)": df_radar["rsi"].map("{:,.1f}".format),
        "Filtro Técnico": df_radar["decision"]
    })
    
    # Mostramos el radar en un recuadro limpio y scannable
    st.dataframe(df_investing, use_container_width=True, hide_index=True)
    
    # 🤖 EJECUCIÓN AUTÓNOMA DEL BOT (Sin interacción del usuario)
    # El bot busca si hay oportunidades de "COMPRAR", si tiene presupuesto y si no repite activo
    for operativo in radar_data:
        if operativo["decision"] == "COMPRAR":
            ya_comprada = any(pos["Ticker"] == operativo["ticker"] for pos in st.session_state.cartera_bot)
            
            if not ya_comprada and len(st.session_state.cartera_bot) < 10 and st.session_state.efectivo >= 3000:
                # El bot ejecuta la compra automáticamente
                st.session_state.cartera_bot.append({
                    "Fecha/Hora": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Ticker": operativo["ticker"],
                    "Precio Ejecución": f"{operativo['precio']:.2f} $",
                    "Capital Invertido": "3.000 €",
                    "RSI Entrada": round(operativo["rsi"], 1),
                    "Estrategia": "Acumulación 4A"
                })
                st.session_state.efectivo -= 3000
                st.toast(f"🤖 Bot ejecutó COMPRA de {operativo['ticker']} automáticamente.")
                st.rerun()
else:
    st.warning("No se han podido recuperar cotizaciones en este momento. Revisa la conexión con el mercado.")

st.markdown("---")

# =========================================================
# CUADRO 2: EL "EXCEL" DE OPERACIONES EJECUTADAS
# =========================================================
st.subheader("📈 Registro de Operaciones y Cartera del Bot (Tu Excel)")
st.caption("Historial de compras ejecutadas de forma autónoma por el algoritmo.")

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Presupuesto Inicial", "30.000 €")
col_m2.metric("Líquido en Caja Ficticia", f"{st.session_state.efectivo:,.2f} €")
col_m3.metric("Posiciones Totales", f"{len(st.session_state.cartera_bot)} / 10")

if st.session_state.cartera_bot:
    df_excel = pd.DataFrame(st.session_state.cartera_bot)
    # Lo renderizamos como tabla limpia simulando tu hoja Excel de seguimiento
    st.table(df_excel)
    
    if st.button("🗑️ Reiniciar todo el Historial del Excel"):
        st.session_state.efectivo = 30000.0
        st.session_state.cartera_bot = []
        st.rerun()
else:
    st.info("El bot está rastreando el mercado en liquidez. Esperando ventanas de entrada óptimas.")
