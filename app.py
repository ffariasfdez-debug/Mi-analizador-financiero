import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import os
import json
import time

# ============================================================================
# 1. CONFIGURACIÓN INICIAL
# ============================================================================
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

ARCHIVO_CARTERA = "cartera_guardada.csv"
ARCHIVO_LISTAS = "listas_permanentes.json"

st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Horizonte:** 4 Años | **Estilo:** Buy & Hold | **Foco:** Robótica & Tech")
st.write(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# ============================================================================
# 2. FUNCIONES AUXILIARES
# ============================================================================

def detectar_moneda(ticker):
    ticker_upper = ticker.upper().strip()
    sufijos_eur = ['.AS', '.PA', '.DE', '.BR', '.MI', '.MC', '.ST', '.HE', '.CO', '.OL', '.VI', '.LS', '.IR']
    for sufijo in sufijos_eur:
        if ticker_upper.endswith(sufijo):
            return 'EUR'
    if ticker_upper.endswith('.L') or ticker_upper.endswith('.LN'):
        return 'GBP'
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if info and 'currency' in info:
            moneda = info['currency']
            if moneda in ['EUR', 'USD', 'GBP', 'CHF', 'JPY', 'CAD']:
                return moneda
    except:
        pass
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

@st.cache_data(ttl=300)
def obtener_info_segura(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info or len(info) < 5:
            return None, None, detectar_moneda(ticker), None, None, None, None
        target = info.get('targetMedianPrice', None)
        dy = info.get('dividendYield', None)
        moneda = info.get('currency', detectar_moneda(ticker))
        pct_inst = info.get('heldPercentInstitutions', None)
        num_inst = info.get('numberOfInstitutionalHolders', None)
        market_cap = info.get('marketCap', None)
        sector = info.get('sector', None)
        if dy is not None:
            if dy > 1.0:
                dy = dy / 100.0
            return target, dy, moneda, pct_inst, num_inst, market_cap, sector
        return target, None, moneda, pct_inst, num_inst, market_cap, sector
    except:
        return None, None, detectar_moneda(ticker), None, None, None, None

def descargar_datos_seguro(tickers, period="1y", interval=None, actions=False):
    if isinstance(tickers, list):
        tickers_str = " ".join(tickers)
    else:
        tickers_str = tickers
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
        st.error(f"Error descargando datos: {e}")
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
        t = yf.Ticker(ticker)
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
        _, dy, _, _, _, _, _ = obtener_info_segura(ticker)
        if dy is not None and dy > 0:
            return dy
    except:
        pass
    try:
        if 'Dividends' in historial.columns:
            dividendos_totales = historial['Dividends'].sum()
            if dividendos_totales > 0 and precio_actual > 0:
                return dividendos_totales / precio_actual
    except:
        pass
    return 0

def calcular_tendencia_volumen(historial):
    try:
        if len(historial) < 30:
            return "➡️ ESTABLE", 0
        vol_reciente = historial['Volume'].iloc[-10:].mean()
        vol_anterior = historial['Volume'].iloc[-20:-10].mean()
        cambio = ((vol_reciente - vol_anterior) / vol_anterior) * 100 if vol_anterior > 0 else 0
        if cambio > 15:
            return "📈 CRECIENDO", cambio
        elif cambio < -15:
            return "📉 DECAYENDO", cambio
        else:
            return "➡️ ESTABLE", cambio
    except:
        return "➡️ ESTABLE", 0

def calcular_interes_institucional(volumen_hf, pct_institucional, tendencia_vol, market_cap=None):
    puntos = 0

    # Volumen alto = +1 punto
    if volumen_hf == "🔥 ALTO":
        puntos += 1

    # Institucional > 50% (bajado de 60% porque Yahoo ya no da este dato fiable)
    if pct_institucional is not None and pct_institucional > 0.50:
        puntos += 1
    # Fallback: si no hay dato institucional pero el market cap es grande (>10B), asumimos interés institucional
    elif pct_institucional is None and market_cap is not None and market_cap > 10e9:
        puntos += 1

    # Volumen creciendo = +1 punto
    if "CRECIENDO" in tendencia_vol:
        puntos += 1

    if puntos >= 3:
        return "🎯 FUERTE"
    elif puntos >= 2:
        return "🎯 MODERADO"
    else:
        return "🎯 DÉBIL"

def generar_veredicto(fila):
    """
    Genera un veredicto contextual para cada acción basado en TODAS sus métricas.
    RECALCULA el interés institucional en tiempo real (no usa el valor guardado).
    """
    try:
        ticker = str(fila.get('Ticker', 'N/A'))

        # Potencial
        potencial_raw = fila.get('Potencial 4Años', fila.get('Potencial Estimado', '0%'))
        if isinstance(potencial_raw, str):
            potencial = float(potencial_raw.replace('%', '').strip()) if '%' in potencial_raw else 0
        else:
            potencial = float(potencial_raw) if pd.notna(potencial_raw) else 0

        # Ratio R:B
        ratio_rb = str(fila.get('Ratio R:B', '1 : 1.0'))
        rb_valor = 1.0
        try:
            if ':' in ratio_rb:
                partes = ratio_rb.split(':')
                if len(partes) > 1:
                    rb_valor = float(partes[1].strip().split()[0])
        except:
            rb_valor = 1.0

        # RECALCULAR interés institucional en tiempo real
        try:
            target, dy, moneda, pct_inst, num_inst, market_cap, sector = obtener_info_segura(ticker)
            # Usar market cap como proxy si no hay dato institucional
            if pct_inst is not None and pct_inst > 0.50:
                interes_txt = "instituciones acumulando"
            elif pct_inst is None and market_cap is not None and market_cap > 10e9:
                interes_txt = "interés estable"  # Grandes caps suelen tener institucionales
            else:
                interes_txt = "sin respaldo institucional"
        except:
            interes_txt = "sin respaldo institucional"

        # Crecimiento
        crecimiento_raw = fila.get('Crecimiento Business', '0%')
        if isinstance(crecimiento_raw, str):
            crecimiento = float(crecimiento_raw.replace('🚀 ', '').replace('%', '').strip()) if '%' in crecimiento_raw else 0
        else:
            crecimiento = float(crecimiento_raw) if pd.notna(crecimiento_raw) else 0

        veredictos = []

        # Análisis de potencial
        if potencial > 100:
            veredictos.append("🚀 Potencial explosivo")
        elif potencial > 50:
            veredictos.append("📈 Alto potencial")
        elif potencial > 20:
            veredictos.append("📊 Potencial moderado")
        else:
            veredictos.append("⚠️ Potencial limitado")

        # Análisis institucional (RECALCULADO)
        veredictos.append(interes_txt)

        # Análisis riesgo/beneficio
        if rb_valor > 3:
            veredictos.append("excelente R:B")
        elif rb_valor > 1.5:
            veredictos.append("buen R:B")
        else:
            veredictos.append("R:B ajustado")

        return " | ".join(veredictos)
    except Exception as e:
        return f"⚠️ Error análisis: {str(e)[:30]}"

def analizar_cartera_global(df):
    """
    Analiza la cartera completa y genera recomendaciones específicas.
    """
    if df.empty:
        return []
    
    recomendaciones = []
    tickers = df['Ticker'].tolist()
    
    # Análisis de potencial medio
    potenciales = []
    for _, fila in df.iterrows():
        try:
            pot_raw = fila.get('Potencial 4Años', fila.get('Potencial Estimado', '0%'))
            if isinstance(pot_raw, str):
                p = float(pot_raw.replace('%', '').strip()) if '%' in pot_raw else 0
            else:
                p = float(pot_raw) if pd.notna(pot_raw) else 0
            potenciales.append(p)
        except:
            pass
    
    potencial_medio = sum(potenciales) / len(potenciales) if potenciales else 0
    
    if potencial_medio > 80:
        recomendaciones.append(f"✅ **Potencial medio del {potencial_medio:.0f}%**: Cartera muy agresiva y orientada a crecimiento. Adecuada para tu horizonte de 4 años.")
    elif potencial_medio > 40:
        recomendaciones.append(f"⚖️ **Potencial medio del {potencial_medio:.0f}%**: Balance entre crecimiento y seguridad.")
    else:
        recomendaciones.append(f"🛡️ **Potencial medio del {potencial_medio:.0f}%**: Cartera conservadora. Considera añadir más tech/robótica.")
    
    # Análisis de institucional
    fuertes = sum(1 for _, f in df.iterrows() if "FUERTE" in str(f.get('Interés Inst.', f.get('Interes Inst.', ''))))
    moderados = sum(1 for _, f in df.iterrows() if "MODERADO" in str(f.get('Interés Inst.', f.get('Interes Inst.', ''))))
    
    if fuertes >= 5:
        recomendaciones.append(f"🏦 **{fuertes} de {len(df)} con interés institucional FUERTE**: Los fondos confían en tu selección. Buena señal de validación.")
    elif fuertes + moderados >= 5:
        recomendaciones.append(f"🏦 **{fuertes + moderados} de {len(df)} con respaldo institucional**: Base sólida, pero algunas carecen de respaldo mayoritario.")
    else:
        recomendaciones.append(f"⚠️ **Poco respaldo institucional**: La mayoría de tus acciones no tienen fuerte seguimiento de fondos. Mayor riesgo pero también mayor recompensa potencial.")
    
    # Análisis de diversificación
    sectores_detectados = set()
    for tick in tickers:
        try:
            _, _, _, _, _, _, sector = obtener_info_segura(tick)
            if sector:
                sectores_detectados.add(sector)
        except:
            pass
    
    if len(sectores_detectados) >= 3:
        recomendaciones.append(f"🔄 **Diversificación en {len(sectores_detectados)} sectores**: Buena cobertura. No todo depende de un solo sector.")
    else:
        recomendaciones.append(f"🎯 **Concentrado en pocos sectores**: Alta correlación entre tus activos. Si cae la robótica, cae toda la cartera.")
    
    # Recomendación de acción
    recomendaciones.append("---")
    recomendaciones.append("**💡 Próximos pasos recomendados:**")
    
    if len(df) < 10:
        recomendaciones.append(f"• Tienes {len(df)}/10 posiciones. Considera completar el cupo para diversificar.")
    
    # Buscar la peor posición
    peor_ratio = 999
    peor_ticker = ""
    for _, fila in df.iterrows():
        try:
            rb_str = str(fila.get('Ratio R:B', '1 : 1.0'))
            if ':' in rb_str:
                partes = rb_str.split(':')
                if len(partes) > 1:
                    rb = float(partes[1].strip().split()[0])
                    if rb < peor_ratio:
                        peor_ratio = rb
                        peor_ticker = fila['Ticker']
        except:
            pass
    
    if peor_ticker and peor_ratio < 1.0:
        recomendaciones.append(f"• **{peor_ticker}** tiene el peor R:B (1:{peor_ratio:.1f}). Reevalúa en 90 días o considera sustituir.")
    
    recomendaciones.append("• Mantén el candado de 90 días. No tomes decisiones impulsivas con pérdidas puntuales.")
    recomendaciones.append("• Revisa esta cartera una vez por semana, no diariamente.")
    
    return recomendaciones

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
    else:
        return f"{mc:.0f}"

def formatear_pnl(ganancia_valor, ganancia_pct, moneda='USD'):
    sym = simbolo_moneda(moneda)
    if ganancia_valor > 0:
        return f"🟩 +{ganancia_valor:.2f} {sym} (+{ganancia_pct:.2f}%)"
    elif ganancia_valor < 0:
        return f"🟥 {ganancia_valor:.2f} {sym} ({ganancia_pct:.2f}%)"
    else:
        return f"⬜ 0.00 {sym} (0.00%)"

def guardar_listas():
    with open(ARCHIVO_LISTAS, "w") as f:
        json.dump(st.session_state.listas_guardadas, f)

def guardar_cartera():
    if not st.session_state.cartera_compras.empty:
        st.session_state.cartera_compras.to_csv(ARCHIVO_CARTERA, index=False)

def regenerar_textos_moneda(df):
    if df.empty:
        return df
    for idx in df.index:
        ticker = str(df.loc[idx, 'Ticker'])
        moneda = detectar_moneda(ticker)
        df.loc[idx, 'Moneda'] = moneda
        sym = simbolo_moneda(moneda)
        if 'Precio Entrada Base' in df.columns:
            precio = df.loc[idx, 'Precio Entrada Base']
            if pd.notna(precio):
                df.loc[idx, 'Precio Entrada'] = f"{float(precio):.2f} {sym}"
        if 'Capital Invertido Base' in df.columns:
            capital = df.loc[idx, 'Capital Invertido Base']
            if pd.notna(capital):
                df.loc[idx, 'Capital Invertido'] = f"{float(capital):.2f} {sym}"
    return df

# ============================================================================
# 3. INICIALIZACIÓN DE SESSION STATE
# ============================================================================

if "listas_guardadas" not in st.session_state:
    if os.path.exists(ARCHIVO_LISTAS):
        try:
            with open(ARCHIVO_LISTAS, "r") as f:
                st.session_state.listas_guardadas = json.load(f)
        except:
            if os.path.exists(ARCHIVO_LISTAS):
                os.remove(ARCHIVO_LISTAS)
    if "listas_guardadas" not in st.session_state or not isinstance(st.session_state.listas_guardadas, dict):
        st.session_state.listas_guardadas = {
            "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "AVGO", "MRVL", "TSM"],
            "Robótica Pura y Satélites": [
                "ISRG", "ZBH", "STE", "ROK", "CGNX", "TER", 
                "ATS", "SYM", "GWW", "AME", "ADI", "FTV", "KEYS", "PTC", 
                "ANSS", "ROCK", "COHR", "DE", "CAT", "AVAV", "GE", "HON",
                "NVDA", "AMD", "ARM", "AVGO", "MRVL",
                "SNPS", "CDNS", "ANSS", "SPLK",
                "SYK", "MDT", "BSX"
            ],
            "Fotónica y Sensores": ["IPGP", "LITE", "COHR", "CGNX"],
            "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR", "NVDA"]
        }

if not st.session_state.listas_guardadas:
    st.session_state.listas_guardadas = {"Mi Lista Principal": []}

if "cartera_compras" not in st.session_state:
    if os.path.exists(ARCHIVO_CARTERA):
        try:
            df_cargada = pd.read_csv(ARCHIVO_CARTERA)
            if 'Moneda' not in df_cargada.columns:
                df_cargada['Moneda'] = 'USD'
            df_cargada = regenerar_textos_moneda(df_cargada)
            st.session_state.cartera_compras = df_cargada
            guardar_cartera()
        except:
            st.session_state.cartera_compras = pd.DataFrame()
    else:
        st.session_state.cartera_compras = pd.DataFrame()

if "params_bot" not in st.session_state:
    st.session_state.params_bot = {
        "max_por_accion": 1000,
        "tope_semanal": 5000,
        "max_activos_cartera": 16
    }

# Seguimiento de compras semanales
ARCHIVO_COMPRAS_SEMANA = "compras_semana.json"

if "compras_semana" not in st.session_state:
    if os.path.exists(ARCHIVO_COMPRAS_SEMANA):
        try:
            with open(ARCHIVO_COMPRAS_SEMANA, "r") as f:
                st.session_state.compras_semana = json.load(f)
        except:
            st.session_state.compras_semana = {}
    else:
        st.session_state.compras_semana = {}

# Obtener semana actual (año-semana)
from datetime import datetime
semana_actual = datetime.now().strftime("%Y-W%U")

if semana_actual not in st.session_state.compras_semana:
    st.session_state.compras_semana[semana_actual] = {
        "compras_realizadas": 0,
        "gastado": 0.0,
        "tickers_comprados": []
    }

def guardar_compras_semana():
    with open(ARCHIVO_COMPRAS_SEMANA, "w") as f:
        json.dump(st.session_state.compras_semana, f)

def get_compras_semana_actual():
    semana = datetime.now().strftime("%Y-W%U")
    if semana not in st.session_state.compras_semana:
        st.session_state.compras_semana[semana] = {
            "compras_realizadas": 0,
            "gastado": 0.0,
            "tickers_comprados": []
        }
    return st.session_state.compras_semana[semana]

def puede_comprar_esta_semana(cantidad=1, costo=1000):
    datos = get_compras_semana_actual()
    tope = st.session_state.params_bot["tope_semanal"]
    max_activos = st.session_state.params_bot["max_activos_cartera"]

    # Check weekly spending limit
    if datos["gastado"] + costo > tope:
        return False, f"Tope semanal alcanzado: {datos['gastado']:.0f}/{tope}"

    # Check weekly purchase count (max 5 per week)
    if datos["compras_realizadas"] + cantidad > 5:
        return False, f"Máximo 5 compras semanales alcanzado: {datos['compras_realizadas']}/5"

    return True, "OK"

def registrar_compra(ticker, costo=1000):
    datos = get_compras_semana_actual()
    datos["compras_realizadas"] += 1
    datos["gastado"] += costo
    datos["tickers_comprados"].append(ticker)
    guardar_compras_semana()

def encontrar_peor_posicion(df_cartera):
    """Encuentra la posición con peor ratio R:B para vender."""
    if df_cartera.empty:
        return None

    peor_ratio = 999
    peor_ticker = None

    for _, fila in df_cartera.iterrows():
        try:
            rb_str = str(fila.get('Ratio R:B', '1 : 1.0'))
            if ':' in rb_str:
                partes = rb_str.split(':')
                if len(partes) > 1:
                    rb = float(partes[1].strip().split()[0])
                    if rb < peor_ratio:
                        peor_ratio = rb
                        peor_ticker = fila['Ticker']
        except:
            continue

    return peor_ticker

# ============================================================================
# 4. MENÚ DE PESTAÑAS
# ============================================================================
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# ============================================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30k
# ============================================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente - Horizonte 4 Años")
    
    mercado_activo = comprobar_mercado_abierto()
    if mercado_activo:
        st.success("🟢 MERCADO ABIERTO")
    else:
        st.info("🕒 MERCADO CERRADO: Análisis con últimos datos disponibles.")

    st.write("#### 🛡️ Reglas de Gestión Monetaria")
    col_r1, col_r2, col_r3 = st.columns(3)
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
        max_activos_cartera = st.number_input(
            "Máx. activos:", min_value=1, max_value=30, 
            value=st.session_state.params_bot["max_activos_cartera"], step=1, key="input_max_act"
        )
        st.session_state.params_bot["max_activos_cartera"] = max_activos_cartera

    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([3, 1, 1, 1])
    with col_btn1:
        ejecutar_bot = st.button("🔄 Ejecutar Bot")
    with col_btn2:
        if st.button("🗑️ Resetear Cartera"):
            st.session_state.cartera_compras = pd.DataFrame()
            if os.path.exists(ARCHIVO_CARTERA):
                os.remove(ARCHIVO_CARTERA)
            if os.path.exists(ARCHIVO_LISTAS):
                os.remove(ARCHIVO_LISTAS)
            if os.path.exists(ARCHIVO_COMPRAS_SEMANA):
                os.remove(ARCHIVO_COMPRAS_SEMANA)
            st.session_state.compras_semana = {}
            st.session_state.listas_guardadas = {
                "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "AVGO", "MRVL", "TSM"],
                "Robótica Pura y Satélites": [
                    "ISRG", "ZBH", "STE", "ROK", "CGNX", "TER", 
                    "ATS", "SYM", "GWW", "AME", "ADI", "FTV", "KEYS", "PTC", 
                    "ANSS", "ROCK", "COHR", "DE", "CAT", "AVAV", "GE", "HON",
                    "NVDA", "AMD", "ARM", "AVGO", "MRVL",
                    "SNPS", "CDNS", "ANSS", "SPLK",
                    "SYK", "MDT", "BSX"
                ],
                "Fotónica y Sensores": ["IPGP", "LITE", "COHR", "CGNX"],
                "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR", "NVDA"]
            }
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("¡Cartera, caché y registro semanal completamente reseteados!")
            time.sleep(1)
            st.rerun()
    with col_btn3:
        if st.button("🧹 Limpiar Duplicados"):
            if not st.session_state.cartera_compras.empty:
                antes = len(st.session_state.cartera_compras)
                st.session_state.cartera_compras = st.session_state.cartera_compras.drop_duplicates(
                    subset=['Ticker'], keep='last'
                )
                guardar_cartera()
                st.success(f"Eliminados {antes - len(st.session_state.cartera_compras)} duplicados.")
                st.rerun()
    with col_btn4:
        if st.button("💱 Forzar Moneda"):
            if not st.session_state.cartera_compras.empty:
                st.session_state.cartera_compras = regenerar_textos_moneda(st.session_state.cartera_compras)
                guardar_cartera()
                st.success("✅ Monedas actualizadas.")
                st.rerun()

    # ============================================================================
    # EJECUCIÓN DEL BOT
    # ============================================================================
    if ejecutar_bot:
        st.cache_data.clear()
        st.toast("Analizando universo de robótica y tech...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        nombre_lista_bot = "Robótica Pura y Satélites" if "Robótica Pura y Satélites" in st.session_state.listas_guardadas else list(st.session_state.listas_guardadas.keys())[0]
        lista_tickers = st.session_state.listas_guardadas[nombre_lista_bot]
        
        if not lista_tickers:
            st.error("Lista vacía.")
        else:
            status_text.text("📥 Descargando datos históricos...")
            datos_globales = descargar_datos_seguro(lista_tickers, period="1y", actions=True)
            progress_bar.progress(20)
            
            status_text.text("📥 Descargando datos recientes...")
            datos_minuto = descargar_datos_seguro(lista_tickers, period="1d", interval="1m")
            progress_bar.progress(40)
            
            candidatas_finalistas = []
            total_tickers = len(lista_tickers)
            
            for idx, tick in enumerate(lista_tickers):
                progress = 40 + int((idx / total_tickers) * 50)
                progress_bar.progress(min(progress, 90))
                status_text.text(f"🔍 {tick}... ({idx+1}/{total_tickers})")
                try:
                    historial = extraer_historial(datos_globales, tick)
                    if historial.empty or len(historial) < 200:
                        continue
                    precio_actual = extraer_precio_actual(datos_minuto, tick, historial)
                    if precio_actual is None or precio_actual <= 0:
                        continue
                    media_30 = historial['Close'].iloc[-30:].mean()
                    media_200 = historial['Close'].iloc[-200:].mean()
                    p_minimo_50 = historial['Close'].iloc[-50:].min()
                    volumen_actual = historial['Volume'].iloc[-1]
                    media_volumen_20 = historial['Volume'].iloc[-21:-1].mean()
                    
                    if precio_actual <= media_200:
                        continue
                    if precio_actual < (media_30 * 0.98):
                        continue
                    
                    precio_hace_60d = historial['Close'].iloc[-60]
                    crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                    crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))
                    if crecimiento_porcentaje < 20.0:
                        continue
                    
                    target_estimado, div_yield, moneda_detectada, pct_inst, num_inst, market_cap, sector = obtener_info_segura(tick)
                    
                    if target_estimado is None:
                        try:
                            t = yf.Ticker(tick)
                            info = t.info
                            target_estimado = info.get('targetMedianPrice', None)
                            div_yield = info.get('dividendYield', None)
                            moneda_detectada = info.get('currency', detectar_moneda(tick))
                            pct_inst = info.get('heldPercentInstitutions', None)
                            num_inst = info.get('numberOfInstitutionalHolders', None)
                            market_cap = info.get('marketCap', None)
                            sector = info.get('sector', None)
                            if div_yield and div_yield > 1.0:
                                div_yield = div_yield / 100.0
                        except:
                            target_estimado = None
                            div_yield = None
                            moneda_detectada = detectar_moneda(tick)
                            pct_inst = None
                            num_inst = None
                            market_cap = None
                            sector = None
                    
                    if div_yield is None or div_yield == 0:
                        div_yield = calcular_dividend_yield(historial, precio_actual, tick)
                    
                    if target_estimado is None or target_estimado == 0:
                        potencial_4a = crecimiento_porcentaje * 1.18
                    else:
                        potencial_4a = ((target_estimado - precio_actual) / precio_actual) * 100
                    
                    riesgo_suelo = ((precio_actual - p_minimo_50) / precio_actual) * 100
                    if riesgo_suelo <= 0:
                        riesgo_suelo = 0.5
                    ratio_rb_calc = potencial_4a / riesgo_suelo
                    
                    fuerza_volumen = "🔥 ALTO" if volumen_actual > (media_volumen_20 * 1.15) else "🟢 NORMAL"
                    tendencia_vol, _ = calcular_tendencia_volumen(historial)
                    interes_inst = calcular_interes_institucional(fuerza_volumen, pct_inst, tendencia_vol, market_cap)
                    
                    sym = simbolo_moneda(moneda_detectada)
                    
                    candidatas_finalistas.append({
                        "Ticker": tick,
                        "Precio Actual": precio_actual,
                        "Crecimiento Anual": crecimiento_porcentaje,
                        "Potencial 4A": potencial_4a,
                        "Ratio R:B": ratio_rb_calc,
                        "Dividendo": div_yield if div_yield else 0,
                        "Volumen H.F.": fuerza_volumen,
                        "Tendencia Vol": tendencia_vol,
                        "Pct Institucional": pct_inst,
                        "Interés Inst.": interes_inst,
                        "Market Cap": market_cap,
                        "Sector": sector,
                        "Moneda": moneda_detectada,
                        "Simbolo": sym,
                        "RSI 14d": round(rsi_valor, 1),
                        "Dist Máx 52s": f"{distancia_max_52s:.1f}%",
                        "Alertas": alerta_txt
                    })
                except:
                    continue
            
            progress_bar.progress(95)
            status_text.text("💼 Construyendo cartera...")
            posiciones_nuevas = []
            caja_total_estrategia = 30000.0
            if not st.session_state.cartera_compras.empty:
                caja_total_estrategia -= st.session_state.cartera_compras["Capital Invertido Base"].sum()
            
            if candidatas_finalistas:
                df_ordenado = pd.DataFrame(candidatas_finalistas).sort_values(by="Potencial 4A", ascending=False)
                tickers_en_cartera = set(st.session_state.cartera_compras["Ticker"].tolist()) if not st.session_state.cartera_compras.empty else set()
                
                # Contador de posiciones compradas en ESTA ejecución
                # Contador de posiciones compradas en ESTA ejecución
                # Contador de posiciones compradas en ESTA ejecución
                posiciones_nuevas_count = 0
                posiciones_vendidas = []
                gastado_semana_actual = 0.0

                for _, fila in df_ordenado.iterrows():
                    # Total = cartera anterior + nuevas de hoy - vendidas hoy
                    pos_act_total = (len(st.session_state.cartera_compras) if not st.session_state.cartera_compras.empty else 0) + posiciones_nuevas_count - len(posiciones_vendidas)

                    # Controlar tope semanal (máximo 5 compras = 5000)
                    if gastado_semana_actual >= tope_semanal:
                        st.info(f"🛑 Tope semanal de {tope_semanal:,.0f} alcanzado. Espera a la próxima semana.")
                        break

                    # Controlar caja disponible
                    if caja_total_estrategia < max_por_accion:
                        st.info(f"🛑 Caja insuficiente: {caja_total_estrategia:.2f} < {max_por_accion}")
                        break

                    # Si cartera llena (16 activos), buscar venta automática
                    if pos_act_total >= max_activos_cartera:
                        if not st.session_state.cartera_compras.empty:
                            # Buscar la peor posición para vender (menor Ratio R:B y candado liberado)
                            hoy = datetime.now()
                            peor_idx = None
                            peor_rb = 999.0

                            for idx_c, row_c in st.session_state.cartera_compras.iterrows():
                                # Verificar si candado de 90 días ya pasó
                                fecha_candado_str = str(row_c.get('Candado', '')).replace('🔒 ', '').strip()
                                try:
                                    fecha_candado = datetime.strptime(fecha_candado_str, '%d/%m/%Y')
                                    dias_restantes = (fecha_candado - hoy).days
                                except:
                                    dias_restantes = -1  # Si no hay fecha, asumir liberado

                                if dias_restantes <= 0:  # Candado liberado
                                    # Extraer ratio R:B
                                    rb_str = str(row_c.get('Ratio R:B', '1 : 1.0'))
                                    try:
                                        if ':' in rb_str:
                                            partes = rb_str.split(':')
                                            if len(partes) > 1:
                                                rb_val = float(partes[1].strip().split()[0])
                                                if rb_val < peor_rb:
                                                    peor_rb = rb_val
                                                    peor_idx = idx_c
                                    except:
                                        pass

                            if peor_idx is not None:
                                ticker_vendido = st.session_state.cartera_compras.loc[peor_idx, 'Ticker']
                                st.session_state.cartera_compras = st.session_state.cartera_compras.drop(peor_idx).reset_index(drop=True)
                                posiciones_vendidas.append(ticker_vendido)
                                st.success(f"🔄 Vendida {ticker_vendido} (peor R:B) para hacer hueco.")
                                guardar_cartera()
                                # Recalcular tickers en cartera
                                tickers_en_cartera = set(st.session_state.cartera_compras["Ticker"].tolist()) if not st.session_state.cartera_compras.empty else set()
                                pos_act_total -= 1
                            else:
                                st.warning(f"⚠️ Cartera llena ({max_activos_cartera} activos) y ninguna con candado liberado. No se puede comprar.")
                                break

                    if fila["Ticker"] in tickers_en_cartera:
                        continue

                    caja_total_estrategia -= max_por_accion
                    gastado_semana_actual += max_por_accion
                    posiciones_nuevas_count += 1
                    fecha_compra = datetime.now().strftime('%d/%m/%Y')
                    fecha_liberacion = (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y')
                    precio = fila["Precio Actual"]
                    if precio <= 0:
                        continue

                    cantidad = round(max_por_accion / precio, 4)
                    sym = fila["Simbolo"]
                    pct_inst_txt = f"{fila['Pct Institucional']*100:.1f}%" if fila['Pct Institucional'] else "N/A"
                    mcap_txt = formatear_market_cap(fila["Market Cap"])

                    posiciones_nuevas.append({
                        "Ticker": fila["Ticker"],
                        "Acciones": cantidad,
                        "Precio Entrada Base": precio,
                        "Precio Entrada": f"{precio:.2f} {sym}",
                        "Crecimiento Business": f"🚀 {fila['Crecimiento Anual']:.1f}%",
                        "Potencial 4Años": f"{fila['Potencial 4A']:.1f}%",
                        "Ratio R:B": f"1 : {fila['Ratio R:B']:.1f}",
                        "Dividendo": formatear_dividendo(fila["Dividendo"]),
                        "Interés Inst.": fila["Interés Inst."],
                        "Pct Institucional": pct_inst_txt,
                        "Market Cap": mcap_txt,
                        "Capital Invertido Base": max_por_accion,
                        "Capital Invertido": f"{max_por_accion:.2f} {sym}",
                        "Fecha Compra": fecha_compra,
                        "Candado": f"🔒 {fecha_liberacion}",
                        "Moneda": fila["Moneda"]
                    })
                if posiciones_nuevas:
                    df_nuevas = pd.DataFrame(posiciones_nuevas)
                    st.session_state.cartera_compras = pd.concat([st.session_state.cartera_compras, df_nuevas], ignore_index=True) if not st.session_state.cartera_compras.empty else df_nuevas
                    guardar_cartera()
                    st.success(f"✅ {len(posiciones_nuevas)} posiciones añadidas. Semana: {get_compras_semana_actual()['compras_realizadas']}/5 compras.")
                else:
                    st.info("Sin nuevas posiciones.")
            else:
                st.info("Ningún activo cumplió los filtros.")
            
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()

    # ============================================================================
    # MOSTRAR CARTERA CON VEREDICTO POR ACCIÓN
    # ============================================================================
    df_mostrar = st.session_state.cartera_compras.copy()
    caja_libre = 30000.0
    gastado_semana = 0.0
    alerta_cupo = False

    if not df_mostrar.empty:
        caja_libre = 30000.0 - df_mostrar["Capital Invertido Base"].sum()
        gastado_semana = df_mostrar["Capital Invertido Base"].sum()
        alerta_cupo = len(df_mostrar) >= max_activos_cartera

        lista_activos_cartera = df_mostrar["Ticker"].tolist()
        
        # Actualizar precios
        precios_vivos = {}
        with st.spinner("🔄 Actualizando precios..."):
            for tick in lista_activos_cartera:
                try:
                    t = yf.Ticker(tick)
                    hist = t.history(period="5d", interval="1d")
                    if not hist.empty and len(hist) > 0:
                        ultimo = float(hist['Close'].iloc[-1])
                        if pd.notna(ultimo) and ultimo > 0:
                            precios_vivos[tick] = ultimo
                            continue
                    hist = t.history(period="1mo", interval="1d")
                    if not hist.empty and len(hist) > 0:
                        ultimo = float(hist['Close'].iloc[-1])
                        if pd.notna(ultimo) and ultimo > 0:
                            precios_vivos[tick] = ultimo
                except:
                    pass

        lista_pnl_formateada = []
        for _, fila in df_mostrar.iterrows():
            t_actual = fila["Ticker"]
            p_entrada = fila["Precio Entrada Base"]
            n_acciones = fila["Acciones"]
            moneda = fila.get("Moneda", "USD")
            p_live = precios_vivos.get(t_actual, p_entrada)
            ganancia_valor = (p_live - p_entrada) * n_acciones
            ganancia_pct = ((p_live - p_entrada) / p_entrada) * 100 if p_entrada > 0 else 0
            lista_pnl_formateada.append(formatear_pnl(ganancia_valor, ganancia_pct, moneda))

        df_mostrar["Rendimiento Actual (P&L)"] = lista_pnl_formateada
        
        # GENERAR VEREDICTO CONTEXTUAL PARA CADA ACCIÓN (con manejo de errores)
        try:
            df_mostrar["📝 Veredicto"] = df_mostrar.apply(generar_veredicto, axis=1)
        except Exception as e:
            st.warning(f"⚠️ No se pudo generar veredictos: {e}")
            df_mostrar["📝 Veredicto"] = "⚠️ Pendiente de análisis"
        
        # Columnas finales
        columnas_mostrar = [
            "Ticker", "Acciones", "Precio Entrada", "Rendimiento Actual (P&L)", 
            "Crecimiento Business", "Potencial 4Años", "Ratio R:B", 
            "Dividendo", "Interés Inst.", "Pct Institucional", "Market Cap",
            "📝 Veredicto", "Capital Invertido", "Fecha Compra", "Candado"
        ]
        columnas_existentes = [c for c in columnas_mostrar if c in df_mostrar.columns]
        df_final_ui = df_mostrar[columnas_existentes]

    total_invertido_hoy = 30000.0 - caja_libre

    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital Total", "30.000,00")
    c2.metric("Invertido", f"{total_invertido_hoy:,.2f}")
    c3.metric("Caja Libre", f"{caja_libre:,.2f}")
    c4.metric("Semanal", f"{gastado_semana:,.2f} / {tope_semanal:,.2f}")

    if alerta_cupo:
        st.warning(f"⚠️ Cupo máximo de {max_activos_cartera} acciones alcanzado.")

    st.write("### 📊 Cartera a 4 Años")
    if not df_mostrar.empty:
        st.dataframe(df_final_ui, use_container_width=True)
        st.success("💾 Cartera guardada.")
    else:
        st.info("Cartera vacía. Ejecuta el bot para empezar a construir.")

    # ============================================================================
    # ANÁLISIS GLOBAL DE TU CARTERA (CONTEXUAL Y ESPECÍFICO)
    # ============================================================================
    if not df_mostrar.empty:
        st.write("---")
        st.write("### 🧠 Análisis de tu Cartera")
        
        try:
            recomendaciones = analizar_cartera_global(df_mostrar)
            
            for rec in recomendaciones:
                if rec.startswith("---"):
                    st.write("---")
                elif rec.startswith("**"):
                    st.write(rec)
                else:
                    st.write(rec)
        except Exception as e:
            st.error(f"⚠️ Error en análisis global: {e}")
        
        st.info("📅 **Recordatorio:** Revisa esta cartera una vez por semana. No tomes decisiones impulsivas antes del candado de 90 días.")

# ============================================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO
# ============================================================================
with pestaña2:
    st.subheader("🔍 Analizador de Oportunidades - Horizonte 4 Años")

    # --- SECCIÓN 1: ANÁLISIS INDIVIDUAL ---
    st.write("### 📈 Análisis Individual")
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        ticker_individual = st.text_input("Introduce un ticker:", value="", placeholder="Ej: NVDA, AMD, ARM...", key="ticker_individual")
    with col_btn:
        analizar_individual = st.button("🔍 Analizar", key="btn_analizar_individual")

    if analizar_individual and ticker_individual.strip():
        tick = ticker_individual.strip().upper()
        with st.spinner(f"Analizando {tick}..."):
            try:
                # Descargar datos
                h = yf.Ticker(tick).history(period="1y")
                if h.empty or len(h) < 200:
                    st.error(f"No hay suficientes datos para {tick}")
                else:
                    p_actual = h['Close'].iloc[-1]
                    media_50 = h['Close'].iloc[-50:].mean()
                    media_200 = h['Close'].iloc[-200:].mean()
                    p_minimo_50 = h['Close'].iloc[-50:].min()

                    # Datos fundamentales
                    target_val, div_yield, moneda, pct_inst, num_inst, market_cap, sector = obtener_info_segura(tick)
                    if target_val is None:
                        try:
                            info = yf.Ticker(tick).info
                            target_val = info.get('targetMedianPrice', None)
                            div_yield = info.get('dividendYield', None)
                            moneda = info.get('currency', detectar_moneda(tick))
                            pct_inst = info.get('heldPercentInstitutions', None)
                            market_cap = info.get('marketCap', None)
                            sector = info.get('sector', None)
                            if div_yield and div_yield > 1.0:
                                div_yield = div_yield / 100.0
                        except:
                            target_val = None; div_yield = None; moneda = detectar_moneda(tick)
                            pct_inst = None; market_cap = None; sector = None

                    if div_yield is None or div_yield == 0:
                        div_yield = calcular_dividend_yield(h, p_actual, tick)

                    # Cálculos
                    precio_60d = h['Close'].iloc[-60] if len(h) >= 60 else h['Close'].iloc[0]
                    crec_pct = ((p_actual - precio_60d) / precio_60d) * 100

                    if target_val is None or target_val == 0:
                        potencial_val = max(20.0, crec_pct * 1.12)
                        target_val = p_actual * (1 + potencial_val/100)
                    else:
                        potencial_val = ((target_val - p_actual) / p_actual) * 100

                    riesgo = ((p_actual - p_minimo_50) / p_actual) * 100
                    if riesgo <= 0:
                        riesgo = 0.5
                    ratio_rb = potencial_val / riesgo

                    tendencia_vol, cambio_vol = calcular_tendencia_volumen(h)
                    volumen_hf = "🔥 ALTO" if h['Volume'].iloc[-1] > h['Volume'].iloc[-21:-1].mean() * 1.15 else "🟢 NORMAL"
                    interes_inst = calcular_interes_institucional(volumen_hf, pct_inst, tendencia_vol, market_cap)

                    sym = simbolo_moneda(moneda)

                    # --- GRÁFICO CON MEDIAS ---
                    st.write("#### 📊 Evolución del Precio con Medias Móviles")

                    # Calcular medias móviles
                    h['MA50'] = h['Close'].rolling(window=50).mean()
                    h['MA200'] = h['Close'].rolling(window=200).mean()

                    # Preparar datos para el gráfico
                    chart_data = pd.DataFrame({
                        'Precio': h['Close'],
                        'Media 50d': h['MA50'],
                        'Media 200d': h['MA200']
                    })

                    st.line_chart(chart_data, use_container_width=True)

                    # --- MÉTRICAS EN COLUMNAS ---
                    st.write("#### 📋 Métricas Clave")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Precio Actual", f"{p_actual:.2f} {sym}")
                    c2.metric("Target", f"{target_val:.2f} {sym}")
                    c3.metric("Potencial", f"{potencial_val:.1f}%")
                    c4.metric("Ratio R:B", f"1:{ratio_rb:.1f}")

                    c5, c6, c7, c8 = st.columns(4)
                    c5.metric("Media 50d", f"{media_50:.2f} {sym}")
                    c6.metric("Media 200d", f"{media_200:.2f} {sym}")
                    c7.metric("Dividendo", formatear_dividendo(div_yield))
                    c8.metric("Market Cap", formatear_market_cap(market_cap))

                    # --- SEMÁFORO DE RECOMENDACIÓN ---
                    st.write("#### 🚦 Semáforo de Recomendación")

                    # Calcular puntuación del semáforo
                    puntos_semaforo = 0
                    razones_verde = []
                    razones_rojo = []

                    # 1. Precio > Media 200 (tendencia alcista)
                    if p_actual > media_200:
                        puntos_semaforo += 1
                        razones_verde.append("✅ Precio por encima de Media 200d")
                    else:
                        razones_rojo.append("❌ Precio por debajo de Media 200d")

                    # 2. Precio > Media 50 (momentum corto)
                    if p_actual > media_50:
                        puntos_semaforo += 1
                        razones_verde.append("✅ Precio por encima de Media 50d")
                    else:
                        razones_rojo.append("❌ Precio por debajo de Media 50d")

                    # 3. Potencial > 50%
                    if potencial_val > 50:
                        puntos_semaforo += 1
                        razones_verde.append("✅ Potencial > 50%")
                    else:
                        razones_rojo.append("❌ Potencial < 50%")

                    # 4. Ratio R:B > 2
                    if ratio_rb > 2:
                        puntos_semaforo += 1
                        razones_verde.append("✅ Excelente Ratio R:B (>2)")
                    elif ratio_rb > 1:
                        puntos_semaforo += 0.5
                        razones_verde.append("⚠️ Ratio R:B aceptable (>1)")
                    else:
                        razones_rojo.append("❌ Ratio R:B bajo (<1)")

                    # 5. Volumen saludable
                    if volumen_hf == "🔥 ALTO":
                        puntos_semaforo += 1
                        razones_verde.append("✅ Volumen alto (interés real)")
                    else:
                        razones_rojo.append("⚠️ Volumen normal")

                    # 6. Interés institucional
                    if "FUERTE" in interes_inst or "MODERADO" in interes_inst:
                        puntos_semaforo += 1
                        razones_verde.append("✅ Respaldo institucional")
                    else:
                        razones_rojo.append("⚠️ Sin respaldo institucional claro")

                    # Mostrar semáforo
                    col_sem1, col_sem2, col_sem3 = st.columns([1, 2, 1])
                    with col_sem2:
                        if puntos_semaforo >= 5:
                            st.success("## 🟢 COMPRA FUERTE")
                            st.write(f"**Puntuación: {puntos_semaforo:.1f}/6**")
                            st.write("Esta acción cumple la mayoría de criterios favorables.")
                        elif puntos_semaforo >= 3:
                            st.warning("## 🟡 COMPRA MODERADA")
                            st.write(f"**Puntuación: {puntos_semaforo:.1f}/6**")
                            st.write("Hay aspectos positivos pero también riesgos a considerar.")
                        else:
                            st.error("## 🔴 NO COMPRAR / ESPERAR")
                            st.write(f"**Puntuación: {puntos_semaforo:.1f}/6**")
                            st.write("Demasiados factores en contra. Mejor esperar o buscar otra oportunidad.")

                    # Razones detalladas
                    with st.expander("📋 Ver detalle de la evaluación"):
                        st.write("**A favor:**")
                        for r in razones_verde:
                            st.write(r)
                        st.write("**En contra:**")
                        for r in razones_rojo:
                            st.write(r)

                    # --- TABLA RESUMEN ---
                    st.write("#### 📊 Resumen del Análisis")
                    resumen_data = {
                        "Métrica": [
                            "Ticker", "Sector", "Precio Actual", "Target", "Potencial", 
                            "Ratio R:B", "Riesgo Suelo", "Dividendo", "Volumen", 
                            "Tendencia Vol", "Interés Inst.", "Market Cap"
                        ],
                        "Valor": [
                            tick, sector or "N/A", f"{p_actual:.2f} {sym}", f"{target_val:.2f} {sym}",
                            f"{potencial_val:.1f}%", f"1:{ratio_rb:.1f}", f"{riesgo:.1f}%",
                            formatear_dividendo(div_yield), volumen_hf, tendencia_vol,
                            interes_inst, formatear_market_cap(market_cap)
                        ]
                    }
                    st.dataframe(pd.DataFrame(resumen_data), use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(f"Error analizando {tick}: {e}")

    st.write("---")

    # --- SECCIÓN 2: ANÁLISIS DE LISTAS ---
    st.write("### 📋 Análisis de Listas Pregrabadas")
    lista_sel = st.selectbox("Universo a analizar:", ["Ninguna"] + list(st.session_state.listas_guardadas.keys()), key="select_lista")

    if lista_sel != "Ninguna":
        tickers_lista = st.session_state.listas_guardadas[lista_sel]
        if tickers_lista:
            with st.spinner("Analizando universo..."):
                datos_globales_p2 = descargar_datos_seguro(tickers_lista, period="1y", actions=True)
                datos_lista = []
                total = len(tickers_lista)
                barra = st.progress(0)

                for idx, tick in enumerate(tickers_lista):
                    barra.progress(int((idx / total) * 100))
                    try:
                        h = extraer_historial(datos_globales_p2, tick)
                        if h.empty or len(h) < 50:
                            continue

                        p_actual = h['Close'].iloc[-1]
                        p_media_50 = h['Close'].iloc[-50:].mean()
                        p_minimo = h['Close'].iloc[-50:].min()

                        target_val, div_yield, moneda, pct_inst, num_inst, market_cap, sector = obtener_info_segura(tick)
                        if target_val is None:
                            try:
                                info = yf.Ticker(tick).info
                                target_val = info.get('targetMedianPrice', None)
                                div_yield = info.get('dividendYield', None)
                                moneda = info.get('currency', detectar_moneda(tick))
                                pct_inst = info.get('heldPercentInstitutions', None)
                                market_cap = info.get('marketCap', None)
                                if div_yield and div_yield > 1.0:
                                    div_yield = div_yield / 100.0
                            except:
                                target_val = None; div_yield = None; moneda = detectar_moneda(tick)
                                pct_inst = None; market_cap = None

                        if div_yield is None or div_yield == 0:
                            div_yield = calcular_dividend_yield(h, p_actual, tick)

                        precio_60d = h['Close'].iloc[-60] if len(h) >= 60 else h['Close'].iloc[0]
                        crec_pct = ((p_actual - precio_60d) / precio_60d) * 100
                        if target_val is None or target_val == 0:
                            potencial_val = max(20.0, crec_pct * 1.12)
                            target_val = p_actual * (1 + potencial_val/100)
                        else:
                            potencial_raw = ((target_val - p_actual) / p_actual) * 100
                            # Si el target del analista es menor que precio actual, usar crecimiento como proxy
                            if potencial_raw < 0:
                                potencial_val = max(20.0, crec_pct * 1.12)
                                target_val = p_actual * (1 + potencial_val/100)
                            else:
                                potencial_val = potencial_raw

                        riesgo = ((p_actual - p_minimo) / p_actual) * 100
                        if riesgo <= 0:
                            riesgo = 0.5
                        ratio_rb = potencial_val / riesgo

                        tendencia_vol, _ = calcular_tendencia_volumen(h)
                        volumen_hf = "🔥 ALTO" if h['Volume'].iloc[-1] > h['Volume'].iloc[-21:-1].mean() * 1.15 else "🟢 NORMAL"
                        interes_inst = calcular_interes_institucional(volumen_hf, pct_inst, tendencia_vol, market_cap)

                        sym = simbolo_moneda(moneda)
                        pct_inst_txt = f"{pct_inst*100:.1f}%" if pct_inst else "N/A"
                        mcap_txt = formatear_market_cap(market_cap)

                        # Calcular semáforo para lista
                        puntos_sem = 0
                        if p_actual > p_media_50: puntos_sem += 1
                        if p_actual > h['Close'].iloc[-200:].mean(): puntos_sem += 1
                        if potencial_val > 50: puntos_sem += 1
                        if ratio_rb > 2: puntos_sem += 1
                        if volumen_hf == "🔥 ALTO": puntos_sem += 1
                        if "FUERTE" in interes_inst or "MODERADO" in interes_inst: puntos_sem += 1

                        if puntos_sem >= 5:
                            semaforo = "🟢 COMPRA FUERTE"
                        elif puntos_sem >= 3:
                            semaforo = "🟡 COMPRA MODERADA"
                        else:
                            semaforo = "🔴 NO COMPRAR"

                        datos_lista.append({
                            "Ticker": tick,
                            "Precio Actual": f"{p_actual:.2f} {sym}",
                            "Media 50d": f"{p_media_50:.2f} {sym}",
                            "Suelo 50d": f"{p_minimo:.2f} {sym}",
                            "Potencial Estimado": f"{potencial_val:.1f}%",
                            "Target": f"{target_val:.2f} {sym}",
                            "Ratio R:B": f"1 : {ratio_rb:.1f}",
                            "Dividendo": formatear_dividendo(div_yield),
                            "Interés Inst.": interes_inst,
                            "Pct Institucional": pct_inst_txt,
                            "Market Cap": mcap_txt,
                            "Tendencia Vol": tendencia_vol,
                            "Sector": sector,
                            "Moneda": moneda,
                            "🚦 Semáforo": semaforo
                        })
                    except Exception as e:
                        continue

                barra.empty()

                if datos_lista:
                    df_lista = pd.DataFrame(datos_lista)
                    st.write(f"**{len(df_lista)} activos analizados**")
                    st.dataframe(df_lista, use_container_width=True)

                    # Top 5 OPORTUNIDADES DE ENTRADA (mejor momento técnico + potencial)
                    st.write("#### 🏆 Top 5 Oportunidades de Entrada")

                    # Filtrar solo semáforo verde/amarillo
                    df_filtrado = df_lista[df_lista["🚦 Semáforo"].str.contains("🟢|🟡", na=False)].copy()

                    if not df_filtrado.empty:
                        # Calcular score de oportunidad de entrada
                        # Más alto = mejor momento para entrar AHORA
                        def calcular_score_entrada(row):
                            score = 0

                            # Potencial alto = +3 a +5 puntos
                            try:
                                pot = float(row["Potencial Estimado"].replace("%","").strip())
                                if pot > 150: score += 5
                                elif pot > 100: score += 4
                                elif pot > 50: score += 3
                                elif pot > 20: score += 2
                                else: score += 1
                            except: score += 1

                            # Semáforo verde = +2, amarillo = +1
                            if "🟢" in str(row.get("🚦 Semáforo","")): score += 2
                            elif "🟡" in str(row.get("🚦 Semáforo","")): score += 1

                            # Ratio R:B alto = +2
                            try:
                                rb_str = str(row.get("Ratio R:B","1 : 1.0"))
                                if ":" in rb_str:
                                    rb_val = float(rb_str.split(":")[1].strip().split()[0])
                                    if rb_val > 3: score += 2
                                    elif rb_val > 1.5: score += 1
                            except: pass

                            # Dividendo 0% = +1 (fiscalidad)
                            if "❌ 0%" in str(row.get("Dividendo","")) or "0%" in str(row.get("Dividendo","")): score += 1

                            # Interés institucional fuerte = +1
                            if "FUERTE" in str(row.get("Interés Inst.","")): score += 1

                            return score

                        df_filtrado["Score Entrada"] = df_filtrado.apply(calcular_score_entrada, axis=1)
                        df_top = df_filtrado.sort_values(by="Score Entrada", ascending=False).head(5)

                        # Mostrar con score
                        cols_mostrar = [c for c in ["Ticker", "Precio Actual", "Potencial Estimado", "Ratio R:B", "Dividendo", "Interés Inst.", "🚦 Semáforo", "Score Entrada"] if c in df_top.columns]
                        st.dataframe(df_top[cols_mostrar], use_container_width=True)
                    else:
                        st.warning("Ninguna acción de la lista cumple los criterios para entrada ahora.")
                else:
                    st.warning("No se pudieron analizar activos de esta lista.")
        else:
            st.info("Lista vacía.")
with pestaña3:
    st.subheader("⚙️ Gestión de Listas de Seguimiento")

    for nombre_lista, tickers_lista in st.session_state.listas_guardadas.items():
        with st.expander(f"📋 {nombre_lista} ({len(tickers_lista)} tickers)"):
            st.write(f"**Tickers:** {', '.join(tickers_lista)}")
            col_edit, col_del = st.columns([1, 1])
            with col_edit:
                nuevo_nombre = st.text_input(f"Renombrar:", value=nombre_lista, key=f"rename_{nombre_lista}")
                if nuevo_nombre != nombre_lista and st.button(f"✅ Guardar nombre", key=f"save_name_{nombre_lista}"):
                    st.session_state.listas_guardadas[nuevo_nombre] = st.session_state.listas_guardadas.pop(nombre_lista)
                    guardar_listas()
                    st.success(f"Lista renombrada a '{nuevo_nombre}'")
                    st.rerun()
            with col_del:
                if st.button(f"🗑️ Eliminar lista", key=f"del_{nombre_lista}"):
                    del st.session_state.listas_guardadas[nombre_lista]
                    guardar_listas()
                    st.success(f"Lista '{nombre_lista}' eliminada.")
                    st.rerun()

    st.write("---")
    st.write("### ➕ Crear Nueva Lista")
    nombre_nueva = st.text_input("Nombre de la nueva lista:", key="nueva_lista_nombre")
    tickers_nueva = st.text_area("Tickers (separados por comas o saltos de línea):", key="nueva_lista_tickers")

    if st.button("💾 Guardar Nueva Lista", key="guardar_nueva"):
        if nombre_nueva and tickers_nueva:
            tickers_limpios = [t.strip().upper() for t in tickers_nueva.replace("\n", ",").split(",") if t.strip()]
            st.session_state.listas_guardadas[nombre_nueva] = tickers_limpios
            guardar_listas()
            st.success(f"✅ Lista '{nombre_nueva}' guardada con {len(tickers_limpios)} tickers.")
            st.rerun()
        else:
            st.error("Completa nombre y tickers.")

    st.write("---")
    st.write("### 📥 Importar/Exportar Listas")

    col_imp, col_exp = st.columns(2)
    with col_imp:
        archivo_subido = st.file_uploader("Subir JSON de listas:", type=["json"], key="upload_json")
        if archivo_subido is not None:
            try:
                listas_importadas = json.load(archivo_subido)
                st.session_state.listas_guardadas.update(listas_importadas)
                guardar_listas()
                st.success("✅ Listas importadas correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error importando: {e}")

    with col_exp:
        json_str = json.dumps(st.session_state.listas_guardadas, indent=2)
        st.download_button(
            label="📥 Descargar listas (JSON)",
            data=json_str,
            file_name="listas_permanentes.json",
            mime="application/json",
            key="download_json"
        )

st.write("---")
st.caption("Centro de Mando Financiero Pro | Desarrollado con Streamlit + yFinance | Datos en tiempo real vía Yahoo Finance")
