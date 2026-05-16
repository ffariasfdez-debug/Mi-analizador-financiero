import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN BÁSICA DE LA PÁGINA
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

st.markdown("""
    <style>
    .stDataFrame div[data-testid="stTable"] {overflow: visible !important;}
    div[data-testid="stMetricValue"] {font-size: 1.6rem !important;}
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DEL CONTROL DE ESTADOS (SESSION STATE)
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

# Contador de compras de 2000€ consecutivas para el freno de mano
if "consecutivas_maximas" not in st.session_state:
    st.session_state.consecutivas_maximas = 0

UNIVERSO_BASE_BOT = [
    "NVDA", "AMD", "QCOM", "INTC", "AVGO", "MRVL", "ADI", "TXN", "MU", "SMCI",
    "ISRG", "SYK", "ZBH", "MDT", "BSX", "GMED", "TFX", "SYM", "ABB", "SIE.DE",
    "ROK", "GWW", "FAST", "AZO", "SNA", "GE", "CGNX", "KEYS", "ROV", "PH",
    "AME", "TDY", "KYCCF", "CDNS", "SNPS", "ANSS", "PTC", "ADSK", "DSY.PA", "SAP.DE",
    "WOLF", "ON", "NXPI", "MPWR", "MCHP", "IFX.DE", "STM", "ASML", "ASM.AS", "AMAT",
    "LRCX", "KLAC", "TER", "ENTG", "MKSI", "COHR", "MBLY", "AUR", "LAZR", "APTIV"
]

# 3. COMPROBACIÓN DE HORARIOS DE MERCADO
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

# 4. MOTOR DE ANÁLISIS DE DATOS Y GESTIÓN DE RIESGO
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
        
        precio_actual = float(df['Close'].iloc[-1])
        sma200 = float(df['Close'].rolling(window=200).mean().iloc[-1])
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float((100 - (100 / (1 + (gain / loss)))).iloc[-1])
        
        precio_anterior = float(df['Close'].iloc[-2])
        variacion = float(((precio_actual - precio_anterior) / precio_anterior) * 100)
        volumen = int(df['Volume'].iloc[-1])
        maximo = float(df['High'].iloc[-1])
        minimo = float(df['Low'].iloc[-1])
        
        broker_optimo = "ING España (0% Div)" if dividend_yield == 0 else "Bolero / Revolut"
        
        # Filtro de compra base
        se_compra = precio_actual > sma200 and 45 <= rsi <= 55
        
        # 📊 CÁCULO DINÁMICO DEL CAPITAL (GESTIÓN MONETARIA POR MOMENTUM)
        distancia_sma200 = ((precio_actual - sma200) / sma200) * 100
        
        # Si el momentum es fuerte (>10% sobre la media de 200) y el freno no está activo
        if distancia_sma200 > 10.0 and st.session_state.consecutivas_maximas < 2:
            capital_asignado = 2000.0
            tipo_entrada = "MOMENTUM MÁXIMO (2k)"
        else:
            capital_asignado = 1000.0
            if distancia_sma200 <= 10.0:
                tipo_entrada = "PRUDENTE BASE (1k)"
            else:
                tipo_entrada = "PRUDENTE (Freno de Mano 1k)"
        
        return {
            "ticker": ticker,
            "precio": precio_actual,
            "var": variacion,
            "max": maximo,
            "min": minimo,
            "vol": volumen,
            "rsi": rsi,
            "broker": broker_optimo,
            "decision": "COMPRAR" if se_compra else "ESPERAR",
            "capital_calculado": capital_asignado,
            "tipo_entrada": tipo_entrada
        }
    except:
        return None

# =========================================================
# 5. DISEÑO INTERFAZ: TRIPLE PESTAÑA CENTRAL
# =========================================================
st.title("🎛️ Centro de Mando Financiero")

pestana1, pestana2, pestana3 = st.tabs([
    "🔍 Escáner Manual de Listas", 
    "🤖 Bot Masivo Automático 30k",
    "⚙️ Configuración de Listas"
])

# ---------------------------------------------------------
# PESTAÑA 1: BÚSQUEDA Y ESCÁNER MANUAL
# ---------------------------------------------------------
with pestana1:
    st.subheader("🔍 Análisis Técnico Manual de Mercado")
    col_ind, col_lst = st.columns(2)
    
    with col_ind:
        st.markdown("### 📊 Opción 1: Ticker Individual")
        ticker_individual = st.text_input("Introduce un ticker único (ej: NVDA):", value="", key="input_ind_manual").upper().strip()
        if st.button("Analizar Ticker Solitario", key="btn_ejecutar_individual"):
            if ticker_individual:
                res_ind = analizar_activo(ticker_individual)
                if res_ind:
                    st.success(f"Resultados de análisis para {ticker_individual}:")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Precio Actual", f"{res_ind['precio']:.2f}")
                    c2.metric("RSI (14)", f"{res_ind['rsi']:.1f}")
                    c3.metric("Filtro Técnico", res_ind['decision'])
                    st.info(f"Asignación Propuesta: {res_ind['tipo_entrada']} | Ruta Fiscal: {res_ind['broker']}")
                else:
                    st.error("No se han podido cruzar datos o el ticker es incorrecto.")
                    
    with col_lst:
        st.markdown("### 📋 Opción 2: Escanear Listas Personales")
        lista_sel = st.selectbox("Selecciona la lista a rastrear:", list(st.session_state.listas_seguimiento.keys()), key="select_lista_manual")
        if st.button("Iniciar Rastreo de Lista", key="btn_ejecutar_lista_manual"):
            resultados_lista = []
            with st.spinner("Procesando histórico técnico de la lista..."):
                for t in st.session_state.listas_seguimiento[lista_sel]:
                    res = analizar_activo(t)
                    if res:
                        resultados_lista.append({
                            "Ticker": t,
                            "Precio": f"{res['precio']:.2f}",
                            "RSI": round(res['rsi'], 1),
                            "Filtro": res['decision'],
                            "Propuesta Bot": res['tipo_entrada'],
                            "Canal Broker": res['broker']
                        })
            if resultados_lista:
                st.dataframe(pd.DataFrame(resultados_lista), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# PESTAÑA 2: BOT AUTOMÁTICO CON ENTRADA ESCALONADA POR MOMENTUM
# ---------------------------------------------------------
with pestana2:
    st.subheader("🤖 Algoritmo de Gestión Autónoma por Momentum Técnico")
    
    cartera_real_input = st.text_input("Acciones a excluir del radar de compra (ej: NVDA, ASML):", value="", key="input_exclusiones_bot").upper()
    exclusiones_reales = [t.strip() for t in cartera_real_input.split(",") if t.strip()]
    
    UNIVERSO_TOTAL = list(set(UNIVERSO_BASE_BOT + st.session_state.manual_tickers))
    UNIVERSO_FILTRADO = [t for t in UNIVERSO_TOTAL if t not in exclusiones_reales]
    
    if st.button("🔄 Refrescar Cotizaciones del Radar", key="btn_refresh_radar_bot"):
        st.rerun()
        
    radar_data = []
    with st.spinner("Sincronizando flujos de capital globales..."):
        for ticker in UNIVERSO_FILTRADO:
            data = analizar_activo(ticker)
            if data:
                abierto, estado_txt = comprobar_horario_mercado(ticker)
                data["mercado_abierto"] = abierto
                data["estado_mercado"] = estado_txt
                radar_data.append(data)
                
    if radar_data:
        df_radar = pd.DataFrame(radar_data)
        
        df_investing = pd.DataFrame()
        df_investing["Ticker"] = df_radar["ticker"]
        df_investing["Último"] = df_radar["precio"].map(lambda x: f"{x:,.2f}")
        df_investing["Var. %"] = df_radar["var"].map(lambda x: f"{x:+.2f}%")
        df_investing["Volumen"] = df_radar["vol"].map(lambda x: f"{x:,.0f}")
        df_investing["RSI"] = df_radar["rsi"].map(lambda x: f"{x:,.1f}")
        df_investing["Mercado"] = df_radar["estado_mercado"]
        df_investing["Asignación"] = df_radar["tipo_entrada"]
        df_investing["Filtro"] = df_radar["decision"]
        
        df_investing = df_investing.sort_values(by="Ticker")
        st.dataframe(df_investing, use_container_width=True, hide_index=True, height=500)
        
        # PROCESO OPERATIVO DINÁMICO
        for operativo in radar_data:
            if operativo["decision"] == "COMPRAR" and operativo["mercado_abierto"]:
                ya_comprada = any(pos["Ticker"] == operativo["ticker"] for pos in st.session_state.cartera_bot)
                monto = operativo["capital_calculado"]
                
                if not ya_comprada and st.session_state.efectivo >= monto:
                    # Registrar la operación
                    st.session_state.cartera_bot.append({
                        "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Ticker": operativo["ticker"],
                        "Precio Ejecución": f"{operativo['precio']:.2f}",
                        "Capital Invertido": f"{monto:,.0f} €",
                        "RSI": round(operativo["rsi"], 1),
                        "Motivo Tipo": operativo["tipo_entrada"],
                        "Canal": operativo["broker"]
                    })
                    st.session_state.efectivo -= monto
                    
                    # Gestionar el contador del freno de mano para la siguiente iteración
                    if monto == 2000.0:
                        st.session_state.consecutivas_maximas += 1
                    else:
                        st.session_state.consecutivas_maximas = 0 # Se resetea la racha si entra una de 1000€
                        
                    st.toast(f"🤖 Compra ejecutada: {operativo['ticker']} con {monto} €")
                    st.rerun()

    st.markdown("---")
    st.subheader("📊 Libro de Registro de Posiciones")
    
    # Añadimos un aviso visual del estado del freno de mano para monitorizarlo en el móvil
    if st.session_state.consecutivas_maximas >= 2:
        st.warning(f"⚠️ **Freno de mano activo:** Se han realizado {st.session_state.consecutivas_maximas} compras seguidas de 2.000 €. Las siguientes operaciones se limitarán a 1.000 € para proteger caja.")
    else:
        st.caption(f"Racha de compras máximas consecutivas: {st.session_state.consecutivas_maximas} / 2")

    cm1, cm2, cm3 = st.columns(3)
    cm1.metric("Fondo Estrategia", "30.000 €")
    cm2.metric("Caja Líquida", f"{st.session_state.efectivo:,.2f} €")
    cm3.metric("Posiciones Abiertas", f"{len(st.session_state.cartera_bot)}")
    
    if st.session_state.cartera_bot:
        st.table(pd.DataFrame(st.session_state.cartera_bot))
        if st.button("🗑️ Resetear Cuenta de Simulación", key="btn_clear_sim_state"):
            st.session_state.efectivo = 30000.0
            st.session_state.cartera_bot = []
            st.session_state.consecutivas_maximas = 0
            st.rerun()
    else:
        st.info("Estrategia en liquidez total. El algoritmo monitoriza el mercado en espera de parámetros de entrada.")

# ---------------------------------------------------------
# PESTAÑA 3: GESTIÓN DE CONFIGURACIÓN
# ---------------------------------------------------------
with pestana3:
    st.subheader("⚙️ Panel de Configuración de Listas")
    
    lista_mod = st.selectbox("Selecciona qué lista quieres editar:", list(st.session_state.listas_seguimiento.keys()), key="select_lista_config")
    componentes = st.session_state.listas_seguimiento[lista_mod]
    
    st.text(f"Componentes en la lista '{lista_mod}': {', '.join(componentes)}")
    st.markdown("---")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("##### ➕ Añadir a Lista Manual")
        t_add = st.text_input("Ticker a incorporar:", value="", key="input_add_ticker_manual").upper().strip()
        if st.button("Guardar en Lista", key="btn_add_ticker_manual"):
            if t_add and t_add not in componentes:
                st.session_state.listas_seguimiento[lista_mod].append(t_add)
                st.success(f"{t_add} añadido correctamente.")
                st.rerun()
                
    with col_b:
        st.markdown("##### ❌ Eliminar de Lista Manual")
        if componentes:
            t_del = st.selectbox("Selecciona cuál remover:", componentes, key="select_del_ticker_manual")
            if st.button("Eliminar de Lista", key="btn_del_ticker_manual"):
                st.session_state.listas_seguimiento[lista_mod].remove(t_del)
                st.success(f"{t_del} retirado de la lista.")
                st.rerun()
                
    with col_c:
        st.markdown("##### 🚀 Forzar Ticker Extra al Radar del Bot")
        t_bot = st.text_input("Inyectar valor nuevo al Bot:", value="", key="input_add_ticker_bot").upper().strip()
        if st.button("Inyectar al Radar", key="btn_add_ticker_bot"):
            if t_bot and t_bot not in st.session_state.manual_tickers:
                st.session_state.manual_tickers.append(t_bot)
                st.success(f"{t_bot} inyectado con éxito en el escáner del bot.")
                st.rerun()
