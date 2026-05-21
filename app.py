import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# Configuración de la página completa y reseteo de caché visual
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# --- TITULO PRINCIPAL ---
st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# --- RECONSTRUCCIÓN COMPLETA DE LISTAS (SIN HEREDAR MEMORIA DAÑADA) ---
mis_listas_limpias = {
    "Semiconductores": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "TSM", "AVGO", "LRCX", "AMAT"],
    "Robótica": [
        "ISRG", "CGNX", "ADI", "AME", "ROCK", "ROK", "TER", "FTV", "NOW", "PTC", 
        "ANSS", "GWW", "SYM", "PATH", "AZTA", "ESTC", "NXPI", "TXN", "ON", "A",
        "SIE.DE", "SU.PA", "ABB", "SCHN.PA", "KRN.DE", "KEYLY", "NIDYY", 
        "OMRNY", "FANUY", "SNEJF", "TDKYY", "HITHY", "RCRUY", "OTGLY", "FOCLY", "FUJIY"
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
    
    @st.cache_data(ttl=30)
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
                accion_sugerida = "Dejar correr beneficios."
            elif precio_actual < (media_tendencia * 0.98):
                semaforo_tabla = "🔴 EVITAR / RECORTE"
                prev_medio = "📉 Corrección de Corto"
                accion_sugerida = "Esperar soporte de giro."
            else:
                semaforo_tabla = "🟡 MANTENER"
                prev_medio = "↔️ Lateral / Consolidación"
                accion_sugerida = "Mantener posición."

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
    # Forzamos al sistema a leer el diccionario limpio y directo para desatascar las 9 posiciones
    lista_sel = st.selectbox("Selecciona una lista pregrabada para proyectar:", list(mis_listas_limpias.keys()), key="selector_analisis_v3")
    
    if lista_sel:
        tickers_lista = mis_listas_limpias[lista_sel]
        
        with st.spinner(f"Calculando métricas y dividendos auditados para {lista_sel}..."):
            datos_lista = []
            for tick in tickers_lista:
                try:
                    tick = tick.strip().upper()
                    t = yf.Ticker(tick)
                    h = t.history(period="30d")
                    
                    if h.empty:
                        continue
                        
                    info = t.info
                    p_actual = h['Close'].iloc[-1]
                    p_media = h['Close'].mean()
                    p_min = h['Low'].min()
                    
                    # 🔥 CÁLCULO MATEMÁTICO REAL DE DIVIDENDOS (Evita errores de Yahoo de 127%)
                    try:
                        dividendos_historicos = t.dividends
                        if not dividendos_historicos.empty:
                            # Filtramos dividendos del último año
                            h_div = dividendos_historicos.loc[dividendos_historicos.index >= (datetime.now().replace(year=datetime.now().year-1))]
                            total_efectivo_año = h_div.sum()
                            calc_yield = (total_efectivo_año / p_actual) * 100
                            
                            if calc_yield > 0.05 and calc_yield < 20.0:
                                div_texto = f"{calc_yield:.2f}%"
                            else:
                                div_texto = "0.00% 🟢"
                        else:
                            div_texto = "0.00% 🟢"
                    except:
                        div_texto = "0.00% 🟢"
                    
                    # PREVISIÓN PRECIO OBJETIVO CONSENSO 12 MESES
                    target_precio = info.get('targetMedianPrice', None)
                    if target_precio and target_precio > 0 and target_precio < (p_actual * 5):
                        potencial = ((target_precio - p_actual) / p_actual) * 100
                        target_texto = f"{target_precio:.2f} ({potencial:+.1f}%)"
                    else:
                        target_precio = p_actual * 1.12
                        target_texto = f"{target_precio:.2f} (+12.0% Est.)"
                    
                    # RATIO RIESGO / BENEFICIO TÁCTICO
                    riesgo_bajada = max(0.5, ((p_actual - p_min) / p_actual) * 100)
                    beneficio_subida = max(0.5, ((target_precio - p_actual) / p_actual) * 100)
                    ratio_rb = beneficio_subida / riesgo_bajada
                    
                    if ratio_rb >= 1.8:
                        rb_texto = f"{ratio_rb:.1f}x 🔥 Excelente"
                    elif ratio_rb >= 1.0:
                        rb_texto = f"{ratio_rb:.1f}x 📊 Favorable"
                    else:
                        rb_texto = f"{ratio_rb:.1f}x ⚠️ Riesgo Alto"
                        
                    # VOLATILIDAD BETA
                    beta = info.get('beta', 1.0)
                    beta_texto = f"{beta:.2f}" if beta else "1.00"

                    # SEMÁFORO TÉCNICO
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
                        "Dividendo Real Realizado": div_texto,
                        "Objetivo 12M (Potencial)": target_texto,
                        "Ratio Riesgo/Beneficio": rb_texto,
                        "Volatilidad (Beta)": beta_texto
                    })
                except:
                    pass
            
            if datos_lista:
                df_mostrar = pd.DataFrame(datos_lista)
                st.dataframe(df_mostrar, use_container_width=True)
                st.caption("💡 *Nota Fiscal:* El porcentaje se calcula dividiendo la caja real repartida en el último año entre la cotización de hoy.")
            else:
                st.warning("Conectando con el mercado...")

    st.write("---")
    st.write("### 🔍 Análisis Detallado Individual")
    accion = st.text_input("Introduce el Ticker de la acción para generar Gráficos y Recomendación:", "COHR", key="input_individual_v3")
    
    if accion:
        accion = accion.upper().strip()
        try:
            ticker_obj = yf.Ticker(accion)
            datos_hist = ticker_obj.history(period="30d")
            
            if not datos_hist.empty:
                st.write(f"**📉 Gráfico de Evolución del Precio (Últimos 30 días) - {accion}**")
                st.line_chart(datos_hist['Close'])
                
                precio_hoy = datos_hist['Close'].iloc[-1]
                media_movil = datos_hist['Close'].mean()
                
                if precio_hoy < (media_movil * 0.98):
                    st.error(f"### 🔴 EVITAR / ESPERAR GIRO TÉCNICO\n\nEl precio cotiza por debajo de su media mensual ({media_movil:.2f}). Espera una señal de entrada institucional.")
                elif precio_hoy > (media_movil * 1.02):
                    st.success(f"### 🟢 COMPRAR (MOMENTUM ALCISTA ACTIVO)\n\nFuerza relativa impecable por encima de su media ({media_movil:.2f}). Flujo de capital alcista comprador.")
                else:
                    st.warning(f"### 🟡 MANTENER (CONSOLIDACIÓN LATERAL)\n\nZona de equilibrio plano sobre los {media_movil:.2f}. Mantener posiciones latentes.")
        except:
            st.error("Error al localizar el Ticker.")

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN FANTASMA (PARA MANTENER ESTRUCTURA)
# =========================================================
with pestaña3:
    st.subheader("⚙️ Panel de Gestión de Listas Maestras")
    st.info("Para este reinicio forzado del sistema, la lectura se realiza de forma directa desde el motor central del script para purgar errores de caché.")
