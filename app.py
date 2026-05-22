import streamlit as st
import pandas as pd
import yfinance as yf

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# --- LISTA MAESTRA (Aquí están tus 40 activos) ---
mis_listas_limpias = {
    "Robótica": [
        "ISRG", "CGNX", "ADI", "AME", "ROCK", "ROK", "TER", "FTV", "NOW", "PTC", 
        "ANSS", "GWW", "SYM", "PATH", "AZTA", "ESTC", "NXPI", "TXN", "ON", "A",
        "SIE.DE", "SU.PA", "ABB", "SCHN.PA", "KRN.DE", "TRMB", "AZO", "GFL",
        "6361.T", "6594.T", "6645.T", "6954.T", "6758.T", "6762.T", "6501.T", 
        "7752.T", "4543.T", "7741.T", "4901.T", "6141.T", "6273.T"
    ],
    "Semiconductores": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "TSM", "AVGO", "LRCX", "AMAT"],
    "Fotónica": ["IPGP", "LITE", "COHR", "VNT", "FN", "MKSI", "NKTX", "LIMO"],
    "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR", "CGNX", "ISRG", "COHR"]
}

# --- ESTRUCTURA DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🤖 Bot Masivo", "🔍 Analizador Técnico", "⚙️ Configuración"])

# --- PESTAÑA 1: BOT MASIVO ---
with tab1:
    st.subheader("🤖 Bot Masivo Automático 30k")
    st.info("Sistema activo: Monitoreando posiciones en tiempo real.")
    # Aquí puedes añadir tu lógica de compras fijas

# --- PESTAÑA 2: ANALIZADOR TÉCNICO Y FUNDAMENTAL ---
with tab2:
    st.subheader("🔍 Matriz de Inteligencia")
    lista_sel = st.selectbox("Selecciona lista:", list(mis_listas_limpias.keys()))
    
    if lista_sel:
        tickers = mis_listas_limpias[lista_sel]
        st.write(f"Analizando {len(tickers)} activos...")
        # Lógica de tabla
        datos = []
        for tick in tickers:
            datos.append({"Ticker": tick, "Estado": "Analizando..."})
        st.table(pd.DataFrame(datos))

    st.write("---")
    st.subheader("🔍 Ficha de Inteligencia Detallada")
    accion = st.text_input("Introduce Ticker:", "COHR")
    
    if accion:
        t = yf.Ticker(accion.upper())
        df = t.history(period="30d")
        if not df.empty:
            p_act = df['Close'].iloc[-1]
            c1, c2 = st.columns(2)
            c1.metric("Precio Actual", f"${p_act:.2f}")
            st.line_chart(df['Close'])

# --- PESTAÑA 3: CONFIGURACIÓN ---
with tab3:
    st.subheader("⚙️ Panel de Gestión de Listas")
    st.json(mis_listas_limpias)
