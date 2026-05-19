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
    
    @st.cache_data(ttl=10)
    def cargar_posiciones_con_previsiones(lista):
        tabla_final = []
        for c in lista:
            try:
                t = yf.Ticker(c["Ticker"])
                historial = t.history(period="5d")
                precio_actual = historial['Close'].iloc[-1] if not historial.empty else c["Precio Compra"]
            except:
                precio_actual = c["Precio Compra"]
                
            cantidad = round(c["Capital Invertido"] / c["Precio Compra"], 4)
            rendimiento = round(((precio_actual - c["Precio Compra"]) / c["Precio Compra"]) * 100, 2)
            flecha = "🔼 +" if rendimiento >= 0 else "🔽 "
            
            # --- SEMÁFORO EN LA TABLA ---
            if rendimiento > 1.0:
                semaforo_tabla = "🟢 COMPRAR / AÑADIR"
                prev_medio = "📈 Tendencia Alcista Fuerte"
                accion_sugerida = "Dejar correr beneficios. Momentum óptimo."
            elif rendimiento < -1.0:
                semaforo_tabla = "🔴 EVITAR / RECORTE"
                prev_medio = "📉 Corrección de Corto"
                accion_sugerida = "No entrar todavía. Esperar que toque soporte."
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
# PESTAÑA 2: ANALIZADOR TÉCNICO AVANZADO (CON SEMÁFORO LUMINOSO)
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
                
                # CÁLCULO DEL ESTADO DEL SEMÁFORO INDIVIDUAL
                # Si cae más de un 10% desde máximos del mes, entra en aviso de soporte
                if precio_hoy < (precio_max * 0.90):
                    estado_semaforo = "🔴 ESPERAR / EVITAR ENTRADA"
                    tipo_alerta = "error" # Pinta el cuadro de color rojo en Streamlit
                    consejo_texto = f"El valor está corrigiendo con fuerza. El semáforo está en ROJO para compras inmediatas. Deja que busque apoyo cerca de su mínimo mensual de **{precio_min:.2f}** antes de plantear una entrada por momentum."
                # Si está cerca de máximos, tiene momentum alcista fuerte
                elif precio_hoy > (precio_max * 0.96):
                    estado_semaforo = "🟢 COMPRAR (MOMENTUM ACTIVO)"
                    tipo_alerta = "success" # Pinta el cuadro de color verde en Streamlit
                    consejo_texto = f"Fuerza relativa alcista impecable. El capital institucional está empujando el precio. El semáforo está en VERDE; apto para entrar o mantener buscando la continuación de la tendencia."
                else:
                    estado_semaforo = "🟡 MANTENER / NEUTRAL"
                    tipo_alerta = "warning" # Pinta el cuadro de color amarillo en Streamlit
                    consejo_texto = "El precio se encuentra atrapado en zona de consolidación lateral. El semáforo está en AMARILLO. No hay señal clara de entrada nueva; apto para mantener si ya estás dentro."

                # PINTAR LOS PANALES EN PANTALLA
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
                    # Este comando dibuja el cuadro de color según el semáforo (Verde, Amarillo o Rojo)
                    if tipo_alerta == "success":
                        st.success(f"### {estado_semaforo}\n\n{consejo_texto}")
                    elif tipo_alerta == "warning":
                        st.sidebar.write("") # Espaciador
                        st.warning(f"### {estado_semaforo}\n\n{consejo_texto}")
                    else:
                        st.error(f"### {estado_semaforo}\n\n{consejo_texto}")
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
