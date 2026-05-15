import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analizador Pro: Momentum & Alertas", layout="wide")

def obtener_recomendacion(m):
    # Lógica de inversión basada en Momentum Técnico
    if m['Precio'] > m['SMA50'] and m['RSI'] > 60:
        return "🔥 COMPRAR (Fuerte Momentum)", "Continuar con la tendencia alcista."
    elif m['Precio'] < m['SMA200']:
        return "❄️ EVITAR / BAJISTA", f"Esperar a que recupere los ${m['SMA200']:.2f}"
    elif m['RSI'] < 35:
        return "🎯 VIGILAR (Posible Rebote)", f"Nivel de compra agresivo cerca de ${m['Precio']:.2f}"
    elif m['Precio'] > m['SMA200'] and m['Precio'] < m['SMA50']:
        return "⌛ ESPERAR (Consolidación)", f"Esperar nivel de ruptura en ${m['SMA50']:.2f}"
    else:
        return "⚖️ MANTENER", "Sin señales claras de cambio."

def calcular_analitica(df):
    if df.empty or len(df) < 200: return None
    
    precio = df['Close'].iloc[-1]
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
    
    m = {
        "Precio": precio,
        "SMA50": df['SMA50'].iloc[-1],
        "SMA200": df['SMA200'].iloc[-1],
        "RSI": rsi,
        "Cambio": df['Close'].pct_change().iloc[-1] * 100,
        "df_grafico": df[['Close', 'SMA50', 'SMA200']].tail(252)
    }
    
    m['Accion'], m['Detalle'] = obtener_recomendacion(m)
    return m

st.sidebar.title("Menú de Inversión")
modo = st.sidebar.radio("Modo:", ["🔍 Análisis Individual", "📊 Comparador de Listas"])

listas_seguimiento = {
    "Tecnología": ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"],
    "Cripto/ETF": ["BTC-USD", "COIN", "MSTR", "IBIT"],
    "Bélgica/EU": ["ASML.AS", "ABI.BR", "UCB.BR", "SAP"]
}

if modo == "🔍 Análisis Individual":
    ticker = st.text_input("Introduce Ticker:", "NVDA").upper()
    if st.button("Generar Informe"):
        data = yf.Ticker(ticker).history(period="2y")
        m = calcular_analitica(data)
        
        if m:
            st.header(f"Recomendación: {m['Accion']}")
            st.info(f"**Estrategia:** {m['Detalle']}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Precio Actual", f"${m['Precio']:.2f}", f"{m['Cambio']:.2f}%")
            c2.metric("Fuerza RSI", f"{m['RSI']:.1f}")
            c3.metric("Nivel Crítico (SMA200)", f"${m['SMA200']:.2f}")

            st.line_chart(m['df_grafico'])
        else:
            st.error("Error al cargar datos.")

else:
    st.title("Momentum de mis Listas")
    lista_sel = st.sidebar.selectbox("Elegir Lista:", list(listas_seguimiento.keys()))
    if st.button("Analizar Lista"):
        res = []
        for t in listas_seguimiento[lista_sel]:
            d = yf.Ticker(t).history(period="2y")
            m = calcular_analitica(d)
            if m:
                res.append({
                    "Ticker": t,
                    "RSI": round(m['RSI'],1),
                    "Acción": m['Accion'],
                    "Nivel Objetivo": f"${m['SMA50']:.2f}"
                })
        st.table(pd.DataFrame(res))
