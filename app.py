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
        # Intentar capturar dividendYield de forma segura
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
                    st.error("No se han podido cruzar datos para este Ticker.")
                    
    with col_lst:
        st.markdown("### 📋 Opción 2: Escanear Listas Guardadas")
        lista_sel = st.selectbox("Selecciona tu lista:", list(st.session_state.listas_seguimiento.keys()), key="sb_lista")
        if st.button("Rastrear Lista Seleccionada", key="btn_lst"):
            resultados = []
            with st.spinner("Analizando componentes..."):
                for t in st.session_state.listas_seguimiento[lista_sel]:
                    res = analizar_activo(t)
                    if res:
                        resultados.append({
                            "Ticker": t,
                            "Precio": f"{res['precio']:.2f}",
                            "RSI": round(res['rsi'], 1),
                            "Filtro": res['decision'],
                            "Broker Recomendado": res['broker']
                        })
            if resultados:
                st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# PESTAÑA 2: BOT AUTOMÁTICO MASIVO
# ---------------------------------------------------------
with pestana2:
    st.subheader("🤖 Algoritmo de Gestión Autónoma")
    
    cartera_real_input = st.text_input("Excluir acciones que ya posees (ej: NVDA, ASML):", value="", key="excl_input").upper()
    exclusiones_reales = [t.strip() for t in cartera_real_input.split(",") if t.strip()]
    
    UNIVERSO_TOTAL = list(set(UNIVERSO_BASE_BOT + st.session_state.manual_tickers))
    UNIVERSO_FILTRADO = [t for t in UNIVERSO_TOTAL if t not in exclusiones_reales]
    
    if st.button("🔄 Refrescar Radar Global", key="ref_bot"):
        st.rerun()
        
    radar_data = []
    with st.spinner("Calculando señales técnicas del universo..."):
        for ticker in UNIVERSO_FILTRADO:
            data = analizar_activo(ticker)
            if data:
                abierto, estado_txt = comprobar_horario_mercado(ticker)
                data["mercado_abierto"] = abierto
                data["estado_mercado"] = estado_txt
                radar_data.append(data)
                
    if radar_data:
        df_radar = pd.DataFrame(radar_data)
        
        df_investing = pd.DataFrame({
            "Ticker": df_radar["ticker"],
            "Último": df_radar["precio"].map("{:,.2f}".format),
            "Var. %": df_radar["var"].map("{:+.2f}%".format),
            "Máx": df_radar["max"].map("{:,.2f}".format),
            "Mín": df_radar["min"].map("{:,.2f}".format),
            "Volumen": df_radar["vol"].map("{:,.0f}".format),
            "RSI": df_radar["rsi"].map("{:,.1f}".format),
            "Mercado": df_radar["estado_mercado"],
            "Filtro": df_radar["decision"]
        }).sort_values(by="Ticker")
        
        st.dataframe(df_investing, use_container_width=True, hide_index=True, height=600)
        
        # EJECUCIÓN SÓLO EN MERCADO ABIERTO
        for operativo in radar_data:
            if operativo["decision"] == "COMPRAR" and operativo["mercado_abierto"]:
                ya_comprada = any(pos["Ticker"] == operativo["ticker"] for pos in st.session_state.cartera_bot)
                if not ya_comprada and len(st.session_state.cartera_bot) < 10 and st.session_state.efectivo >= 3000:
                    st.session_state.cartera_bot.append({
                        "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Ticker": operativo["ticker"],
                        "Precio Ejecución": f"{operativo['precio']:.2f}",
                        "Capital": "3.000 €",
                        "RSI": round(operativo["rsi"], 1),
                        "Canal": operativo["broker"]
                    })
                    st.session_state.efectivo -= 3000
                    st.toast(f"🤖 Ejecutada compra automática de {operativo['ticker']}")
                    st.rerun()

    st.markdown("---")
    st.subheader("📊 Carteras y Métricas de Simulación")
    cm1, cm2, cm3 = st.columns(3)
    cm1.metric("Presupuesto Estrategia", "30.000 €")
    cm2.metric("Efectivo Disponible", f"{st.session_state.efectivo:,.2f} €")
    
    # Arreglado cálculo dinámico de longitud de cartera de forma segura
    pos_ocupadas = len(st.session_state.cartera_bot)
    cm3.metric("Posiciones Ocupadas", f"{pos_ocupadas} / 10")
    
    if st.session_state.cartera_bot:
        st.table(pd.DataFrame(st.session_state.cartera_bot))
        if st.button("🗑️ Reiniciar Historial Simulador", key="btn_reset_sim"):
            st.session_state.efectivo = 30000.0
            st.session_state.cartera_bot = []
            st.rerun()
    else:
        st.info("Ninguna posición abierta todavía. El bot aguarda entradas válidas.")

# ---------------------------------------------------------
# PESTAÑA 3: CONFIGURADOR DE LISTAS
# ---------------------------------------------------------
with pestana3:
    st.subheader("⚙️ Gestor de Listas de Seguimiento")
    
    lista_mod = st.selectbox("Selecciona la lista a editar:", list(st.session_state.listas_seguimiento.keys()), key="sb_mod")
    componentes = st.session_state.listas_seguimiento[lista_mod]
    
    st.text(f"Acciones en '{lista_mod}': {', '.join(componentes)}")
    
    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("##### ➕ Añadir Activo a Lista")
        t_add = st.text_input("Ticker a meter:", value="", key="t_add").upper().strip()
        if st.button("Añadir a Lista", key="btn_add_l"):
            if t_add and t_add not in componentes:
                st.session_state.listas_seguimiento[lista_mod].append(t_add)
                st.success(f"{t_add} añadido.")
                st.rerun()
                
    with col_b:
        st.markdown("##### ❌ Eliminar Activo de Lista")
        if componentes:
            t_del = st.selectbox("Ticker a quitar:", componentes, key="sb_del")
            if st.button("Eliminar de Lista", key="btn_del_l"):
                st.session_state.listas_seguimiento[lista_mod].remove(t_del)
                st.success(f"{t_del} eliminado.")
                st.rerun()
                
    with col_c:
        st.markdown("##### 🚀 Forzar Ticker Extra al Radar del Bot")
        t_bot = st.text_input("Ticker nuevo para el Bot:", value="", key="t_bot").upper().strip()
        if st.button("Inyectar al Radar", key="btn_add_b"):
            if t_bot and t_bot not in st.session_state.manual_tickers:
                st.session_state.manual_tickers.append(t_bot)
                st.success(f"{t_bot} inyectado al radar global.")
                st.rerun()
