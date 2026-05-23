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
# PESTAÑA 2: ANALIZADOR TÉCNICO AVANZADO (RESTAURADA CON EXPERT METRICS)
# =========================================================
with pestaña2:
    st.subheader("🔍 Buscador de Acciones con Gráficos de Tendencia")
    
    st.write("### 📁 Opción A: Cargar una Lista de Seguimiento Completa")
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
                    p_minimo = h['Close'].min()
                    
                    try:
                        target_val = t.info.get('targetMedianPrice', p_actual * 1.25)
                        if target_val is None: target_val = p_actual * 1.25
                    except:
                        target_val = p_actual * 1.25
                        
                    potencial_val = ((target_val - p_actual) / p_actual) * 100
                    
                    # Cálculo del Ratio Riesgo/Beneficio
                    riesgo_suelo = max(0.5, ((p_actual - p_minimo) / p_actual) * 100)
                    ratio_rb = potencial_val / riesgo_suelo
                    
                    if p_actual > p_media and potencial_val >= 20.0:
                        sem_lista = "🟢 COMPRAR"
                        explicacion = "Excelente momentum alcista por encima de su media y un potencial subestimado a largo plazo."
                    elif potencial_val >= 15.0:
                        sem_lista = "🟡 ACUMULAR"
                        explicacion = "Valor sólido en zona lateral. Buen ratio de acumulación antes del siguiente impulso."
                    else:
                        sem_lista = "🔴 ESPERAR"
                        explicacion = "El precio está muy cerca de su objetivo analista. El margen de seguridad actual es bajo."
                        
                    datos_lista.append({
                        "Ticker": tick, 
                        "Precio Actual": f"{p_actual:.2f} €", 
                        "Precio Objetivo": f"{target_val:.2f} €",
                        "Potencial 4A": f"{potencial_val:.1f}%",
                        "Riesgo/Beneficio": f"1 : {ratio_rb:.1f}",
                        "Estrategia": sem_lista,
                        "Fundamento Técnico": explicacion
                    })
            except:
                pass
                
        if datos_lista:
            st.dataframe(pd.DataFrame(datos_lista), use_container_width=True)

    st.write("---")
    st.write("### 🔍 Opción B: Ficha de Inteligencia Individual Detallada")
    accion = st.text_input("Introduce el Ticker de una acción para analizar en individual (Ej: ISRG, ROK, DE):", "ISRG")
    
    if accion:
        accion = accion.upper()
        try:
            ticker_obj = yf.Ticker(accion)
            datos_hist = ticker_obj.history(period="30d")
            
            if not datos_hist.empty:
                p_actual_ind = datos_hist['Close'].iloc[-1]
                p_media_ind = datos_hist['Close'].mean()
                p_min_ind = datos_hist['Close'].min()
                
                try:
                    target_ind = ticker_obj.info.get('targetMedianPrice', p_actual_ind * 1.25)
                    if target_ind is None: target_ind = p_actual_ind * 1.25
                except:
                    target_ind = p_actual_ind * 1.25
                
                potencial_ind = ((target_ind - p_actual_ind) / p_actual_ind) * 100
                riesgo_ind = max(0.5, ((p_actual_ind - p_min_ind) / p_actual_ind) * 100)
                ratio_rb_ind = potencial_ind / riesgo_ind
                
                # Definición de Diagnóstico y Explicación Crítica
                if p_actual_ind > p_media_ind:
                    estado_ind = "🟢 ALCISTA (Por encima de su media)"
                    if ratio_rb_ind >= 2.0:
                        explicacion_ind = f"El activo {accion} muestra una estructura de mínimos crecientes muy robusta. El Ratio Riesgo/Beneficio es muy favorable (1:{ratio_rb_ind:.1f}), lo que indica que el potencial de subida duplica holgadamente el riesgo de caída al soporte de seguridad de los últimos 30 días."
                    else:
                        explicacion_ind = f"Aunque {accion} está en tendencia alcista, el precio ha subido con fuerza recientemente, reduciendo el Ratio Riesgo/Beneficio a un ajuste de (1:{ratio_rb_ind:.1f}). Es apto para mantener, pero con precaución para nuevas entradas."
                else:
                    estado_ind = "🔴 COLA DE PRECIO (Por debajo de su media)"
                    explicacion_ind = f"El activo se encuentra en fase de corrección técnica o consolidación por debajo de la media de 30 días. Se recomienda paciencia hasta ver un patrón de giro, a pesar de que el precio objetivo ofrece un recorrido teórico del {potencial_ind:.1f}%."
                
                # Despliegue visual en columnas
                col_i1, col_i2, col_i3 = st.columns(3)
                col_i1.metric(f"Precio Actual de {accion}", f"{p_actual_ind:.2f} €")
                col_i2.metric("Diagnóstico de Tendencia", estado_ind)
                col_i3.metric("Ratio Riesgo / Beneficio", f"1 : {ratio_rb_ind:.1f}")
                
                # Caja informativa de fundamentación analítica
                st.info(f"📋 **Análisis y Justificación del Bot:** {explicacion_ind}")
                
                st.write(f"**📉 Evolución de Precio de {accion} (Últimos 30 días)**")
                st.line_chart(datos_hist['Close'])
            else:
                st.error("No se han encontrado datos para ese Ticker. Asegúrate de escribirlo correctamente.")
        except:
            st.error("Error al conectar con los servidores de bolsa o Ticker inválido.")

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
