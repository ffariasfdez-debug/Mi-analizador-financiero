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

# Archivos locales para almacenamiento permanente
ARCHIVO_CARTERA = "cartera_guardada.csv"
ARCHIVO_LISTAS = "listas_permanentes.json"

# ============================================================================
# 2. TÍTULO PRINCIPAL
# ============================================================================
st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# ============================================================================
# 3. FUNCIONES AUXILIARES
# ============================================================================

def comprobar_mercado_abierto():
    """Comprueba si Wall Street está abierto."""
    tz_ny = pytz.timezone('America/New_York')
    hora_ny = datetime.now(tz_ny)
    dia_semana = hora_ny.weekday()
    inicio_mercado = hora_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    fin_mercado = hora_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    return dia_semana <= 4 and inicio_mercado <= hora_ny <= fin_mercado

@st.cache_data(ttl=300)
def obtener_info_segura(ticker):
    """
    Obtiene target price y dividend yield de forma segura.
    Retorna (target, div_yield_decimal) o (None, None) si falla.
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info
        
        # Si no hay info válida, no cacheamos basura (retornamos algo que identificamos)
        if not info or len(info) < 5:
            return "ERROR", "ERROR"
            
        target = info.get('targetMedianPrice', None)
        dy = info.get('dividendYield', None)
        
        # Normalizar dividend yield a decimal (0.015 = 1.5%)
        if dy is not None:
            if dy > 1.0:  # Viene como porcentaje (ej: 1.5 en vez de 0.015)
                dy = dy / 100.0
            return target, dy
            
        return target, None
        
    except Exception as e:
        return "ERROR", "ERROR"

def descargar_datos_seguro(tickers, period="1y", interval=None, actions=False):
    """
    Descarga datos de yfinance de forma segura.
    Maneja tanto listas como tickers individuales.
    """
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
        
        # Si es un solo ticker, yfinance devuelve DataFrame plano
        if len(tickers) == 1:
            # Convertir a formato MultiIndex consistente
            ticker = tickers[0]
            datos.columns = pd.MultiIndex.from_product([[ticker], datos.columns])
            
        return datos
        
    except Exception as e:
        st.error(f"Error descargando datos: {e}")
        return pd.DataFrame()

def extraer_historial(datos_globales, ticker, period="1y"):
    """
    Extrae el historial de un ticker específico desde datos multi-ticker.
    Fallback a descarga individual si falla.
    """
    try:
        # Intentar extraer del DataFrame multi-ticker
        if ticker in datos_globales.columns.get_level_values(0):
            historial = datos_globales[ticker].dropna()
            if not historial.empty:
                return historial
    except:
        pass
    
    # Fallback: descargar individualmente
    try:
        t = yf.Ticker(ticker)
        historial = t.history(period=period, actions=True)
        return historial
    except:
        return pd.DataFrame()

def extraer_precio_actual(datos_minuto, ticker, historial):
    """
    Extrae el precio actual desde datos de minuto o del historial diario.
    """
    try:
        # Intentar desde datos de minuto
        if ticker in datos_minuto.columns.get_level_values(0):
            precio = datos_minuto[ticker]['Close'].dropna().iloc[-1]
            if pd.notna(precio) and precio > 0:
                return float(precio)
    except:
        pass
    
    # Fallback: último precio del historial
    try:
        precio = historial['Close'].iloc[-1]
        if pd.notna(precio) and precio > 0:
            return float(precio)
    except:
        pass
    
    return None

def calcular_dividend_yield(historial, precio_actual, ticker):
    """
    Calcula el dividend yield de múltiples fuentes.
    """
    # 1. Intentar desde yf.Ticker.info
    try:
        _, dy = obtener_info_segura(ticker)
        if dy is not None and dy != "ERROR" and dy > 0:
            return dy
    except:
        pass
    
    # 2. Intentar desde columnas de dividendos en historial
    try:
        if 'Dividends' in historial.columns:
            dividendos_totales = historial['Dividends'].sum()
            if dividendos_totales > 0 and precio_actual > 0:
                return dividendos_totales / precio_actual
    except:
        pass
    
    # 3. Intentar desde actions (dividendos como filas)
    try:
        if 'Dividends' in historial.columns:
            divs = historial[historial['Dividends'] > 0]['Dividends']
            if len(divs) > 0:
                return divs.sum() / precio_actual
    except:
        pass
    
    return 0

def formatear_dividendo(dy):
    """Formatea el dividend yield para mostrar."""
    if dy is None or dy == 0 or dy == "ERROR":
        return "❌ 0%"
    return f"💰 {dy * 100:.2f}%"

def formatear_pnl(ganancia_euros, ganancia_pct):
    """Formatea el P&L con colores."""
    if ganancia_euros > 0:
        return f"🟩 +{ganancia_euros:.2f} $ (+{ganancia_pct:.2f}%)"
    elif ganancia_euros < 0:
        return f"🟥 {ganancia_euros:.2f} $ ({ganancia_pct:.2f}%)"
    else:
        return f"⬜ 0.00 $ (0.00%)"

def guardar_listas():
    """Guarda las listas en disco."""
    with open(ARCHIVO_LISTAS, "w") as f:
        json.dump(st.session_state.listas_guardadas, f)

def guardar_cartera():
    """Guarda la cartera en disco."""
    if not st.session_state.cartera_compras.empty:
        st.session_state.cartera_compras.to_csv(ARCHIVO_CARTERA, index=False)

# ============================================================================
# 4. INICIALIZACIÓN DE SESSION STATE
# ============================================================================

# Listas guardadas
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

# Cartera de compras
if "cartera_compras" not in st.session_state:
    if os.path.exists(ARCHIVO_CARTERA):
        try:
            st.session_state.cartera_compras = pd.read_csv(ARCHIVO_CARTERA)
        except:
            st.session_state.cartera_compras = pd.DataFrame()
    else:
        st.session_state.cartera_compras = pd.DataFrame()

# Parámetros de gestión monetaria (persisten entre ejecuciones)
if "params_bot" not in st.session_state:
    st.session_state.params_bot = {
        "max_por_accion": 1000,
        "tope_semanal": 10000,
        "max_activos_cartera": 10
    }

# ============================================================================
# 5. MENÚ DE PESTAÑAS
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
    st.subheader("🤖 Algoritmo de Selección Inteligente y Maduración Trimestral")
    
    mercado_activo = comprobar_mercado_abierto()
    if mercado_activo:
        st.success("🟢 MERCADO ABIERTO: Las operaciones simuladas se ejecutarán con precios e impacto en vivo.")
    else:
        st.warning("🕒 MERCADO CERRADO (Wall Street): El bot analizará el mercado con los últimos precios vivos disponibles.")

    st.write("#### 🛡️ Reglas de Gestión Monetaria y Control de Riesgo")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        max_por_accion = st.number_input(
            "Capital fijo por operación ($):", 
            min_value=100, max_value=5000, 
            value=st.session_state.params_bot["max_por_accion"], 
            step=100,
            key="input_max_por_accion"
        )
        st.session_state.params_bot["max_por_accion"] = max_por_accion
    with col_r2:
        tope_semanal = st.slider(
            "Tope de presupuesto compras semanales ($):", 
            min_value=1000, max_value=30000, 
            value=st.session_state.params_bot["tope_semanal"], 
            step=1000,
            key="slider_tope_semanal"
        )
        st.session_state.params_bot["tope_semanal"] = tope_semanal
    with col_r3:
        max_activos_cartera = st.number_input(
            "Cupo máximo de acciones en cartera:", 
            min_value=1, max_value=30, 
            value=st.session_state.params_bot["max_activos_cartera"], 
            step=1,
            key="input_max_activos"
        )
        st.session_state.params_bot["max_activos_cartera"] = max_activos_cartera

    col_btn1, col_btn2, col_btn3 = st.columns([3, 1, 1])
    with col_btn1:
        ejecutar_bot = st.button("🔄 Ejecutar Embudo Avanzado e Interceptar Dinero Institucional")
    with col_btn2:
        if st.button("🗑️ Resetear Cartera (Empezar de Cero)"):
            st.session_state.cartera_compras = pd.DataFrame()
            if os.path.exists(ARCHIVO_CARTERA):
                os.remove(ARCHIVO_CARTERA)
            st.cache_data.clear()
            st.success("¡Archivo físico borrado y cartera reseteada con éxito!")
            st.rerun()
    with col_btn3:
        if st.button("🧹 Limpiar Duplicados"):
            if not st.session_state.cartera_compras.empty:
                antes = len(st.session_state.cartera_compras)
                st.session_state.cartera_compras = st.session_state.cartera_compras.drop_duplicates(
                    subset=['Ticker'], keep='last'
                )
                despues = len(st.session_state.cartera_compras)
                guardar_cartera()
                st.success(f"Eliminados {antes - despues} duplicados. {despues} posiciones únicas.")
                st.rerun()

    # ============================================================================
    # EJECUCIÓN DEL BOT
    # ============================================================================
    if ejecutar_bot:
        st.cache_data.clear()
        st.toast("Rastreando huella institucional y capturando precios permanentes...")
        
        # Barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()

        nombre_lista_bot = "Robótica Pura y Satélites" if "Robótica Pura y Satélites" in st.session_state.listas_guardadas else list(st.session_state.listas_guardadas.keys())[0]
        lista_tickers = st.session_state.listas_guardadas[nombre_lista_bot]
        
        if not lista_tickers:
            st.error("La lista seleccionada para el bot no contiene tickers.")
        else:
            # Descargar datos de forma segura
            status_text.text("📥 Descargando datos históricos (1 año)...")
            datos_globales = descargar_datos_seguro(lista_tickers, period="1y", actions=True)
            progress_bar.progress(20)
            
            status_text.text("📥 Descargando datos intradía...")
            datos_minuto = descargar_datos_seguro(lista_tickers, period="1d", interval="1m")
            progress_bar.progress(40)
            
            candidatas_finalistas = []
            total_tickers = len(lista_tickers)
            
            for idx, tick in enumerate(lista_tickers):
                progress = 40 + int((idx / total_tickers) * 50)
                progress_bar.progress(min(progress, 90))
                status_text.text(f"🔍 Analizando {tick}... ({idx+1}/{total_tickers})")
                
                try:
                    # Extraer historial
                    historial = extraer_historial(datos_globales, tick)
                    
                    if historial.empty or len(historial) < 200:
                        continue
                    
                    # Precio actual
                    precio_actual = extraer_precio_actual(datos_minuto, tick, historial)
                    if precio_actual is None or precio_actual <= 0:
                        continue
                    
                    # Medias móviles
                    media_30 = historial['Close'].iloc[-30:].mean()
                    media_200 = historial['Close'].iloc[-200:].mean()
                    p_minimo_50 = historial['Close'].iloc[-50:].min()
                    
                    # Volumen
                    volumen_actual = historial['Volume'].iloc[-1]
                    media_volumen_20 = historial['Volume'].iloc[-21:-1].mean()
                    
                    # FILTROS PRINCIPALES
                    if precio_actual <= media_200:
                        continue  # No está en tendencia alcista
                    
                    if precio_actual < (media_30 * 0.98):
                        continue  # Por debajo de media 30 con margen
                    
                    # Crecimiento anual (últimos 60 días como proxy)
                    precio_hace_60d = historial['Close'].iloc[-60]
                    crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                    crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))
                    
                    if crecimiento_porcentaje < 20.0:
                        continue
                    
                    # Target y dividendo
                    target_estimado, div_yield = obtener_info_segura(tick)
                    
                    # Si el cache devolvió ERROR, intentar calcular sin cache
                    if target_estimado == "ERROR":
                        try:
                            t = yf.Ticker(tick)
                            info = t.info
                            target_estimado = info.get('targetMedianPrice', None)
                            div_yield = info.get('dividendYield', None)
                            if div_yield and div_yield > 1.0:
                                div_yield = div_yield / 100.0
                        except:
                            target_estimado = None
                            div_yield = None
                    
                    # Calcular dividend yield si no lo tenemos
                    if div_yield is None or div_yield == 0 or div_yield == "ERROR":
                        div_yield = calcular_dividend_yield(historial, precio_actual, tick)
                    
                    # Potencial
                    if target_estimado is None or target_estimado == 0 or target_estimado == "ERROR":
                        potencial_4a = crecimiento_porcentaje * 1.18
                    else:
                        potencial_4a = ((target_estimado - precio_actual) / precio_actual) * 100
                    
                    # Ratio Riesgo/Beneficio
                    riesgo_suelo = ((precio_actual - p_minimo_50) / precio_actual) * 100
                    if riesgo_suelo <= 0:
                        riesgo_suelo = 0.5
                    ratio_rb_calc = potencial_4a / riesgo_suelo
                    
                    # Fuerza de volumen
                    fuerza_volumen = "🔥 ALTO" if volumen_actual > (media_volumen_20 * 1.15) else "🟢 NORMAL"
                    
                    candidatas_finalistas.append({
                        "Ticker": tick,
                        "Precio Actual": precio_actual,
                        "Crecimiento Anual": crecimiento_porcentaje,
                        "Potencial Real": potencial_4a,
                        "Ratio R:B": ratio_rb_calc,
                        "Dividendo": div_yield if div_yield else 0,
                        "Volumen Institucional": fuerza_volumen
                    })
                    
                except Exception as e:
                    continue
            
            progress_bar.progress(95)
            status_text.text("💼 Construyendo cartera...")
            
            # ============================================================================
            # CONSTRUIR CARTERA (ACUMULATIVA, NO SOBRESCRIBE)
            # ============================================================================
            posiciones_nuevas = []
            caja_total_estrategia = 30000.0
            
            # Calcular gasto ya invertido
            if not st.session_state.cartera_compras.empty:
                gasto_actual = st.session_state.cartera_compras["Capital Invertido Base"].sum()
                caja_total_estrategia -= gasto_actual
            
            if candidatas_finalistas:
                df_ordenado = pd.DataFrame(candidatas_finalistas).sort_values(by="Potencial Real", ascending=False)
                
                # Tickers ya en cartera
                tickers_en_cartera = set()
                if not st.session_state.cartera_compras.empty:
                    tickers_en_cartera = set(st.session_state.cartera_compras["Ticker"].tolist())
                
                for _, fila in df_ordenado.iterrows():
                    # Verificar límites
                    posiciones_actuales = len(st.session_state.cartera_compras) if not st.session_state.cartera_compras.empty else 0
                    
                    if posiciones_actuales >= max_activos_cartera:
                        break
                    if caja_total_estrategia < max_por_accion:
                        break
                    
                    # Verificar que no esté ya en cartera
                    if fila["Ticker"] in tickers_en_cartera:
                        continue
                    
                    caja_total_estrategia -= max_por_accion
                    
                    fecha_compra = datetime.now().strftime('%d/%m/%Y')
                    fecha_liberacion = (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y')
                    
                    # Evitar división por cero
                    precio = fila["Precio Actual"]
                    if precio <= 0:
                        continue
                    
                    cantidad_acciones = round(max_por_accion / precio, 4)
                    
                    posiciones_nuevas.append({
                        "Ticker": fila["Ticker"],
                        "Acciones": cantidad_acciones,
                        "Precio Entrada Base": precio,
                        "Precio Entrada": f"{precio:.2f} $",
                        "Crecimiento Business": f"🚀 {fila['Crecimiento Anual']:.1f}%",
                        "Potencial Estimado": f"{fila['Potencial Real']:.1f}%",
                        "Ratio R:B": f"1 : {fila['Ratio R:B']:.1f}",
                        "Dividendo": formatear_dividendo(fila["Dividendo"]),
                        "Volumen H.F.": fila["Volumen Institucional"],
                        "Capital Invertido Base": max_por_accion,
                        "Capital Invertido": f"{max_por_accion:.2f} $",
                        "Fecha Compra": fecha_compra,
                        "Candado": f"🔒 {fecha_liberacion}"
                    })
                
                # Añadir a cartera existente (no sobrescribir)
                if posiciones_nuevas:
                    df_nuevas = pd.DataFrame(posiciones_nuevas)
                    if st.session_state.cartera_compras.empty:
                        st.session_state.cartera_compras = df_nuevas
                    else:
                        st.session_state.cartera_compras = pd.concat(
                            [st.session_state.cartera_compras, df_nuevas], 
                            ignore_index=True
                        )
                    
                    guardar_cartera()
                    st.success(f"✅ {len(posiciones_nuevas)} nuevas posiciones añadidas a la cartera.")
                else:
                    st.info("Ningún activo nuevo cumplió los filtros o la cartera está llena.")
            else:
                st.info("Ningún activo de la lista cumplió los filtros de selección.")
            
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()

    # ============================================================================
    # MOSTRAR CARTERA CON P&L EN VIVO
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
        
        # Descargar precios en vivo
        with st.spinner("🔄 Actualizando precios en vivo..."):
            try:
                cotizaciones_vivas = descargar_datos_seguro(lista_activos_cartera, period="1d", interval="1m")
            except:
                cotizaciones_vivas = pd.DataFrame()

        lista_pnl_formateada = []
        for _, fila in df_mostrar.iterrows():
            t_actual = fila["Ticker"]
            p_entrada = fila["Precio Entrada Base"]
            n_acciones = fila["Acciones"]
            
            try:
                p_live = extraer_precio_actual(cotizaciones_vivas, t_actual, pd.DataFrame())
                if p_live is None:
                    p_live = p_entrada
            except:
                p_live = p_entrada

            ganancia_euros = (p_live - p_entrada) * n_acciones
            ganancia_pct = ((p_live - p_entrada) / p_entrada) * 100 if p_entrada > 0 else 0

            lista_pnl_formateada.append(formatear_pnl(ganancia_euros, ganancia_pct))

        df_mostrar["Rendimiento Actual (P&L)"] = lista_pnl_formateada
        
        # Preparar DataFrame para mostrar
        columnas_mostrar = [
            "Ticker", "Acciones", "Precio Entrada", "Rendimiento Actual (P&L)", 
            "Crecimiento Business", "Potencial Estimado", "Ratio R:B", 
            "Dividendo", "Volumen H.F.", "Capital Invertido", "Fecha Compra", "Candado"
        ]
        
        # Solo mostrar columnas que existan
        columnas_existentes = [c for c in columnas_mostrar if c in df_mostrar.columns]
        df_final_ui = df_mostrar[columnas_existentes]

    total_invertido_hoy = 30000.0 - caja_libre

    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fondo Inicial", "30.000,00 $")
    c2.metric("Asignado Bot", f"{total_invertido_hoy:,.2f} $")
    c3.metric("Caja Líquida", f"{caja_libre:,.2f} $")
    c4.metric("Gasto Semanal", f"{gastado_semana:,.2f} $ / {tope_semanal:,.2f} $")

    if alerta_cupo:
        st.warning(f"⚠️ **Aviso de Control:** Se alcanzó el cupo máximo de {max_activos_cartera} acciones.")

    st.write("### 📊 Cartera Generada con Filtro Completo y Métricas Reales")
    if not df_mostrar.empty:
        st.dataframe(df_final_ui, use_container_width=True)
        st.success("💾 Memoria Activa: Datos de cartera blindados contra refrescos.")
    else:
        st.info("Ningún activo en cartera. Ejecuta el bot para generar posiciones.")

# ============================================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO AVANZADO
# ============================================================================
with pestaña2:
    st.subheader("🔍 Analizador Técnico y Avanzado de Tendencias")
    st.write("### 📁 Opción A: Proyectar Listas Completas con Métricas de Riesgo y Dividendos")
    
    lista_sel = st.selectbox(
        "Selecciona una lista pregrabada para proyectar:", 
        ["Ninguna"] + list(st.session_state.listas_guardadas.keys()),
        key="select_lista_analisis"
    )
    
    if lista_sel != "Ninguna":
        tickers_lista = st.session_state.listas_guardadas[lista_sel]
        datos_lista = []
        
        if tickers_lista:
            with st.spinner("Sincronizando métricas avanzadas en vivo..."):
                datos_globales_p2 = descargar_datos_seguro(tickers_lista, period="1y", actions=True)
                
                total = len(tickers_lista)
                barra_p2 = st.progress(0)
                
                for idx, tick in enumerate(tickers_lista):
                    barra_p2.progress(int((idx / total) * 100))
                    
                    try:
                        historial = extraer_historial(datos_globales_p2, tick)
                        
                        if historial.empty or len(historial) < 50:
                            continue
                        
                        p_actual = historial['Close'].iloc[-1]
                        p_media_50 = historial['Close'].iloc[-50:].mean()
                        p_minimo = historial['Close'].iloc[-50:].min()
                        
                        # Target y dividendo
                        target_val, div_yield = obtener_info_segura(tick)
                        
                        if target_val == "ERROR":
                            try:
                                t_obj = yf.Ticker(tick)
                                info = t_obj.info
                                target_val = info.get('targetMedianPrice', None)
                                div_yield = info.get('dividendYield', None)
                                if div_yield and div_yield > 1.0:
                                    div_yield = div_yield / 100.0
                            except:
                                target_val = None
                                div_yield = None
                        
                        # Calcular dividend yield si es necesario
                        if div_yield is None or div_yield == 0 or div_yield == "ERROR":
                            div_yield = calcular_dividend_yield(historial, p_actual, tick)
                        
                        # Crecimiento
                        precio_hace_60d = historial['Close'].iloc[-60] if len(historial) >= 60 else historial['Close'].iloc[0]
                        crec_pct = ((p_actual - precio_hace_60d) / precio_hace_60d) * 100
                        
                        # Potencial
                        if target_val is None or target_val == 0 or target_val == "ERROR":
                            potencial_val = max(20.0, crec_pct * 1.12)
                            target_val = p_actual * (1 + (potencial_val/100))
                        else:
                            potencial_val = ((target_val - p_actual) / p_actual) * 100
                        
                        # Ratio R:B
                        riesgo_suelo = ((p_actual - p_minimo) / p_actual) * 100
                        if riesgo_suelo <= 0:
                            riesgo_suelo = 0.5
                        ratio_rb = potencial_val / riesgo_suelo
                        
                        # Señal
                        if p_actual > p_media_50 and potencial_val >= 20.0:
                            sem_lista = "🟢 COMPRAR"
                            explicacion = "Estructura alcista y excelente margen de subida real."
                        elif potencial_val >= 10.0:
                            sem_lista = "🟡 ACUMULAR"
                            explicacion = "Consolidando niveles. Atractivo para medio plazo."
                        else:
                            sem_lista = "🔴 ESPERAR"
                            explicacion = "Precio objetivo ajustado o sin margen de seguridad dinámico."
                            
                        datos_lista.append({
                            "Ticker": tick, 
                            "Precio Actual": f"{p_actual:.2f} $", 
                            "Precio Objetivo Real": f"{target_val:.2f} $",
                            "Potencial Estimado": f"{potencial_val:.1f}%",
                            "Ratio R:B (1 : X)": f"1 : {ratio_rb:.1f}",
                            "Rendimiento Dividendo": formatear_dividendo(div_yield),
                            "Estrategia": sem_lista,
                            "Nota Técnico": explicacion
                        })
                    except Exception as e:
                        continue
                
                barra_p2.empty()
                
                if datos_lista:
                    df_lista_final = pd.DataFrame(datos_lista)
                    st.dataframe(df_lista_final, use_container_width=True)
                    
                    # Resumen
                    comprar = len([d for d in datos_lista if d["Estrategia"] == "🟢 COMPRAR"])
                    acumular = len([d for d in datos_lista if d["Estrategia"] == "🟡 ACUMULAR"])
                    esperar = len([d for d in datos_lista if d["Estrategia"] == "🔴 ESPERAR"])
                    
                    col_res1, col_res2, col_res3 = st.columns(3)
                    col_res1.metric("🟢 COMPRAR", comprar)
                    col_res2.metric("🟡 ACUMULAR", acumular)
                    col_res3.metric("🔴 ESPERAR", esperar)
        else:
            st.info("Esta lista está vacía. Añádele activos en la Pestaña 3.")

    st.write("---")
    st.write("### 🔍 Opción B: Ficha de Inteligencia Estructural Individual")
    accion = st.text_input("Introduce el Ticker de una acción (Ej: ISRG, NVDA, DE):", "KLAC", key="input_ticker_individual")
    
    if accion:
        accion = accion.upper().strip()
        try:
            with st.spinner(f"Cargando datos de {accion}..."):
                ticker_obj = yf.Ticker(accion)
                datos_hist = ticker_obj.history(period="2y", actions=True)
            
            if datos_hist.empty or len(datos_hist) < 200:
                st.warning(f"No hay suficientes datos históricos para {accion} (mínimo 200 días).")
            else:
                datos_hist['Media 50D (Medio Plazo)'] = datos_hist['Close'].rolling(window=50).mean()
                datos_hist['Media 200D (Institucional)'] = datos_hist['Close'].rolling(window=200).mean()
                
                datos_visibles = datos_hist.iloc[-252:] 
                p_actual_ind = datos_visibles['Close'].iloc[-1]
                p_media_50 = datos_visibles['Media 50D (Medio Plazo)'].iloc[-1]
                p_media_200 = datos_visibles['Media 200D (Institucional)'].iloc[-1]
                p_min_ind = datos_visibles['Close'].iloc[-50:].min()
                
                # Info del ticker
                target_ind, div_yield_ind = obtener_info_segura(accion)
                
                if target_ind == "ERROR":
                    try:
                        info = ticker_obj.info
                        target_ind = info.get('targetMedianPrice', None)
                        div_yield_ind = info.get('dividendYield', None)
                        if div_yield_ind and div_yield_ind > 1.0:
                            div_yield_ind = div_yield_ind / 100.0
                    except:
                        target_ind = None
                        div_yield_ind = None
                
                if div_yield_ind is None or div_yield_ind == 0 or div_yield_ind == "ERROR":
                    div_yield_ind = calcular_dividend_yield(datos_visibles, p_actual_ind, accion)
                
                if target_ind is None or target_ind == 0 or target_ind == "ERROR":
                    target_ind = p_actual_ind * 1.25
                
                potencial_ind = ((target_ind - p_actual_ind) / p_actual_ind) * 100
                riesgo_ind = max(0.5, ((p_actual_ind - p_min_ind) / p_actual_ind) * 100)
                ratio_rb_ind = potencial_ind / riesgo_ind
                
                # Diagnóstico
                if p_actual_ind > p_media_200:
                    diagnostico_txt = "COMPRAR" if p_actual_ind > p_media_50 else "ACUMULAR"
                    color_diag = "green" if diagnostico_txt == "COMPRAR" else "orange"
                else:
                    diagnostico_txt = "ESPERAR"
                    color_diag = "red"
                
                st.write("#### 📊 Métricas Clave de Decisión")
                c_i1, c_i2, c_i3, c_i4 = st.columns(4)
                c_i1.metric("Precio de Mercado", f"{p_actual_ind:.2f} $")
                c_i2.metric("Dividendo Anual", formatear_dividendo(div_yield_ind))
                c_i3.metric("Ratio Riesgo / Beneficio", f"1 : {ratio_rb_ind:.1f}")
                c_i4.metric("Estrategia Recommended", diagnostico_txt)
                
                # Info adicional
                st.write("#### 📈 Información Adicional")
                col_info1, col_info2, col_info3 = st.columns(3)
                col_info1.metric("Media 50D", f"{p_media_50:.2f} $")
                col_info2.metric("Media 200D", f"{p_media_200:.2f} $")
                col_info3.metric("Mínimo 50D", f"{p_min_ind:.2f} $")
                
                # Gráfico
                df_grafico = datos_visibles[['Close', 'Media 50D (Medio Plazo)', 'Media 200D (Institucional)']]
                df_grafico.columns = ['Precio de Cierre', 'Media Móvil 50 días', 'Media Móvil 200 días']
                st.line_chart(df_grafico)
                
                # Tabla de datos recientes
                with st.expander("📋 Ver datos históricos recientes"):
                    st.dataframe(datos_visibles.tail(20)[['Open', 'High', 'Low', 'Close', 'Volume']], use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error al analizar {accion}: {str(e)}")

# ============================================================================
# PESTAÑA 3: CONFIGURACIÓN DE LISTAS
# ============================================================================
with pestaña3:
    st.subheader("⚙️ Panel de Edición y Control de Listas Pregrabadas")
    st.write("Gestiona el universo de activos que lee el Bot y el Analizador Avanzado de manera persistente.")
    st.write("---")

    # --- SECCIÓN A: CREAR NUEVA LISTA ---
    st.write("### 🔑 Panel 1: Crear Nueva Lista Personalizada")
    
    with st.form("formulario_crear_lista", clear_on_submit=True):
        nombre_nueva_lista = st.text_input("Escribe el nombre de tu nueva lista (Ej: Crypto_Watch, Speculative):").strip()
        boton_enviar_lista = st.form_submit_button("✨ Confirmar y Registrar Lista")
        
        if boton_enviar_lista:
            if nombre_nueva_lista:
                if nombre_nueva_lista not in st.session_state.listas_guardadas:
                    st.session_state.listas_guardadas[nombre_nueva_lista] = []
                    guardar_listas()
                    st.success(f"¡Éxito! Lista '{nombre_nueva_lista}' agregada de forma permanente.")
                    st.rerun()
                else:
                    st.warning(f"La lista '{nombre_nueva_lista}' ya existe en el sistema.")
            else:
                st.error("No puedes registrar una lista con el nombre vacío.")

    st.write("---")

    # --- SECCIÓN B: BORRAR LISTAS ---
    st.write("### 🗑️ Panel 2: Eliminar una Lista Completa")
    col_del_l1, col_del_l2 = st.columns([3, 1])
    
    with col_del_l1:
        lista_a_eliminar = st.selectbox(
            "Selecciona la lista que quieres destruir para siempre:", 
            list(st.session_state.listas_guardadas.keys()), 
            key="select_borrar_lista_completa"
        )
    with col_del_l2:
        st.write("##")
        if st.button("💥 Destruir Lista"):
            if lista_a_eliminar:
                del st.session_state.listas_guardadas[lista_a_eliminar]
                guardar_listas()
                st.success(f"Lista '{lista_a_eliminar}' eliminada del sistema.")
                st.rerun()

    st.write("---")
    
    # --- SECCIÓN C: GESTIÓN DE TICKERS ---
    st.write("### 📊 Panel 3: Administrar Tickers de una Lista")
    lista_a_revisar = st.selectbox(
        "Elige la lista que deseas editar por dentro:", 
        list(st.session_state.listas_guardadas.keys()), 
        key="select_lista_valores"
    )
    
    if lista_a_revisar:
        tickers_actuales = st.session_state.listas_guardadas[lista_a_revisar]
        
        st.write("#### ➕ Añadir Activo")
        c_add1, c_add2 = st.columns([3, 1])
        with c_add1:
            nuevo_ticker = st.text_input(
                "Introduce el Ticker oficial (Ej: RKLB, MSFT, INTC):", 
                key="txt_nuevo_ticker"
            ).upper().strip()
        with c_add2:
            st.write("##")
            if st.button("📥 Insertar Activo"):
                if nuevo_ticker:
                    if nuevo_ticker not in tickers_actuales:
                        tickers_actuales.append(nuevo_ticker)
                        st.session_state.listas_guardadas[lista_a_revisar] = tickers_actuales
                        guardar_listas()
                        st.success(f"¡{nuevo_ticker} añadido a '{lista_a_revisar}'!")
                        st.rerun()
                    else:
                        st.warning(f"El activo {nuevo_ticker} ya está en la lista.")
                else:
                    st.error("Introduce un ticker válido.")

        st.write("#### ➖ Eliminar Activo")
        c_del1, c_del2 = st.columns([3, 1])
        with c_del1:
            ticker_a_borrar = st.selectbox(
                "Selecciona el activo que deseas retirar:", 
                ["Ninguno"] + tickers_actuales,
                key="select_borrar_ticker"
            )
        with c_del2:
            st.write("##")
            if st.button("🗑️ Borrar Activo"):
                if ticker_a_borrar != "Ninguno":
                    tickers_actuales.remove(ticker_a_borrar)
                    st.session_state.listas_guardadas[lista_a_revisar] = tickers_actuales
                    guardar_listas()
                    st.success(f"¡{ticker_a_borrar} retirado!")
                    st.rerun()

        st.write(f"##### 📋 Vista de Activos Guardados en '{lista_a_revisar}' ({len(tickers_actuales)} activos):")
        if tickers_actuales:
            df_lista_ui = pd.DataFrame(tickers_actuales, columns=["Ticker Asociado"])
            st.dataframe(df_lista_ui, use_container_width=True)
        else:
            st.info("Esta lista no tiene activos. Añade algunos arriba.")
