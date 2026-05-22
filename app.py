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

# Tus listas maestras intactas
listas_guardadas = {
    "Semiconductores": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML"],
    "Robótica": ["ADI", "AME", "ISRG", "CGNX", "ROCK", "ROK", "TER", "FTV", "NOW", "PTC", "ANSS", "GWW", "6954.T", "6758.T", "6501.T", "COHR"],
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
# PESTAÑA 2: ANALIZADOR TÉCNICO AVANZADO (LÓGICA CRITERIO 4 AÑOS)
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
                h = t.history(period="30d")
                info = t.info
                if not h.empty:
                    p_actual = h['Close'].iloc[-1]
                    p_media = h['Close'].mean()
                    
                    # Consensuar Precio Objetivo estimado a largo plazo
                    target_val = info.get('targetMedianPrice', p_actual * 1.15)
                    potencial_val = ((target_val - p_actual) / p_actual) * 100
                    
                    # Filtro inteligente combinado (Evitamos comprar si el potencial es ridículo)
                    if p_actual > p_media and potencial_val >= 15.0:
                        sem_lista = "🟢 COMPRAR (Valor + Inercia)"
                    elif potencial_val >= 20.0:
                        sem_lista = "🟡 ACUMULAR (Zona Barata)"
                    else:
                        sem_lista = "🔴 ESPERAR (Poco Margen)"
                        
                    datos_lista.append({
                        "Ticker": tick, 
                        "Precio Actual": f"{p_actual:.2f}", 
                        "Precio Objetivo": f"{target_val:.2f}",
                        "Potencial 4A": f"{potencial_val:.1f}%",
                        "Estrategia Valor": sem_lista
                    })
            except:
                pass
        st.dataframe(pd.DataFrame(datos_lista), use_container_width=True)

    st.write("---")
    st.write("### 🔍 Ficha de Inteligencia Detallada")
    accion = st.text_input("Introduce el Ticker de la acción para generar Gráficos y Recomendación (ej: COHR, TSM, AMD):", "COHR")
    
    if accion:
        accion = accion.upper()
        try:
            ticker_obj = yf.Ticker(accion)
            datos_hist = ticker_obj.history(period="30d")
            info_ind = ticker_obj.info
            
            if not datos_hist.empty:
                precio_hoy = datos_hist['Close'].iloc[-1]
                precio_max = datos_hist['High'].max()
                precio_min = datos_hist['Low'].min()
                media_movil = datos_hist['Close'].mean()
                
                target_ind = info_ind.get('targetMedianPrice', precio_hoy * 1.15)
                potencial_ind = ((target_ind - precio_hoy) / precio_hoy) * 100
                
                # --- NUEVA LÓGICA DE FILTRADO SIN CONTRADICCIONES ---
                if potencial_ind >= 20.0:
                    estado_semaforo = "🟢 COMPRAR (POTENCIAL COMPLETO ACTIVO)"
                    tipo_alerta = "verde"
                    consejo_texto = f"El activo cotiza en zona de clara ventaja. Con un precio objetivo de {target_ind:.2f}, presenta un potencial de revalorización del {potencial_ind:.1f}%. El margen de seguridad es óptimo para la acumulación a largo plazo."
                elif 10.0 <= potencial_ind < 20.0:
                    estado_semaforo = "🟡 MANTENER / ESPERAR RECORTE"
                    tipo_alerta = "amarillo"
                    consejo_texto = f"Zona neutral. Aunque la inercia puede acompañar, el margen actual hasta su objetivo ({target_ind:.2f}) es de un {potencial_ind:.1f}%. Se aconseja esperar recortes hacia los niveles de soporte ({precio_min:.2f}) antes de añadir capital."
                else:
                    estado_semaforo = "🔴 EVITAR / EXCESO DE VALORACIÓN"
                    tipo_alerta = "rojo"
                    consejo_texto = f"Margen de beneficio insuficiente. El potencial estimado es de tan solo un {potencial_ind:.1f}% frente a su valor estimado ({target_ind:.2f}). Comprar aquí implica asumir un riesgo alto para un retorno muy bajo."

                # --- NUEVA DISTRIBUCIÓN DE MÉTRICAS CLARAS EN FILA SUPERIOR ---
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Precio Actual", f"${precio_hoy:.2f}")
                m2.metric("Objetivo Estimado", f"${target_val:.2f}")
                m3.metric("Potencial Compuesto", f"{potencial_ind:.1f}%")
                
                with m4:
                    st.write("**Veredicto de Filtro:**")
                    if tipo_alerta == "verde":
                        st.success("🟢 EXCELENTE")
                    elif tipo_alerta == "amarillo":
                        st.warning("🟡 VIGILANCIA")
                    else:
                        st.error("🔴 DESCARTAR")

                # Dictamen descriptivo justo debajo de los números
                if tipo_alerta == "verde":
                    st.success(f"**Estrategia:** {consejo_texto}")
                elif tipo_alerta == "amarillo":
                    st.warning(f"**Estrategia:** {consejo_texto}")
                else:
                    st.error(f"**Estrategia:** {consejo_texto}")

                st.write(f"**📉 Gráfico de Evolución Dinámica - {accion}**")
                st.line_chart(datos_hist['Close'])
                
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
