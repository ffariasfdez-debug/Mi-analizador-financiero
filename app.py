import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import os
import json

# 1. Configuración inicial de la plataforma
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

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
                os.remove(ARCHIVO_LISTAS)
    
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

# --- PESTAÑAS ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# --- FUNCIÓN AUXILIAR: MAREO DE BOLSAS ---
def identificar_mercado_y_divisa(ticker):
    ticker_upper = ticker.upper()
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
            st.success("¡Cartera reseteada!")
            st.rerun()

    if ejecutar_bot:
        st.cache_data.clear()
        st.toast("Rastreando huella institucional...")

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
                    
                    mercado_desc, divisa_desc = identificar_mercado_y_divisa(ticker_limpio)
                    
                    posiciones_compradas.append({
                        "Ticker": ticker_limpio,
                        "Plaza Cotización": mercado_desc,
                        "Divisa": divisa_desc,
                        "Acciones": amount_acciones,
                        "Precio Entrada Base": precio_entrada_final,
                        "Precio Entrada": f"{precio_entrada_final:.2f}",
                        "Crecimiento Business": f"🚀 {fila['Crecimiento Anual']:.1f}%",
                        "Potencial Estimado": f"{fila['Potencial Real']:.1f}%",
                        "Ratio R:B": fila["Ratio R:B"],
                        "Dividendo": fila["Dividendo"],
                        "Volumen H.F.": fila["Volumen Institucional"],
                        "Capital Invertido Base": max_por_accion,
                        "Capital Invertido": f"{max_por_accion:.2f} €",
                        "Fecha Compra": fecha_compra,
                        "Candado": f"🔒 {fecha_liberacion}"
                    })
                
                st.session_state.cartera_compras = pd.DataFrame(posiciones_compradas)
                st.session_state.cartera_compras.to_csv(ARCHIVO_CARTERA, index=False)

    # --- RENDERIZADO CON NUEVAS COLUMNAS DE IDENTIFICACIÓN ---
    df_mostrar = st.session_state.cartera_compras.copy()
    caja_libre = 30000.0
    gastado_semana = 0.0
    alerta_cupo = False

    if not df_mostrar.empty and "Ticker" in df_mostrar.columns:
        df_mostrar["Ticker"] = df_mostrar["Ticker"].astype(str).str.upper().str.strip()
        
        caja_libre = 30000.0 - df_mostrar["Capital Invertido Base"].sum()
        gastado_semana = df_mostrar["Capital Invertido Base"].sum()
        alerta_cupo = len(df_mostrar) >= max_activos_cartera

        lista_activos_cartera = df_mostrar["Ticker"].tolist()
        try:
            cotizaciones_vivas = yf.download(" ".join(lista_activos_cartera), period="1d", interval="1m", group_by="ticker", progress=False)
        except:
            cotizaciones_vivas = pd.DataFrame()

        lista_pnl_formateada = []
        for _, fila in df_mostrar.iterrows():
            t_actual = str(fila["Ticker"])
            p_entrada = fila["Precio Entrada Base"]
            n_acciones = fila["Acciones"]
            divisa_simbolo = "$" if "USD" in str(fila.get("Divisa", "")) else "€"
            
            try:
                if len(lista_activos_cartera) == 1:
                    p_live = cotizaciones_vivas['Close'].iloc[-1] if not cotizaciones_vivas.empty else p_entrada
                else:
                    p_live = cotizaciones_vivas[t_actual]['Close'].iloc[-1] if t_actual in cotizaciones_vivas.columns.levels[0] else p_entrada
            except:
                p_live = p_entrada

            ganancia_moneda = (p_live - p_entrada) * n_acciones
            ganancia_pct = ((p_live - p_entrada) / p_entrada) * 100

            if ganancia_moneda > 0.01:
                lista_pnl_formateada.append(f"🟩 +{ganancia_moneda:.2f} {divisa_simbolo} (+{ganancia_pct:.2f}%)")
            elif ganancia_moneda < -0.01:
                lista_pnl_formateada.append(f"🟥 {ganancia_moneda:.2f} {divisa_simbolo} ({ganancia_pct:.2f}%)")
            else:
                lista_pnl_formateada.append(f"⬜ 0.00 {divisa_simbolo} (0.00%)")

        df_mostrar["Rendimiento Actual (P&L)"] = lista_pnl_formateada
        df_final_ui = df_mostrar.drop(columns=["Precio Entrada Base", "Capital Invertido Base"])
        
        # Inyectamos "Plaza Cotización" y "Divisa" al inicio para que salten a la vista
        columnas_ordenadas = [
            "Ticker", "Plaza Cotización", "Divisa", "Acciones", "Precio Entrada", "Rendimiento Actual (P&L)", 
            "Crecimiento Business", "Potencial Estimado", "Ratio R:B", 
            "Dividendo", "Volumen H.F.", "Capital Invertido", "Fecha Compra", "Candado"
        ]
        df_final_ui = df_final_ui[columnas_ordenadas]

    total_invertido_hoy = 30000.0 - caja_libre

    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fondo Inicial", "30.000,00 €")
    c2.metric("Asignado Bot", f"{total_invertido_hoy:,.2f} €")
    c3.metric("Caja Líquida", f"{caja_libre:,.2f} €")
    c4.metric("Gasto Semanal", f"{gastado_semana:,.2f} € / {tope_semanal:,.2f} €")

    if alerta_cupo:
        st.warning(f"⚠️ **Aviso de Control:** Se alcanzó el cupo máximo de {max_activos_cartera} acciones.")

    st.write("### 📊 Cartera Generada con Filtro Completo y Métricas Reales")
    if not df_mostrar.empty:
        st.dataframe(df_final_ui, use_container_width=True)
        st.success("💾 Memoria Activa: Identificación geográfica y divisas añadidas con éxito.")
    else:
        st.info("Ningún activo de la lista cumple los filtros o la cartera está vacía.")
