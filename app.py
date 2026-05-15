import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analizador Pro: Estrategia Definitiva", layout="wide")

def obtener_recomendacion(m):
    # Lógica de Inversión Refinada (Evitando comprar en picos)
    dist_sma50 = ((m['Precio'] / m['SMA50']) - 1) * 100
    
    if m['RSI'] > 75:
        return "🚨 SOBRECOMPRA EXTREMA", f"Riesgo muy alto. No comprar aquí. Esperar retroceso a la zona de ${m['SMA50']:.2f}."
    
    elif 68 < m['RSI'] <= 75:
        return "⚠️ MANTENER / NO PERSEGUIR", "Fuerza brutal, pero el precio está extendido. Si ya las tienes, mantén; si no, espera un descanso."
    
    elif m['Precio'] > m['SMA50'] and 50 < m['RSI'] <= 68:
        return "🔥 COMPRAR (Punto Óptimo)", "Combinación ideal: Tendencia alcista con margen de subida antes de sobrecompra."
    
    elif m['Precio'] < m['SMA200']:
        return "❄️ EVITAR / BAJISTA", f"Bajo la media de 200. Mucho riesgo. Solo entrar si recupera los ${m['SMA200']:.2f}."
    
    elif m['RSI'] < 35:
        return "🎯 OPORTUNIDAD (Sobreventa)", f"Posible suelo temporal. Nivel de rebote técnico en ${m['Precio']:.2f}."
    
    else:
        return "⌛ ESPERAR / VIGILAR", f"Buscando dirección. Vigilar si rompe los ${m['SMA50']:.2f} con volumen."

def calcular_analitica(df):
    if df.empty or len(df) < 200: return None
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
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

# --- INTERFAZ ---
st.sidebar.title("Estrategia 2026-2030")
modo = st.sidebar.radio("Modo:", ["🔍 Análisis Individual", "📊 Comparador de Listas"])

listas_seguimiento = {
    "Tecnología": ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"],
    "Semicond": ["ASML", "AVGO", "ARM", "SMCI", "MU"],
    "Cripto/ETF": ["BTC-USD", "COIN", "MSTR", "IBIT"],
    "Bélgica/EU": ["ABI.BR", "UCB.BR", "SAP", "ASML.AS"]
}

if modo == "🔍 Análisis Individual":
    ticker = st.text_input("Ticker:", "NVDA").upper()
    if st.button("Analizar"):
        data = yf.Ticker(ticker).history(period="2y")
        m = calcular_analitica(data)
        if m:
            st.subheader(f"Estrategia: {m['Accion']}")
            st.info(f"**Nota Técnica:** {m['Detalle']}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Precio", f"${m['Precio']:.2f}", f"{m['Cambio']:.2f}%")
            c2.metric("RSI", f"{m['RSI']:.1f}")
            c3.metric("Suelo (SMA200)", f"${m['SMA200']:.2f}")

            st.line_chart(m['df_grafico'])
        else:
            st.error("Error de datos.")
else:
    st.title("Panel de Momentum")
    lista_sel = st.sidebar.selectbox("Lista:", list(listas_seguimiento.keys()))
    if st.button("Analizar Lista"):
        res = []
        for t in listas_seguimiento[lista_sel]:
            d = yf.Ticker(t).history(period="2y")
            m = calcular_analitica(d)
            if m:
                res.append({"Ticker": t, "RSI": round(m['RSI'], 1), "Acción": m['Accion']})
        st.table(pd.DataFrame(res))
