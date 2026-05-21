import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# Configuración de la página completa
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# --- TITULO PRINCIPAL ---
st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# --- INICIALIZACIÓN DEL DISCO DURO TEMPORAL (SESSION STATE) ---
if "mis_listas" not in st.session_state:
    st.session_state["mis_listas"] = {
        "Semiconductores": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "TSM", "AVGO", "LRCX", "AMAT"],
        "Robótica": [
            # --- LÍDERES NORTEAMERICANOS ---
            "ISRG", "CGNX", "ADI", "AME", "ROCK", "ROK", "TER", "FTV", "NOW", "PTC", 
            "ANSS", "GWW", "SYM", "PATH", "AZTA", "ESTC", "NXPI", "TXN", "ON", "A",
            # --- GIGANTES EUROPEOS ---
            "SIE.DE", "SU.PA", "ABB", "SCHN.PA", "KRN.DE", "ASML", "ASM.AS",
            # --- SECTOR JAPÓN Y ASIA (ADRs y Directos) ---
            "KEYLY", "NIDYY", "OMRNY", "FANUY", "SNEJF", "TDKYY", "HITHY", "RCRUY", "OTGLY", "FOCLY", "FUJIY"
        ],
        "Fotónica": ["IPGP", "LITE", "COHR", "VNT", "FN", "MKSI", "NKTX", "LIMO"],
        "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR", "CGNX", "ISRG", "COHR"]
    }

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico y Fundamental", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Gestión Autónoma por Momentum Técnico")
    
    compras_fijas = [
        {"Ticker": "ASM.AS", "Precio Compra": 852.00, "Capital Invertido": 2000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "KLAC", "Precio Compra": 1755.30, "Capital Invertido": 2000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "TFX", "Precio Compra": 133.32, "Capital Invertido": 1000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "AME", "Precio Compra": 227.10, "Capital Invertido": 1000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "MPWR", "Precio Compra": 1514.83, "Capital Invertido": 2000.0, "Broker": "ING España"}
    ]
    
    @st.cache_data(ttl=15)
    def cargar_posiciones_con_previsiones(lista):
        tabla_final = []
        for c in lista:
            try:
                t = yf.Ticker(c["Ticker"])
                historial = t.history(period="30d")
                precio_actual = historial['Close'].iloc[-1] if not historial.empty else c["Precio Compra"]
                media_tendencia = historial['Close'].mean()
            except:
                precio_actual = c["Precio Compra"]
                media_tendencia = c["Precio Compra"]
                
            cantidad = round(c["Capital Invertido"] / c["Precio Compra"], 4)
            rendimiento = round(((precio_actual - c["Precio Compra"]) / c["Precio Compra"]) * 100, 2)
            flecha = "🔼 +" if rendimiento >= 0 else "🔽 "
            
            if precio_actual > (media_tendencia * 1.02):
                semaforo_tabla = "🟢 COMPRAR / AÑADIR"
                prev_medio = "📈 Tendencia Alcista Fuerte"
                accion_sugerida = "Dejar correr beneficios. Momentum óptimo."
            elif precio_actual < (media_tendencia * 0.98):
                semaforo_tabla = "🔴 EVITAR / RECORTE"
                prev_medio = "📉 Corrección de Corto"
                accion_sugerida = "No entrar todavía. Esperar soporte de giro."
            else:
                semaforo_tabla = "🟡 MANTENER"
                prev_medio = "↔️ Lateral / Consolidación"
                accion_sugerida = "Mantener posición actual de simulación."

            tabla_final.append({
                "Ticker": c["Ticker"],
                "Cantidad": cantidad,
                "Precio Compra": f"{c['Precio Compra']:.2f}",
                "Precio Actual": f"{precio_actual:.2f}",
                "Rendimiento": f"{flecha}{rendimiento}%",
                "Semáforo Corto Plazo": semaforo_tabla,
                "Previsión Medio Plazo": prev_medio,
                "Consejo del Radar": accion_sugerida,
                "Broker": c["Broker"]
            })
        return pd.DataFrame(tabla_final)

    if st.button("🔄 Refrescar Precios y Previsiones"):
        st.cache_data.clear()
        st.toast("Actualizando mercado...")

    df_bot = cargar_posiciones_con_previsiones(compras_fijas)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Fondo Estrategia", "30.000 €")
    c2.metric("Caja Líquida", "22.000,00 €")
    c3.metric("Posiciones Abiertas", "5")
    
    st.dataframe(df_bot, use_container_width=True)

# =========================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO Y FUNDAMENTAL AVANZADO
# =========================================================
with pestaña2:
    st.subheader("🔍 Matriz de Inteligencia de Mercado (Flujos y Valoración)")
    
    st.write("### 📁 Cargar una Lista de Seguimiento Completa")
    opciones_selector = ["Ninguna"] + list(st.session_state["mis_listas"].keys())
    lista_sel = st.selectbox("Selecciona una lista pregrabada para proyectar:", opciones_selector)
    
    if lista_sel != "Ninguna":
        tickers_lista = st.session_state["mis_listas"][lista_sel]
        
        with st.spinner(f"Calculando métricas avanzadas, dividendos y ratios institucionales para {lista_sel}..."):
            datos_lista = []
            for tick in tickers_lista:
                try:
                    t = yf.Ticker(tick)
                    h = t.history(period="30d")
                    info = t.info
                    
                    if not h.empty:
                        p_actual = h['Close'].iloc[-1]
                        p_media = h['Close'].mean()
                        p_min = h['Low'].min()
                        
                        # 1. Extracción de dividendos (Por seguridad fiscal)
                        div_yield = info.get('dividendYield', 0.0)
                        div_texto = f"{div_yield * 100:.2f}%" if div_yield else "0.00% 🟢"
                        
                        # 2. Previsión Consenso 12 Meses (Evolución estimada de precio)
                        target_precio = info.get('targetMedianPrice', None)
                        if target_precio:
                            potencial = ((target_precio - p_actual) / p_actual) * 100
                            target_texto = f"{target_precio:.2f} ({potencial:+.1f}%)"
                        else:
                            target_precio = p_actual * 1.10  # Estimación genérica si falta dato
                            target_texto = "No disp. (~+10%)"
                        
                        # 3. Cálculo Matemático de Riesgo / Beneficio
                        riesgo_bajada = max(0.5, ((p_actual - p_min) / p_actual) * 100)
                        beneficio_subida = max(0.5, ((target_precio - p_actual) / p_actual) * 100)
                        ratio_rb = beneficio_subida / riesgo_bajada
                        
                        if ratio_rb >= 2.0:
                            rb_texto = f"{ratio_rb:.1f}x 🔥 Excelente"
                        elif ratio_rb >= 1.0:
                            rb_texto = f"{ratio_rb:.1f}x 📊 Favorable"
                        else:
                            rb_texto = f"{ratio_rb:.1f}x ⚠️ Riesgo Alto"
                            
                        # 4. Volatilidad (Beta)
                        beta = info.get('beta', 1.0)
                        beta_texto = f"{beta:.2f}" if beta else "1.00"

                        # 5. Semáforo Combinado de Flujo Técnico
                        if p_actual > (p_media * 1.02):
                            sem_lista = "🟢 COMPRAR"
                        elif p_actual < (p_media * 0.98):
                            sem_lista = "🔴 EVITAR"
                        else:
                            sem_lista = "🟡 MANTENER"
                            
                        datos_lista.append({
                            "Ticker": tick, 
                            "Precio Actual": round(p_actual, 2), 
                            "Semáforo Técnico": sem_lista,
                            "Dividendo Anual": div_texto,
                            "Objetivo 12M (Potencial)": target_texto,
                            "Ratio Riesgo/Beneficio": rb_texto,
                            "Volatilidad (Beta)": beta_texto
                        })
                except:
                    pass
            
            if datos_lista:
                df_mostrar = pd.DataFrame(datos_lista)
                st.dataframe(df_mostrar, use_container_width=True)
                st.caption("💡 *Nota Fiscal:* Los valores marcados con '0.00% 🟢' son óptimos para carteras radicadas en España sin impacto impositivo por reparto.")
            else:
                st.warning("No se han podido descargar datos en este momento.")

    st.write("---")
    st.write("### 🔍 Análisis Detallado Individual")
    accion = st.text_input("Introduce el Ticker de la acción para generar Gráficos y Recomendación:", "TSM")
    
    if accion:
        accion = accion.upper()
        try:
            ticker_obj = yf.Ticker(accion)
            datos_hist = ticker_obj.history(period="30d")
            
            if not datos_hist.empty:
                st.write(f"**📉 Gráfico de Evolución del Precio (Últimos 30 días) - {accion}**")
                st.line_chart(datos_hist['Close'])
                
                precio_hoy = datos_hist['Close'].iloc[-1]
                precio_max = datos_hist['High'].max()
                precio_min = datos_hist['Low'].min()
                media_movil = datos_hist['Close'].mean()
                
                if precio_hoy < (media_movil * 0.98):
                    estado_semaforo = "🔴 EVITAR / ESPERAR GIRO TÉCNICO"
                    tipo_alerta = "rojo"
                    consejo_texto = f"El valor está en fase de corrección por debajo de su tendencia media de {media_movil:.2f}. El precio se acerca al suelo mensual de {precio_min:.2f}. No compres hasta que veamos un giro al alza confirmado."
                elif precio_hoy > (media_movil * 1.02):
                    estado_semaforo = "🟢 COMPRAR (MOMENTUM ALCISTA ACTIVO)"
                    tipo_alerta = "verde"
                    consejo_texto = f"Fuerza relativa alcista impecable. Cotizando sólidamente por encima de su media de {media_movil:.2f}. El capital institucional empuja activamente la cotización; apto para abrir o incrementar posiciones."
                else:
                    estado_semaforo = "🟡 MANTENER (CONSOLIDACIÓN LATERAL)"
                    tipo_alerta = "amarillo"
                    consejo_texto = f"El precio está oscilando plano alrededor de su media de {media_movil:.2f}. Zona neutral. Apto para mantener la posición si estás dentro, pero espera una ruptura para comprar más."

                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"""
                    **📊 Métricas Recientes de {accion}:**
                    * **Precio Actual:** {precio_hoy:.2f}
                    * **Máximo del Mes:** {precio_max:.2f}
                    * **Mínimo del Mes (Soporte):** {precio_min:.2f}
                    """)
                
                with col_b:
                    st.write("**🚦 Semáforo de Operación:**")
                    if tipo_alerta == "verde":
                        st.success(f"### {estado_semaforo}\n\n**Estrategia Recomendada:** {consejo_texto}")
                    elif tipo_alerta == "amarillo":
                        st.warning(f"### {estado_semaforo}\n\n**Estrategia Recomendada:** {consejo_texto}")
                    else:
                        st.error(f"### {estado_semaforo}\n\n**Estrategia Recomendada:** {consejo_texto}")
            else:
                st.error("No se han localizado datos para este Ticker.")
        except:
            st.error("Error al conectar con los servidores de bolsa.")

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN Y CREACIÓN DE LISTAS
# =========================================================
with pestaña3:
    st.subheader("⚙️ Gestión de Listas Pregrabadas")
    col_izquierda, col_derecha = st.columns(2)
    
    with col_izquierda:
        st.write("### 📝 Editar o Consultar Listas Existentes")
        lista_editar = st.selectbox("Selecciona qué lista quieres gestionar o revisar:", list(st.session_state["mis_listas"].keys()))
        
        tickers_actuales = ", ".join(st.session_state["mis_listas"][lista_editar])
        nuevos_tickers = st.text_area("Modificar valores incluidos (separados por comas):", tickers_actuales, key="edit_area")
        
        if st.button("💾 Guardar Cambios en esta Lista"):
            lista_limpia = [t.strip().upper() for t in nuevos_tickers.split(",") if t.strip()]
            st.session_state["mis_listas"][lista_editar] = lista_limpia
            st.success(f"¡Lista '{lista_editar}' actualizada con éxito!")
            st.rerun()

    with col_derecha:
        st.write("### ➕ Crear una Lista de Seguimiento Nueva")
        nombre_nueva_lista = st.text_input("1. Nombre de la nueva lista (ej: Aeroespacial, Ciberseguridad):", "")
        tickers_nuevos_lista = st.text_area("2. Introduce los Tickers separados por comas (ej: PLTR, CRWD, RKLB):", "")
        
        if st.button("🚀 Crear y Dar de Alta Nueva Lista"):
            if nombre_nueva_lista.strip() == "":
                st.error("Por favor, introduce un nombre válido para la lista.")
            elif tickers_nuevos_lista.strip() == "":
                st.error("Por favor, introduce al menos un Ticker.")
            else:
                lista_tickers_procesada = [t.strip().upper() for t in tickers_nuevos_lista.split(",") if t.strip()]
                st.session_state["mis_listas"][nombre_nueva_lista.strip()] = lista_tickers_procesada
                st.success(f"¡Fabuloso! La lista **'{nombre_nueva_lista}'** se ha creado correctamente.")
                st.rerun()
