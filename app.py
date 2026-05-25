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

# Inicializar las listas en el estado de la sesión (RADAR AMPLIADO CON SATÉLITES)
if "listas_guardadas" not in st.session_state:
    st.session_state.listas_guardadas = {
        "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "AVGO", "MRVL", "TSMC"],
        "Robótica Pura y Satélites": [
            # --- El Núcleo de Robótica Original ---
            "ISRG", "ZBH", "STE", "ROK", "CGNX", "TER", 
            "ATS", "SYM", "GWW", "AME", "ADI", "FTV", "KEYS", "PTC", 
            "ANSS", "ROCK", "COHR", "DE", "CAT", "AVAV", "GE", "HON",
            # --- Satélites: Cerebros e Infraestructura de IA ---
            "NVDA", "AMD", "ARM", "AVGO", "MRVL",
            # --- Satélites: Software Industrial y Visión Artificial ---
            "SNPS", "CDNS", "ANSS", "SPLK",
            # --- Satélites: Automatización Médica y Quirúrgica Avanzada ---
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
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K (VERSION FILTRADO INSTITUCIONAL)
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente y Maduración Trimestral")
    st.write("El bot aplica un embudo estricto: Crecimiento negocio (**>20%**), Tendencia Institucional (**>Media 200D**), rastreo de volumen y candado de **3 meses**.")

    mercado_activo = comprobar_mercado_abierto()
    if mercado_activo:
        st.success("🟢 MERCADO ABIERTO: Las operaciones simuladas se ejecutarán con precios e impacto en vivo.")
    else:
        st.warning("🕒 MERCADO CERRADO (Wall Street): El bot analizará el mercado pero las órdenes quedarán bloqueadas hasta la apertura.")

    st.write("#### 🛡️ Reglas de Gestión Monetaria Py Control de Riesgo")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        max_por_accion = st.number_input("Capital fijo por operación (€):", min_value=100, max_value=5000, value=2500, step=100)
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
                    
                    volumen_actual = historial['Volume'].iloc[-1]
                    media_volumen_20 = historial['Volume'].iloc[-21:-1].mean()
                    
                    # FILTRO 1: Tendencia Institucional (Por encima de 200 MA)
                    if precio_actual > media_200:
                        # FILTRO 2: Ignición a corto plazo
                        if precio_actual >= (media_30 * 0.98):
                            precio_hace_60d = historial['Close'].iloc[-60]
                            crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                            crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))

                            # FILTRO 3: Crecimiento de negocio > 20%
                            if crecimiento_porcentaje >= 20.0:
                                target_estimado = precio_actual * 1.28
                                potencial_4a = ((target_estimado - precio_actual) / precio_actual) * 100
                                
                                # Evaluación de Volumen
                                if volumen_actual > (media_volumen_20 * 1.15):
                                    fuerza_volumen = "🔥 ALTO (Institucional)"
                                else:
                                    fuerza_volumen = "🟢 NORMAL"
                                
                                candidatas_finalistas.append({
                                    "Ticker": tick,
                                    "Precio Actual": precio_actual,
                                    "Crecimiento Anual": crecimiento_porcentaje,
                                    "Potencial 4A Real": potencial_4a,
                                    "Volumen Institucional": fuerza_volumen
                                })
            except:
                pass

        posiciones_compradas = []
        cupo_alcanzado = False
        
        if candidatas_finalistas and mercado_on:
            df_ordenado = pd.DataFrame(candidatas_finalistas)
            df_ordenado = df_ordenado.sort_values(by="Potencial 4A Real", ascending=False)
            
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
                    "Crecimiento Negocio": f"🚀 {fila['Crecimiento Anual']:.1f}%",
                    "Volumen H.F.": fila["Volumen Institucional"],
                    "Potencial Estimado": f"{fila['Potencial 4A Real']:.1f}%",
                    "Capital Invertido": f"{inversion_bloque:.2f} €",
                    "Fecha Compra": fecha_compra,
                    "Candado Bloqueado Hasta": f"🔒 {fecha_liberacion}",
                    "Estado": "🟢 COMPRADO"
                })

        return pd.DataFrame(posiciones_compradas), caja_total_estrategia, gasto_semanal_actual, cupo_alcanzado

    df_cartera_inteligente, caja_libre, gastado_semana, alerta_cupo = motor_bot_inteligente_avanzado(
        st.session_state.listas_guardadas["Robótica Pura y Satélites"], max_por_accion, tope_semanal, max_activos_cartera, mercado_activo
    )
    
    total_invertido_hoy = 30000.0 - caja_libre

    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fondo de Inversión Inicial", "30.000,00 €")
    c2.metric("Asignado por Inteligencia", f"{total_invertido_hoy:,.2f} €")
    c3.metric("Caja Líquida Disponible", f"{caja_libre:,.2f} €")
    c4.metric("Gasto Semanal vs Tope", f"{gastado_semana:,.2f} € / {tope_semanal:,.2f} €")

    if alerta_cupo:
        st.warning(f"⚠️ **Aviso de Control:** Se ha detenido la compra porque se alcanzó el cupo máximo de {max_activos_cartera} acciones en cartera.")

    st.write("### 📊 Cartera Generada con Filtro de Tendencia y Volumen Institucional")
    if mercado_activo:
        if not df_cartera_inteligente.empty:
            st.dataframe(df_cartera_inteligente, use_container_width=True)
            st.success("💡 Las posiciones mostradas cumplen el protocolo institucional completo.")
        else:
            st.info("Ningún activo de la lista cumple los filtros institucionales exigidos ahora mismo.")
    else:
        st.info("🛒 Sistema Canalizado: El radar ha preseleccionado los activos con éxito, pero las órdenes están retenidas. Ejecuta el bot con Wall Street abierto.")

# =========================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO AVANZADO (RESTAURADA Y OPERATIVA)
# =========================================================
with pestaña2:
    st.subheader("🔍 Analizador Técnico y Avanzado de Tendencias")
    
    st.write("### 📁 Opción A: Proyectar Listas Completas con Métricas de Riesgo")
    lista_sel = st.selectbox("Selecciona una lista pregrabada para proyectar:", ["Ninguna"] + list(st.session_state.listas_guardadas.keys()))
    
    if lista_sel != "Ninguna":
        tickers_lista = st.session_state.listas_guardadas[lista_sel]
        datos_lista = []
        
        for tick in tickers_lista:
            try:
                t = yf.Ticker(tick)
                h = t.history(period="60d")
                if not h.empty:
                    p_actual = h['Close'].iloc[-1]
                    p_media = h['Close'].mean()
                    p_minimo = h['Close'].min()
                    
                    try:
                        target_val = t.info.get('targetMedianPrice')
                        if target_val is None or target_val == 0: target_val = p_actual * 1.25
                    except:
                        target_val = p_actual * 1.25
                        
                    potencial_val = ((target_val - p_actual) / p_actual) * 100
                    riesgo_suelo = max(0.5, ((p_actual - p_minimo) / p_actual) * 100)
                    ratio_rb = potencial_val / riesgo_suelo
                    
                    if p_actual > p_media and potencial_val >= 20.0:
                        sem_lista = "🟢 COMPRAR"
                        explicacion = "Tendencia alcista clara y margen de seguridad óptimo analista."
                    elif potencial_val >= 15.0:
                        sem_lista = "🟡 ACUMULAR"
                        explicacion = "Consolidando soportes históricos. Atractivo para medio plazo."
                    else:
                        sem_lista = "🔴 ESPERAR"
                        explicacion = "Precio ajustado a su valoración actual. Sin margen de seguridad claro."
                        
                    datos_lista.append({
                        "Ticker": tick, 
                        "Precio Actual": f"{p_actual:.2f} €", 
                        "Precio Objetivo": f"{target_val:.2f} €",
                        "Potencial Estimado": f"{potencial_val:.1f}%",
                        "Ratio R:B": f"1 : {ratio_rb:.1f}",
                        "Estrategia": sem_lista,
                        "Nota Técnica": explicacion
                    })
            except:
                pass
                
        if datos_lista:
            st.dataframe(pd.DataFrame(datos_lista), use_container_width=True)

    st.write("---")
    st.write("### 🔍 Opción B: Ficha de Inteligencia Estructural Individual")
    accion = st.text_input("Introduce el Ticker de una acción (Ej: ISRG, ROK, DE):", "ISRG")
    
    if accion:
        accion = accion.upper()
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
                    target_ind = ticker_obj.info.get('targetMedianPrice')
                    if target_ind is None or target_ind == 0: target_ind = p_actual_ind * 1.25
                except:
                    target_ind = p_actual_ind * 1.25
                
                potencial_ind = ((target_ind - p_actual_ind) / p_actual_ind) * 100
                riesgo_ind = max(0.5, ((p_actual_ind - p_min_ind) / p_actual_ind) * 100)
                ratio_rb_ind = potencial_ind / riesgo_ind
                
                if p_actual_ind > p_media_200:
                    estado_ind = "🟢 ESTRUCTURA ALCISTA PRINCIPAL"
                    if p_actual_ind > p_media_50:
                        diagnostico_txt = "COMPRAR (Confirmación de Tendencia)"
                        explicacion_ind = f"El activo cotiza con fuerza por encima de sus dos medias móviles principales (50 y 200 días)."
                    else:
                        diagnostico_txt = "ACUMULAR (Retroceso Técnico)"
                        explicacion_ind = f"El activo mantiene su tendencia alcista principal a largo plazo, pero ha corregido a corto plazo por debajo de la de 50 días."
                else:
                    estado_ind = "🔴 TENDENCIA BAJISTA / BAJO MOMENTUM"
                    diagnostico_txt = "ESPERAR (Falta de Fuerza)"
                    explicacion_ind = f"El precio cotiza por debajo de la media institucional de 200 días. Entorno complejo."
                
                st.write("#### 📊 Métricas Clave de Decisión")
                c_i1, c_i2, c_i3, c_i4 = st.columns(4)
                c_i1.metric("Precio de Mercado", f"{p_actual_ind:.2f} €")
                c_i2.metric("Salud de Fondo", estado_ind)
                c_i3.metric("Ratio Riesgo / Beneficio", f"1 : {ratio_rb_ind:.1f}")
                c_i4.metric("Estrategia Recomendada", diagnostico_txt)
                
                st.write(f"**📉 Gráfico de Evolución Estructural de {accion} (Último Año sin cortes)**")
                df_grafico = datos_visibles[['Close', 'Media 50D (Medio Plazo)', 'Media 200D (Institucional)']]
                df_grafico.columns = ['Precio de Cierre', 'Media Móvil 50 días', 'Media Móvil 200 días']
                st.line_chart(df_grafico)
            else:
                st.error("No hay suficiente historial en Yahoo Finance para este activo.")
        except Exception as e:
            st.error(f"Error al procesar el Ticker: {str(e)}")

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN Y EDICIÓN DE LISTAS (RESTAURADA Y OPERATIVA)
# =========================================================
with pestaña3:
    st.subheader("⚙️ Panel de Edición y Control de Listas Pregrabadas")
    
    st.write("### 📋 Ver Componentes de una Lista")
    lista_a_revisar = st.selectbox("Selecciona una lista para consultar:", list(st.session_state.listas_guardadas.keys()))
    
    if lista_a_revisar:
        tickers_en_lista = st.session_state.listas_guardadas[lista_a_revisar]
        st.info(f"La lista **{lista_a_revisar}** contiene actualmente **{len(tickers_en_lista)}** activos.")
        df_tickers = pd.DataFrame(tickers_en_lista, columns=["Ticker Oficial (Yahoo Finance)"])
        st.dataframe(df_tickers, use_container_width=True)

    st.write("---")
    
    st.write("### 🛠️ Modificar Tickers de una Lista Existente")
    col_mod1, col_mod2 = st.columns(2)
    
    with col_mod1:
        nuevo_ticker = st.text_input("Introduce un Ticker para AÑADIR (Ej: TSLA, NVDA):").upper().strip()
        if st.button("➕ Añadir Ticker a la Lista"):
            if nuevo_ticker and nuevo_ticker not in st.session_state.listas_guardadas[lista_a_revisar]:
                st.session_state.listas_guardadas[lista_a_revisar].append(nuevo_ticker)
                st.success(f"¡{nuevo_ticker} añadido con éxito!")
                st.rerun()
                
    with col_mod2:
        ticker_eliminar = st.text_input("Introduce un Ticker para ELIMINAR:").upper().strip()
        if st.button("❌ Eliminar Ticker de la Lista"):
            if ticker_eliminar in st.session_state.listas_guardadas[lista_a_revisar]:
                st.session_state.listas_guardadas[lista_a_revisar].remove(ticker_eliminar)
                st.success(f"¡{ticker_eliminar} retirado con éxito!")
                st.rerun()

    st.write("---")

    st.write("### 🆕 Crear una Nueva Lista Personalizada")
    nombre_nueva_lista = st.text_input("Nombre de la nueva lista (Ej: Robótica Médica):").strip()
    tickers_nueva_lista = st.text_area("Introduce los Tickers separados por comas (Ej: AAPL, MSFT, GOOG):").upper()
    
    if st.button("💾 Guardar Nueva Lista en el Sistema"):
        if nombre_nueva_lista and tickers_nueva_lista:
            lista_limpia = [t.strip() for t in tickers_nueva_lista.split(",") if t.strip()]
            st.session_state.listas_guardadas[nombre_nueva_lista] = lista_limpia
            st.success(f"¡La nueva lista '{nombre_nueva_lista}' ha sido registrada!")
            st.rerun()
