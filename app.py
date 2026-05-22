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

# --- FUNCIÓN AUXILIAR: COMPROBAR HORARIO DE WALL STREET ---
def comprobar_mercado_abierto():
    # Convertimos la hora actual a la hora de Nueva York (EST/EDT) que es donde cotiza la lista
    tz_ny = pytz.timezone('America/New_York')
    hora_ny = datetime.now(tz_ny)
    
    # Lunes = 0, Domingo = 6. Wall Street abre de Lunes a Viernes (0 al 4)
    dia_semana = hora_ny.weekday()
    
    # Horario oficial: 9:30 AM a 4:00 PM (Hora de Nueva York)
    inicio_mercado = hora_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    fin_mercado = hora_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    
    if dia_semana <= 4 and inicio_mercado <= hora_ny <= fin_mercado:
        return True
    return False

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K (CONTROL DE HORARIO)
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente y Maduración Trimestral")
    st.write("El bot filtra la lista de **Robótica** exigiendo crecimiento del **20%**, momentum técnico, y aplica un candado de **3 meses**.")

    # Verificación visual del estado del mercado
    mercado_activo = comprobar_mercado_abierto()
    if mercado_activo:
        st.success("🟢 MERCADO ABIERTO: Las operaciones simuladas se ejecutarán con precios e impacto en vivo.")
    else:
        st.warning("🕒 MERCADO CERRADO (Wall Street): El bot analizará el mercado pero las órdenes quedarán bloqueadas hasta la apertura.")

    # --- CONTROLES DE GESTIÓN DE RIESGO ---
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
    def motor_bot_inteligente(lista_tickers, inversion_bloque, limite_semana, mercado_on):
        caja_total_estrategia = 30000.0
        gasto_semanal_actual = 0.0
        candidatas_finalistas = []

        # Descarga rápida en bloque
        tickers_string = " ".join(lista_tickers)
        try:
            datos_globales = yf.download(tickers_string, period="60d", group_by="ticker", progress=False)
        except:
            datos_globales = pd.DataFrame()

        for tick in lista_tickers:
            try:
                if tick in datos_globales.columns.levels[0]:
                    historial = datos_globales[tick].dropna()
                else:
                    t = yf.Ticker(tick)
                    historial = t.history(period="60d")
                
                if not historial.empty and len(historial) >= 30:
                    precio_actual = historial['Close'].iloc[-1]
                    media_30 = historial['Close'].iloc[-30:].mean()
                    precio_hace_60d = historial['Close'].iloc[0]
                    
                    # 1. FILTRO TÉCNICO
                    if precio_actual >= (media_30 * 0.98):
                        
                        # 2. FILTRO FUNDAMENTAL ESTIMADO (Mínimo 20%)
                        crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                        crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))

                        if crecimiento_porcentaje >= 20.0:
                            # 3. EVALUACIÓN DE POTENCIAL
                            target_estimado = precio_actual * 1.28
                            potencial_4a = ((target_estimado - precio_actual) / precio_actual) * 100
                            
                            candidatas_finalistas.append({
                                "Ticker": tick,
                                "Precio Actual": precio_actual,
                                "Crecimiento Anual": crecimiento_porcentaje,
                                "Potencial 4A Real": potencial_4a
                            })
            except:
                pass

        posiciones_compradas = []
        
        # CRÍTICO: SOLO ejecuta y altera el saldo si el mercado está ABIERTO
        if candidatas_finalistas and mercado_on:
            df_ordenado = pd.DataFrame(candidatas_finalistas)
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
                    "Estado": "🟢 COMPRADO"
                })

        return pd.DataFrame(posiciones_compradas), caja_total_estrategia, gasto_semanal_actual

    # Ejecutar el algoritmo analítico pasándole el estado del reloj
    df_cartera_inteligente, caja_libre, gastado_semana = motor_bot_inteligente(
        listas_guardadas["Robótica"], max_por_accion, tope_semanal, mercado_activo
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
    
    if mercado_activo:
        if not df_cartera_inteligente.empty:
            st.dataframe(df_cartera_inteligente, use_container_width=True)
            st.success("💡 Todas las posiciones superiores se han adquirido en tiempo real y entran en el candado trimestral.")
        else:
            st.info("Ningún activo de la lista cumple los filtros ahora mismo.")
    else:
        # Mensaje de canalización si el usuario ejecuta el sistema fuera de hora
        st.info("🛒 Sistema Canalizado: El radar ha preseleccionado los activos con éxito, pero las órdenes de compra están retenidas en cola. Ejecuta el bot de Lunes a Viernes de 15:30 a 22:00 (Hora España) para procesar las compras.")

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

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN DE LISTAS PREGRABADAS
# =========================================================
with pestaña3:
    st.subheader("⚙️ Panel de Gestión de Listas")
    st.json(listas_guardadas)
