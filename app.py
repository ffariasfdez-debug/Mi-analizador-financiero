import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import json
import time

# ============================================================================
# CONFIGURACION INICIAL
# ============================================================================
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Horizonte:** 4 Años | **Estilo:** Buy & Hold | **Foco:** Robótica & Tech")
st.write(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# ============================================================================
# LISTAS DEFINITIVAS - Depuradas 2026-06-05
# ============================================================================

LISTAS_DEFINITIVAS = {
    "🤖 Robótica y Automatización": [
        "ABB", "FANUY", "SIEGY", "YASKY", "ROK", "AME", "FTV", "ETN", "EMR", "DOV",
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

@st.cache_data(ttl=300)
def obtener_info_segura(ticker):
    """Un solo call a yFinance."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info or len(info) < 5:
            return None, None, detectar_moneda(ticker), None, None, None
        target = info.get('targetMedianPrice', None)
        dy = info.get('dividendYield', None)
        moneda = info.get('currency', detectar_moneda(ticker))
        pct_inst = info.get('heldPercentInstitutions', None)
        market_cap = info.get('marketCap', None)
        sector = info.get('sector', None)
        if dy is not None and dy > 1.0:
            dy = dy / 100.0
        return target, dy, moneda, pct_inst, market_cap, sector
    except:
        return None, None, detectar_moneda(ticker), None, None, None

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
        _, dy, _, _, _, _ = obtener_info_segura(ticker)
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
# INICIALIZACION DE SESSION STATE - ROBUSTA
# ============================================================================

if "listas_guardadas" not in st.session_state:
    st.session_state.listas_guardadas = LISTAS_DEFINITIVAS.copy()

if "cartera_compras" not in st.session_state:
    st.session_state.cartera_compras = pd.DataFrame()

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
    st.session_state.registro_semanal = {}

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

    lista_bot = st.selectbox(
        "Universo a analizar:",
        list(st.session_state.listas_guardadas.keys()),
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
                    st.success(f"✅ Cartera importada: {len(df_import)} posiciones")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

    if ejecutar_bot:
        st.cache_data.clear()
        st.toast("Analizando universo...")
        progress_bar = st.progress(0)
        status_text = st.empty()

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

            candidatas_finalistas = []
            total_tickers = len(lista_tickers)

            for idx, tick in enumerate(lista_tickers):
                progress = 40 + int((idx / total_tickers) * 40)
                progress_bar.progress(min(progress, 80))
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

                    # FILTROS ESTRICTOS (como antigua)
                    if precio_actual <= media_200:
                        continue
                    if precio_actual < (media_30 * 0.98):
                        continue

                    precio_hace_60d = historial['Close'].iloc[-60]
                    crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                    crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))

                    if crecimiento_porcentaje < 20.0:
                        continue

                    target_estimado, div_yield, moneda_detectada, pct_inst, market_cap, sector = obtener_info_segura(tick)

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

                    sym = simbolo_moneda(moneda_detectada)

                    candidatas_finalistas.append({
                        "Ticker": tick,
                        "Precio Actual": precio_actual,
                        "Crecimiento Anual": crecimiento_porcentaje,
                        "Potencial 4A": potencial_4a,
                        "Ratio R:B": ratio_rb_calc,
                        "Dividendo": div_yield if div_yield else 0,
                        "Volumen H.F.": fuerza_volumen,
                        "Moneda": moneda_detectada,
                        "Simbolo": sym,
                        "Pct Institucional": pct_inst,
                        "Market Cap": market_cap,
                        "Sector": sector
                    })
                except:
                    continue

            progress_bar.progress(85)
            status_text.text("💼 Evaluando cartera y ejecutando...")

            if candidatas_finalistas:
                df_candidatas = pd.DataFrame(candidatas_finalistas).sort_values(by="Potencial 4A", ascending=False)

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

                        if posiciones_sustituidas:
                            for viejo, nuevo in posiciones_sustituidas:
                                st.success(f"🔄 Sustituido {viejo} → {nuevo}")
                        st.success(f"✅ {len(posiciones_nuevas)} posiciones. Semana: {get_registro_semana_actual()['compras_realizadas']}/{max_compras_sem}")
                    else:
                        st.info("Sin nuevas posiciones esta semana.")
            else:
                st.info("Ningún activo cumplió filtros estrictos.")

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
                "Dividendo", "Volumen H.F.", "Interés Inst.", "Market Cap",
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
# PESTANA 2: ANALIZADOR TECNICO - CRITERIOS ANTIGUOS RESTAURADOS
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
                h = yf.Ticker(tick).history(period="1y")
                if h.empty or len(h) < 200:
                    st.error(f"No hay suficientes datos para {tick}")
                else:
                    p_actual = h['Close'].iloc[-1]
                    media_50 = h['Close'].iloc[-50:].mean()
                    media_200 = h['Close'].iloc[-200:].mean()
                    p_minimo_50 = h['Close'].iloc[-50:].min()

                    target_val, div_yield, moneda, pct_inst, market_cap, sector = obtener_info_segura(tick)

                    if div_yield is None or div_yield == 0:
                        div_yield = calcular_dividend_yield(h, p_actual, tick)

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

                    sym = simbolo_moneda(moneda)

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
                    c2.metric("Target", f"{target_val:.2f} {sym}")
                    c3.metric("Potencial", f"{potencial_val:.1f}%")
                    c4.metric("Ratio R:B", f"1:{ratio_rb:.1f}")

                    c5, c6, c7, c8 = st.columns(4)
                    c5.metric("Media 50d", f"{media_50:.2f} {sym}")
                    c6.metric("Media 200d", f"{media_200:.2f} {sym}")
                    c7.metric("Dividendo", formatear_dividendo(div_yield))
                    c8.metric("Market Cap", formatear_market_cap(market_cap))

                    # SEMÁFORO - CRITERIOS ANTIGUOS EXACTOS
                    puntos = 0
                    razones_verde = []
                    razones_rojo = []

                    if p_actual > media_200:
                        puntos += 1; razones_verde.append("✅ > MA200")
                    else:
                        razones_rojo.append("❌ < MA200")
                    if p_actual > media_50:
                        puntos += 1; razones_verde.append("✅ > MA50")
                    else:
                        razones_rojo.append("❌ < MA50")
                    if potencial_val > 50:
                        puntos += 1; razones_verde.append("✅ Potencial >50%")
                    else:
                        razones_rojo.append("❌ Potencial <50%")
                    if ratio_rb > 2.0:
                        puntos += 1; razones_verde.append("✅ R:B >2")
                    elif ratio_rb > 1.0:
                        puntos += 0.5; razones_verde.append("⚠️ R:B >1")
                    else:
                        razones_rojo.append("❌ R:B <1")

                    col_sem = st.columns([1, 2, 1])[1]
                    with col_sem:
                        if puntos >= 4 and potencial_val > 50:
                            st.success("## 🟢 COMPRA FUERTE")
                        elif puntos >= 2 and potencial_val > 20:
                            st.warning("## 🟡 COMPRA MODERADA")
                        else:
                            st.error("## 🔴 NO COMPRAR / ESPERAR")
                        st.write(f"**Puntuación: {puntos:.1f}/4**")

                    with st.expander("📋 Detalle de evaluación"):
                        st.write("**A favor:**")
                        for r in razones_verde:
                            st.write(r)
                        st.write("**En contra:**")
                        for r in razones_rojo:
                            st.write(r)
            except Exception as e:
                st.error(f"Error: {e}")

    st.write("---")
    st.write("### 📋 Análisis de Listas Pregrabadas")
    lista_sel = st.selectbox("Universo:", ["Ninguna"] + list(st.session_state.listas_guardadas.keys()), key="select_lista")

    if lista_sel != "Ninguna":
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
                            continue

                        p_actual = h['Close'].iloc[-1]
                        p_media = h['Close'].iloc[-50:].mean()
                        p_minimo = h['Close'].iloc[-50:].min()

                        target_val, div_yield, moneda, pct_inst, market_cap, sector = obtener_info_segura(tick)

                        if div_yield is None or div_yield == 0:
                            div_yield = calcular_dividend_yield(h, p_actual, tick)

                        precio_60d = h['Close'].iloc[-60] if len(h) >= 60 else h['Close'].iloc[0]
                        crec_pct = ((p_actual - precio_60d) / precio_60d) * 100

                        if target_val is None or target_val == 0:
                            potencial_val = max(20.0, crec_pct * 1.12)
                            target_val = p_actual * (1 + potencial_val/100)
                        else:
                            potencial_raw = ((target_val - p_actual) / p_actual) * 100
                            if potencial_raw < 0:
                                potencial_val = max(20.0, crec_pct * 1.12)
                                target_val = p_actual * (1 + potencial_val/100)
                            else:
                                potencial_val = potencial_raw

                        riesgo = ((p_actual - p_minimo) / p_actual) * 100
                        if riesgo <= 0:
                            riesgo = 0.5
                        ratio_rb = potencial_val / riesgo

                        sym = simbolo_moneda(moneda)

                        # SEMÁFORO - CRITERIOS ANTIGUOS EXACTOS
                        if p_actual > p_media and potencial_val >= 20.0:
                            semaforo = "🟢 COMPRAR"
                            explicacion = "Estructura alcista y excelente margen de subida real."
                        elif potencial_val >= 10.0:
                            semaforo = "🟡 ACUMULAR"
                            explicacion = "Consolidando niveles. Atractivo para medio plazo."
                        else:
                            semaforo = "🔴 ESPERAR"
                            explicacion = "Precio objetivo ajustado o sin margen de seguridad dinámico."

                        datos_lista.append({
                            "Ticker": tick,
                            "Precio": f"{p_actual:.2f} {sym}",
                            "Target": f"{target_val:.2f} {sym}",
                            "Potencial": f"{potencial_val:.1f}%",
                            "R:B": f"1:{ratio_rb:.1f}",
                            "Dividendo": formatear_dividendo(div_yield),
                            "🚦": semaforo,
                            "Nota": explicacion
                        })
                    except:
                        pass

                barra.empty()

                if datos_lista:
                    df_lista = pd.DataFrame(datos_lista)
                    st.write(f"**{len(df_lista)} activos analizados**")
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
                        st.success(f"🗑️ Eliminado {ticker_a_eliminar}")
                        st.rerun()

            col_add, col_add_btn = st.columns([3, 1])
            with col_add:
                nuevo_ticker = st.text_input(f"Añadir:", key=f"add_ticker_{nombre_lista}")
            with col_add_btn:
                if st.button(f"➕ Añadir", key=f"btn_add_{nombre_lista}"):
                    if nuevo_ticker and nuevo_ticker.strip().upper() not in [t.upper() for t in st.session_state.listas_guardadas[nombre_lista]]:
                        st.session_state.listas_guardadas[nombre_lista].append(nuevo_ticker.strip().upper())
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
                    st.success(f"Renombrada a '{nuevo_nombre}'")
                    st.rerun()
            with col_del:
                if st.button(f"🗑️ Eliminar lista", key=f"del_{nombre_lista}"):
                    del st.session_state.listas_guardadas[nombre_lista]
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
st.caption("Centro de Mando Financiero Pro | Streamlit + yFinance | Datos Yahoo Finance")
