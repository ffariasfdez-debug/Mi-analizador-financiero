import streamlit as st
import yfinance as yf
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Analizador Financiero Pro", layout="wide")

def obtener_datos(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1y", interval="1d")
        if df.empty: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        # Indicadores
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        return df
    except:
        return None

# Sidebar
st.sidebar.title("🚀 Menú Principal")
ticker = st.sidebar.text_input("Ticker:", "TSLA").upper()
btn = st.sidebar.button("Analizar Ahora")

# Cuerpo Principal
st.title(f"📈 Análisis Detallado: {ticker}")

if btn:
    data = obtener_datos(ticker)
    if data is not None:
        # 1. Métricas Clave (Fila superior)
        col1, col2, col3 = st.columns(3)
        ultimo_precio = data['Close'].iloc[-1]
        cambio = ultimo_precio - data['Close'].iloc[-2]
        
        col1.metric("Precio Actual", f"${ultimo_precio:.2f}", f"{cambio:.2f}")
        col2.metric("Máximo (52 sem)", f"${data['High'].max():.2f}")
        col3.metric("Volumen", f"{data['Volume'].iloc[-1]:,.0f}")

        # 2. Gráfico Principal
        st.subheader("Evolución de Precio y Medias Móviles")
        st.line_chart(data[['Close', 'SMA50', 'SMA200']])

        # 3. Tabla de Datos
        with st.expander("Ver histórico completo"):
            st.dataframe(data.sort_index(ascending=False))
    else:
        st.error("No se pudo obtener información de este Ticker.")
