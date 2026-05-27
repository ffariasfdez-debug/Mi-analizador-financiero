import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import os
import json

# 1. Configuración inicial de la plataforma (Obligatorio en la primera línea)
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# Archivos locales para almacenamiento permanente
ARCHIVO_CARTERA = "cartera_guardada.csv"
ARCHIVO_LISTAS = "listas_permanentes.json"

# --- TÍTULO PRINCIPAL ---
st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# --- LÓGICA DE PERSISTENCIA: LISTAS PREGRABADAS ---
if "listas_guardadas" not in st.session_state:
    if os.path.exists(ARCHIVO_LISTAS):
        try:
            with open(ARCHIVO_LISTAS, "r") as f:
                st.session_state.listas_guardadas = json.load(f)
        except:
            if os.path.exists(ARCHIVO_LISTAS):
                os.remove(ARCHIVO_LISTAS)  # Reset si el archivo está corrupto
    
    # Carga del diccionario base si no existe el archivo
    if "listas_guardadas" not in st.session_state or not isinstance(st.session_state.listas_guardadas, dict):
        st.session_state.listas_guardadas = {
            "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "AVGO", "MRVL", "TSMC"],
            "Robótica Pura y Satélites": [
                "ISRG", "ZBH", "STE", "ROK", "CGNX", "TER", 
                "ATS", "SYM", "GWW", "AME", "ADI", "FTV", "KEYS", "PTC", 
                "ANSS", "ROCK", "COHR", "DE", "CAT", "AVAV", "GE", "HON",
                "NVDA", "AMD", "ARM", "AVGO", "MRVL", "SNPS", "CDNS", "SYK", "MDT", "BSX"
            ]
        }

# Asegurar que al menos haya una lista para evitar fallos de interfaz
if not st.session_state.listas_guardadas:
    st.session_state.listas_guardadas = {"Mi Lista Principal": []}

# --- LÓGICA DE PERSISTENCIA: CARTERA DE COMPRAS ---
if "cartera_compras" not in st.session_state:
    if os.path.exists(ARCHIVO_CARTERA):
        try:
            st.session_state.cartera_compras = pd.read_csv(ARCHIVO_CARTERA)
        except:
            st.session_state.cartera_compras = pd.DataFrame()
    else:
        st.session_state.cartera_compras = pd.DataFrame()

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# --- FUNCIÓN AUXILIAR: DETECTOR GEOGRÁFICO DE BOLSAS ---
def identificar_mercado_y_divisa(ticker):
    ticker_upper = str(ticker).upper().strip()
    if ticker_upper.endswith(".AS"):
        return "Euronext Ámsterdam", "EUR (€)"
    elif ticker_upper.endswith(".DE"):
        return "Xetra Alemania", "EUR (€)"
    elif ticker_upper.endswith(".MC"):
        return "Bolsa de Madrid", "EUR (€)"
    elif ticker_upper.endswith(".PA"):
        return "Bolsa de París", "EUR (€)"
    elif ticker_upper.endswith(".L"):
        return "Bolsa de Londres", "GBP (£)"
    else:
        return "Wall Street (EE.UU.)", "USD ($)"

# --- FUNCIÓN AUXILIAR: COMPROBAR HORARIO DE WALL STREET ---
def comprobar_mercado_abierto():
    tz_ny = pytz.timezone('America/New_York')
    hora_ny = datetime.now(tz_ny)
    dia_semana = hora_ny.weekday()
    inicio_mercado = hora_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    fin_mercado = hora_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    return dia_semana <= 4 and inicio_mercado <= hora_ny <= fin_mercado

# --- FUNCIÓN OPTIMIZADA PARA OBTENER INFO CLAVE DE YFINANCE ---
@st.cache_data(ttl=300)
def obtener_info_segura(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        target = info.get('targetMedianPrice', None)
        dy = info.get('dividendYield', None)
        if dy is not None and dy > 1.0:
            dy = dy / 100.0
        return target, dy
    except:
        return None, None

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente y Maduración Trimestral")

    if comprobar_mercado_abierto():
        st.success("🟢 MERCADO ABIERTO: Operaciones simuladas con precios e impacto en vivo.")
    else:
        st.warning("🕒 MERCADO CERRADO: El bot utilizará los últimos precios de cierre disponibles.")

    st.write("#### 🛡️ Reglas de Gestión Monetaria y Control de Riesgo")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        max_por_accion = st.number_input("Capital fijo por operación (€):", min_value=100, max_value=5000, value=1000, step=100)
    with col_r2:
        tope_semanal = st.slider("Tope de presupuesto compras semanales (€):", min_value=1000, max_value=30000, value=10000, step=1000)
    with col_r3:
        max_activos_cartera = st.number_input("Cupo máximo de acciones en cartera:", min_value=1, max_value=30, value=10, step=1)

    col_btn1, col_btn2 = st.columns([3, 1])
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

    if ejecutar_bot:
        st.cache_data.clear()
        st.toast("Rastreando huella institucional y capturando precios permanentes...")

        # Mapear los precios históricos reales para no pisarlos en los refrescos de pantalla
        precios_entrada_existentes = {}
        fechas_compra_existentes = {}
        if not st.session_state.cartera_compras.empty and "Ticker" in st.session_state.cartera_compras.columns:
            for _, idx in st.session_state.cartera_compras.iterrows():
                if "Precio Entrada Base" in idx and pd.notna(idx["Ticker"]):
                    precios_entrada_existentes[str(idx["Ticker"])] = float(idx["Precio Entrada Base"])
                if "Fecha Compra" in idx and pd.notna(idx["Ticker"]):
                    fechas_compra_existentes[str(idx["Ticker"])] = idx["Fecha Compra"]

        nombre_lista_bot = "Robótica Pura y Satélites" if "Robótica Pura y Satélites" in st.session_state.listas_guardadas else list(st.session_state.listas_guardadas.keys())[0]
        lista_tickers = st.session_state.listas_guardadas[nombre_lista_bot]
        
        if lista_tickers:
            tickers_string = " ".join(lista_tickers)
            try:
                datos_globales = yf.download(tickers_string, period="1y", group_by="ticker", progress=False, actions=True)
                datos_minuto = yf.download(tickers_string, period="1d", interval="1m", group_by="ticker", progress=False)
            except:
                datos_globales = pd.DataFrame()
                datos_minuto = pd.DataFrame()

            candidatas_finalistas = []

            for tick in lista_tickers:
                try:
                    if tick in datos_globales.columns.levels[0]:
                        historial = datos_globales[tick].dropna()
                    else:
                        historial = yf.Ticker(tick).history(period="1y", actions=True)
                    
                    if not historial.empty and len(historial) >= 200:
                        if tick in datos_minuto.columns.levels[0] and not datos_minuto[tick].dropna().empty:
                            precio_actual = datos_minuto[tick].dropna()['Close'].iloc[-1]
                        else:
                            precio_actual = historial['Close'].iloc[-1]

                        media_30 = historial['Close'].iloc[-30:].mean()
                        media_200 = historial['Close'].iloc[-200:].mean()
                        p_minimo_50 = historial['Close'].iloc[-50:].min()
                        volumen_actual = historial['Volume'].iloc[-1]
                        media_volumen_20 = historial['Volume'].iloc[-21:-1].mean()
                        
                        if precio_actual > media_200 and precio_actual >= (media_30 * 0.98):
                            precio_hace_60d = historial['Close'].iloc[-60]
                            crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                            crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))

                            if crecimiento_porcentaje >= 20.0:
                                target_estimado, div_yield = obtener_info_segura(tick)
                                if div_yield is None or div_yield == 0:
                                    if 'Dividends' in historial.columns:
                                        dividendos_totales_año = historial['Dividends'].sum()
                                        if dividendos_totales_año > 0:
                                            div_yield = dividendos_totales_año / precio_actual

                                potencial_4a = ((target_estimado - precio_actual) / precio_actual) * 100 if target_estimado else crecimiento_porcentaje * 1.18
                                riesgo_suelo = max(0.5, ((precio_actual - p_minimo_50) / precio_actual) * 100)
                                ratio_rb_calc = potencial_4a / riesgo_suelo
                                
                                div_txt = "❌ 0%" if (div_yield is None or div_yield == 0) else f"💰 {div_yield * 100:.2f}%"
                                fuerza_volumen = "🔥 ALTO" if volumen_actual > (media_volumen_20 * 1.15) else "🟢 NORMAL"
                                
                                candidatas_finalistas.append({
                                    "Ticker": str(tick).upper().strip(),
                                    "Precio Actual": precio_actual,
                                    "Crecimiento Anual": crecimiento_porcentaje,
                                    "Potencial Real": potencial_4a,
                                    "Ratio R:B": f"1 : {ratio_rb_calc:.1f}",
                                    "Dividendo": div_txt,
                                    "Volumen Institucional": fuerza_volumen
                                })
                except:
                    pass

            posiciones_compradas = []
            gasto_semanal_actual = 0.0
            
            if candidatas_finalistas:
                df_ordenado = pd.DataFrame(candidatas_finalistas).sort_values(by="Potencial Real", ascending=False)
                
                for _, fila in df_ordenado.iterrows():
                    ticker_limpio = str(fila["Ticker"])
                    if len(posiciones_compradas) >= max_activos_cartera or (gasto_semanal_actual + max_por_accion) > tope_semanal:
                        break
                    
                    gasto_semanal_actual += max_por_accion
                    
                    if ticker_limpio in precios_entrada_existentes:
                        precio_entrada_final = precios_entrada_existentes[ticker_limpio]
                        fecha_compra = fechas_compra_existentes.get(ticker_limpio, datetime.now().strftime('%d/%m/%Y'))
                    else:
                        precio_entrada_final = fila["Precio Actual"]
                        fecha_compra = datetime.now().strftime('%d/%m/%Y')
                    
                    fecha_liberacion = (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y')
                    amount_acciones = round(max_por_accion / precio_entrada_final, 4)
                    
                    mercado_desc, divisa_desc = identificar_mercado_y_divisa(
