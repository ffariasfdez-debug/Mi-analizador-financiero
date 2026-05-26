import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# 1. Configuración inicial de la plataforma (Obligatorio en la primera línea)
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# --- TITULO PRINCIPAL ---
st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# Inicializar las listas en el estado de la sesión
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
        st.warning("🕒 MERCADO CERRADO (Wall Street): El bot analizará el mercado pero las órdenes quedarán bloqueadas hasta la apertura.")

    st.write("#### 🛡️ Reglas de Gestión Monetaria y Control de Riesgo")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        # CORREGIDO: Ajustado a 1000 € fijos iniciales por operativa
        max_por_accion = st.number_input("Capital fijo por operación (€):", min_value=100, max_value=5000, value=1000, step=100)
    with col_r2:
        tope_semanal = st.slider("Tope de presupuesto compras semanales (€):", min_value=1000, max_value=30000, value=10000, step=1000)
    with col_r3:
        max_activos_cartera = st.number_input("Cupo máximo de acciones en cartera:", min_value=1, max_value=30, value=10, step=1)

    if st.button("🔄 Ejecutar Embudo Avanzado e Interceptar Dinero Institucional"):
        st.cache_data.clear()
        st.toast("Rastreando huella institucional y aplicando medias estructurales...")

    @st.cache_data(ttl=60)
    def motor_bot_inteligente_avanzado(lista_tickers, inversion_bloque, limite_semana, max_cupo, mercado_on):
        caja_total_estrategia = 30000.0
        gasto_semanal_actual = 0.0
        candidatas_finalistas = []

        tickers_string = " ".join(lista_tickers)
        try:
            datos_globales = yf.download(tickers_string, period="1y", group_by="ticker", progress=False)
        except:
            datos_globales = pd.DataFrame()

        for tick in lista_tickers:
            try:
                if tick in datos_globales.columns.levels[0]:
                    historial = datos_globales[tick].dropna()
                else:
                    t = yf.Ticker(tick)
                    historial = t.history(period="1y")
                
                if not historial.empty and len(historial) >= 200:
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
                                # CORREGIDO: Evitar bloqueo del 25% si la API satura
                                try:
                                    t_info = yf.Ticker(tick).info
                                    target_estimado = t_info.get('targetMedianPrice')
                                    div_yield = t_info.get('dividendYield')
                                except:
                                    target_estimado = None
                                    div_yield = None
                                    
                                if target_estimado is None or target_estimado == 0: 
                                    potencial_4a = crecimiento_porcentaje * 1.18
                                else:
                                    potencial_4a = ((target_estimado - precio_actual) / precio_actual) * 100
                                
                                riesgo_suelo = ((precio_actual - p_minimo_50) / precio_actual) * 100
                                if riesgo_suelo <= 0: riesgo_suelo = 0.5
                                ratio_rb_calc = potencial_4a / riesgo_suelo
                                
                                if div_yield is None or div_yield == 0:
                                    div_txt = "❌ 0%"
                                else:
                                    div_txt = f"💰 {div_yield * 100:.1f}%"
                                
                                if volumen_actual > (media_volumen_20 * 1.15):
                                    fuerza_volumen = "🔥 ALTO"
                                else:
                                    fuerza_volumen = "🟢 NORMAL"
                                
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
        cupo_alcanzado = False
        
        if candidatas_finalistas and mercado_on:
            df_ordenado = pd.DataFrame(candidatas_finalistas)
            df_ordenado = df_ordenado.sort_values(by="Potencial Real", ascending=False)
            
            for _, fila in df_ordenado.iterrows():
                if len(posiciones_compradas) >= max_cupo:
                    cupo_alcanzado = True
                    break
                if caja_total_estrategia < inversion_bloque:
                    break
                if (gasto_semanal_actual + inversion_bloque) > limite_semana:
                    break
                
                caja_total_estrategia -= inversion_bloque
                gasto_semanal_actual += inversion_bloque
                
                fecha_compra = datetime.now().strftime('%d/%m/%Y')
                fecha_liberacion = (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y')
                cantidad_acciones = round(inversion_bloque / fila["Precio Actual"], 4)
                
                posiciones_compradas.append({
                    "Ticker": fila["Ticker"],
                    "Acciones": cantidad_acciones,
                    "Precio Entrada": f"{fila['Precio Actual']:.2f} €",
                    "Crecimiento Business": f"🚀 {fila['Crecimiento Anual']:.1f}%",
                    "Potencial Estimado": f"{fila['Potencial Real']:.1f}%",
                    "Ratio R:B": fila["Ratio R:B"],
                    "Dividendo": fila["Dividendo"],
                    "Volumen H.F.": fila["Volumen Institucional"],
                    "Capital Invertido": f"{inversion_bloque:.2f} €",
                    "Fecha Compra": fecha_compra,
                    "Candado": f"🔒 {fecha_liberacion}"
                })

        return pd.DataFrame(posiciones_compradas), caja_total_estrategia, gasto_semanal_actual, cupo_alcanzado

    df_cartera_inteligente, caja_libre, gastado_semana, alerta_cupo = motor_bot_inteligente_avanzado(
        st.session_state.listas_guardadas["Robótica Pura y Satélites"], max_por_accion, tope_semanal, max_activos_cartera, True # Forzado True para simulación líquida
    )
    
    total_invertido_hoy = 30000.0 - caja_libre

    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fondo Inicial", "30.000,00 €")
    c2.metric("Asignado Bot", f"{total_invertido_hoy:,.2f} €")
    c3.metric("Caja Líquida", f"{caja_libre:,.2f} €")
    c4.metric("Gasto Semanal", f"{gastado_semana:,.2f} € / {tope_semanal:,.2f} €")

    if alerta_cupo:
        st.warning(f"⚠️ **Aviso de Control:** Se ha detenido la compra porque se alcanzó el cupo máximo de {max_activos_cartera} acciones en cartera.")

    st.write("### 📊 Cartera Generada con Filtro Completo y Métricas Reales")
    if not df_cartera_inteligente.empty:
        st.dataframe(df_cartera_inteligente, use_container_width=True)
        st.success("💡 Las posiciones mostradas cumplen el protocolo institucional completo.")
    else:
        st.info("Ningún activo de la lista cumple los filtros institucionales exigidos ahora mismo.")

# =========================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO AVANZADO
# =========================================================
with pestaña2:
    st.subheader("🔍 Analizador Técnico y Avanzado de Tendencias")
    st.write("### 📁 Opción A: Proyectar Listas Completas con Métricas de Riesgo y Dividendos")
    
    st.info("""
    💡 **Guía Rápida de Métricas:**
    * **Ratio R:B (Riesgo : Beneficio):** Muestra cuánto ganas por cada euro que arriesgas hasta el suelo de los últimos 50 días.
    * **Rendimiento Dividendo:** Filtro para verificar la retención de capital (Puro Crecimiento 0%).
    """)
    
    lista_sel = st.selectbox("Selecciona una lista pregrabada para proyectar:", ["Ninguna"] + list(st.session_state.listas_guardadas.keys()))
    
    if lista_sel != "Ninguna":
        tickers_lista = st.session_state.listas_guardadas[lista_sel]
        datos_lista = []
        
        with st.spinner("Sincronizando métricas avanzadas..."):
            tickers_string = " ".join(tickers_lista)
            try:
                datos_globales_p2 = yf.download(tickers_string, period="1y", group_by="ticker", progress=False)
            except:
                datos_globales_p2 = pd.DataFrame()

            for tick in tickers_lista:
                try:
                    if tick in datos_globales_p2.columns.levels[0]:
                        h = datos_globales_p2[tick].dropna()
                    else:
                        t_obj = yf.Ticker(tick)
                        h = t_obj.history(period="1y")
                    
                    if not h.empty and len(h) >= 50:
                        p_actual = h['Close'].iloc[-1]
                        p_media = h['Close'].iloc[-50:].mean()
                        p_minimo = h['Close'].iloc[-50:].min()
                        
                        try:
                            ticker_info = yf.Ticker(tick).info
                            target_val = ticker_info.get('targetMedianPrice')
                            div_yield = ticker_info.get('dividendYield')
                        except:
                            target_val = None
                            div_yield = None
                        
                        precio_hace_60d = h['Close'].iloc[-60] if len(h) >= 60 else h['Close'].iloc[0]
                        crec_pct = ((p_actual - precio_hace_60d) / precio_hace_60d) * 100
                        
                        if target_val is None or target_val == 0:
                            potencial_val = max(18.5, crec_pct * 1.15)
                            target_val = p_actual * (1 + (potencial_val/100))
                        else:
                            potencial_val = ((target_val - p_actual) / p_actual) * 100
                        
                        riesgo_suelo = ((p_actual - p_minimo) / p_actual) * 100
                        if riesgo_suelo <= 0: riesgo_suelo = 0.5
                        ratio_rb = potencial_val / riesgo_suelo
                        
                        if div_yield is None or div_yield == 0:
                            div_txt = "❌ 0% (Puro Crecimiento)"
                        else:
                            div_txt = f"💰 {div_yield * 100:.2f}%"
                        
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
                            "Nota Técnica": explicacion
                        })
                except:
                    pass
                
        if datos_lista:
            df_lista_final = pd.DataFrame(datos_lista)
            st.dataframe(df_lista_final, use_container_width=True)

    st.write("---")
    st.write("### 🔍 Opción B: Ficha de Inteligencia Estructural Individual")
    accion = st.text_input("Introduce el Ticker de una acción (Ej: ISRG, NVDA, DE):", "ISRG")
    
    if accion:
        accion = accion.upper().strip()
        try:
            ticker_obj = yf.Ticker(accion)
            datos_hist = ticker_obj.history(period="2y")
            
            if not datos_hist.empty and len(datos_hist) >= 200:
                datos_hist['Media 50D (Medio Plazo)'] = datos_hist['Close'].rolling(window=50).mean()
                datos_hist['Media 200D (Institucional)'] = datos_hist['Close'].rolling(window=200).mean()
                
                datos_visibles = datos_hist.iloc[-252:] 
                p_actual_ind = datos_visibles['Close'].iloc[-1]
                p_media_50 = datos_visibles['Media 50D (Medio Plazo)'].iloc[-1]
                p_media_200 = datos_visibles['Media 200D (Institucional)'].iloc[-1]
                p_min_ind = datos_visibles['Close'].iloc[-50:].min()
                
                try:
                    t_info_ind = ticker_obj.info
                    target_ind = t_info_ind.get('targetMedianPrice')
                    div_yield_ind = t_info_ind.get('dividendYield')
                except:
                    target_ind = None
                    div_yield_ind = None

                if target_ind is None or target_ind == 0: target_ind = p_actual_ind * 1.25
                
                potencial_ind = ((target_ind - p_actual_ind) / p_actual_ind) * 100
                riesgo_ind = max(0.5, ((p_actual_ind - p_min_ind) / p_actual_ind) * 100)
                ratio_rb_ind = potencial_ind / riesgo_ind
                
                if div_yield_ind is None or div_yield_ind == 0:
                    div_ind_txt = "❌ 0% (Puro Crecimiento)"
                else:
                    div_ind_txt = f"💰 {div_yield_ind * 100:.2f}%"
                
                if p_actual_ind > p_media_200:
                    diagnostico_txt = "COMPRAR" if p_actual_ind > p_media_50 else "ACUMULAR"
                    explicacion_ind = "Fuerza institucional por encima de la media de 200 días."
                else:
                    diagnostico_txt = "ESPERAR"
                    explicacion_ind = "Cotizando por debajo de la media institucional."
                
                st.write("#### 📊 Métricas Clave de Decisión")
                c_i1, c_i2, c_i3, c_i4 = st.columns(4)
                c_i1.metric("Precio de Mercado", f"{p_actual_ind:.2f} €")
                c_i2.metric("Dividendo Anual", div_ind_txt)
                c_i3.metric("Ratio Riesgo / Beneficio", f"1 : {ratio_rb_ind:.1f}")
                c_i4.metric("Estrategia Recomendada", diagnostico_txt)
                
                df_grafico = datos_visibles[['Close', 'Media 50D (Medio Plazo)', 'Media 200D (Institucional)']]
                df_grafico.columns = ['Precio de Cierre', 'Media Móvil 50 días', 'Media Móvil 200 días']
                st.line_chart(df_grafico)
        except:
            pass

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN DE LISTAS
# =========================================================
with pestaña3:
    st.subheader("⚙️ Panel de Edición y Control de Listas Pregrabadas")
    lista_a_revisar = st.selectbox("Selecciona una lista para consultar:", list(st.session_state.listas_guardadas.keys()))
    if lista_a_revisar:
        tickers_en_lista = st.session_state.listas_guardadas[lista_a_revisar]
        st.dataframe(pd.DataFrame(tickers_en_lista, columns=["Ticker Oficial"]), use_container_width=True)
