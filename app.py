import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. LISTA MAESTRA (Aquí están tus activos. Asegúrate de tener los 40) ---
mis_listas_limpias = {
    "Robótica": ["ISRG", "CGNX", "ADI", "AME", "ROCK", "ROK", "TER", "FTV", "NOW", "PTC", 
                 "ANSS", "GWW", "6954.T", "6758.T", "6501.T", "ABT", "AAPL", "MSFT", "NVDA", 
                 "AMD", "TSLA", "INTC", "QCOM", "TXN", "AVGO", "AMAT", "LRCX", "KLAC", "MU", 
                 "SNPS", "CDNS", "TEAM", "ADSK", "DOCU", "SPLK", "CRWD", "OKTA", "ZS", "DDOG", "MDB"]
}

st.set_page_config(page_title="Centro de Mando Pro", layout="wide")
st.title("Centro de Mando Financiero Pro")

# --- 2. ESTRUCTURA DE PESTAÑAS (La que ya tenías y funcionaba) ---
tab1, tab2, tab3 = st.tabs(["Bot Masivo", "Analizador Técnico y Fundamental", "Configuración"])

# --- 3. LÓGICA DE ANALIZADOR ---
with tab2:
    st.subheader("Matriz de Inteligencia de Mercado (Horizonte 4 Años)")
    lista_sel = st.selectbox("Selecciona lista:", list(mis_listas_limpias.keys()))
    
    if lista_sel:
        tickers = mis_listas_limpias[lista_sel]
        datos = []
        
        # Procesamiento de la lista completa de 40 activos
        for tick in tickers:
            t = yf.Ticker(tick)
            hist = t.history(period="30d")
            info = t.info
            
            if not hist.empty:
                p_act = hist['Close'].iloc[-1]
                target = info.get('targetMedianPrice', p_act * 1.15)
                potencial = ((target - p_act) / p_act) * 100
                
                # Tu semáforo lógico
                if potencial >= 20: veredicto = "🟢 COMPRAR"
                elif potencial >= 10: veredicto = "🟡 MANTENER"
                else: veredicto = "🔴 ESPERAR"
                
                datos.append({"Ticker": tick, "Precio": round(p_act, 2), "Veredicto": veredicto, "Potencial 4A": f"{potencial:.1f}%"})
        
        st.dataframe(pd.DataFrame(datos), use_container_width=True)

    st.write("---")
    st.subheader("Ficha de Inteligencia Detallada")
    accion = st.text_input("Introduce Ticker:", "COHR")
    
    if accion:
        t = yf.Ticker(accion.upper())
        df = t.history(period="30d")
        if not df.empty:
            p_act = df['Close'].iloc[-1]
            target = t.info.get('targetMedianPrice', p_act * 1.15)
            potencial = ((target - p_act) / p_act) * 100
            
            # Ficha con métricas claras
            c1, c2, c3 = st.columns(3)
            c1.metric("Precio Actual", f"${p_act:.2f}")
            c2.metric("Potencial 4A", f"{potencial:.1f}%")
            c3.write(f"### Veredicto: {'🟢 COMPRAR' if potencial >= 20 else '🔴 ESPERAR'}")
            
            st.line_chart(df['Close'])

# --- 4. CONFIGURACIÓN (Restaurada) ---
with tab3:
    st.subheader("Gestión de Listas")
    st.json(mis_listas_limpias)
