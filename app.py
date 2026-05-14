import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Analizador Financiero Pro", layout="wide")

def obtener_datos(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1y", interval="1d")
        if df.empty: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Indicadores Técnicos
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        
        # Cálculo de RSI (Momentum)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    except:
        return None

# Barra Lateral
st.sidebar.title("🚀 Menú Principal")
ticker_input = st.sidebar.text_input("Ticker:", "TSLA").upper()
btn = st.sidebar.button("Analizar Ahora")

if btn:
    data = obtener_datos(ticker_input)
    if data is not None:
        st.title(f"📊 Análisis Detallado: {ticker_input}")
        
        # 1. MÉTRICAS SUPERIORES
        col1, col2, col3 = st.columns(3)
        precio_actual = data['Close'].iloc[-1]
        rsi_actual = data['RSI'].iloc[-1]
        max_52 = data['High'].max()
        col1.metric("Precio Actual", f"${precio_actual:.2f}")
        col2.metric("Máximo (52 sem)", f"${max_52:.2f}")
        col3.metric("Momentum (RSI)", f"{rsi_actual:.2f}")

        # 2. CUADRO DE RECOMENDACIÓN (Lo que faltaba)
        sma50 = data['SMA50'].iloc[-1]
        if rsi_actual > 70:
            rec, color = "VENDER (Sobrecompra)", "#d32f2f" # Rojo
        elif rsi_actual < 30:
            rec, color = "COMPRAR (Sobreventa)", "#2e7d32" # Verde
        elif precio_actual > sma50:
            rec, color = "MANTENER (Tendencia Alcista)", "#1976d2" # Azul
        else:
            rec, color = "MANTENER (Neutral)", "#757575" # Gris

        st.markdown(f"""
            <div style="background-color: {color}; padding: 25px; border-radius: 15px; text-align: center; margin: 20px 0;">
                <h1 style="color: white; margin: 0; font-size: 2em;">Sugerencia: {rec}</h1>
                <p style="color: white; opacity: 0.8;">Basado en RSI y Medias Móviles</p>
            </div>
        """, unsafe_allow_html=True)

        # 3. GRÁFICOS
        st.subheader("Evolución de Precio y Medias Móviles")
        st.line_chart(data[['Close', 'SMA50', 'SMA200']])
        
        st.subheader("Indicador de Momentum (RSI)")
        st.area_chart(data['RSI'])
    else:
        st.error("No se pudo obtener información.")
