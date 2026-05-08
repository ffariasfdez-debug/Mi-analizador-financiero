import streamlit as st
import yfinance as yf
import pandas as pd

# Configuración estética de la web
st.set_page_config(page_title="Mi Terminal Quant", page_icon="📈", layout="wide")

st.title("🚀 Mi Terminal de Inversión Automática")
st.markdown("---")

# Buscador en la barra lateral
ticker = st.sidebar.text_input("Introduce el Ticker (ej: NVDA, MSFT, BTC-USD):", "NVDA").upper()
boton = st.sidebar.button("Analizar Ahora")

if boton:
    with st.spinner('Analizando mercado...'):
        df = yf.download(ticker, period="1y", progress=False)
        
        if not df.empty:
            # Cálculos técnicos para medio plazo
            df['SMA50'] = df['Close'].rolling(window=50).mean()
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Datos actuales
            precio_act = df['Close'].iloc[-1]
            rsi_act = df['RSI'].iloc[-1]
            sma50_act = df['SMA50'].iloc[-1]

           # Mostrar métricas destacadas
    c1, c2, c3 = st.columns(3)
    c1.metric("Precio Actual", f"${precio_act:.2f}")
    c2.metric("Media 50d", f"${sma50_act:.2f}")
    c3.metric("RSI (Fuerza)", f"{rsi_act:.2f}")
            # Veredicto visual
    st.markdown("### 📋 Veredicto de Actuación")
    if precio_act > sma50_act:
                if rsi_act > 70:
                    st.warning("🟡 MANTENER: Tendencia alcista pero con mucha euforia. No compres más ahora.")
                else:
                    st.success("🟢 COMPRA / MANTENER: El activo tiene salud y fuerza.")
            else:
                st.error("🔴 ESPERAR: El activo está débil o en tendencia bajista.")

            # Gráfico interactivo
            st.markdown("### 📉 Gráfico de Medio Plazo")
            st.line_chart(df[['Close', 'SMA50']])
        else:
            st.error("No se encontraron datos.")

st.sidebar.info("Usa esta herramienta una vez por semana para tu proyecto de medio plazo.")
