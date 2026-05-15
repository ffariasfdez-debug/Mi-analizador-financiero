import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analizador Pro: Momentum & Alertas", layout="wide")

def obtener_recomendacion(m):
    # Lógica de Inversión basada en Tendencia y Fuerza
    dist_sma50 = ((m['Precio'] / m['SMA50']) - 1) * 100
    
    if m['Precio'] > m['SMA50'] and m['RSI'] > 60:
        return "🔥 COMPRAR (Fuerte Momentum)", "El activo tiene fuerza. Mantener o ampliar mientras siga sobre la media de 50."
    
    elif m['RSI'] > 75:
        return "⚠️ VIGILAR (Sobrecompra)", "Está muy extendido. No comprar aquí, esperar a que el RSI baje de 70."
    
    elif m['Precio'] < m['SMA200']:
        return "❄️ EVITAR / BAJISTA", f"En tendencia bajista. Solo mirar si recupera los ${m['SMA200']:.2f}."
    
    elif m['RSI'] < 35:
        return "🎯 OPORTUNIDAD (Rebote)", f"Nivel de sobreventa. Posible compra especulativa en ${m['Precio']:.2f}."
    
    elif abs(dist_sma50) < 2:
        return "⚖️ VIGILAR NIVEL", f"Punto de decisión. Si rebota en ${m['SMA50']:.2f}, es señal de compra."
    
    else:
        return "⌛ ESPERAR", f"Sin señal clara. Esperar ruptura de ${m['SMA50']:.2f} o rebote en ${m['SMA200']:.2f}."

def calcular_analitica(df):
    if df.empty or len(df) < 200: return None
    
    # Limpiar nombres de columnas si vienen como tuplas de yfinance
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
st.sidebar.title("Menú de Inversión")
modo = st.sidebar.radio("Seleccionar Modo:", ["🔍 Análisis Individual", "📊 Comparador de Listas"])

listas_seguimiento = {
    "Tecnología": ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"],
    "Semicond": ["ASML", "AVGO", "ARM", "SMCI"],
    "Cripto/ETF": ["BTC-USD", "COIN", "MSTR", "IBIT"],
    "Bélgica/EU": ["ABI.BR", "UCB.BR", "SAP", "ASML.AS"]
}

if modo == "🔍 Análisis Individual":
    ticker = st.text_input("Introduce Ticker:", "NVDA").upper()
    if st.button("Generar Informe Técnico"):
        data = yf.Ticker(ticker).history(period="2y")
        m = calcular_analitica(data)
        
        if m:
            st.subheader(f"Estrategia sugerida: {m['Accion']}")
            st.info(f"**Análisis:** {m['Detalle']}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Precio Actual", f"${m['Precio']:.2f}", f"{m['Cambio']:.2f}%")
            c2.metric("Fuerza RSI", f"{m['RSI']:.1f}")
            c3.metric("Suelo Crítico (SMA200)", f"${m['SMA200']:.2f}")

            st.line_chart(m['df_grafico'])
        else:
            st.error("No hay datos suficientes para este Ticker.")

else:
    st.title("Momentum de mis Listas")
    lista_sel = st.sidebar.selectbox("Elegir Lista:", list(listas_seguimiento.keys()))
    if st.button("Actualizar Toda la Lista"):
        res = []
        bar = st.progress(0)
        for i, t in enumerate(listas_seguimiento[lista_sel]):
            d = yf.Ticker(t).history(period="2y")
            m = calcular_analitica(d)
            if m:
                res.append({
                    "Ticker": t,
                    "RSI": round(m['RSI'], 1),
                    "Acción": m['Accion'],
                    "Nivel a Vigilar": f"${m['SMA50']:.2f}"
                })
            bar.progress((i + 1) / len(listas_seguimiento[lista_sel]))
        
        st.table(pd.DataFrame(res))
