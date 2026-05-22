import streamlit as st
import yfinance as yf
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Centro de Mando Pro", layout="wide")

# Lista de ejemplo
mis_listas_limpias = {
    "Robótica": ["ISRG", "CGNX", "ADI", "AME", "ROCK", "PTC", "COHR", "6954.T", "6758.T", "6501.T"]
}

# --- ESTRUCTURA DE PESTAÑAS (Aquí se soluciona el error) ---
tab1, tab2, tab3 = st.tabs(["Bot Masivo", "Analizador Técnico y Fundamental", "Configuración"])

# --- PESTAÑA 2: ANALIZADOR ---
with tab2:
    st.subheader("🔍 Matriz de Inteligencia de Mercado (Horizonte 4 Años)")
    lista_sel = st.selectbox("Selecciona una lista:", list(mis_listas_limpias.keys()))
    
    if lista_sel:
        tickers = mis_listas_limpias[lista_sel]
        datos_tabla = []
        for tick in tickers:
            t = yf.Ticker(tick)
            hist = t.history(period="30d")
            info = t.info
            if not hist.empty:
                p_actual = hist['Close'].iloc[-1]
                target = info.get('targetMedianPrice', p_actual * 1.15)
                potencial = ((target - p_actual) / p_actual) * 100
                
                if potencial >= 20.0: veredicto = "🟢 COMPRAR (Zona de Valor)"
                elif potencial >= 10.0: veredicto = "🟡 MANTENER (Equilibrio)"
                else: veredicto = "🔴 ESPERAR (Sobrevalorada)"
                
                datos_tabla.append({"Ticker": tick, "Precio": round(p_actual, 2), "Veredicto": veredicto, "Potencial 4A": f"{potencial:.1f}%"})
        st.dataframe(pd.DataFrame(datos_tabla), use_container_width=True)

    st.write("---")
    st.subheader("🔍 Ficha de Inteligencia Detallada")
    accion = st.text_input("Introduce Ticker:", "COHR")
    
    if accion:
        t = yf.Ticker(accion.upper())
        df = t.history(period="30d")
        if not df.empty:
            p_act = df['Close'].iloc[-1]
            target = t.info.get('targetMedianPrice', p_act * 1.15)
            potencial = ((target - p_act) / p_act) * 100
            
            # Ficha mejorada: columnas con más peso informativo
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Precio Actual", f"${p_act:.2f}")
            c2.metric("Precio Objetivo", f"${target:.2f}")
            c3.metric("Potencial 4A", f"{potencial:.1f}%")
            c4.write(f"### Dictamen:\n{'🟢 COMPRAR' if potencial >= 20 else '🔴 ESPERAR'}")
            
            # Gráfico con leyenda
            st.line_chart(df['Close'])
