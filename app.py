import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import json
import time
import numpy as np
import os

# ============================================================================
# PERSISTENCIA DE CARTERA
# ============================================================================
CARTERA_FILE = "cartera_guardada.json"
LISTAS_FILE = "listas_guardadas.json"
REGISTRO_FILE = "registro_semanal.json"

def cargar_cartera():
    """Carga la cartera desde archivo JSON si existe"""
    if os.path.exists(CARTERA_FILE):
        try:
            with open(CARTERA_FILE, 'r') as f:
                data = json.load(f)
            if data and len(data) > 0:
                return pd.DataFrame(data)
        except:
            pass
    return pd.DataFrame()

def guardar_cartera(df):
    """Guarda la cartera en archivo JSON"""
    try:
        df.to_json(CARTERA_FILE, orient='records', date_format='iso')
    except Exception as e:
        st.error(f"Error guardando cartera: {e}")

def cargar_listas():
    """Carga las listas personalizadas desde archivo JSON si existe"""
    if os.path.exists(LISTAS_FILE):
        try:
            with open(LISTAS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def guardar_listas(listas):
    """Guarda las listas en archivo JSON"""
    try:
        with open(LISTAS_FILE, 'w') as f:
            json.dump(listas, f, indent=2)
    except Exception as e:
        st.error(f"Error guardando listas: {e}")

def cargar_registro():
    """Carga el registro semanal desde archivo JSON si existe"""
    if os.path.exists(REGISTRO_FILE):
        try:
            with open(REGISTRO_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def guardar_registro(registro):
    """Guarda el registro semanal en archivo JSON"""
    try:
        with open(REGISTRO_FILE, 'w') as f:
            json.dump(registro, f, indent=2)
    except Exception as e:
        st.error(f"Error guardando registro: {e}")

# ============================================================================
# CONFIGURACION INICIAL
# ============================================================================
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Horizonte:** 4 Años | **Estilo:** Buy & Hold | **Foco:** Robótica & Tech")
st.write(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# ============================================================================
# LISTAS DEFINITIVAS
# ============================================================================

LISTAS_DEFINITIVAS = {
    "🤖 Robótica y Automatización": [
        "ABJ", "ABB", "FANUY", "SIEGY", "YASKY", "ROK", "AME", "FTV", "ETN", "EMR", "DOV",
        "ISRG", "TER", "CGNX", "NVMI", "PTC", "IRBT", "SYM", "DFKCY", "KIGRY",
        "TDY", "KEYS", "ZBRA", "SYK", "GMED", "PRCT", "DE", "CAT", "AGCO", "PCAR",
        "CMI", "ITW", "HON", "OCDO.L", "AUTO.OL"
    ],
    "🧠 IA y Semiconductores": [
        "NVDA", "AMD", "ARM", "AVGO", "TSM", "ASML", "LRCX", "KLAC", "AMAT",
        "ENTG", "MU", "PSTG", "ON", "ADI", "TXN", "NXPI", "MPWR", "STM",
        "MCHP", "ANET"
    ],
    "🛡️ Defensa y Drones": [
        "RTX", "LMT", "GD", "NOC", "GE", "AVAV", "KTOS", "LHX", "HII",
        "TXT", "CW", "BAH", "SAIC", "LDOS", "CACI", "AXON", "KBR", "BWXT"
    ],
    "⚡ Energía, Fotónica y Espacio": [
        "ENPH", "SEDG", "FSLR", "NEE", "HASI", "EVRG", "AES", "FLNC",
        "VST", "IPGP", "COHR", "LITE", "RKLB", "ASTS", "IRDM"
    ],
    "🧬 Biotecnología y Genómica": [
        "VRTX", "ILMN", "CRSP", "EDIT", "BEAM", "NTLA", "PACB", "EXAS",
        "TMO", "DHR", "RGEN", "ZTS", "INCY", "REGN", "MRNA", "LLY"
    ]
}

# Mapeo de tickers alternativos (broker-specific)
TICKER_ALIASES = {
    "ABJ": "ABB",
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def detectar_moneda(ticker):
    ticker_upper = ticker.upper().strip()
    sufijos_eur = ['.AS', '.PA', '.DE', '.BR', '.MI', '.MC', '.ST', '.HE', '.CO', '.OL', '.VI', '.LS', '.IR']
    for sufijo in sufijos_eur:
        if ticker_upper.endswith(sufijo):
            return 'EUR'
    if ticker_upper.endswith('.L') or ticker_upper.endswith('.LN'):
        return 'GBP'
    return 'USD'

def simbolo_moneda(moneda):
    simbolos = {'EUR': '€', 'USD': '$', 'GBP': '£', 'CHF': 'CHF', 'JPY': '¥', 'CAD': 'C$'}
    return simbolos.get(moneda, '$')

def comprobar_mercado_abierto():
    tz_ny = pytz.timezone('America/New_York')
    hora_ny = datetime.now(tz_ny)
    dia_semana = hora_ny.weekday()
    inicio_mercado = hora_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    fin_mercado = hora_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    return dia_semana <= 4 and inicio_mercado <= hora_ny <= fin_mercado

def calcular_rsi(historial, periodo=14):
    try:
        delta = historial['Close'].diff()
        ganancia = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
        perdida = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
        rs = ganancia / perdida
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    except:
        return 50

def calcular_beta(historial):
    try:
        ticker_spy = yf.Ticker("SPY")
        spy_hist = ticker_spy.history(period="6mo")
        if spy_hist.empty or len(spy_hist) < 50:
            return None
        common_dates = historial.index.intersection(spy_hist.index)
        if len(common_dates) < 30:
            return None
        stock_returns = historial.loc[common_dates, 'Close'].pct_change().dropna()
        spy_returns = spy_hist.loc[common_dates, 'Close'].pct_change().dropna()
        if len(stock_returns) < 30 or len(spy_returns) < 30:
            return None
        covariance = stock_returns.cov(spy_returns)
        spy_variance = spy_returns.var()
        if spy_variance == 0:
            return None
        beta = covariance / spy_variance
        return round(beta, 2)
    except:
        return None

@st.cache_data(ttl=300)
def obtener_info_segura(ticker):
    try:
        ticker_real = TICKER_ALIASES.get(ticker.upper(), ticker)
        t = yf.Ticker(ticker_real)
        info = t.info
        if not info or len(info) < 5:
            return None, None, detectar_moneda(ticker), None, None, None
        target = info.get('targetMedianPrice', None)
        dy = info.get('dividendYield', None)
        moneda = info.get('currency', detectar_moneda(ticker))
        pct_inst = info.get('heldPercentInstitutions', None)
        market_cap = info.get('marketCap', None)
        sector = info.get('sector', None)
        if dy is not None:
            if dy > 1.0:
                dy = dy / 100.0
            if dy > 0.10:
                dy = 0.0
        return target, dy, moneda, pct_inst, market_cap, sector
    except:
        return None, None, detectar_moneda(ticker), None, None, None

def descargar_datos_seguro(tickers, period="1y", interval=None, actions=False):
    if isinstance(tickers, list):
        tickers_resueltos = [TICKER_ALIASES.get(t.upper(), t) for t in tickers]
        tickers_str = " ".join(tickers_resueltos)
    else:
        tickers_str = TICKER_ALIASES.get(tickers.upper(), tickers)
        tickers = [tickers]
    try:
        kwargs = {"period": period, "progress": False, "group_by": "ticker"}
        if interval:
            kwargs["interval"] = interval
        if actions:
            kwargs["actions"] = True
        datos = yf.download(tickers_str, **kwargs)
        if len(tickers) == 1 and isinstance(datos.columns, pd.Index):
            ticker = tickers[0]
            datos.columns = pd.MultiIndex.from_product([[ticker], datos.columns])
        return datos
    except Exception as e:
        st.error(f"Error descargando datos batch: {e}")
        return pd.DataFrame()

def extraer_historial(datos_globales, ticker, period="1y"):
    try:
        if not datos_globales.empty:
            niveles = datos_globales.columns.get_level_values(0)
            if ticker in niveles:
                historial = datos_globales[ticker].dropna()
                if not historial.empty:
                    return historial
    except:
        pass
    try:
        ticker_real = TICKER_ALIASES.get(ticker.upper(), ticker)
        t = yf.Ticker(ticker_real)
        historial = t.history(period=period, actions=True)
        return historial
    except:
        return pd.DataFrame()

def extraer_precio_actual(datos_minuto, ticker, historial):
    try:
        if not datos_minuto.empty:
            niveles = datos_minuto.columns.get_level_values(0)
            if ticker in niveles:
                precio = datos_minuto[ticker]['Close'].dropna()
                if len(precio) > 0:
                    ultimo = precio.iloc[-1]
                    if pd.notna(ultimo) and float(ultimo) > 0:
                        return float(ultimo)
    except:
        pass
    try:
        if not historial.empty:
            precio = historial['Close'].iloc[-1]
            if pd.notna(precio) and float(precio) > 0:
                return float(precio)
    except:
        pass
    return None

def calcular_dividend_yield(historial, precio_actual, ticker):
    try:
        _, dy, _, _, _, _ = obtener_info_segura(ticker)
        if dy is not None and dy > 0:
            return dy
    except:
        pass
    try:
        if 'Dividends' in historial.columns and precio_actual > 0:
            dividendos_anuales = historial['Dividends'].tail(252).sum()
            if dividendos_anuales > 0:
                dy_calc = dividendos_anuales / precio_actual
                return min(dy_calc, 0.10)
    except:
        pass
    return 0

def formatear_dividendo(dy):
    if dy is None or dy == 0:
        return "❌ 0%"
    return f"💰 {dy * 100:.2f}%"

def formatear_market_cap(mc):
    if mc is None:
        return "N/A"
    if mc >= 1e12:
        return f"{mc/1e12:.2f}T"
    elif mc >= 1e9:
        return f"{mc/1e9:.2f}B"
    elif mc >= 1e6:
        return f"{mc/1e6:.2f}M"
    return f"{mc:.0f}"

def formatear_pnl(ganancia_valor, ganancia_pct, moneda='USD'):
    sym = simbolo_moneda(moneda)
    if ganancia_valor > 0:
        return f"🟩 +{ganancia_valor:.2f} {sym} (+{ganancia_pct:.2f}%)"
    elif ganancia_valor < 0:
        return f"🟥 {ganancia_valor:.2f} {sym} ({ganancia_pct:.2f}%)"
    return f"⬜ 0.00 {sym} (0.00%)"

def calcular_dias_candado(fecha_candado_str):
    try:
        fecha_candado = datetime.strptime(fecha_candado_str.replace('🔒 ', '').strip(), '%d/%m/%Y')
        hoy = datetime.now()
        dias = (fecha_candado - hoy).days
        return dias
    except:
        return -999

def esta_candado_liberado(fecha_candado_str):
    return calcular_dias_candado(fecha_candado_str) <= 0

def generar_veredicto(fila):
    try:
        ticker = str(fila.get('Ticker', 'N/A'))
        potencial_raw = fila.get('Potencial 4Años', '0%')
        if isinstance(potencial_raw, str):
            potencial = float(potencial_raw.replace('%', '').strip()) if '%' in potencial_raw else 0
        else:
            potencial = float(potencial_raw) if pd.notna(potencial_raw) else 0
        ratio_rb = str(fila.get('Ratio R:B', '1 : 1.0'))
        rb_valor = 1.0
        try:
            if ':' in ratio_rb:
                partes = ratio_rb.split(':')
                if len(partes) > 1:
                    rb_valor = float(partes[1].strip().split()[0])
        except:
            rb_valor = 1.0
        veredictos = []
        if potencial > 100:
            veredictos.append("🚀 Potencial explosivo")
        elif potencial > 50:
            veredictos.append("📈 Alto potencial")
        elif potencial > 20:
            veredictos.append("📊 Potencial moderado")
        else:
            veredictos.append("⚠️ Potencial limitado")
        if rb_valor > 3:
            veredictos.append("excelente R:B")
        elif rb_valor > 1.5:
            veredictos.append("buen R:B")
        else:
            veredictos.append("R:B ajustado")
        return " | ".join(veredictos)
    except Exception as e:
        return f"⚠️ Error: {str(e)[:30]}"

def analizar_cartera_global(df):
    if df.empty:
        return []
    recomendaciones = []
    potenciales = []
    for _, fila in df.iterrows():
        try:
            pot_raw = fila.get('Potencial 4Años', '0%')
            if isinstance(pot_raw, str):
                p = float(pot_raw.replace('%', '').strip()) if '%' in pot_raw else 0
            else:
                p = float(pot_raw) if pd.notna(pot_raw) else 0
            potenciales.append(p)
        except:
            pass
    potencial_medio = sum(potenciales) / len(potenciales) if potenciales else 0
    if potencial_medio > 80:
        recomendaciones.append(f"✅ **Potencial medio del {potencial_medio:.0f}%**: Cartera muy agresiva.")
    elif potencial_medio > 40:
        recomendaciones.append(f"⚖️ **Potencial medio del {potencial_medio:.0f}%**: Balance crecimiento/seguridad.")
    else:
        recomendaciones.append(f"🛡️ **Potencial medio del {potencial_medio:.0f}%**: Cartera conservadora.")
    candados_proximos = []
    for _, fila in df.iterrows():
        candado = str(fila.get('Candado', ''))
        dias = calcular_dias_candado(candado)
        if 0 < dias <= 14:
            candados_proximos.append(f"{fila['Ticker']} ({dias}d)")
    if candados_proximos:
        recomendaciones.append(f"🔓 **Candados próximos:** {', '.join(candados_proximos)}")
    sectores = set()
    for tick in df['Ticker'].tolist():
        try:
            _, _, _, _, _, sector = obtener_info_segura(tick)
            if sector:
                sectores.add(sector)
        except:
            pass
    if len(sectores) >= 3:
        recomendaciones.append(f"🔄 **Diversificación en {len(sectores)} sectores.**")
    else:
        recomendaciones.append(f"🎯 **Concentrado en pocos sectores:** Alta correlación.")
    recomendaciones.append("---")
    recomendaciones.append("**💡 Próximos pasos:**")
    recomendaciones.append("• Mantén el candado de 90 días. No tomes decisiones impulsivas.")
    recomendaciones.append("• Revisa esta cartera una vez por semana, no diariamente.")
    return recomendaciones

# ============================================================================
# DETECCION DE CAIDA VIOLENTA (FALLING KNIFE)
# ============================================================================

def detectar_caida_violenta(historial, precio_actual):
    """
    Detecta si hay una caída violenta reciente que debería bloquear compras.
    Devuelve: (es_peligroso, motivo, severidad)
    severidad: 0=normal, 1=alerta, 2=peligro, 3=extremo
    """
    try:
        # Caída del día vs cierre anterior
        precio_ayer = historial['Close'].iloc[-2]
        cambio_hoy = ((precio_actual - precio_ayer) / precio_ayer) * 100

        # Caída vs máximo reciente (20 días)
        maximo_20d = historial['Close'].iloc[-20:].max()
        caida_vs_max = ((precio_actual - maximo_20d) / maximo_20d) * 100

        # Volumen de hoy vs media
        volumen_hoy = historial['Volume'].iloc[-1]
        media_volumen_20 = historial['Volume'].iloc[-21:-1].mean()
        ratio_volumen = volumen_hoy / media_volumen_20 if media_volumen_20 > 0 else 1

        # CRITERIO 1: Caída diaria extrema
        if cambio_hoy < -10:
            if ratio_volumen > 2.5:
                return True, f"CAIDA VIOLENTA: {cambio_hoy:.1f}% hoy con volumen x{ratio_volumen:.1f} (pánico institucional)", 3
            else:
                return True, f"CAIDA EXTREMA: {cambio_hoy:.1f}% en un día", 3
        elif cambio_hoy < -7:
            if ratio_volumen > 2.0:
                return True, f"CAIDA FUERTE: {cambio_hoy:.1f}% con volumen x{ratio_volumen:.1f}", 2
            else:
                return True, f"CAIDA FUERTE: {cambio_hoy:.1f}%", 2
        elif cambio_hoy < -5:
            return True, f"CAIDA SIGNIFICATIVA: {cambio_hoy:.1f}%", 1

        # CRITERIO 2: Caída acelerada vs máximo reciente
        if caida_vs_max < -20 and cambio_hoy < -3:
            return True, f"EN CAIDA LIBRE: -{abs(caida_vs_max):.1f}% desde máximo 20d, hoy {cambio_hoy:.1f}%", 2

        # CRITERIO 3: Ruptura de soporte (precio bajo mínimo 20 días)
        minimo_20d = historial['Close'].iloc[-20:].min()
        if precio_actual < minimo_20d * 0.98 and cambio_hoy < -3:
            return True, f"RUPTURA DE SOPORTE: rompió mínimo 20d con {cambio_hoy:.1f}%", 2

        return False, "", 0

    except Exception as e:
        return False, "", 0

# ============================================================================
# FUNCION DE SCORING UNIFICADA
# ============================================================================

def calcular_score_unificado(precio_actual, media_30, media_200, crecimiento_porcentaje, 
                             potencial_4a, tiene_target, ratio_rb_calc, div_yield, 
                             rsi_valor, beta_valor, fuerza_volumen, historial=None):
    """
    Calcula el score de forma unificada para Bot y Analizador.
    Si se pasa historial, detecta caídas violentas.
    Devuelve: (score, status, motivos_list, alerta_caida)
    """
    # DETECTAR CAIDA VIOLENTA PRIMERO
    alerta_caida = None
    if historial is not None:
        es_peligroso, motivo_caida, severidad = detectar_caida_violenta(historial, precio_actual)
        if es_peligroso:
            alerta_caida = motivo_caida
            # Si es caída extrema, devolver score 0 y status de peligro
            if severidad >= 2:
                return 0, "🔴 NO COMPRAR", [motivo_caida], alerta_caida

    score = 0
    motivos = []

    # Tendencia alcista (2 puntos)
    if precio_actual > media_200:
        score += 2
        motivos.append("Tendencia alcista")

    # Momentum (1 punto)
    if precio_actual > (media_30 * 0.98):
        score += 1
        motivos.append("Momentum positivo")

    # Crecimiento reciente (3 puntos)
    if crecimiento_porcentaje >= 20.0:
        score += 3
        motivos.append("Crecimiento fuerte")
    elif crecimiento_porcentaje >= 10.0:
        score += 1
        motivos.append("Crecimiento moderado")

    # Potencial (2 puntos) - diferenciado según disponibilidad de target
    if tiene_target:
        if potencial_4a >= 50:
            score += 2
            motivos.append("Alto potencial")
        elif potencial_4a >= 20:
            score += 1
            motivos.append("Potencial moderado")
    else:
        if potencial_4a >= 30:
            score += 2
            motivos.append("Momentum técnico fuerte")
        elif potencial_4a >= 15:
            score += 1
            motivos.append("Momentum técnico moderado")

    # R:B favorable (2 puntos)
    if ratio_rb_calc >= 2.0:
        score += 2
        motivos.append("Excelente R:B")
    elif ratio_rb_calc >= 1.0:
        score += 1
        motivos.append("Buen R:B")

    # Volumen (1 punto)
    if fuerza_volumen == "🔥 ALTO":
        score += 1
        motivos.append("Volumen alto")

    # Dividendo (1 punto)
    if div_yield and div_yield > 0:
        score += 1
        motivos.append("Con dividendo")

    # RSI penalización reforzada
    if rsi_valor > 70:
        score -= 3
        motivos.append(f"⚠️ RSI {rsi_valor:.0f} SOBRECOMPRA (-3)")
    elif rsi_valor > 65:
        score -= 1
        motivos.append(f"⚡ RSI {rsi_valor:.0f} elevado (-1)")
    elif rsi_valor < 30:
        score += 1
        motivos.append(f"RSI {rsi_valor:.0f} sobreventa (+1)")

    # Beta penalización
    if beta_valor is not None and beta_valor > 2.5:
        score -= 1
        motivos.append(f"Beta {beta_valor} muy alto (-1)")

    score = max(0, score)

    # Status según score
    if score >= 8:
        status = "🟢 COMPRAR"
    elif score >= 5:
        status = "🟡 ACUMULAR"
    elif score >= 3:
        status = "🟠 OBSERVAR"
    else:
        status = "🔴 ESPERAR"

    return score, status, motivos, alerta_caida

# ============================================================================
# INICIALIZACION DE SESSION STATE
# ============================================================================

if "listas_guardadas" not in st.session_state:
    listas_persistidas = cargar_listas()
    if listas_persistidas:
        st.session_state.listas_guardadas = listas_persistidas
    else:
        st.session_state.listas_guardadas = LISTAS_DEFINITIVAS.copy()

if "cartera_compras" not in st.session_state:
    st.session_state.cartera_compras = cargar_cartera()

PARAMS_DEFAULT = {
    "capital_total": 30000,
    "max_por_accion": 1000,
    "tope_semanal": 5000,
    "max_compras_semanal": 5,
    "max_activos_cartera": 10,
    "dias_candado": 90,
    "umbral_sustitucion": 1.5
}

if "params_bot" not in st.session_state:
    st.session_state.params_bot = PARAMS_DEFAULT.copy()
else:
    for key, val in PARAMS_DEFAULT.items():
        if key not in st.session_state.params_bot:
            st.session_state.params_bot[key] = val

if "registro_semanal" not in st.session_state:
    st.session_state.registro_semanal = cargar_registro()

semana_actual = datetime.now().strftime("%Y-W%U")
if semana_actual not in st.session_state.registro_semanal:
    st.session_state.registro_semanal[semana_actual] = {
        "compras_realizadas": 0,
        "gastado": 0.0,
        "tickers_comprados": []
    }

def get_registro_semana_actual():
    semana = datetime.now().strftime("%Y-W%U")
    if semana not in st.session_state.registro_semanal:
        st.session_state.registro_semanal[semana] = {
            "compras_realizadas": 0,
            "gastado": 0.0,
            "tickers_comprados": []
        }
    return st.session_state.registro_semanal[semana]

def puede_comprar_esta_semana(cantidad=1, costo=1000):
    datos = get_registro_semana_actual()
    tope = st.session_state.params_bot["tope_semanal"]
    max_compras = st.session_state.params_bot["max_compras_semanal"]
    if datos["gastado"] + costo > tope:
        return False, f"Tope semanal: {datos['gastado']:.0f}/{tope}"
    if datos["compras_realizadas"] + cantidad > max_compras:
        return False, f"Máx {max_compras} compras: {datos['compras_realizadas']}/{max_compras}"
    return True, "OK"

def registrar_compra(ticker, costo=1000):
    datos = get_registro_semana_actual()
    datos["compras_realizadas"] += 1
    datos["gastado"] += costo
    datos["tickers_comprados"].append(ticker)
    guardar_registro(st.session_state.registro_semanal)

# ============================================================================
# MENU DE PESTANAS
# ============================================================================
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# ============================================================================
# PESTANA 1: BOT MASIVO AUTOMATICO 30K
# ============================================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente - Horizonte 4 Años")

    mercado_activo = comprobar_mercado_abierto()
    if mercado_activo:
        st.success("🟢 MERCADO ABIERTO")
    else:
        st.info("🕒 MERCADO CERRADO: Análisis con últimos datos disponibles.")

    st.write("#### 🛡️ Reglas de Gestión Monetaria")
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    with col_r1:
        max_por_accion = st.number_input(
            "Capital por operación:", min_value=100, max_value=5000, 
            value=st.session_state.params_bot["max_por_accion"], step=100, key="input_max"
        )
        st.session_state.params_bot["max_por_accion"] = max_por_accion
    with col_r2:
        tope_semanal = st.slider(
            "Tope semanal:", min_value=1000, max_value=30000, 
            value=st.session_state.params_bot["tope_semanal"], step=1000, key="slider_tope"
        )
        st.session_state.params_bot["tope_semanal"] = tope_semanal
    with col_r3:
        max_activos = st.number_input(
            "Máx. activos:", min_value=1, max_value=30, 
            value=st.session_state.params_bot["max_activos_cartera"], step=1, key="input_max_act"
        )
        st.session_state.params_bot["max_activos_cartera"] = max_activos
    with col_r4:
        max_compras_sem = st.number_input(
            "Máx. compras/semana:", min_value=1, max_value=10,
            value=st.session_state.params_bot["max_compras_semanal"], step=1, key="input_max_comp"
        )
        st.session_state.params_bot["max_compras_semanal"] = max_compras_sem

    opciones_lista = ["🌍 TODAS LAS LISTAS"] + list(st.session_state.listas_guardadas.keys())
    lista_bot = st.selectbox(
        "Universo a analizar:",
        opciones_lista,
        key="select_lista_bot"
    )

    col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns([2, 1, 1, 1, 1])
    with col_btn1:
        ejecutar_bot = st.button("🔄 Ejecutar Bot")
    with col_btn2:
        if st.button("🗑️ Resetear Cartera"):
            st.session_state.cartera_compras = pd.DataFrame()
            st.session_state.registro_semanal = {}
            st.cache_data.clear()
            if os.path.exists(CARTERA_FILE):
                os.remove(CARTERA_FILE)
            if os.path.exists(REGISTRO_FILE):
                os.remove(REGISTRO_FILE)
            st.success("¡Cartera y registro reseteados!")
            time.sleep(1)
            st.rerun()
    with col_btn3:
        if st.button("🧹 Limpiar Duplicados"):
            if not st.session_state.cartera_compras.empty:
                antes = len(st.session_state.cartera_compras)
                st.session_state.cartera_compras = st.session_state.cartera_compras.drop_duplicates(
                    subset=['Ticker'], keep='last'
                ).reset_index(drop=True)
                guardar_cartera(st.session_state.cartera_compras)
                st.success(f"Eliminados {antes - len(st.session_state.cartera_compras)} duplicados.")
                st.rerun()
    with col_btn4:
        if not st.session_state.cartera_compras.empty:
            csv_cartera = st.session_state.cartera_compras.to_csv(index=False)
            st.download_button(
                label="📥 Exportar", data=csv_cartera,
                file_name="cartera_guardada.csv", mime="text/csv",
                key="export_cartera"
            )
        else:
            st.button("📥 Exportar", disabled=True, key="export_cartera_disabled")
    with col_btn5:
        archivo_cartera = st.file_uploader("📤 Importar CSV", type=["csv"], key="import_cartera", label_visibility="collapsed")
        if archivo_cartera is not None:
            try:
                df_import = pd.read_csv(archivo_cartera)
                if not df_import.empty:
                    st.session_state.cartera_compras = df_import
                    guardar_cartera(st.session_state.cartera_compras)
                    st.success(f"✅ Cartera importada: {len(df_import)} posiciones")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

    if ejecutar_bot:
        st.cache_data.clear()
        st.toast("Analizando universo...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        if lista_bot == "🌍 TODAS LAS LISTAS":
            # Combinar todas las listas, eliminar duplicados
            lista_tickers = []
            for lista in st.session_state.listas_guardadas.values():
                for t in lista:
                    if t not in lista_tickers:
                        lista_tickers.append(t)
            st.info(f"🌍 Analizando {len(lista_tickers)} tickers de todas las listas")
        else:
            lista_tickers = st.session_state.listas_guardadas[lista_bot]

        if not lista_tickers:
            st.error("Lista vacía.")
        else:
            status_text.text("📥 Descargando datos históricos...")
            datos_globales = descargar_datos_seguro(lista_tickers, period="1y", actions=True)
            progress_bar.progress(20)

            status_text.text("📥 Descargando datos recientes...")
            datos_minuto = descargar_datos_seguro(lista_tickers, period="1d", interval="1m")
            progress_bar.progress(40)

            resultados_analisis = []
            total_tickers = len(lista_tickers)

            for idx, tick in enumerate(lista_tickers):
                progress = 40 + int((idx / total_tickers) * 40)
                progress_bar.progress(min(progress, 80))
                status_text.text(f"🔍 {tick}... ({idx+1}/{total_tickers})")

                try:
                    historial = extraer_historial(datos_globales, tick)
                    if historial.empty or len(historial) < 50:
                        resultados_analisis.append({
                            "Ticker": tick, "Status": "⚪ SIN DATOS", "Score": 0,
                            "Precio Actual": None, "Crecimiento Anual": 0,
                            "Potencial 4A": 0, "Ratio R:B": 0, "Dividendo": 0,
                            "RSI": "N/A", "Beta": "N/A", "Alerta Volatilidad": "",
                            "Volumen H.F.": "N/A",
                            "Moneda": detectar_moneda(tick),
                            "Simbolo": simbolo_moneda(detectar_moneda(tick)),
                            "Pct Institucional": None, "Market Cap": None,
                            "Sector": None, "Motivo": "Datos insuficientes"
                        })
                        continue

                    precio_actual = extraer_precio_actual(datos_minuto, tick, historial)
                    if precio_actual is None or precio_actual <= 0:
                        resultados_analisis.append({
                            "Ticker": tick, "Status": "⚪ SIN DATOS", "Score": 0,
                            "Precio Actual": None, "Crecimiento Anual": 0,
                            "Potencial 4A": 0, "Ratio R:B": 0, "Dividendo": 0,
                            "RSI": "N/A", "Beta": "N/A", "Alerta Volatilidad": "",
                            "Volumen H.F.": "N/A",
                            "Moneda": detectar_moneda(tick),
                            "Simbolo": simbolo_moneda(detectar_moneda(tick)),
                            "Pct Institucional": None, "Market Cap": None,
                            "Sector": None, "Motivo": "Precio no disponible"
                        })
                        continue

                    rsi_valor = calcular_rsi(historial)
                    beta_valor = calcular_beta(historial)

                    media_30 = historial['Close'].iloc[-30:].mean()
                    media_200 = historial['Close'].iloc[-200:].mean() if len(historial) >= 200 else media_30
                    p_minimo_50 = historial['Close'].iloc[-50:].min()
                    volumen_actual = historial['Volume'].iloc[-1]
                    media_volumen_20 = historial['Volume'].iloc[-21:-1].mean()

                    precio_hace_60d = historial['Close'].iloc[-60] if len(historial) >= 60 else historial['Close'].iloc[0]
                    crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                    crecimiento_porcentaje = max(0, round(crecimiento_precio, 1))

                    target_estimado, div_yield, moneda_detectada, pct_inst, market_cap, sector = obtener_info_segura(tick)

                    if div_yield is None or div_yield == 0:
                        div_yield = calcular_dividend_yield(historial, precio_actual, tick)

                    tiene_target = target_estimado is not None and target_estimado > 0

                    potencial_tecnico = crecimiento_porcentaje * 1.18

                    if tiene_target:
                        potencial_target = ((target_estimado - precio_actual) / precio_actual) * 100
                        if abs(potencial_target) > 200:
                            potencial_4a = potencial_tecnico
                            tiene_target = False
                        else:
                            potencial_4a = (potencial_tecnico + potencial_target) / 2
                    else:
                        potencial_4a = potencial_tecnico

                    potencial_4a = max(-50, min(potencial_4a, 200))

                    riesgo_suelo = ((precio_actual - p_minimo_50) / precio_actual) * 100
                    if riesgo_suelo <= 0:
                        riesgo_suelo = 0.1

                    ratio_rb_calc = min(potencial_4a / riesgo_suelo, 10.0)
                    fuerza_volumen = "🔥 ALTO" if volumen_actual > (media_volumen_20 * 1.15) else "🟢 NORMAL"

                    alerta_vol = ""
                    if beta_valor is not None and beta_valor > 2.0:
                        alerta_vol = "⚠️ BETA ALTO"
                    elif beta_valor is not None and beta_valor > 1.5:
                        alerta_vol = "⚡ Volátil"

                    # SCORING UNIFICADO
                    score, status, motivos, alerta_caida = calcular_score_unificado(
                        precio_actual, media_30, media_200, crecimiento_porcentaje,
                        potencial_4a, tiene_target, ratio_rb_calc, div_yield,
                        rsi_valor, beta_valor, fuerza_volumen, historial
                    )

                    # La alerta de caída se muestra en la columna Motivo

                    sym = simbolo_moneda(moneda_detectada)

                    resultados_analisis.append({
                        "Ticker": tick,
                        "Status": status,
                        "Score": score,
                        "Precio Actual": precio_actual,
                        "Crecimiento Anual": crecimiento_porcentaje,
                        "Potencial 4A": potencial_4a,
                        "Ratio R:B": ratio_rb_calc,
                        "Dividendo": div_yield if div_yield else 0,
                        "RSI": f"{rsi_valor:.1f}",
                        "Beta": f"{beta_valor:.2f}" if beta_valor is not None else "N/A",
                        "Alerta Volatilidad": alerta_vol,
                        "Volumen H.F.": fuerza_volumen,
                        "Moneda": moneda_detectada,
                        "Simbolo": sym,
                        "Pct Institucional": pct_inst,
                        "Market Cap": market_cap,
                        "Sector": sector,
                        "Motivo": (f"🚨 {alerta_caida}; " if alerta_caida else "") + "; ".join(motivos) if motivos else (f"🚨 {alerta_caida}" if alerta_caida else "Sin fortalezas destacadas")
                    })
                except Exception as e:
                    resultados_analisis.append({
                        "Ticker": tick, "Status": "⚪ ERROR", "Score": 0,
                        "Precio Actual": None, "Crecimiento Anual": 0,
                        "Potencial 4A": 0, "Ratio R:B": 0, "Dividendo": 0,
                        "RSI": "N/A", "Beta": "N/A", "Alerta Volatilidad": "",
                        "Volumen H.F.": "N/A",
                        "Moneda": detectar_moneda(tick),
                        "Simbolo": simbolo_moneda(detectar_moneda(tick)),
                        "Pct Institucional": None, "Market Cap": None,
                        "Sector": None, "Motivo": f"Error: {str(e)[:30]}"
                    })

            progress_bar.progress(85)
            status_text.text("💼 Procesando resultados...")

            df_resultados = pd.DataFrame(resultados_analisis)
            df_resultados = df_resultados.sort_values(by="Score", ascending=False)

            st.write("#### 📊 Resultados del Análisis Completo")
            st.write(f"**{len(df_resultados)} activos analizados**")

            cols_mostrar = ["Ticker", "Status", "Score", "Precio Actual", "Crecimiento Anual", 
                           "Potencial 4A", "Ratio R:B", "Dividendo", "RSI", "Beta", 
                           "Alerta Volatilidad", "Volumen H.F.", "Motivo"]
            cols_existentes = [c for c in cols_mostrar if c in df_resultados.columns]
            st.dataframe(df_resultados[cols_existentes], use_container_width=True)

            # COMPRA: SOLO LAS 🟢 COMPRAR (Score >= 8)
            df_candidatas = df_resultados[df_resultados["Status"] == "🟢 COMPRAR"].sort_values(by="Score", ascending=False)

            puede_comprar, msg = puede_comprar_esta_semana()
            if not puede_comprar:
                st.warning(f"🛑 {msg}")
            else:
                cartera_actual = st.session_state.cartera_compras
                tickers_en_cartera = set(cartera_actual["Ticker"].tolist()) if not cartera_actual.empty else set()
                activos_actuales = len(cartera_actual) if not cartera_actual.empty else 0
                cupo_libre = max_activos - activos_actuales

                capital_total = st.session_state.params_bot["capital_total"]
                invertido_total = cartera_actual["Capital Invertido Base"].sum() if not cartera_actual.empty else 0
                caja_libre = capital_total - invertido_total

                posiciones_nuevas = []
                posiciones_sustituidas = []

                for _, fila in df_candidatas.iterrows():
                    puede, msg = puede_comprar_esta_semana(cantidad=1, costo=max_por_accion)
                    if not puede:
                        break

                    if caja_libre < max_por_accion:
                        st.info(f"🛑 Caja insuficiente: {caja_libre:.2f}")
                        break

                    if fila["Ticker"] in tickers_en_cartera:
                        continue

                    if cupo_libre > 0:
                        caja_libre -= max_por_accion
                        cupo_libre -= 1

                        fecha_compra = datetime.now().strftime('%d/%m/%Y')
                        fecha_liberacion = (datetime.now() + timedelta(days=st.session_state.params_bot["dias_candado"])).strftime('%d/%m/%Y')
                        precio = fila["Precio Actual"]
                        cantidad = round(max_por_accion / precio, 4)

                        posiciones_nuevas.append({
                            "Ticker": fila["Ticker"],
                            "Acciones": cantidad,
                            "Precio Entrada Base": precio,
                            "Precio Entrada": f"{precio:.2f} {fila['Simbolo']}",
                            "Crecimiento Business": f"🚀 {fila['Crecimiento Anual']:.1f}%",
                            "Potencial 4Años": f"{fila['Potencial 4A']:.1f}%",
                            "Ratio R:B": f"1 : {fila['Ratio R:B']:.1f}",
                            "Dividendo": formatear_dividendo(fila["Dividendo"]),
                            "RSI": fila["RSI"],
                            "Beta": fila["Beta"],
                            "Alerta Volatilidad": fila["Alerta Volatilidad"],
                            "Volumen H.F.": fila["Volumen H.F."],
                            "Interés Inst.": "🎯 FUERTE" if fila["Pct Institucional"] and fila["Pct Institucional"] > 0.5 else "🎯 MODERADO" if fila["Pct Institucional"] else "🎯 DÉBIL",
                            "Pct Institucional": f"{fila['Pct Institucional']*100:.1f}%" if fila['Pct Institucional'] else "N/A",
                            "Market Cap": formatear_market_cap(fila["Market Cap"]),
                            "Capital Invertido Base": max_por_accion,
                            "Capital Invertido": f"{max_por_accion:.2f} {fila['Simbolo']}",
                            "Fecha Compra": fecha_compra,
                            "Candado": f"🔒 {fecha_liberacion}",
                            "Moneda": fila["Moneda"]
                        })
                        registrar_compra(fila["Ticker"], max_por_accion)

                    else:
                        hoy = datetime.now()
                        peor_rb = 999.0
                        peor_idx = None

                        for idx_c, row_c in cartera_actual.iterrows():
                            if esta_candado_liberado(str(row_c.get('Candado', ''))):
                                rb_str = str(row_c.get('Ratio R:B', '1 : 1.0'))
                                try:
                                    if ':' in rb_str:
                                        rb_val = float(rb_str.split(':')[1].strip().split()[0])
                                        if rb_val < peor_rb:
                                            peor_rb = rb_val
                                            peor_idx = idx_c
                                except:
                                    pass

                        if peor_idx is not None:
                            rb_candidato = fila["Ratio R:B"]
                            umbral = st.session_state.params_bot["umbral_sustitucion"]

                            if rb_candidato > peor_rb * umbral:
                                ticker_vendido = cartera_actual.loc[peor_idx, 'Ticker']
                                capital_liberado = cartera_actual.loc[peor_idx, 'Capital Invertido Base']

                                cartera_actual = cartera_actual.drop(peor_idx).reset_index(drop=True)
                                st.session_state.cartera_compras = cartera_actual
                                tickers_en_cartera = set(cartera_actual["Ticker"].tolist()) if not cartera_actual.empty else set()

                                caja_libre += capital_liberado - max_por_accion

                                fecha_compra = datetime.now().strftime('%d/%m/%Y')
                                fecha_liberacion = (datetime.now() + timedelta(days=st.session_state.params_bot["dias_candado"])).strftime('%d/%m/%Y')
                                precio = fila["Precio Actual"]
                                cantidad = round(max_por_accion / precio, 4)

                                posiciones_nuevas.append({
                                    "Ticker": fila["Ticker"],
                                    "Acciones": cantidad,
                                    "Precio Entrada Base": precio,
                                    "Precio Entrada": f"{precio:.2f} {fila['Simbolo']}",
                                    "Crecimiento Business": f"🚀 {fila['Crecimiento Anual']:.1f}%",
                                    "Potencial 4Años": f"{fila['Potencial 4A']:.1f}%",
                                    "Ratio R:B": f"1 : {fila['Ratio R:B']:.1f}",
                                    "Dividendo": formatear_dividendo(fila["Dividendo"]),
                                    "RSI": fila["RSI"],
                                    "Beta": fila["Beta"],
                                    "Alerta Volatilidad": fila["Alerta Volatilidad"],
                                    "Volumen H.F.": fila["Volumen H.F."],
                                    "Interés Inst.": "🎯 FUERTE" if fila["Pct Institucional"] and fila["Pct Institucional"] > 0.5 else "🎯 MODERADO" if fila["Pct Institucional"] else "🎯 DÉBIL",
                                    "Pct Institucional": f"{fila['Pct Institucional']*100:.1f}%" if fila['Pct Institucional'] else "N/A",
                                    "Market Cap": formatear_market_cap(fila["Market Cap"]),
                                    "Capital Invertido Base": max_por_accion,
                                    "Capital Invertido": f"{max_por_accion:.2f} {fila['Simbolo']}",
                                    "Fecha Compra": fecha_compra,
                                    "Candado": f"🔒 {fecha_liberacion}",
                                    "Moneda": fila["Moneda"]
                                })
                                posiciones_sustituidas.append((ticker_vendido, fila["Ticker"]))
                                registrar_compra(fila["Ticker"], max_por_accion)
                            else:
                                break
                        else:
                            st.info("🔒 Cartera llena, ningún candado liberado.")
                            break

                if posiciones_nuevas:
                    df_nuevas = pd.DataFrame(posiciones_nuevas)
                    if st.session_state.cartera_compras.empty:
                        st.session_state.cartera_compras = df_nuevas
                    else:
                        st.session_state.cartera_compras = pd.concat(
                            [st.session_state.cartera_compras, df_nuevas], 
                            ignore_index=True
                        )
                    guardar_cartera(st.session_state.cartera_compras)

                    if posiciones_sustituidas:
                        for viejo, nuevo in posiciones_sustituidas:
                            st.success(f"🔄 Sustituido {viejo} → {nuevo}")
                    st.success(f"✅ {len(posiciones_nuevas)} posiciones. Semana: {get_registro_semana_actual()['compras_realizadas']}/{max_compras_sem}")
                else:
                    st.info("Sin nuevas posiciones esta semana.")

            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()

    # MOSTRAR CARTERA
    df_mostrar = st.session_state.cartera_compras.copy()
    capital_total = st.session_state.params_bot["capital_total"]
    caja_libre = capital_total
    gastado_semana = 0.0
    alerta_cupo = False

    if not df_mostrar.empty:
        invertido_total = df_mostrar["Capital Invertido Base"].sum()
        caja_libre = capital_total - invertido_total
        gastado_semana = get_registro_semana_actual()["gastado"]
        alerta_cupo = len(df_mostrar) >= max_activos

        lista_activos = df_mostrar["Ticker"].tolist()
        precios_vivos = {}

        with st.spinner("🔄 Actualizando precios..."):
            try:
                cotizaciones_batch = yf.download(" ".join(lista_activos), period="5d", interval="1d", group_by="ticker", progress=False)
                if len(lista_activos) == 1:
                    precios_vivos[lista_activos[0]] = float(cotizaciones_batch['Close'].iloc[-1])
                else:
                    for tick in lista_activos:
                        if tick in cotizaciones_batch.columns.levels[0]:
                            precios_vivos[tick] = float(cotizaciones_batch[tick]['Close'].iloc[-1])
            except:
                pass

        lista_pnl = []
        for _, fila in df_mostrar.iterrows():
            t = fila["Ticker"]
            p_entrada = fila["Precio Entrada Base"]
            n = fila["Acciones"]
            moneda = fila.get("Moneda", "USD")
            p_live = precios_vivos.get(t, p_entrada)
            ganancia_valor = (p_live - p_entrada) * n
            ganancia_pct = ((p_live - p_entrada) / p_entrada) * 100 if p_entrada > 0 else 0
            lista_pnl.append(formatear_pnl(ganancia_valor, ganancia_pct, moneda))

        df_mostrar["Rendimiento Actual (P&L)"] = lista_pnl

        try:
            df_mostrar["📝 Veredicto"] = df_mostrar.apply(generar_veredicto, axis=1)
        except:
            df_mostrar["📝 Veredicto"] = "⚠️ Pendiente"

        df_mostrar["Estado Candado"] = df_mostrar["Candado"].apply(
            lambda x: "🔓 LIBERADO" if esta_candado_liberado(x) else x
        )

    total_invertido = capital_total - caja_libre

    st.write("---")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Capital Total", f"{capital_total:,.0f}")
    c2.metric("Invertido", f"{total_invertido:,.2f}")
    c3.metric("Caja Libre", f"{caja_libre:,.2f}")
    c4.metric("Semanal", f"{gastado_semana:,.0f}/{tope_semanal:,.0f}")
    c5.metric("Compras Sem", f"{get_registro_semana_actual()['compras_realizadas']}/{max_compras_sem}")

    if alerta_cupo:
        st.warning(f"⚠️ Cupo máximo {max_activos} alcanzado.")

    st.write("---")
    st.write("### 📊 Cartera a 4 Años")
    if not df_mostrar.empty:
        cols = ["Ticker", "Acciones", "Precio Entrada", "Rendimiento Actual (P&L)", 
                "Crecimiento Business", "Potencial 4Años", "Ratio R:B", 
                "Dividendo", "RSI", "Beta", "Alerta Volatilidad", "Volumen H.F.", 
                "Interés Inst.", "Market Cap",
                "📝 Veredicto", "Estado Candado", "Capital Invertido", "Fecha Compra"]
        cols_existentes = [c for c in cols if c in df_mostrar.columns]
        st.dataframe(df_mostrar[cols_existentes], use_container_width=True)
    else:
        st.info("Cartera vacía. Ejecuta el bot.")

    if not df_mostrar.empty:
        st.write("---")
        st.write("### 🧠 Análisis de tu Cartera")
        try:
            for rec in analizar_cartera_global(df_mostrar):
                st.write(rec)
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
        st.info("📅 Revisa una vez por semana. No tomes decisiones impulsivas.")

# ============================================================================
# PESTANA 2: ANALIZADOR TECNICO
# ============================================================================
with pestaña2:
    st.subheader("🔍 Analizador de Oportunidades - Horizonte 4 Años")

    st.write("### 📈 Análisis Individual")
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        ticker_individual = st.text_input("Ticker:", value="", placeholder="Ej: NVDA, AMD, ARM...", key="ticker_individual")
    with col_btn:
        analizar_individual = st.button("🔍 Analizar", key="btn_analizar_individual")

    if analizar_individual and ticker_individual.strip():
        tick = ticker_individual.strip().upper()
        with st.spinner(f"Analizando {tick}..."):
            try:
                ticker_real = TICKER_ALIASES.get(tick, tick)
                h = yf.Ticker(ticker_real).history(period="1y")
                if h.empty or len(h) < 50:
                    st.error(f"No hay suficientes datos para {tick}")
                else:
                    p_actual = h['Close'].iloc[-1]
                    media_50 = h['Close'].iloc[-50:].mean()
                    media_200 = h['Close'].iloc[-200:].mean() if len(h) >= 200 else media_50
                    p_minimo_50 = h['Close'].iloc[-50:].min()

                    rsi_valor = calcular_rsi(h)
                    beta_valor = calcular_beta(h)

                    target_val, div_yield, moneda, pct_inst, market_cap, sector = obtener_info_segura(tick)

                    if div_yield is None or div_yield == 0:
                        div_yield = calcular_dividend_yield(h, p_actual, tick)

                    precio_60d = h['Close'].iloc[-60] if len(h) >= 60 else h['Close'].iloc[0]
                    crec_pct = ((p_actual - precio_60d) / precio_60d) * 100

                    tiene_target = target_val is not None and target_val > 0
                    potencial_tecnico = max(20.0, crec_pct * 1.12)

                    if tiene_target:
                        potencial_target = ((target_val - p_actual) / p_actual) * 100
                        if abs(potencial_target) > 200:
                            potencial_val = potencial_tecnico
                            tiene_target = False
                        else:
                            potencial_val = (potencial_tecnico + potencial_target) / 2
                    else:
                        potencial_val = potencial_tecnico

                    potencial_val = max(-50, min(potencial_val, 200))

                    riesgo = ((p_actual - p_minimo_50) / p_actual) * 100
                    if riesgo <= 0:
                        riesgo = 0.1
                    ratio_rb = min(potencial_val / riesgo, 10.0)

                    sym = simbolo_moneda(moneda)

                    # Volumen simplificado para análisis individual
                    fuerza_volumen_ind = "🟢 NORMAL"

                    # SCORING UNIFICADO (misma función que el Bot)
                    score, status, motivos, alerta_caida = calcular_score_unificado(
                        p_actual, media_50, media_200, crec_pct,
                        potencial_val, tiene_target, ratio_rb, div_yield,
                        rsi_valor, beta_valor, fuerza_volumen_ind, h
                    )

                    # La alerta de caída se muestra en el detalle de puntuación

                    alerta_vol = ""
                    if beta_valor is not None and beta_valor > 2.0:
                        alerta_vol = "⚠️ BETA ALTO"
                    elif beta_valor is not None and beta_valor > 1.5:
                        alerta_vol = "⚡ Volátil"

                    st.write("#### 📊 Evolución del Precio")
                    h['MA50'] = h['Close'].rolling(window=50).mean()
                    h['MA200'] = h['Close'].rolling(window=200).mean()
                    chart_data = pd.DataFrame({
                        'Precio': h['Close'],
                        'Media 50d': h['MA50'],
                        'Media 200d': h['MA200']
                    })
                    st.line_chart(chart_data, use_container_width=True)

                    st.write("#### 📋 Métricas Clave")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Precio Actual", f"{p_actual:.2f} {sym}")
                    c2.metric("Target", f"{target_val:.2f} {sym}" if target_val else "N/A (Modo Técnico)")
                    c3.metric("Potencial", f"{potencial_val:.1f}%")
                    c4.metric("Ratio R:B", f"1:{ratio_rb:.1f}")

                    c5, c6, c7, c8 = st.columns(4)
                    c5.metric("Media 50d", f"{media_50:.2f} {sym}")
                    c6.metric("Media 200d", f"{media_200:.2f} {sym}")
                    c7.metric("Dividendo", formatear_dividendo(div_yield))
                    c8.metric("RSI (14)", f"{rsi_valor:.1f}")

                    if beta_valor is not None:
                        c_beta = st.columns([1, 2, 1])[1]
                        with c_beta:
                            if beta_valor > 2.0:
                                st.error(f"**Beta: {beta_valor:.2f}** {alerta_vol}")
                            elif beta_valor > 1.5:
                                st.warning(f"**Beta: {beta_valor:.2f}** ⚡ Volátil")
                            else:
                                st.info(f"**Beta: {beta_valor:.2f}** ✅ Normal")

                    col_sem = st.columns([1, 2, 1])[1]
                    with col_sem:
                        if alerta_caida:
                            st.error(f"## 🚨 {alerta_caida}")
                            st.error("## 🔴 NO COMPRAR / PELIGRO")
                        elif score >= 8:
                            st.success("## 🟢 COMPRA FUERTE")
                        elif score >= 5:
                            st.warning("## 🟡 COMPRA MODERADA")
                        elif score >= 3:
                            st.warning("## 🟠 OBSERVAR")
                        else:
                            st.error("## 🔴 NO COMPRAR / ESPERAR")
                        st.write(f"**Score: {score}/11**")
                        motivos_display = [f"🚨 {alerta_caida}"] + motivos if alerta_caida else motivos
                        st.write(f"**Motivos:** {', '.join(motivos_display) if motivos_display else 'Sin fortalezas'}")

                    with st.expander("📋 Detalle de puntuación"):
                        st.write("**Puntuación:**")
                        st.write(f"• Tendencia (MA200): {'+2' if p_actual > media_200 else '0'}")
                        st.write(f"• Momentum (MA50): {'+1' if p_actual > media_50 else '0'}")
                        st.write(f"• Crecimiento 60d: {'+3' if crec_pct >= 20 else '+1' if crec_pct >= 10 else '0'}")
                        if tiene_target:
                            st.write(f"• Potencial (con target): {'+2' if potencial_val >= 50 else '+1' if potencial_val >= 20 else '0'}")
                        else:
                            st.write(f"• Potencial (técnico puro): {'+2' if potencial_val >= 30 else '+1' if potencial_val >= 15 else '0'}")
                        st.write(f"• R:B: {'+2' if ratio_rb >= 2 else '+1' if ratio_rb >= 1 else '0'}")
                        st.write(f"• Dividendo: {'+1' if div_yield and div_yield > 0 else '0'}")
                        st.write(f"• RSI: {'-3' if rsi_valor > 70 else '-1' if rsi_valor > 65 else '+1' if rsi_valor < 30 else '0'}")
                        st.write(f"• Beta: {'-1' if beta_valor and beta_valor > 2.5 else '0'}")
            except Exception as e:
                st.error(f"Error: {e}")

    st.write("---")
    st.write("### 📋 Análisis de Listas Pregrabadas")
    opciones_lista2 = ["Ninguna", "🌍 TODAS LAS LISTAS"] + list(st.session_state.listas_guardadas.keys())
    lista_sel = st.selectbox("Universo:", opciones_lista2, key="select_lista")

    if lista_sel != "Ninguna":
        if lista_sel == "🌍 TODAS LAS LISTAS":
            tickers_lista = []
            for lista in st.session_state.listas_guardadas.values():
                for t in lista:
                    if t not in tickers_lista:
                        tickers_lista.append(t)
            st.info(f"🌍 Analizando {len(tickers_lista)} tickers de todas las listas")
        else:
            tickers_lista = st.session_state.listas_guardadas[lista_sel]
        if tickers_lista:
            with st.spinner("Analizando..."):
                datos_globales_p2 = descargar_datos_seguro(tickers_lista, period="1y", actions=True)
                datos_lista = []

                barra = st.progress(0)
                tickers_unicos = list(dict.fromkeys(tickers_lista))
                total = len(tickers_unicos)

                for idx, tick in enumerate(tickers_unicos):
                    barra.progress(int((idx / total) * 100))
                    try:
                        h = extraer_historial(datos_globales_p2, tick)
                        if h.empty or len(h) < 50:
                            datos_lista.append({
                                "Ticker": tick, "Status": "⚪ SIN DATOS", "Score": 0,
                                "Precio": "N/A", "Target": "N/A", "Potencial": "N/A",
                                "R:B": "N/A", "Dividendo": "N/A", "RSI": "N/A",
                                "Beta": "N/A", "Alerta Volatilidad": "",
                                "Motivo": "Datos insuficientes"
                            })
                            continue

                        p_actual = h['Close'].iloc[-1]
                        p_media = h['Close'].iloc[-50:].mean()
                        p_minimo = h['Close'].iloc[-50:].min()
                        rsi_valor = calcular_rsi(h)
                        beta_valor = calcular_beta(h)

                        target_val, div_yield, moneda, pct_inst, market_cap, sector = obtener_info_segura(tick)

                        if div_yield is None or div_yield == 0:
                            div_yield = calcular_dividend_yield(h, p_actual, tick)

                        precio_60d = h['Close'].iloc[-60] if len(h) >= 60 else h['Close'].iloc[0]
                        crec_pct = ((p_actual - precio_60d) / precio_60d) * 100

                        tiene_target = target_val is not None and target_val > 0
                        potencial_tecnico = max(20.0, crec_pct * 1.12)

                        if tiene_target:
                            potencial_target = ((target_val - p_actual) / p_actual) * 100
                            if abs(potencial_target) > 200:
                                potencial_val = potencial_tecnico
                                tiene_target = False
                            else:
                                potencial_val = (potencial_tecnico + potencial_target) / 2
                        else:
                            potencial_val = potencial_tecnico

                        potencial_val = max(-50, min(potencial_val, 200))

                        riesgo = ((p_actual - p_minimo) / p_actual) * 100
                        if riesgo <= 0:
                            riesgo = 0.1
                        ratio_rb = min(potencial_val / riesgo, 10.0)

                        sym = simbolo_moneda(moneda)

                        # Volumen para listas
                        volumen_actual = h['Volume'].iloc[-1]
                        media_volumen_20 = h['Volume'].iloc[-21:-1].mean() if len(h) >= 21 else volumen_actual
                        fuerza_volumen_lst = "🔥 ALTO" if volumen_actual > (media_volumen_20 * 1.15) else "🟢 NORMAL"

                        # SCORING UNIFICADO (misma función exacta que el Bot)
                        score, status, motivos, alerta_caida = calcular_score_unificado(
                            p_actual, p_media, p_media, crec_pct,
                            potencial_val, tiene_target, ratio_rb, div_yield,
                            rsi_valor, beta_valor, fuerza_volumen_lst, h
                        )

                        alerta_vol = ""
                        if beta_valor is not None and beta_valor > 2.0:
                            alerta_vol = "⚠️ BETA ALTO"
                        elif beta_valor is not None and beta_valor > 1.5:
                            alerta_vol = "⚡ Volátil"

                        datos_lista.append({
                            "Ticker": tick, "Status": status, "Score": score,
                            "Precio": f"{p_actual:.2f} {sym}",
                            "Target": f"{target_val:.2f} {sym}" if target_val else "N/A",
                            "Potencial": f"{potencial_val:.1f}%",
                            "R:B": f"1:{ratio_rb:.1f}",
                            "Dividendo": formatear_dividendo(div_yield),
                            "RSI": f"{rsi_valor:.1f}",
                            "Beta": f"{beta_valor:.2f}" if beta_valor is not None else "N/A",
                            "Alerta Volatilidad": alerta_vol,
                            "Motivo": (f"🚨 {alerta_caida}; " if alerta_caida else "") + "; ".join(motivos) if motivos else (f"🚨 {alerta_caida}" if alerta_caida else "Sin fortalezas")
                        })
                    except Exception as e:
                        datos_lista.append({
                            "Ticker": tick, "Status": "⚪ ERROR", "Score": 0,
                            "Precio": "N/A", "Target": "N/A", "Potencial": "N/A",
                            "R:B": "N/A", "Dividendo": "N/A", "RSI": "N/A",
                            "Beta": "N/A", "Alerta Volatilidad": "",
                            "Motivo": f"Error: {str(e)[:30]}"
                        })

                barra.empty()

                if datos_lista:
                    df_lista = pd.DataFrame(datos_lista)
                    df_lista = df_lista.sort_values(by="Score", ascending=False)
                    st.write(f"**{len(df_lista)} activos analizados**")

                    # Destacar cuáles compraría el bot
                    df_comprar = df_lista[df_lista["Status"] == "🟢 COMPRAR"]
                    if not df_comprar.empty:
                        st.success(f"🟢 El Bot compraría: {', '.join(df_comprar['Ticker'].tolist())}")

                    st.dataframe(df_lista, use_container_width=True)
                else:
                    st.warning("No se pudieron analizar activos.")
        else:
            st.info("Lista vacía.")

# ============================================================================
# PESTANA 3: CONFIGURACION DE LISTAS
# ============================================================================
with pestaña3:
    st.subheader("⚙️ Gestión de Listas de Seguimiento")

    for nombre_lista, tickers_lista in list(st.session_state.listas_guardadas.items()):
        with st.expander(f"📋 {nombre_lista} ({len(tickers_lista)} tickers)"):
            st.write(f"**Tickers:** {', '.join(tickers_lista)}")

            st.write("**✏️ Editar tickers:**")

            col_del_sel, col_del_btn = st.columns([3, 1])
            with col_del_sel:
                ticker_a_eliminar = st.selectbox(
                    f"Eliminar:", tickers_lista, key=f"del_select_{nombre_lista}"
                )
            with col_del_btn:
                if st.button(f"🗑️ Eliminar", key=f"btn_del_{nombre_lista}"):
                    if ticker_a_eliminar in st.session_state.listas_guardadas[nombre_lista]:
                        st.session_state.listas_guardadas[nombre_lista].remove(ticker_a_eliminar)
                        guardar_listas(st.session_state.listas_guardadas)
                        st.success(f"🗑️ Eliminado {ticker_a_eliminar}")
                        st.rerun()

            col_add, col_add_btn = st.columns([3, 1])
            with col_add:
                nuevo_ticker = st.text_input(f"Añadir:", key=f"add_ticker_{nombre_lista}")
            with col_add_btn:
                if st.button(f"➕ Añadir", key=f"btn_add_{nombre_lista}"):
                    if nuevo_ticker and nuevo_ticker.strip().upper() not in [t.upper() for t in st.session_state.listas_guardadas[nombre_lista]]:
                        st.session_state.listas_guardadas[nombre_lista].append(nuevo_ticker.strip().upper())
                        guardar_listas(st.session_state.listas_guardadas)
                        st.success(f"➕ Añadido {nuevo_ticker.strip().upper()}")
                        st.rerun()
                    else:
                        st.error("Vacío o duplicado")

            st.write("---")
            col_edit, col_del = st.columns([1, 1])
            with col_edit:
                nuevo_nombre = st.text_input(f"Renombrar:", value=nombre_lista, key=f"rename_{nombre_lista}")
                if nuevo_nombre != nombre_lista and st.button(f"✅ Guardar", key=f"save_name_{nombre_lista}"):
                    st.session_state.listas_guardadas[nuevo_nombre] = st.session_state.listas_guardadas.pop(nombre_lista)
                    guardar_listas(st.session_state.listas_guardadas)
                    st.success(f"Renombrada a '{nuevo_nombre}'")
                    st.rerun()
            with col_del:
                if st.button(f"🗑️ Eliminar lista", key=f"del_{nombre_lista}"):
                    del st.session_state.listas_guardadas[nombre_lista]
                    guardar_listas(st.session_state.listas_guardadas)
                    st.success(f"Lista '{nombre_lista}' eliminada.")
                    st.rerun()

    st.write("---")
    st.write("### ➕ Crear Nueva Lista")
    nombre_nueva = st.text_input("Nombre:", key="nueva_lista_nombre")
    tickers_nueva = st.text_area("Tickers (separados por comas):", key="nueva_lista_tickers")

    if st.button("💾 Guardar", key="guardar_nueva"):
        if nombre_nueva and tickers_nueva:
            tickers_limpios = [t.strip().upper() for t in tickers_nueva.replace("\n", ",").split(",") if t.strip()]
            st.session_state.listas_guardadas[nombre_nueva] = tickers_limpios
            guardar_listas(st.session_state.listas_guardadas)
            st.success(f"✅ Lista '{nombre_nueva}' guardada ({len(tickers_limpios)} tickers).")
            st.rerun()
        else:
            st.error("Completa nombre y tickers.")

    st.write("---")
    st.write("### 📥 Importar/Exportar Listas")
    col_imp, col_exp = st.columns(2)
    with col_imp:
        archivo_subido = st.file_uploader("Subir JSON:", type=["json"], key="upload_json")
        if archivo_subido is not None:
            try:
                listas_importadas = json.load(archivo_subido)
                st.session_state.listas_guardadas.update(listas_importadas)
                guardar_listas(st.session_state.listas_guardadas)
                st.success("✅ Listas importadas.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    with col_exp:
        json_str = json.dumps(st.session_state.listas_guardadas, indent=2)
        st.download_button(
            label="📥 Descargar JSON",
            data=json_str,
            file_name="listas_permanentes.json",
            mime="application/json",
            key="download_json"
        )

st.write("---")
st.caption("Centro de Mando Financiero Pro v4.0 | Scoring Unificado + Persistencia | Streamlit + yFinance")
