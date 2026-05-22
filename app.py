import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. LISTA MAESTRA ---
mis_listas_limpias = {
    "Robótica": ["ISRG", "CGNX", "ADI", "AME", "ROCK", "ROK", "TER", "FTV", "NOW", "PTC", 
                 "ANSS", "GWW", "6954.T", "6758.T", "6501.T", "ABT", "AAPL", "MSFT", "NVDA", 
                 "AMD", "TSLA", "INTC", "QCOM", "TXN", "AVGO", "AMAT", "LRCX", "KLAC", "MU", 
                 "SNPS", "CDNS", "TEAM", "ADSK", "DOCU", "SPLK", "CRWD", "OKTA", "ZS", "DDOG", "MDB"]
}

st.set_page_config(page_title="Centro de Mando Pro", layout="wide")
st.title("Centro de Mando Financiero Pro")

tab1, tab2, tab3 = st.tabs(["Bot Masivo", "Analizador Técnico y Fundamental", "Configuración"])

# --- 2. PESTAÑA ANALIZADOR (OPTIMIZADA) ---
with tab2:
    st.subheader("Matriz de Inteligencia de Mercado")
    lista_sel = st.selectbox("Selecciona lista:", list(mis_listas_limpias.keys()))
    
    if lista_sel:
        tickers = mis_listas_limpias[lista_sel]
        
        # Descarga masiva de precios (segura)
        with st.spinner("Descargando precios..."):
            df_precios = yf.download(tickers, period="30d", group_by='ticker', progress=False)
            
        datos_tabla = []
        for tick in tickers:
            if tick in df_precios.columns.levels[0]:
                hist = df_precios[tick].dropna()
                if not hist.empty:
                    p_act = hist['Close'].iloc[-1]
                    # ESTO ES LO QUE NO ROMPE: 
                    # Si no tienes el target, usamos una estimación lógica para no llamar a .info
                    # Asumimos un 15% de crecimiento si no hay target real
                    potencial = 15.0 
                    
                    veredicto = "🟡 MANTENER (Sin datos de target)"
                    datos_tabla.append({"Ticker": tick, "Precio": round(p_act, 2), "Veredicto": veredicto, "Potencial 4A": f"{potencial:.1f}%"})
        
        st.dataframe(pd.DataFrame(datos_tabla), use_container_width=True)

    st.write("---")
    st.subheader("Ficha de Inteligencia Detallada")
    accion = st.text_input("Introduce Ticker:", "COHR")
    
    if accion:
        # Aquí SÍ podemos llamar a un solo .info porque es solo UNA acción
        t = yf.Ticker(accion.upper())
        df = t.history(period="30d")
        info = t.info # Esto solo ocurre una vez por búsqueda
        p_act = df['Close'].iloc[-1]
        target = info.get('targetMedianPrice', p_act * 1.15)
        potencial = ((target - p_act) / p_act) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Precio Actual", f"${p_act:.2f}")
        c2.metric("Potencial 4A", f"{potencial:.1f}%")
        c3.write(f"### Veredicto: {'🟢 COMPRAR' if potencial >= 20 else '🔴 ESPERAR'}")
        st.line_chart(df['Close'])

# --- 3. CONFIGURACIÓN ---
with tab3:
    st.subheader("Gestión de Listas")
    st.json(mis_listas_limpias)
