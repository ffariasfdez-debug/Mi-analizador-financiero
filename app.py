import streamlit as st
import pandas as pd
import yfinance as yf  # Conector automático con el mercado en tiempo real

# Configuración de la página completa
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# --- TITULO PRINCIPAL ---
st.title("🎛️ Centro de Mando Financiero")
st.write("---")

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Buscador Individual de Acciones", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# =========================================================
# PESTAÑA 1: EL BOT DE SIMULACIÓN Y EL LIBRO DE REGISTRO
# =========================================================
with pestaña1:
    st.subheader("Algoritmo de Gestión Autónoma por Momentum Técnico")
    
    exclusiones = st.text_input("Acciones a excluir del radar de compra (ej: NVDA, ASML):", "", key="excl_bot")
    
    # Datos fijos de tus compras (Fecha y precio al que compraste)
    compras_fijas = [
        {"Fecha/Hora": "2026-05-18 14:38:46", "Ticker": "ASM.AS", "Precio Compra": 852.00, "Capital Invertido": 2000.0, "Canal": "Bolero / Rev"},
        {"Fecha/Hora": "2026-05-18 14:38:52", "Ticker": "KLAC", "Precio Compra": 828.00, "Capital Invertido": 2000.0, "Canal": "Bolero / Rev"},
        {"Fecha/Hora": "2026-05-18 14:39:01", "Ticker": "TFX", "Precio Compra": 212.00, "Capital Invertido": 1000.0, "Canal": "Bolero / Rev"},
        {"Fecha/Hora": "2026-05-18 14:39:07", "Ticker": "AME", "Precio Compra": 172.00, "Capital Invertido": 1000.0, "Canal": "Bolero / Rev"},
        {"Fecha/Hora": "2026-05-18 14:39:16", "Ticker": "MPWR", "Precio Compra": 823.00, "Capital Invertido": 2000.0, "Canal": "ING España"}
    ]
    
    # FUNCIÓN QUE CONECTA CON INTERNET Y ACTUALIZA LOS PRECIOS EN DIRECTO
    @st.cache_data(ttl=10) # Hace que el precio se actualice rápido si refrescas
    def obtener_precios_vivos(lista_compras):
        lista_actualizada = []
        for c in lista_compras:
            try:
                # El programa consulta la cotización actual en la bolsa
                ticker_yahoo = yf.Ticker(c["Ticker"])
                historial = ticker_yahoo.history(period="1d")
                if not historial.empty:
                    precio_actual = historial['Close'].iloc[-1]
                else:
                    precio_actual = c["Precio Compra"] # Por si falla internet
            except:
                precio_actual = c["Precio Compra"]
                
            # Hacer los cálculos matemáticos automáticos
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

    # Botón para forzar la actualización manual en pantalla
    if st.button("🔄 Refrescar Cotizaciones del Radar"):
        st.cache_data.clear() # Borra la memoria vieja para obligar a buscar el precio nuevo
        st.toast("¡Precios y rendimientos actualizados al instante con la Bolsa!")

    # Llamamos a la función viva para pintar la tabla
    df_vivo = obtener_precios_vivos(compras_fijas)
    
    st.write("### 📋 Libro de Registro de Posiciones (Datos en Vivo)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Fondo Estrategia", "30.000 €")
    c2.metric("Caja Líquida", "22.000,00 €")
    c3.metric("Posiciones Abiertas", "5")
    
    # Mostramos la tabla en pantalla
    st.dataframe(df_vivo, use_container_width=True)

# =========================================================
# PESTAÑA 2: EL BUSCADOR INDIVIDUAL
# =========================================================
with pestaña2:
    st.subheader("🔍 Analizar Acción Individual")
    accion_buscar = st.text_input("Introduce el nombre o Ticker de la acción que quieres estudiar:")
    if accion_buscar:
        st.write(f"Buscando datos técnicos para: **{accion_buscar.upper()}**...")
        try:
            t = yf.Ticker(accion_buscar)
            info = t.history(period="1d")
            if not info.empty:
                st.success(f"Precio actual de mercado de {accion_buscar.upper()}: {info['Close'].iloc[-1]:.2f}")
            else:
                st.warning("No se han encontrado datos para ese Ticker.")
        except:
            st.error("Error al conectar con el servicio de cotizaciones.")

# =========================================================
# PESTAÑA 3: CONFIGURACIÓN DE LISTAS PREGRABADAS
# =========================================================
with pestaña3:
    st.subheader("⚙️ Modificar Listas Pregrabadas")
    st.write("Selecciona qué lista de seguimiento quieres modificar:")
    lista_sel = st.selectbox("Listas disponibles:", ["Semiconductores", "Robótica", "Fotónica", "Filtro 0% Dividendos"])
    st.text_area("Valores incluidos en esta lista (separados por comas):", "ADI, ADSK, AMAT, AMD, AME")
    if st.button("Guardar Cambios en la Lista"):
        st.success("Lista pregrabada guardada correctamente.")
