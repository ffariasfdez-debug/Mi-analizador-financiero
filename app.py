import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- 1. LISTA MAESTRA ---
mis_listas_limpias = {
    "Robótica": ["ISRG", "CGNX", "ADI", "AME", "ROCK", "ROK", "TER", "FTV", "NOW", "PTC", 
                 "ANSS", "GWW", "6954.T", "6758.T", "6501.T", "ABT", "AAPL", "MSFT", "NVDA", 
                 "AMD", "TSLA", "INTC", "QCOM", "TXN", "AVGO", "AMAT", "LRCX", "KLAC", "MU", 
                 "SNPS", "CDNS", "TEAM", "ADSK", "DOCU", "SPLK", "CRWD", "OKTA", "ZS", "DDOG", "MDB"]
}

st.set_page_config(page_title="Centro de Mando Pro", layout="wide")
st.title("Centro de Mando Financiero Pro")

# --- 2. ESTRUCTURA DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["Bot Masivo", "Analizador Técnico y Fundamental", "Configuración"])

# --- 3. PESTAÑA ANALIZADOR ---
with tab2:
    st.subheader("Matriz de Inteligencia (Horizonte 4 Años)")
    lista_sel = st.selectbox("Selecciona lista:", list(mis_listas_limpias.keys()))
    
    if lista_sel:
        tickers = mis_listas_limpias[lista_sel]
        
        # Descarga masiva para evitar bloqueos
        with st.spinner("Procesando mercado..."):
            datos_mercado = yf.download(tickers, period="30d", group_by='ticker', progress=False)
            datos_tabla = []
            
            for tick in tickers:
                if tick in datos_mercado.columns.levels[0]:
                    hist = datos_mercado[tick].dropna()
                    if not hist.empty:
                        p_act = hist['Close'].iloc[-1]
                        # Pequeño delay para no saturar
                        time.sleep(0.1) 
                        info = yf.Ticker(tick).info
                        target = info.get('targetMedianPrice', p_act * 1.15)
                        potencial = ((target - p_act) / p_act) * 100
                        
                        if potencial >= 20: veredicto = "🟢 COMPRAR"
                        elif potencial >= 10: veredicto = "🟡 MANTENER"
                        else: veredicto = "🔴 ESPERAR"
                        
                        datos_tabla.append({"Ticker": tick, "Precio": round(p_act, 2), "Veredicto": veredicto, "Potencial 4A": f"{potencial:.1f}%"})
            
            st.dataframe(pd.DataFrame(datos_tabla), use_container_width=True)

    st.write("---")
    st.subheader("Ficha de Inteligencia Detallada")
    accion = st.text_input("Ticker:", "COHR")
    
    if accion:
        t = yf.Ticker(accion.upper())
        df = t.history(period="30d")
        if not df.empty:
            p_act = df['Close'].iloc[-1]
            target = t.info.get('targetMedianPrice', p_act * 1.15)
            potencial = ((target - p_act) / p_act) * 100
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Precio Actual", f"${p_act:.2f}")
            c2.metric("Potencial 4A", f"{potencial:.1f}%")
            c3.write(f"### Veredicto: {'🟢 COMPRAR' if potencial >= 20 else '🔴 ESPERAR'}")
            st.line_chart(df['Close'])

# --- 4. CONFIGURACIÓN ---
with tab3:
    st.subheader("Gestión de Listas Maestras")
    st.json(mis_listas_limpias)
