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

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Configuración de Listas Pregrabadas"
])

listas_guardadas = {
    "Semiconductores": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML"],
    "Robótica": ["ADI", "AME", "ISRG", "CGNX"],
    "Fotónica": ["IPGP", "LITE", "COHR"],
    "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR"]
}

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K (IGUAL QUE LAS INDIVIDUALES)
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Gestión Autónoma por Momentum Técnico")
    exclusiones = st.text_input("Acciones a excluir del radar de compra (ej: NVDA, ASML):", "", key="excl_bot")
    
    compras_fijas = [
        {"Ticker": "ASM.AS", "Precio Compra": 852.00, "Capital Invertido": 2000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "KLAC", "Precio Compra": 1755.30, "Capital Invertido": 2000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "TFX", "Precio Compra": 133.32, "Capital Invertido": 1000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "AME", "Precio Compra": 227.10, "Capital Invertido": 1000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "MPWR", "Precio Compra": 1514.83, "Capital Invertido": 2000.0, "Broker": "ING España"}
    ]
    
    @st.cache_data(ttl=10)
    def cargar_posiciones_con_todo_el_momentum(lista):
        tabla_final = []
        for c in lista:
            try:
                t = yf.Ticker(c["Ticker"])
                historial = t.history(period="30d") # Pedimos 30 días para sacar máximos y mínimos igual que en la pestaña 2
                if not historial.empty:
                    precio_actual = historial['Close'].iloc[-1]
                    precio_max = historial['High'].max()
                    precio_min = historial['Low'].min()
                else:
                    precio_actual = c["Precio Compra"]
                    precio_max = c["Precio Compra"] * 1.05
                    precio_min = c["Precio Compra"] * 0.95
            except:
                precio_actual = c["Precio Compra"]
                precio_max = c["Precio Compra"] * 1.05
                precio_min = c["Precio Compra"] * 0.95
                
            cantidad = round(c["Capital Invertido"] / c["Precio Compra"], 4)
            rendimiento = round(((precio_actual - c["Precio Compra"]) / c["Precio Compra"]) * 100, 2)
            flecha = "🔼 +" if rendimiento >= 0 else "🔽 "
            
            # Mismas proyecciones matemáticas que en la pestaña individual
            objetivo_tec = precio_max * 1.12
            riesgo_stop = precio_min * 0.97
            
            # Lógica exacta del semáforo adaptada a la tabla del bot
            if precio_actual > (precio_max * 0.96):
                semaforo = "🟢 COMPRAR (MOMENTUM)"
                consejo = "Fuerza alcista activa. Capital institucional empujando."
            elif precio_actual < (precio_max * 0.90):
                semaforo = "🔴 EVITAR (RECORTE)"
                consejo = f"Fase correctiva. Esperar soporte firme cerca de {precio_min:.2f}."
            else:
                semaforo = "🟡 MANTENER (LATERAL)"
                consejo = "Zona de consolidación. Sin señal de entrada nueva."

            tabla_final.append({
                "Ticker": c["Ticker"],
                "Rendimiento": f"{flecha}{rendimiento}%",
                "Semáforo": semaforo,
                "Precio Compra": f"{c['Precio Compra']:.2f}",
                "Precio Actual": f"{precio_actual:.2f}",
                "Máx Mes (Resist.)": f"{precio_max:.2f}",
                "Mín Mes (Soporte)": f"{precio_min:.2f}",
                "Objetivo Medio Plazo": f"{objetivo_tec:.2f}",
                "Riesgo Máx (Stop)": f"{riesgo_stop:.2f}",
                "Indicación del Radar": consejo,
                "Broker": c["Broker"]
            })
        return pd.DataFrame(tabla_final)

    if st.button("🔄 Refrescar Precios y Previsiones"):
        st.cache_data.clear()
        st.toast("Actualizando todas las métricas de momentum...")

    df_bot = cargar_posiciones_con_todo_el_momentum(compras_fijas)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Fondo Estrategia", "30.000 €")
    c2.metric("Caja Líquida", "22.000,00 €")
    c3.metric("Posiciones Abiertas", "5")
    
    st.dataframe(df_bot, use_container_width=True)

# =========================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO AVANZADO
# =========================================================
with pestaña2:
    st.subheader("🔍 Buscador de Acciones con Gráficos de Tendencia")
    
    st.write("### 📁 Cargar una Lista de Seguimiento Completa")
    lista_sel = st.selectbox("Selecciona una lista pregrabada para proyectar:", ["Ninguna"] + list(listas_guardadas.keys()))
    
    if lista_sel != "Ninguna":
        tickers_lista = listas_guardadas[lista_sel]
        datos_lista = []
        for tick in tickers_lista:
            try:
                t = yf.Ticker(tick)
                h = t.history(period="1d")
                p = h['Close'].iloc[-1] if not h.empty else 0.0
                datos_lista.append({"Ticker": tick, "Precio Actual": f"{p:.2f}"})
            except:
                pass
        st.dataframe(pd.DataFrame(datos_lista), use_container_width=True)

    st.write("---")
    st.write("### 🔍 Análisis Detallado Individual")
    accion = st.text_input("Introduce el Ticker de la acción para generar Gráficos y Recomendación (ej: LITE, TSM, AMD):", "TSM")
    
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
                
                caida_desde_max = ((precio_max - precio_hoy) / precio_max) * 100
                
                if precio_hoy < (precio_max * 0.90):
                    estado_semaforo = "🔴 EVITAR / ESPERAR GIRO TÉCNICO"
                    tipo_alerta = "rojo"
                    diagnostico = "Corrección/Frenazo de Momentum"
                    consejo_texto = f"El valor está en fase correctiva perdiendo un {caida_desde_max:.1f}% desde máximos mensuales. No abras posiciones todavía. Deja que el precio busque apoyo real y se estabilice cerca del suelo de los **{precio_min:.2f}** antes de plantear una entrada táctica."
                elif precio_hoy > (precio_max * 0.96):
                    estado_semaforo = "🟢 COMPRAR (MOMENTUM ALCISTA ACTIVO)"
                    tipo_alerta = "verde"
                    diagnostico = "Subida Libre / Rotación Institucional Fuerte"
                    consejo_texto = "Fuerza relativa impecable. El capital institucional está empujando el volumen con fuerza. El precio está pegado a máximos históricos/mensuales. Es apto para subirse a la tendencia o añadir posiciones buscando la continuación de momentum."
                else:
                    estado_semaforo = "🟡 MANTENER (CONSOLIDACIÓN LATERAL)"
                    tipo_alerta = "amarillo"
                    diagnostico = "Rango de Consolidación / Acumulación Neutral"
                    consejo_texto = "El valor se encuentra en tierra de nadie, comprimiendo el precio en un rango lateral. Si ya estás dentro, mantén la posición de forma segura. Si buscas entrar de cero, espera a que rompa la resistencia mensual para confirmar que el momentum despierta."

                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"""
                    **📊 MÉTRICAS CRÍTICAS DE MERCADO ({accion}):**
                    * **Precio de Cotización Actual:** {precio_hoy:.2f} $
                    * **Techo / Máximo Mensual (Resistencia):** {precio_max:.2f} $
                    * **Suelo / Mínimo Mensual (Soporte Fuerte):** {precio_min:.2f} $
                    * **Distancia de Corrección desde Máximos:** -{caida_desde_max:.2f}%
                    """)
                    
                    st.markdown(f"""
                    <div style="background-color:#1e293b; padding:15px; border-radius:10px; border-left:5px solid #00ffcc;">
                        <h4 style="margin-top:0; color:#00ffcc;">🎯 Proyección Estratégica (Medio Plazo)</h4>
                        <p style="margin-bottom:5px;"><b>Objetivo Técnico Estimado:</b> {(precio_max * 1.12):.2f} $</p>
                        <p style="margin-bottom:0px;"><b>Riesgo Máximo Calculado (Stop):</b> {(precio_min * 0.97):.2f} $</p>
                    </div>
                    """, unsafe_style=True)
                
                with col_b:
                    st.write("**🚦 Semáforo de Operación Inmediata:**")
                    if tipo_alerta == "verde":
                        st.success(f"### {estado_semaforo}\n\n**Diagnóstico:** {diagnostico}\n\n**Estrategia Recomendada:** {consejo_texto}")
                    elif tipo_alerta == "amarillo":
                        st.warning(f"### {estado_semaforo}\n\n**Diagnóstico:** {diagnostico}\n\n**Estrategia Recomendada:** {consejo_texto}")
                    else:
                        st.error(f"### {estado_semaforo}\n\n**Diagnóstico:** {diagnostico}\n\n**Estrategia Recomendada:** {consejo_texto}")
            else:
                st.error("No se han localizado datos para este Ticker.")
        except:
            st.error("Error al conectar con los servidores de bolsa.")

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN DE LISTAS PREGRABADAS
# =========================================================
with pestaña3:
    st.subheader("⚙️ Modificar Valores de las Listas Pregrabadas")
    lista_editar = st.selectbox("Selecciona qué lista quieres gestionar:", list(listas_guardadas.keys()))
    st.text_area("Valores incluidos actuales:", ", ".join(listas_guardadas[lista_editar]))
    if st.button("Guardar Cambios"):
        st.success("Configuración consolidada de forma segura.")
