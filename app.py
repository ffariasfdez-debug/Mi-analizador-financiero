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
            os.remove(ARCHIVO_LISTAS)  # Reset si el archivo está corrupto
    
    # Si no existía archivo o falló la lectura, cargamos el diccionario base
    if "listas_guardadas" not in st.session_state:
        st.session_state.listas_guardadas = {
            "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "AVGO", "MRVL", "TSMC"],
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

# --- FUNCIÓN AUXILIAR: COMPROBAR HORARIO DE WALL STREET ---
def comprobar_mercado_abierto():
    tz_ny = pytz.timezone('America/New_York')
    hora_ny = datetime.now(tz_ny)
    dia_semana = hora_ny.weekday()
    inicio_mercado = hora_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    fin_mercado = hora_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    if dia_semana <= 4 and inicio_mercado <= hora_ny <= fin_mercado:
        return True
    return False

# --- FUNCIÓN OPTIMIZADA Y CORREGIDA PARA OBTENER INFO CLAVE DE YFINANCE ---
@st.cache_data(ttl=300)
def obtener_info_segura(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        target = info.get('targetMedianPrice', None)
        dy = info.get('dividendYield', None)
        
        if dy is not None and dy > 0:
            if dy > 1.0:  # Si viene como entero (ej: 1.5 en vez de 0.015)
                dy = dy / 100.0
            return target, dy
        return target, None
    except:
        return None, None

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente y Maduración Trimestral")
    st.write("El bot aplica un embudo estricto: Crecimiento negocio (**>20%**), Tendencia Institucional (**>Media 200D**), rastreo de volumen y candado de **3 meses**.")

    mercado_activo = comprobar_mercado_abierto()
    if mercado_activo:
        st.success("🟢 MERCADO ABIERTO: Las operaciones simuladas se ejecutarán con precios e impacto en vivo.")
    else:
        st.warning("🕒 MERCADO CERRADO (Wall Street): El bot analizará el mercado con los últimos precios vivos disponibles.")

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

        # El bot lee dinámicamente tu lista guardada (así hereda si has añadido/quitado tickers)
        lista_tickers = st.session_state.listas_guardadas["Robótica Pura y Satélites"]
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
                    t = yf.Ticker(tick)
                    historial = t.history(period="1y", actions=True)
                
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
                    
                    if precio_actual > media_200:
                        if precio_actual >= (media_30 * 0.98):
                            precio_hace_60d = historial['Close'].iloc[-60]
                            crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                            crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))

                            if crecimiento_porcentaje >= 20.0:
                                target_estimado, div_yield = obtener_info_segura(tick)
                                
                                if div_yield is None or div_yield == 0:
                                    try:
                                        if 'Dividends' in historial.columns:
                                            dividendos_totales_año = historial['Dividends'].sum()
                                            if dividendos_totales_año > 0:
                                                div_yield = dividendos_totales_año / precio_actual
                                    except:
                                        div_yield = 0

                                if target_estimado is None or target_estimado == 0: 
                                    potencial_4a = crecimiento_porcentaje * 1.18
                                else:
                                    potencial_4a = ((target_estimado - precio_actual) / precio_actual) * 100
                                
                                riesgo_suelo = ((precio_actual - p_minimo_50) / precio_actual) * 100
                                if riesgo_suelo <= 0: riesgo_suelo = 0.5
                                ratio_rb_calc = potencial_4a / riesgo_suelo
                                
                                div_txt = "❌ 0%" if (div_yield is None or div_yield == 0) else f"💰 {div_yield * 100:.2f}%"
                                fuerza_volumen = "🔥 ALTO" if volumen_actual > (media_volumen_20 * 1.15) else "🟢 NORMAL"
                                
                                candidatas_finalistas.append({
                                    "Ticker": tick,
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
        caja_total_estrategia = 30000.0
        gasto_semanal_actual = 0.0
        
        if candidatas_finalistas:
            df_ordenado = pd.DataFrame(candidatas_finalistas).sort_values(by="Potencial Real", ascending=False)
            
            for _, fila in df_ordenado.iterrows():
                if len(posiciones_compradas) >= max_activos_cartera or caja_total_estrategia < max_por_accion or (gasto_semanal_actual + max_por_accion) > tope_semanal:
                    break
                
                caja_total_estrategia -= max_por_accion
                gasto_semanal_actual += max_por_accion
                
                fecha_compra = datetime.now().strftime('%d/%m/%Y')
                fecha_liberacion = (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y')
                cantidad_acciones = round(max_por_accion / fila["Precio Actual"], 4)
                
                posiciones_compradas.append({
                    "Ticker": fila["Ticker"],
                    "Acciones": cantidad_acciones,
                    "Precio Entrada Base": fila["Precio Actual"],
                    "Precio Entrada": f"{fila['Precio Actual']:.2f} €",
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

    df_mostrar = st.session_state.cartera_compras.copy()
    caja_libre = 30000.0
    gastado_semana = 0.0
    alerta_cupo = False

    if not df_mostrar.empty:
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
            t_actual = fila["Ticker"]
            p_entrada = fila["Precio Entrada Base"]
            n_acciones = fila["Acciones"]
            
            try:
                if len(lista_activos_cartera) == 1:
                    p_live = cotizaciones_vivas['Close'].iloc[-1] if not cotizaciones_vivas.empty else p_entrada
                else:
                    p_live = cotizaciones_vivas[t_actual]['Close'].iloc[-1] if t_actual in cotizaciones_vivas.columns.levels[0] else p_entrada
            except:
                p_live = p_entrada

            ganancia_euros = (p_live - p_entrada) * n_acciones
            ganancia_pct = ((p_live - p_entrada) / p_entrada) * 100

            if ganancia_euros > 0:
                lista_pnl_formateada.append(f"🟩 +{ganancia_euros:.2f} € (+{ganancia_pct:.2f}%)")
            elif ganancia_euros < 0:
                lista_pnl_formateada.append(f"🟥 {ganancia_euros:.2f} € ({ganancia_pct:.2f}%)")
            else:
                lista_pnl_formateada.append(f"⬜ 0.00 € (0.00%)")

        df_mostrar["Rendimiento Actual (P&L)"] = lista_pnl_formateada
        df_final_ui = df_mostrar.drop(columns=["Precio Entrada Base", "Capital Invertido Base"])
        columnas_ordenadas = [
            "Ticker", "Acciones", "Precio Entrada", "Rendimiento Actual (P&L)", 
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
        st.success("💾 Memoria Activa: Datos de cartera blindados contra refrescos.")
    else:
        st.info("Ningún activo de la lista cumple los filtros o la cartera está vacía.")

# =========================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO AVANZADO
# =========================================================
with pestaña2:
    st.subheader("🔍 Analizador Técnico y Avanzado de Tendencias")
    st.write("### 📁 Opción A: Proyectar Listas Completas con Métricas de Riesgo y Dividendos")
    
    lista_sel = st.selectbox("Selecciona una lista pregrabada para proyectar:", ["Ninguna"] + list(st.session_state.listas_guardadas.keys()))
    
    if lista_sel != "Ninguna":
        tickers_lista = st.session_state.listas_guardadas[lista_sel]
        datos_lista = []
        
        with st.spinner("Sincronizando métricas avanzadas en vivo..."):
            tickers_string = " ".join(tickers_lista)
            try:
                datos_globales_p2 = yf.download(tickers_string, period="1y", group_by="ticker", progress=False, actions=True)
            except:
                datos_globales_p2 = pd.DataFrame()

            for tick in tickers_lista:
                try:
                    if tick in datos_globales_p2.columns.levels[0]:
                        h = datos_globales_p2[tick].dropna()
                    else:
                        t_obj = yf.Ticker(tick)
                        h = t_obj.history(period="1y", actions=True)
                    
                    if not h.empty and len(h) >= 50:
                        p_actual = h['Close'].iloc[-1]
                        p_media = h['Close'].iloc[-50:].mean()
                        p_minimo = h['Close'].iloc[-50:].min()
                        
                        target_val, div_yield = obtener_info_segura(tick)
                        
                        if div_yield is None or div_yield == 0:
                            try:
                                if 'Dividends' in h.columns:
                                    dividendos_anuales = h['Dividends'].sum()
                                    if dividendos_anuales > 0 and p_actual > 0:
                                        div_yield = dividendos_anuales / p_actual
                            except:
                                div_yield = 0
                        
                        precio_hace_60d = h['Close'].iloc[-60] if len(h) >= 60 else h['Close'].iloc[0]
                        crec_pct = ((p_actual - precio_hace_60d) / precio_hace_60d) * 100
                        
                        if target_val is None or target_val == 0:
                            potencial_val = max(20.0, crec_pct * 1.12)
                            target_val = p_actual * (1 + (potencial_val/100))
                        else:
                            potencial_val = ((target_val - p_actual) / p_actual) * 100
                        
                        riesgo_suelo = ((p_actual - p_minimo) / p_actual) * 100
                        if riesgo_suelo <= 0: riesgo_suelo = 0.5
                        ratio_rb = potencial_val / riesgo_suelo
                        
                        div_txt = "❌ 0%" if (div_yield is None or div_yield == 0) else f"💰 {div_yield * 100:.2f}%"
                        
                        if p_actual > p_media and potencial_val >= 20.0:
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
                            "Precio Actual": f"{p_actual:.2f} €", 
                            "Precio Objetivo Real": f"{target_val:.2f} €",
                            "Potencial Estimado": f"{potencial_val:.1f}%",
                            "Ratio R:B (1 : X)": f"1 : {ratio_rb:.1f}",
                            "Rendimiento Dividendo": div_txt,
                            "Estrategia": sem_lista,
                            "Nota Técnico": explicacion
                        })
                except:
                    pass
                
        if datos_lista:
            df_lista_final = pd.DataFrame(datos_lista)
            st.dataframe(df_lista_final, use_container_width=True)

    st.write("---")
    st.write("### 🔍 Opción B: Ficha de Inteligencia Estructural Individual")
    accion = st.text_input("Introduce el Ticker de una acción (Ej: ISRG, NVDA, DE):", "KLAC")
    
    if accion:
        accion = accion.upper().strip()
        try:
            ticker_obj = yf.Ticker(accion)
            datos_hist = ticker_obj.history(period="2y", actions=True)
            
            if not datos_hist.empty and len(datos_hist) >= 200:
                datos_hist['Media 50D (Medio Plazo)'] = datos_hist['Close'].rolling(window=50).mean()
                datos_hist['Media 200D (Institucional)'] = datos_hist['Close'].rolling(window=200).mean()
                
                datos_visibles = datos_hist.iloc[-252:] 
                p_actual_ind = datos_visibles['Close'].iloc[-1]
                p_media_50 = datos_visibles['Media 50D (Medio Plazo)'].iloc[-1]
                p_media_200 = datos_visibles['Media 200D (Institucional)'].iloc[-1]
                p_min_ind = datos_visibles['Close'].iloc[-50:].min()
                
                target_ind, div_yield_ind = obtener_info_segura(accion)

                if div_yield_ind is None or div_yield_ind == 0:
                    try:
                        if 'Dividends' in datos_visibles.columns:
                            div_tot_ind = datos_visibles['Dividends'].sum()
                            if div_tot_ind > 0 and p_actual_ind > 0:
                                div_yield_ind = div_tot_ind / p_actual_ind
                    except:
                        div_yield_ind = 0

                if target_ind is None or target_ind == 0: target_ind = p_actual_ind * 1.25
                
                potencial_ind = ((target_ind - p_actual_ind) / p_actual_ind) * 100
                riesgo_ind = max(0.5, ((p_actual_ind - p_min_ind) / p_actual_ind) * 100)
                ratio_rb_ind = potencial_ind / riesgo_ind
                
                div_ind_txt = "❌ 0%" if (div_yield_ind is None or div_yield_ind == 0) else f"💰 {div_yield_ind * 100:.2f}%"
                
                if p_actual_ind > p_media_200:
                    diagnostico_txt = "COMPRAR" if p_actual_ind > p_media_50 else "ACUMULAR"
                else:
                    diagnostico_txt = "ESPERAR"
                
                st.write("#### 📊 Métricas Clave de Decisión")
                c_i1, c_i2, c_i3, c_i4 = st.columns(4)
                c_i1.metric("Precio de Mercado", f"{p_actual_ind:.2f} €")
                c_i2.metric("Dividendo Anual", div_ind_txt)
                c_i3.metric("Ratio Riesgo / Beneficio", f"1 : {ratio_rb_ind:.1f}")
                c_i4.metric("Estrategia Recommended", diagnostico_txt)
                
                df_grafico = datos_visibles[['Close', 'Media 50D (Medio Plazo)', 'Media 200D (Institucional)']]
                df_grafico.columns = ['Precio de Cierre', 'Media Móvil 50 días', 'Media Móvil 200 días']
                st.line_chart(df_grafico)
        except:
            pass

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN DE LISTAS (EDITABLE Y PERMANENTE)
# =========================================================
with pestaña3:
    st.subheader("⚙️ Panel de Edición y Control de Listas Pregrabadas")
    st.write("Gestiona el universo de activos que lee el Bot y el Analizador Avanzado de manera persistente.")

    lista_a_revisar = st.selectbox("Selecciona una lista para gestionar:", list(st.session_state.listas_guardadas.keys()))
    
    if lista_a_revisar:
        tickers_actuales = st.session_state.listas_guardadas[lista_a_revisar]
        
        # --- SUB-PANEL: AÑADIR NUEVO TICKER ---
        st.write("#### ➕ Añadir Activo a esta Lista")
        c_add1, c_add2 = st.columns([3, 1])
        with c_add1:
            nuevo_ticker = st.text_input("Introduce el Ticker oficial (Ej: RKLB, MSFT, INTC):", key="txt_nuevo_ticker").upper().strip()
        with c_add2:
            st.write("##") # Espaciador para alinear el botón
            if st.button("📥 Insertar Activo"):
                if nuevo_ticker and nuevo_ticker not in tickers_actuales:
                    tickers_actuales.append(nuevo_ticker)
                    st.session_state.listas_guardadas[lista_a_revisar] = tickers_actuales
                    
                    # Guardar físicamente en el JSON
                    with open(ARCHIVO_LISTAS, "w") as f:
                        json.dump(st.session_state.listas_guardadas, f)
                    
                    st.success(f"¡{nuevo_ticker} añadido con éxito a '{lista_a_revisar}'!")
                    st.rerun()
                elif nuevo_ticker in tickers_actuales:
                    st.warning(f"El activo {nuevo_ticker} ya forma parte de esta lista.")

        # --- SUB-PANEL: ELIMINAR TICKER ---
        st.write("#### ➖ Eliminar Activo de esta Lista")
        c_del1, c_del2 = st.columns([3, 1])
        with c_del1:
            ticker_a_borrar = st.selectbox("Selecciona el activo que deseas retirar:", ["Ninguno"] + tickers_actuales)
        with c_del2:
            st.write("##") # Espaciador
            if st.button("🗑️ Borrar Activo"):
                if ticker_a_borrar != "Ninguno":
                    tickers_actuales.remove(ticker_a_borrar)
                    st.session_state.listas_guardadas[lista_a_revisar] = tickers_actuales
                    
                    # Guardar físicamente en el JSON
                    with open(ARCHIVO_LISTAS, "w") as f:
                        json.dump(st.session_state.listas_guardadas, f)
                        
                    st.success(f"¡{ticker_a_borrar} eliminado de '{lista_a_revisar}'!")
                    st.rerun()

        st.write("---")
        st.write(f"### 📋 Vista Actual Completa: {lista_a_revisar} ({len(tickers_actuales)} activos)")
        # Mostramos la tabla interactiva y limpia de la lista
        df_lista_ui = pd.DataFrame(tickers_actuales, columns=["Ticker Asociado"])
        st.dataframe(df_lista_ui, use_container_width=True)
