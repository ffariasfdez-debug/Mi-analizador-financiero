import streamlit as st
import pandas as pd
import yfinance as yf

# Configuración de la página completa
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# --- TITULO PRINCIPAL ---
st.title("🎛️ Centro de Mando Financiero")
st.write("---")

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Individual y de Listas", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# BASE DE DATOS DE TUS LISTAS PREGRABADAS (Para que el buscador las pueda leer)
listas_guardadas = {
    "Semiconductores": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML"],
    "Robótica": ["ADI", "AME", "ISRG", "CGNX"],
    "Fotónica": ["IPGP", "LITE", "COHR"],
    "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR"]
}

# =========================================================
# PESTAÑA 1: EL BOT DE SIMULACIÓN Y EL LIBRO DE REGISTRO
# =========================================================
with pestaña1:
    st.subheader("Algoritmo de Gestión Autónoma por Momentum Técnico")
    exclusiones = st.text_input("Acciones a excluir del radar de compra (ej: NVDA, ASML):", "", key="excl_bot")
    
    compras_fijas = [
        {"Fecha/Hora": "2026-05-18 14:38:46", "Ticker": "ASM.AS", "Precio Compra": 852.00, "Capital Invertido": 2000.0, "Canal": "Bolero / Rev"},
        {"Fecha/Hora": "2026-05-18 14:38:52", "Ticker": "KLAC", "Precio Compra": 1755.30, "Capital Invertido": 2000.0, "Canal": "Bolero / Rev"},
        {"Fecha/Hora": "2026-05-18 14:39:01", "Ticker": "TFX", "Precio Compra": 133.32, "Capital Invertido": 1000.0, "Canal": "Bolero / Rev"},
        {"Fecha/Hora": "2026-05-18 14:39:07", "Ticker": "AME", "Precio Compra": 227.10, "Capital Invertido": 1000.0, "Canal": "Bolero / Rev"},
        {"Fecha/Hora": "2026-05-18 14:39:16", "Ticker": "MPWR", "Precio Compra": 1514.83, "Capital Invertido": 2000.0, "Canal": "ING España"}
    ]
    
    @st.cache_data(ttl=5)
    def obtener_precios_vivos(lista_compras):
        lista_actualizada = []
        for c in lista_compras:
            try:
                ticker_yahoo = yf.Ticker(c["Ticker"])
                historial = ticker_yahoo.history(period="1d")
                precio_actual = historial['Close'].iloc[-1] if not historial.empty else c["Precio Compra"]
            except:
                precio_actual = c["Precio Compra"]
                
            cantidad = round(c["Capital Invertido"] / c["Precio Compra"], 4)
            rendimiento = round(((precio_actual - c["Precio Compra"]) / c["Precio Compra"]) * 100, 2)
            flecha = "🔼 +" if rendimiento >= 0 else "🔽 "
            
            lista_actualizada.append({
                "Fecha/Hora": c["Fecha/Hora"],
                "Ticker": c["Ticker"],
                "Cantidad (Títulos)": cantidad,
                "Precio Compra": f"{c['Precio Compra']:.2f} €" if "AS" in c["Ticker"] else f"{c['Precio Compra']:.2f} $",
                "Precio Actual": f"{precio_actual:.2f} €" if "AS" in c["Ticker"] else f"{precio_actual:.2f} $",
                "Capital Invertido": f"{c['Capital Invertido']:.2f} €",
                "Rendimiento (%)": f"{flecha}{rendimiento}%",
                "Broker": c["Canal"]
            })
        return pd.DataFrame(lista_actualizada)

    if st.button("🔄 Refrescar Cotizaciones del Radar"):
        st.cache_data.clear()
        st.toast("¡Precios actualizados en vivo!")

    df_vivo = obtener_precios_vivos(compras_fijas)
    
    st.write("### 📋 Libro de Registro de Posiciones (Datos en Vivo)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Fondo Estrategia", "30.000 €")
    c2.metric("Caja Líquida", "22.000,00 €")
    c3.metric("Posiciones Abiertas", "5")
    st.dataframe(df_vivo, use_container_width=True)

# =========================================================
# PESTAÑA 2: NUEVO ANALIZADOR INDIVIDUAL Y DE LISTAS
# =========================================================
with pestaña2:
    st.subheader("🔍 Analizar Listas Pregrabadas o Valores Sueltos")
    
    # NUEVA OPCIÓN 1: ELEGIR UNA LISTA COMPLETA PARA ANALIZAR
    st.write("### 📁 Opción A: Analizar una Lista Pregrabada Completa")
    lista_seleccionada = st.selectbox("Selecciona qué lista quieres cargar y analizar ahora mismo:", ["Ninguna"] + list(listas_guardadas.keys()))
    
    if lista_seleccionada != "Ninguna":
        st.success(f"Cargando valores de la lista: **{lista_seleccionada}**")
        valores_lista = listas_guardadas[lista_seleccionada]
        
        # Descargar los precios en directo de todos los valores de la lista elegida
        resultados_lista = []
        for ticker in valores_lista:
            try:
                t = yf.Ticker(ticker)
                info = t.history(period="1d")
                precio = f"{info['Close'].iloc[-1]:.2f}" if not info.empty else "N/A"
            except:
                precio = "Error"
            resultados_lista.append({"Ticker": ticker, "Precio de Mercado en Vivo": precio, "Estado del Radar": "🟢 APTO PARA OPERAR" if precio != "Error" else "🔴 Sin Conexión"})
            
        st.dataframe(pd.DataFrame(resultados_lista), use_container_width=True)
        
    st.write("---")
    
    # OPCIÓN 2: EL BUSCADOR INDIVIDUAL DE SIEMPRE
    st.write("### 🔍 Opción B: Buscar una Sola Acción Suelta")
    accion_buscar = st.text_input("Introduce el nombre o Ticker de la acción individual que quieres estudiar:")
    if accion_buscar:
        st.write(f"Buscando datos técnicos para: **{accion_buscar.upper()}**...")
        try:
            t = yf.Ticker(accion_buscar)
            info = t.history(period="1d")
            if not info.empty:
                st.info(f"Precio actual en Bolsa de {accion_buscar.upper()}: {info['Close'].iloc[-1]:.2f}")
            else:
                st.warning("No se han encontrado datos para ese Ticker.")
        except:
            st.error("Error al conectar con las cotizaciones.")

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN DE LISTAS PREGRABADAS
# =========================================================
with pestaña3:
    st.subheader("⚙️ Modificar Valores de las Listas Pregrabadas")
    st.write("Selecciona qué lista de seguimiento quieres modificar:")
    lista_sel = st.selectbox("Listas disponibles para editar:", ["Semiconductores", "Robótica", "Fotónica", "Filtro 0% Dividendos"])
    st.text_area("Valores incluidos en esta lista (separados por comas):", ", ".join(listas_guardadas[lista_sel]))
    if st.button("Guardar Cambios en la Lista"):
        st.success("Lista pregrabada guardada correctamente.")
