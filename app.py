import streamlit as st
import yfinance as yf
import pandas as pd

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Centro de Mando Pro", layout="wide")

# (Asegúrate de que aquí tengas definidos tus diccionarios de listas)
mis_listas_limpias = {
    "Robótica": ["ISRG", "CGNX", "ADI", "AME", "ROCK", "PTC", "COHR", "6954.T", "6758.T", "6501.T"]
}

# --- DEFINICIÓN DE PESTAÑAS (Esto corrige el NameError) ---
tab1, pestaña2, pestaña3 = st.tabs(["Bot Masivo", "Analizador Técnico y Fundamental", "Configuración"])

# --- PESTAÑA 2: ANALIZADOR (Lógica 4 años) ---
with pestaña2:
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
                
                # LÓGICA DE DECISIÓN A 4 AÑOS
                potencial_4a = ((target - p_actual) / p_actual) * 100
                
                if potencial_4a >= 20.0:
                    veredicto = "🟢 COMPRAR (Zona de Valor)"
                elif 10.0 <= potencial_4a < 20.0:
                    veredicto = "🟡 MANTENER (Equilibrio)"
                else:
                    veredicto = "🔴 ESPERAR (Sobrevalorada)"
                
                datos_tabla.append({
                    "Ticker": tick,
                    "Precio": round(p_actual, 2),
                    "Veredicto": veredicto,
                    "Potencial 4A": f"{potencial_4a:.1f}%",
                    "Target": round(target, 2)
                })
        
        st.dataframe(pd.DataFrame(datos_tabla), use_container_width=True)

    st.write("---")
    st.subheader("🔍 Ficha de Inteligencia Individual")
    accion = st.text_input("Introduce el Ticker:", "COHR")
    
    if accion:
        t = yf.Ticker(accion.upper())
        df = t.history(period="30d")
        
        # Estructura clara en columnas
        col1, col2, col3 = st.columns(3)
        p_act = df['Close'].iloc[-1]
        target = t.info.get('targetMedianPrice', p_act * 1.15)
        potencial = ((target - p_act) / p_act) * 100
        
        col1.metric("Precio Actual", f"${p_act:.2f}")
        col2.metric("Potencial 4A", f"{potencial:.1f}%")
        col3.write(f"### Veredicto: {'🟢 COMPRAR' if potencial >= 20 else '🔴 ESPERAR'}")
        
        st.line_chart(df['Close'], use_container_width=True)
