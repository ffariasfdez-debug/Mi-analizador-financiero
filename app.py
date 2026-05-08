import streamlit as st
import yfinance as yf
import pandas as pd

# Configuración básica
st.set_page_config(page_title="Terminal Pro", layout="wide")

# Listas de seguimiento
listas = {
    "Tecnología": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AMD"],
    "Dividendos": ["KO", "PEP", "JNJ", "PG", "MMM", "XOM"],
    "Cripto": ["BTC-USD", "ETH-USD", "SOL-USD"]
}

st.sidebar.title("Menú")
modo = st.sidebar.radio("Ir a:", ["Análisis Individual", "Mis Listas"])

if modo == "Análisis Individual":
    st.title("🔍 Buscador de Acciones")
    ticker = st.sidebar.text_input("Introduce Ticker:", "NVDA").upper()
    if st.sidebar.button("Analizar"):
        df = yf.download(ticker, period="1y")
        if not df.empty:
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
            st.metric("Precio Actual", f"${df['Close'].iloc[-1]:.2f}")
            st.line_chart(df['Close'])
            st.bar_chart(df['Volume'])

else:
    st.title("📂 Mis Listas")
    sel = st.sidebar.selectbox("Selecciona Lista:", list(listas.keys()))
    if st.sidebar.button("Escanear Todo"):
        res = []
        for t in listas[sel]:
            d = yf.download(t, period="1y", progress=False)
            if not d.empty:
                d.columns = [col[0] if isinstance(col, tuple) else col for col in d.columns]
                precio = d['Close'].iloc[-1]
                res.append({"Activo": t, "Precio": f"${precio:.2f}"})
        st.table(pd.DataFrame(res))
