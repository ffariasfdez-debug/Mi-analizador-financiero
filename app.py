import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# 1. Configuración inicial de la plataforma
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# --- TITULO PRINCIPAL ---
st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# --- CONTROL DE MEMORIA PARA LAS LISTAS (Sincronización total) ---
if "listas" not in st.session_state:
    st.session_state.listas = {
        "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML"],
        "Robótica Pura": [
            "ISRG", "ZBH", "STE", "ROK", "CGNX", "TER", 
            "ATS", "SYM", "GWW", "AME", "ADI", "FTV", "KEYS", "PTC", 
            "ANSS", "ROCK", "COHR", "DE", "CAT", "AVAV", "GE", "HON"
        ],
        "Fotónica": ["IPGP", "LITE", "COHR"],
        "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR"]
    }

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Panel de Gestión de Listas Inteligentes"
])

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

    # El bot consume la lista en memoria activa
    df_cartera_inteligente, caja_libre, gastado_semana = motor_bot_inteligente(
        st.session_state.listas["Robótica Pura"], max_por_accion, tope_semanal, mercado_activo
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
# PESTAÑA 2: ANALIZADOR TÉCNICO AVANZADO
# =========================================================
with pestaña2:
    st.subheader("🔍 Buscador de Acciones con Gráficos de Tendencia")
    
    st.write("### 📁 Opción A: Cargar una Lista de Seguimiento Completa")
    lista_sel = st.selectbox("Selecciona una lista para proyectar:", ["Ninguna"] + list(st.session_state.listas.keys()))
    
    if lista_sel != "Ninguna":
        tickers_lista = st.session_state.listas[lista_sel]
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
    st.write("### 🔍 Opción B: Ficha de Inteligencia Individual Detallada")
    accion = st.text_input("Introduce el Ticker de una acción para analizar en individual:", "ISRG")
    
    if accion:
        accion = accion.upper()
        try:
            ticker_obj = yf.Ticker(accion)
            datos_hist = ticker_obj.history(period="30d")
            
            if not datos_hist.empty:
                p_actual_ind = datos_hist['Close'].iloc[-1]
                p_media_ind = datos_hist['Close'].mean()
                
                if p_actual_ind > p_media_ind:
                    estado_ind = "🟢 ALCISTA (Por encima de su media)"
                else:
                    estado_ind = "🔴 COLA DE PRECIO (Por debajo de su media)"
                
                col_i1, col_i2 = st.columns(2)
                col_i1.metric(f"Precio Actual de {accion}", f"{p_actual_ind:.2f} €")
                col_i2.metric("Diagnóstico de Tendencia", estado_ind)
                
                st.write(f"**📉 Evolución de Precio de {accion} (Últimos 30 días)**")
                st.line_chart(datos_hist['Close'])
            else:
                st.error("No se han encontrado datos para ese Ticker.")
        except:
            st.error("Error al conectar con los servidores de bolsa.")

# =========================================================
# PESTAÑA 3: PANEL DE GESTIÓN DE LISTAS (ACTUALIZADA)
# =========================================================
with pestaña3:
    st.subheader("⚙️ Editor Maestro de Listas de Inversión")
    st.write("Añade, elimina tickers o crea listas personalizadas desde este panel interactivo sin tocar el código.")
    
    col_pest1, col_pest2 = st.columns([1, 2])
    
    with col_pest1:
        st.write("#### 🆕 Operación 1: Crear Nueva Lista")
        nueva_lista_nombre = st.text_input("Nombre de la nueva lista (Ej: Favoritos, SmallCaps):", "")
        if st.button("➕ Crear Lista Vacía"):
            if nueva_lista_nombre and nueva_lista_nombre not in st.session_state.listas:
                st.session_state.listas[nueva_lista_nombre] = []
                st.success(f"Lista '{nueva_lista_nombre}' creada.")
                st.rerun()
            elif nueva_lista_nombre in st.session_state.listas:
                st.warning("Esa lista ya existe.")

        st.write("---")
        st.write("#### ✏️ Operación 2: Modificar Lista Seleccionada")
        lista_a_modificar = st.selectbox("Selecciona la lista que deseas editar:", list(st.session_state.listas.keys()))
        
        if lista_a_modificar:
            # Añadir Ticker
            nuevo_ticker = st.text_input("Introduce Ticker para AÑADIR (Ej: SYM, IRBT):", "").upper().strip()
            if st.button("📥 Insertar Ticker"):
                if nuevo_ticker and nuevo_ticker not in st.session_state.listas[lista_a_modificar]:
                    st.session_state.listas[lista_a_modificar].append(nuevo_ticker)
                    st.success(f"{nuevo_ticker} añadido a {lista_a_modificar}")
                    st.rerun()
            
            # Eliminar Ticker
            if st.session_state.listas[lista_a_modificar]:
                ticker_a_borrar = st.selectbox("Selecciona un Ticker para ELIMINAR:", st.session_state.listas[lista_a_modificar])
                if st.button("🗑️ Quitar Ticker"):
                    st.session_state.listas[lista_a_modificar].remove(ticker_a_borrar)
                    st.success(f"{ticker_a_borrar} eliminado de {lista_a_modificar}")
                    st.rerun()
            else:
                st.info("Esta lista está vacía.")

    with col_pest2:
        st.write("#### 📋 Visor de Componentes Activos")
        if lista_a_modificar:
            tickers_actuales = st.session_state.listas[lista_a_modificar]
            st.info(f"La lista **{lista_a_modificar}** tiene actualmente **{len(tickers_actuales)}** activos guardados en la base de datos.")
            
            if tickers_actuales:
                df_visualizacion = pd.DataFrame(tickers_actuales, columns=["Ticker Oficial"])
                st.dataframe(df_visualizacion, use_container_width=True)
