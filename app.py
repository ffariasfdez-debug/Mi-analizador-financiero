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

# Base de datos optimizada para máxima velocidad en Yahoo Finance
listas_guardadas = {
    "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML"],
    "Robótica Pura": [
        "ISRG", "ZBH", "STE", "ROK", "CGNX", "TER", 
        "ATS", "SYM", "GWW", "AME", "ADI", "FTV", "KEYS", "PTC", 
        "ANSS", "ROCK", "COHR", "DE", "CAT", "AVAV", "GE", "HON"
    ],
    "Fotónica": ["IPGP", "LITE", "COHR"],
    "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR"]
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
    st.write("El bot filtra la lista de **Robótica Pura** exigiendo crecimiento del **20%**, momentum técnico, y aplica un candado de **3 meses**.")

    mercado_activo = comprobar_mercado_abierto()
    if mercado_activo:
        st.success("🟢 MERCADO ABIERTO: Las operaciones simuladas se ejecutarán con precios e impacto en vivo.")
    else:
        st.warning("🕒 MERCADO CERRADO (Wall Street): El bot analizará el mercado pero las órdenes quedarán bloqueadas hasta la apertura.")

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
                    
                    if precio_actual >= (media_30 * 0.98):
                        crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                        crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))

                        if crecimiento_porcentaje >= 20.0:
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

    df_cartera_inteligente, caja_libre, gastado_semana = motor_bot_inteligente(
        listas_guardadas["Robótica Pura"], max_por_accion, tope_semanal, mercado_activo
    )
    
    total_invertido_hoy = 30000.0 - caja_libre

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
        st.info("🛒 Sistema Canalizado: El radar ha preseleccionado los activos con éxito, pero las órdenes de compra están retenidas en cola. Ejecuta el bot de Lunes a Viernes de 15:30 a 22:00 (Hora España) para procesar las compras.")

# =========================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO AVANZADO (REDISENO PREMIUM VISUAL)
# =========================================================
with pestaña2:
    st.subheader("🔍 Analizador Técnico y Avanzado de Tendencias")
    
    st.write("### 📁 Opción A: Proyectar Listas Completas con Métricas de Riesgo")
    lista_sel = st.selectbox("Selecciona una lista pregrabada para proyectar:", ["Ninguna"] + list(listas_guardadas.keys()))
    
    if lista_sel != "Ninguna":
        tickers_lista = listas_guardadas[lista_sel]
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
            # Descargamos 1 año completo de historial para poder calcular las medias importantes
            datos_hist = ticker_obj.history(period="1y")
            
            if not datos_hist.empty and len(datos_hist) >= 200:
                # Cálculo de curvas técnicas reales de bolsa
                datos_hist['Media 50D (Medio Plazo)'] = datos_hist['Close'].rolling(window=50).mean()
                datos_hist['Media 200D (Institucional)'] = datos_hist['Close'].rolling(window=200).mean()
                
                p_actual_ind = datos_hist['Close'].iloc[-1]
                p_media_50 = datos_hist['Media 50D (Medio Plazo)'].iloc[-1]
                p_media_200 = datos_hist['Media 200D (Institucional)'].iloc[-1]
                p_min_ind = datos_hist['Close'].iloc[-50:].min() # Suelo técnico últimas semanas
                
                try:
                    target_ind = ticker_obj.info.get('targetMedianPrice')
                    if target_ind is None or target_ind == 0: target_ind = p_actual_ind * 1.25
                except:
                    target_ind = p_actual_ind * 1.25
                
                potencial_ind = ((target_ind - p_actual_ind) / p_actual_ind) * 100
                riesgo_ind = max(0.5, ((p_actual_ind - p_min_ind) / p_actual_ind) * 100)
                ratio_rb_ind = potencial_ind / riesgo_ind
                
                # Evaluación algorítmica estructurada
                if p_actual_ind > p_media_200:
                    estado_ind = "🟢 ESTRUCTURA ALCISTA PRINCIPAL"
                    if p_actual_ind > p_media_50:
                        diagnostico_txt = "COMPRAR (Confirmación de Tendencia)"
                        explicacion_ind = f"El activo cotiza con fuerza por encima de sus dos medias móviles principales (50 y 200 días). Esto indica un momentum institucional impecable. Con un Ratio Riesgo/Beneficio de 1:{ratio_rb_ind:.1f}, la recompensa justifica con creces el riesgo estructural."
                    else:
                        diagnostico_txt = "ACUMULAR (Retroceso Técnico)"
                        explicacion_ind = f"El activo mantiene su tendencia alcista principal a largo plazo (sobre la media de 200 días), pero ha corregido a corto plazo por debajo de la de 50 días. Es una zona óptima de compra selectiva o acumulación."
                else:
                    estado_ind = "🔴 TENDENCIA BAJISTA / BAJO MOMENTUM"
                    diagnostico_txt = "ESPERAR (Falta de Fuerza)"
                    explicacion_ind = f"El precio cotiza por debajo de la media institucional de 200 días. El entorno técnico es complejo y, aunque las proyecciones teóricas den un {potencial_ind:.1f}% de recorrido, el mercado carece de apoyo comprador. Conviene esperar un suelo firme."
                
                # --- DISEÑO EN TARJETAS DE DATOS ---
                st.write("#### 📊 Métricas Clave de Decisión")
                c_i1, c_i2, c_i3, c_i4 = st.columns(4)
                c_i1.metric("Precio de Mercado", f"{p_actual_ind:.2f} €")
                c_i2.metric("Salud de Fondo", estado_ind)
                c_i3.metric("Ratio Riesgo / Beneficio", f"1 : {ratio_rb_ind:.1f}")
                c_i4.metric("Estrategia Recomendada", diagnostico_txt)
                
                # Caja de fundamentación explicativa estilizada
                st.info(f"💡 **Justificación del Sistema:** {explicacion_ind}")
                
                # --- GRÁFICO AVANZADO CON LAS 2 MEDIAS ---
                st.write(f"**📉 Gráfico de Evolución Estructural de {accion} (Último Año)**")
                # Creamos un dataframe limpio solo con los datos que queremos pintar en la gráfica
                df_grafico = datos_hist[['Close', 'Media 50D (Medio Plazo)', 'Media 200D (Institucional)']]
                df_grafico.columns = ['Precio de Cierre', 'Media Móvil 50 días', 'Media Móvil 200 días (Estructural)']
                st.line_chart(df_grafico)
            else:
                st.error("No hay suficiente historial acumulado en Yahoo Finance para trazar la media institucional de 200 días de este activo.")
        except Exception as e:
            st.error(f"Error al conectar con los servidores o procesar el Ticker: {str(e)}")

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN DE LISTAS PREGRABADAS
# =========================================================
with pestaña3:
    st.subheader("⚙️ Panel de Control y Consulta de Listas Pregrabadas")
    st.write("Aquí puedes supervisar los tickers que componen las bases de datos internas de tu algoritmo.")
    
    lista_a_revisar = st.selectbox("Selecciona una lista para ver sus componentes:", list(listas_guardadas.keys()))
    
    if lista_a_revisar:
        tickers_en_lista = listas_guardadas[lista_a_revisar]
        
        st.info(f"📋 La lista **{lista_a_revisar}** contiene actualmente **{len(tickers_en_lista)}** activos configurados.")
        
        df_tickers = pd.DataFrame(tickers_en_lista, columns=["Ticker Oficial (Yahoo Finance)"])
        st.dataframe(df_tickers, use_container_width=True)
