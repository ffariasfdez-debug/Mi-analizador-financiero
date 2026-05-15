import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analizador Pro: Momentum & Robótica", layout="wide")

def obtener_recomendacion(m):
    # Lógica de Inversión Refinada
    if m['RSI'] > 75:
        return "🚨 SOBRECOMPRA EXTREMA", f"Riesgo muy alto de corrección. No comprar aquí. Esperar retroceso a zona de ${m['SMA50']:.2f}."
    elif 68 < m['RSI'] <= 75:
        return "⚠️ MANTENER / NO PERSEGUIR", "Fuerza alta, pero el precio está extendido. Si ya las tienes, mantén; si no, espera un descanso."
    elif m['Precio'] > m['SMA50'] and 50 < m['RSI'] <= 68:
        return "🔥 COMPRAR (Punto Óptimo)", "Tendencia alcista con margen de subida antes de sobrecompra."
    elif m['Precio'] < m['SMA200']:
        return "❄️ EVITAR / BAJISTA", f"Tendencia negativa a largo plazo. Solo entrar si recupera los ${m['SMA200']:.2f}."
    elif m['RSI'] < 35:
        return "🎯 OPORTUNIDAD (Sobreventa)", f"Posible suelo temporal. Rebote técnico probable cerca de ${m['Precio']:.2f}."
    else:
        return "⌛ ESPERAR / VIGILAR", "Buscando dirección clara. Vigilar si rompe la media de 50 con fuerza."

def calcular_analitica(df):
    if df.empty or len(df) < 200: return None
    # Limpieza de columnas para yfinance
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

# --- CONFIGURACIÓN DE LISTAS ---
listas_seguimiento = {
    "Robótica/IA": ["ISRG", "ABB", "6861.T", "SYM", "SERV", "272210.KS", "TER", "6954.T", "SYK", "CGNX", "AUR", "MBLY"],
    "Tecnología": ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"],
    "Cripto/ETF": ["BTC-USD", "COIN", "MSTR", "IBIT"],
    "Bélgica/EU": ["ABI.BR", "UCB.BR", "SAP", "ASML.AS"]
}

# --- INTERFAZ ---
st.sidebar.title("Estrategia 2026-2030")
modo = st.sidebar.radio("Modo:", ["🔍 Análisis Individual", "📊 Comparador de Listas"])

if modo == "🔍 Análisis Individual":
    ticker = st.text_input("Introduce Ticker:", "ISRG").upper()
    if st.button("Analizar"):
        data = yf.Ticker(ticker).history(period="2y")
        m = calcular_analitica(data)
        if m:
            st.header(f"Estrategia: {m['Accion']}")
            st.info(f"**Análisis Técnico:** {m['Detalle']}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Precio Actual", f"${m['Precio']:.2f}", f"{m['Cambio']:.2f}%")
            c2.metric("Fuerza RSI", f"{m['RSI']:.1f}")
            c3.metric("Suelo Largo Plazo", f"${m['SMA200']:.2f}")

            st.line_chart(m['df_grafico'])
        else:
            st.error("No se encontraron datos suficientes. Revisa el Ticker.")

else:
    st.title("Momentum de mis Listas")
    lista_sel = st.sidebar.selectbox("Selecciona Lista:", list(listas_seguimiento.keys()))
    if st.button("Ejecutar Análisis"):
        res = []
        progreso = st.progress(0)
        for i, t in enumerate(listas_seguimiento[lista_sel]):
            d = yf.Ticker(t).history(period="2y")
            m = calcular_analitica(d)
            if m:
                res.append({"Ticker": t, "RSI": round(m['RSI'], 1), "Estado": m['Accion']})
            progreso.progress((i + 1) / len(listas_seguimiento[lista_sel]))
        
        st.table(pd.DataFrame(res))
