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

def calcular_interes_institucional(volumen_hf, pct_institucional, tendencia_vol):
    puntos = 0
    if volumen_hf == "🔥 ALTO":
        puntos += 1
    if pct_institucional is not None and pct_institucional > 0.60:
        puntos += 1
    if "CRECIENDO" in tendencia_vol:
        puntos += 1
    if puntos >= 3:
        return "🎯 FUERTE"
    elif puntos >= 2:
        return "🎯 MODERADO"
    else:
        return "🎯 DÉBIL"

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
        "tope_semanal": 10000,
        "max_activos_cartera": 10
    }

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
            st.cache_data.clear()
            st.success("¡Cartera reseteada!")
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

    # Mostrar estado de monedas
    if not st.session_state.cartera_compras.empty:
        st.write("---")
        st.write("**💱 Monedas Detectadas:**")
        monedas_resumen = {}
        for _, fila in st.session_state.cartera_compras.iterrows():
            tick = fila['Ticker']
            mon = fila.get('Moneda', '???')
            monedas_resumen[tick] = mon
        cols = st.columns(min(len(monedas_resumen), 10))
        for i, (tick, mon) in enumerate(monedas_resumen.items()):
            sym = simbolo_moneda(mon)
            with cols[i % len(cols)]:
                st.write(f"**{tick}**: {mon} {sym}")

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
                    
                    # Filtros de tendencia (para buy & hold)
                    if precio_actual <= media_200:
                        continue
                    if precio_actual < (media_30 * 0.98):
                        continue
                    
                    # Crecimiento anualizado (últimos 60 días como proxy)
                    precio_hace_60d = historial['Close'].iloc[-60]
                    crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                    crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))
                    if crecimiento_porcentaje < 20.0:
                        continue
                    
                    # Datos extendidos con info institucional y empresa
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
                    
                    # Potencial a 4 años
                    if target_estimado is None or target_estimado == 0:
                        potencial_4a = crecimiento_porcentaje * 1.18
                    else:
                        potencial_4a = ((target_estimado - precio_actual) / precio_actual) * 100
                    
                    # Riesgo/suelo (cuánto puede caer desde aquí)
                    riesgo_suelo = ((precio_actual - p_minimo_50) / precio_actual) * 100
                    if riesgo_suelo <= 0:
                        riesgo_suelo = 0.5
                    ratio_rb_calc = potencial_4a / riesgo_suelo
                    
                    # Volumen e institucional
                    fuerza_volumen = "🔥 ALTO" if volumen_actual > (media_volumen_20 * 1.15) else "🟢 NORMAL"
                    tendencia_vol, _ = calcular_tendencia_volumen(historial)
                    interes_inst = calcular_interes_institucional(fuerza_volumen, pct_inst, tendencia_vol)
                    
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
                        "Simbolo": sym
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
                
                for _, fila in df_ordenado.iterrows():
                    pos_act = len(st.session_state.cartera_compras) if not st.session_state.cartera_compras.empty else 0
                    if pos_act >= max_activos_cartera or caja_total_estrategia < max_por_accion:
                        break
                    if fila["Ticker"] in tickers_en_cartera:
                        continue
                    
                    caja_total_estrategia -= max_por_accion
                    fecha_compra = datetime.now().strftime('%d/%m/%Y')
                    fecha_liberacion = (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y')
                    precio = fila["Precio Actual"]
                    if precio <= 0:
                        continue
                    
                    cantidad = round(max_por_accion / precio, 4)
                    sym = fila["Simbolo"]
                    pct_inst_txt = f"{fila['Pct Institucional']*100:.1f}%" if fila['Pct Institucional'] else "N/A"
                    mcap_txt = formatear_market_cap(fila['Market Cap'])
                    
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
                        "Volumen H.F.": fila["Volumen H.F."],
                        "Tendencia Vol": fila["Tendencia Vol"],
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
                    st.success(f"✅ {len(posiciones_nuevas)} posiciones añadidas a la cartera.")
                else:
                    st.info("Sin nuevas posiciones.")
            else:
                st.info("Ningún activo cumplió los filtros.")
            
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()

    # ============================================================================
    # MOSTRAR CARTERA - OPTIMIZADO PARA BUY & HOLD 4 AÑOS
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
        
        # Actualizar precios (una vez por semana es suficiente para buy & hold)
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
        
        # Columnas optimizadas para buy & hold (sin datos intradía irrelevantes)
        columnas_mostrar = [
            "Ticker", "Acciones", "Precio Entrada", "Rendimiento Actual (P&L)", 
            "Crecimiento Business", "Potencial 4Años", "Ratio R:B", 
            "Dividendo", "Interés Inst.", "Pct Institucional", "Market Cap",
            "Capital Invertido", "Fecha Compra", "Candado"
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
        
        # Leyenda para inversor de largo plazo
        with st.expander("📖 Guía para Inversor a 4 Años"):
            st.write("""
            **🎯 Interés Institucional:**
            - **FUERTE**: Los fondos están acumulando. Señal de confianza para largo plazo.
            - **MODERADO**: Interés estable. Empresa consolidada.
            - **DÉBIL**: Poco seguimiento institucional. Puede ser oportunidad temprana o valor en declive.
            
            **Potencial 4Años:**
            - Estimación de revalorización basada en target de analistas o tendencia.
            - No es garantía, pero indica el consenso del mercado.
            
            **Ratio R:B (Riesgo/Beneficio):**
            - Cuanto más alto, mejor. Indica cuánto puedes ganar por cada $ arriesgado.
            - >1:3 es excelente para buy & hold.
            
            **Market Cap:**
            - Tamaño de la empresa. Las grandes (>10B) son más estables.
            - Las pequeñas tienen más potencial pero más riesgo.
            
            **Candado 🔒:**
            - Fecha mínima para reconsiderar la posición (90 días).
            - Evita decisiones impulsivas. El verdadero valor se crea en años, no días.
            """)
        st.success("💾 Cartera guardada. Revisa semanalmente, no diariamente.")
    else:
        st.info("Cartera vacía. Ejecuta el bot para empezar a construir.")

# ============================================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO
# ============================================================================
with pestaña2:
    st.subheader("🔍 Analizador de Oportunidades - Horizonte 4 Años")
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
                            potencial_val = ((target_val - p_actual) / p_actual) * 100
                        
                        riesgo = ((p_actual - p_minimo) / p_actual) * 100
                        if riesgo <= 0:
                            riesgo = 0.5
                        ratio_rb = potencial_val / riesgo
                        
                        # Métricas institucionales
                        tendencia_vol, _ = calcular_tendencia_volumen(h)
                        volumen_hf = "🔥 ALTO" if h['Volume'].iloc[-1] > h['Volume'].iloc[-21:-1].mean() * 1.15 else "🟢 NORMAL"
                        interes_inst = calcular_interes_institucional(volumen_hf, pct_inst, tendencia_vol)
                        
                        sym = simbolo_moneda(moneda)
                        pct_inst_txt = f"{pct_inst*100:.1f}%" if pct_inst else "N/A"
                        mcap_txt = formatear_market_cap(market_cap)
                        
                        if p_actual > p_media_50 and potencial_val >= 20.0:
                            semaforo = "🟢 COMPRAR"; nota = "Tendencia alcista + alto potencial."
                        elif potencial_val >= 10.0:
                            semaforo = "🟡 ACUMULAR"; nota = "Consolidando. Buen punto de entrada parcial."
                        else:
                            semaforo = "🔴 ESPERAR"; nota = "Sin margen de seguridad suficiente."
                        
                        datos_lista.append({
                            "Ticker": tick,
                            "Precio Actual": f"{p_actual:.2f} {sym}",
                            "Precio Objetivo": f"{target_val:.2f} {sym}",
                            "Potencial 4A": f"{potencial_val:.1f}%",
                            "Ratio R:B": f"1 : {ratio_rb:.1f}",
                            "Dividendo": formatear_dividendo(div_yield),
                            "Interés Inst.": interes_inst,
                            "Pct Inst.": pct_inst_txt,
                            "Market Cap": mcap_txt,
                            "Estrategia": semaforo,
                            "Nota": nota
                        })
                    except:
                        continue
                
                barra.empty()
                
                if datos_lista:
                    st.dataframe(pd.DataFrame(datos_lista), use_container_width=True)
                    
                    # Resumen por estrategia
                    c1, c2, c3 = st.columns(3)
                    comprar = len([d for d in datos_lista if d["Estrategia"] == "🟢 COMPRAR"])
                    acumular = len([d for d in datos_lista if d["Estrategia"] == "🟡 ACUMULAR"])
                    esperar = len([d for d in datos_lista if d["Estrategia"] == "🔴 ESPERAR"])
                    c1.metric("🟢 COMPRAR", comprar)
                    c2.metric("🟡 ACUMULAR", acumular)
                    c3.metric("🔴 ESPERAR", esperar)
                    
                    st.info(f"💡 **Consejo:** Prioriza las 🟢 para posiciones iniciales y 🟡 para ampliar gradualmente.")
        else:
            st.info("Lista vacía.")

    st.write("---")
    st.write("### 🔍 Ficha Individual")
    accion = st.text_input("Ticker a analizar:", "KLAC", key="input_ind")
    
    if accion:
        accion = accion.upper().strip()
        try:
            with st.spinner(f"Cargando {accion}..."):
                t_obj = yf.Ticker(accion)
                datos_hist = t_obj.history(period="2y", actions=True)
            
            if datos_hist.empty or len(datos_hist) < 200:
                st.warning("Datos insuficientes.")
            else:
                datos_hist['MM50'] = datos_hist['Close'].rolling(50).mean()
                datos_hist['MM200'] = datos_hist['Close'].rolling(200).mean()
                dv = datos_hist.iloc[-252:]
                p_act = dv['Close'].iloc[-1]
                p_50 = dv['MM50'].iloc[-1]
                p_200 = dv['MM200'].iloc[-1]
                p_min = dv['Close'].iloc[-50:].min()
                
                target, dy, mon, pct_inst, num_inst, market_cap, sector = obtener_info_segura(accion)
                if target is None:
                    try:
                        inf = t_obj.info
                        target = inf.get('targetMedianPrice', None)
                        dy = inf.get('dividendYield', None)
                        mon = inf.get('currency', detectar_moneda(accion))
                        pct_inst = inf.get('heldPercentInstitutions', None)
                        market_cap = inf.get('marketCap', None)
                        sector = inf.get('sector', None)
                        if dy and dy > 1.0:
                            dy = dy / 100.0
                    except:
                        target = None; dy = None; mon = detectar_moneda(accion)
                        pct_inst = None; market_cap = None; sector = None
                
                if dy is None or dy == 0:
                    dy = calcular_dividend_yield(dv, p_act, accion)
                if target is None or target == 0:
                    target = p_act * 1.25
                
                pot = ((target - p_act) / p_act) * 100
                riesgo = max(0.5, ((p_act - p_min) / p_act) * 100)
                rb = pot / riesgo
                
                tendencia_vol, _ = calcular_tendencia_volumen(dv)
                volumen_hf = "🔥 ALTO" if dv['Volume'].iloc[-1] > dv['Volume'].iloc[-21:-1].mean() * 1.15 else "🟢 NORMAL"
                interes_inst = calcular_interes_institucional(volumen_hf, pct_inst, tendencia_vol)
                
                sym = simbolo_moneda(mon)
                pct_inst_txt = f"{pct_inst*100:.1f}%" if pct_inst else "N/A"
                mcap_txt = formatear_market_cap(market_cap)
                
                diag = "COMPRAR" if p_act > p_200 and p_act > p_50 else ("ACUMULAR" if p_act > p_200 else "ESPERAR")
                
                st.write("#### 📊 Métricas Clave")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Precio", f"{p_act:.2f} {sym}")
                c2.metric("Potencial 4A", f"{pot:.1f}%")
                c3.metric("R:B", f"1 : {rb:.1f}")
                c4.metric("Estrategia", diag)
                
                st.write("#### 🏦 Perfil Institucional")
                c1, c2, c3 = st.columns(3)
                c1.metric("Interés Inst.", interes_inst)
                c2.metric("% Institucional", pct_inst_txt)
                c3.metric("Market Cap", mcap_txt)
                
                st.write(f"**Sector:** {sector if sector else 'N/A'}")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("MM50", f"{p_50:.2f} {sym}")
                c2.metric("MM200", f"{p_200:.2f} {sym}")
                c3.metric("Dividendo", formatear_dividendo(dy))
                
                dg = dv[['Close', 'MM50', 'MM200']]
                dg.columns = ['Precio', 'MM 50D', 'MM 200D']
                st.line_chart(dg)
                
                with st.expander("📋 Datos históricos"):
                    st.dataframe(dv.tail(20)[['Open', 'High', 'Low', 'Close', 'Volume']], use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error: {e}")

# ============================================================================
# PESTAÑA 3: CONFIGURACIÓN
# ============================================================================
with pestaña3:
    st.subheader("⚙️ Configuración de Listas")
    with st.form("crear_lista", clear_on_submit=True):
        nombre = st.text_input("Nueva lista:").strip()
        if st.form_submit_button("✨ Crear"):
            if nombre and nombre not in st.session_state.listas_guardadas:
                st.session_state.listas_guardadas[nombre] = []
                guardar_listas(); st.success(f"Lista '{nombre}' creada."); st.rerun()
            elif nombre in st.session_state.listas_guardadas:
                st.warning("Ya existe.")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        eliminar = st.selectbox("Eliminar lista:", list(st.session_state.listas_guardadas.keys()), key="del")
    with c2:
        st.write("##")
        if st.button("💥 Eliminar"):
            del st.session_state.listas_guardadas[eliminar]
            guardar_listas(); st.success("Eliminada."); st.rerun()
    
    editar = st.selectbox("Editar lista:", list(st.session_state.listas_guardadas.keys()), key="edit")
    if editar:
        tickers = st.session_state.listas_guardadas[editar]
        c1, c2 = st.columns([3, 1])
        with c1:
            nuevo = st.text_input("Añadir ticker:", key="add").upper().strip()
        with c2:
            st.write("##")
            if st.button("📥 Añadir"):
                if nuevo and nuevo not in tickers:
                    tickers.append(nuevo)
                    st.session_state.listas_guardadas[editar] = tickers
                    guardar_listas(); st.success(f"{nuevo} añadido."); st.rerun()
        
        c1, c2 = st.columns([3, 1])
        with c1:
            borrar = st.selectbox("Eliminar ticker:", ["Ninguno"] + tickers, key="rem")
        with c2:
            st.write("##")
            if st.button("🗑️ Eliminar"):
                if borrar != "Ninguno":
                    tickers.remove(borrar)
                    st.session_state.listas_guardadas[editar] = tickers
                    guardar_listas(); st.success(f"{borrar} eliminado."); st.rerun()
        
        st.write(f"**{len(tickers)} activos:**")
        if tickers:
            st.dataframe(pd.DataFrame(tickers, columns=["Ticker"]), use_container_width=True)
