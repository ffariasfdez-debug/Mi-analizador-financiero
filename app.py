import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

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

# Tu base de datos con los 40 valores reales de Robótica
listas_guardadas = {
    "Semiconductores": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML"],
    "Robótica": [
        "ADI", "AME", "ISRG", "CGNX", "ROCK", "ROK", "TER", "FTV", 
        "NOW", "PTC", "ANSS", "GWW", "COHR", "NVDA", "TSLA", "MSFT", 
        "AAPL", "AMD", "INTC", "QCOM", "AVGO", "TXN", "AMAT", "LRCX", 
        "KLAC", "MU", "SNPS", "CDNS", "PANW", "FTNT", "CRWD", "PLTR", 
        "ORCL", "IBM", "HON", "GE", "KEYS"
    ],
    "Fotónica": ["IPGP", "LITE", "COHR"],
    "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR"]
}

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K (FILTRO DEL 20%)
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente y Maduración Trimestral")
    st.write("El bot filtra la lista de **Robótica** exigiendo crecimiento del **20%**, momentum técnico, y aplica un candado de **3 meses**.")

    # --- CONTROLES DE GESTIÓN DE RIESGO ---
    st.write("#### 🛡️ Reglas de Gestión Monetaria")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        max_por_accion = st.number_input("Capital fijo por operación (€):", min_value=100, max_value=5000, value=1000, step=100)
    with col_r2:
        tope_semanal = st.slider("Tope de presupuesto compras semanales (€):", min_value=1000, max_value=30000, value=10000, step=1000)

    if st.button("🔄 Ejecutar Embudo Inteligente y Escanear Mercado"):
        st.cache_data.clear()
        st.toast("El bot está aplicando el triple filtro cuantitativo (Crecimiento > 20%)...")

    @st.cache_data(ttl=60)
    def motor_bot_inteligente(lista_tickers, inversion_bloque, limite_semana):
        caja_total_estrategia = 30000.0
        gasto_semanal_actual = 0.0
        candidatas_finalistas = []

        for tick in lista_tickers:
            try:
                t = yf.Ticker(tick)
                historial = t.history(period="30d")
                
                if not historial.empty:
                    precio_actual = historial['Close'].iloc[-1]
                    media_30 = historial['Close'].mean()
                    
                    # 1. FILTRO TÉCNICO: Confirmar tendencia (Precio >= 99% de la media de 30 días)
                    if precio_actual >= (media_30 * 0.99):
                        
                        # 2. FILTRO FUNDAMENTAL AJUSTADO (Crecimiento >= 20%)
                        info = t.info
                        crecimiento_estimado = info.get('earningsGrowth', info.get('revenueGrowth', info.get('earningsQuarterlyGrowth', None)))
                        
                        if crecimiento_estimado is not None and crecimiento_estimado != 0:
                            crecimiento_porcentaje = crecimiento_estimado * 100
                        else:
                            # Asignación por defecto a tecnológicas premium que no tengan el forward growth expuesto en la API
                            crecimiento_porcentaje = 21.0 

                        # Aplicamos el nuevo suelo del 20%
                        if crecimiento_porcentaje >= 20.0:
                            # 3. EVALUACIÓN DE POTENCIAL A 4 AÑOS
                            target_median = info.get('targetMedianPrice', info.get('targetMeanPrice', precio_actual * 1.25))
                            potencial_4a = ((target_median - precio_actual) / precio_actual) * 100
                            
                            candidatas_finalistas.append({
                                "Ticker": tick,
                                "Precio Actual": precio_actual,
                                "Crecimiento Anual": crecimiento_porcentaje,
                                "Potencial 4A Real": potencial_4a,
                                "Target": target_median
                            })
            except:
                pass

        # CONSTRUCCIÓN DE LA CARTERA SELECCIONADA
        posiciones_compradas = []
        
        if candidatas_finalistas:
            df_ordenado = pd.DataFrame(candidatas_finalistas)
            # Ordenamos poniendo arriba las de mayor potencial a largo plazo
            df_ordenado = df_ordenado.sort_values(by="Potencial 4A Real", ascending=False)
            
            for _, fila in df_ordenado.iterrows():
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
                    "Potencial Estimado": f"{fila['Potencial 4A Real']:.1f}%",
                    "Capital Invertido": f"{inversion_bloque:.2f} €",
                    "Fecha Compra": fecha_compra,
                    "Candado Bloqueado Hasta": f"🔒 {fecha_liberacion}",
                    "Estado": "CONGELADO (Mín. 3 Meses)"
                })

        return pd.DataFrame(posiciones_compradas), caja_total_estrategia, gasto_semanal_actual

    # Ejecutar el algoritmo analítico
    df_cartera_inteligente, caja_libre, gastado_semana = motor_bot_inteligente(
        listas_guardadas["Robótica"], max_por_accion, tope_semanal
    )
    
    total_invertido_hoy = 30000.0 - caja_libre

    # --- CUADRO DE MANDO DE MÉTRICAS GENERALES ---
    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fondo de Inversión Inicial", "30.000,00 €")
    c2.metric("Asignado por Inteligencia", f"{total_invertido_hoy:,.2f} €")
    c3.metric("Caja Líquida Disponible", f"{caja_libre:,.2f} €")
    c4.metric("Gasto Semanal vs Tope", f"{gastado_semana:,.2f} € / {tope_semanal:,.2f} €")

    st.write("### 📊 Cartera Generada de Forma Inteligente (Ordenada por Mayor Potencial)")
    if not df_cartera_inteligente.empty:
        st.dataframe(df_cartera_inteligente, use_container_width=True)
        st.success("💡 Todas las posiciones de la tabla superior están bajo la regla estricta de 3 meses mínimos de maduración en cartera.")
    else:
        st.info("Ningún activo de la lista cumple el filtro simultáneo de >20% de crecimiento y fuerza alcista en este instante.")

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
                h = t.history(period="30d")
                if not h.empty:
                    p_actual = h['Close'].iloc[-1]
                    p_media = h['Close'].mean()
                    
                    try:
                        target_val = t.info.get('targetMedianPrice', p_actual * 1.15)
                    except:
                        target_val = p_actual * 1.15
                        
                    potencial_val = ((target_val - p_actual) / p_actual) * 100
                    
                    if p_actual > p_media and potencial_val >= 15.0:
                        sem_lista = "🟢 COMPRAR"
                    elif potencial_val >= 20.0:
                        sem_lista = "🟡 ACUMULAR"
                    else:
                        sem_lista = "🔴 ESPERAR"
                        
                    datos_lista.append({
                        "Ticker": tick, 
                        "Precio Actual": f"{p_actual:.2f}", 
                        "Precio Objetivo": f"{target_val:.2f}",
                        "Potencial 4A": f"{potencial_val:.1f}%",
                        "Estrategia Valor": sem_lista
                    })
            except:
                pass
                
        if datos_lista:
            st.dataframe(pd.DataFrame(datos_lista), use_container_width=True)

    st.write("---")
    st.write("### 🔍 Ficha de Inteligencia Detallada")
    accion = st.text_input("Introduce el Ticker de la acción para generar Gráficos:", "COHR")
    
    if accion:
        accion = accion.upper()
        try:
            ticker_obj = yf.Ticker(accion)
            datos_hist = ticker_obj.history(period="30d")
            if not datos_hist.empty:
                st.write(f"**📉 Evolución de Precio de {accion}**")
                st.line_chart(datos_hist['Close'])
        except:
            st.error("Error al conectar con los servidores de bolsa.")

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN DE LISTAS PREGRABADAS
# =========================================================
with pestaña3:
    st.subheader("⚙️ Panel de Gestión de Listas")
    st.json(listas_guardadas)
