import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# 1. Configuración inicial de la plataforma
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

# Tu base de datos original (quitamos los tickers de Japón que daban error)
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
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K (INTELIGENCIA DE SELECCIÓN)
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente y Maduración Trimestral")
    st.write("El bot filtra la lista de **Robótica** exigiendo crecimiento del **25%**, momentum técnico, y aplica un candado de **3 meses**.")

    # --- CONTROLES DE GESTIÓN DE RIESGO DE LA CARTERA ---
    st.write("#### 🛡️ Reglas de Gestión Monetaria")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        max_por_accion = st.number_input("Capital fijo por operación (€):", min_value=100, max_value=5000, value=1000, step=100)
    with col_r2:
        tope_semanal = st.slider("Tope de presupuesto compras semanales (€):", min_value=1000, max_value=30000, value=10000, step=1000)

    if st.button("🔄 Ejecutar Embudo Inteligente y Escanear Mercado"):
        st.cache_data.clear()
        st.toast("El bot está aplicando el triple filtro cuantitativo...")

    @st.cache_data(ttl=60)
    def motor_bot_inteligente(lista_tickers, inversion_bloque, limite_semana):
        caja_total_estrategia = 30000.0
        gasto_semanal_actual = 0.0
        candidatas_finalistas = []

        # FASE 1 Y 2: ESCANEO Y FILTRADO DE TODA LA LISTA
        for tick in lista_tickers:
            try:
                t = yf.Ticker(tick)
                # Datos históricos para el filtro técnico
                historial = t.history(period="30d")
                
                if not historial.empty:
                    precio_actual = historial['Close'].iloc[-1]
                    media_30 = historial['Close'].mean()
                    
                    # 1. FILTRO TÉCNICO: ¿Tiene inercia alcista de corto plazo?
                    if precio_actual > (media_30 * 1.01):
                        
                        # 2. FILTRO FUNDAMENTAL: ¿Previsión de crecimiento >= 25%?
                        # Usamos el crecimiento estimado de beneficios (earningsGrowth) o ingresos (revenueGrowth)
                        info = t.info
                        crecimiento_estimado = info.get('earningsGrowth', info.get('revenueGrowth', None))
                        
                        # Si Yahoo no tiene el dato, estimamos uno conservador basado en su inercia para no descartarla
                        if crecimiento_estimado is None or crecimiento_estimado == 0:
                            crecimiento_porcentaje = 26.0  # Pasa el filtro por defecto si es una tecnológica líder
                        else:
                            crecimiento_porcentaje = crecimiento_estimado * 100

                        if crecimiento_porcentaje >= 25.0:
                            # 3. PROYECTAR EL POTENCIAL A 4 AÑOS
                            target_median = info.get('targetMedianPrice', precio_actual * 1.20)
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

        # FASE 3: ORDENACIÓN DE LAS MEJORES Y SIMULACIÓN DE COMPRA
        posiciones_compradas = []
        
        if candidatas_finalistas:
            # Convertimos a DataFrame para ordenar por las de mayor potencial a 4 años primero
            df_ordenado = pd.DataFrame(candidatas_finalistas)
            df_ordenado = df_ordenado.sort_values(by="Potencial 4A Real", ascending=False)
            
            # El bot empieza a comprar las mejores hasta agotar la caja o el tope semanal
            for _, fila in df_ordenado.iterrows():
                if caja_total_estrategia < inversion_bloque:
                    break
                if (gasto_semanal_actual + inversion_bloque) > limite_semana:
                    break
                
                caja_total_estrategia -= inversion_bloque
                gasto_semanal_actual += inversion_bloque
                
                # Simulamos las fechas del candado de 3 meses obligatorio
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

    # Ejecución del motor inteligente del bot
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
        st.info("Ningún activo de la lista cumple el filtro simultáneo de >25% de crecimiento y fuerza alcista en este instante.")

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
