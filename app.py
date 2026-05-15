import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analizador Pro: Individual & Listas", layout="wide")

# --- FUNCIONES DE CÁLCULO ---
def calcular_metricas(df):
    if df.empty: return None
    
    precio_actual = df['Close'].iloc[-1]
    sma50 = df['Close'].rolling(window=50).mean().iloc[-1]
    sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
    max_52w = df['Close'].rolling(window=252).max().iloc[-1]
    vol_medio = df['Volume'].rolling(window=20).mean().iloc[-1]
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
    
    return {
        "Precio": precio_actual,
        "SMA50": sma50,
        "SMA200": sma200,
        "RSI": rsi,
        "Max52w": max_52w,
        "VolMedio": vol_medio,
        "Cambio": df['Close'].pct_change().iloc[-1] * 100
    }

# --- CONFIGURACIÓN SIDEBAR ---
st.sidebar.title("Navegación")
modo = st.sidebar.radio("Seleccionar Modo:", ["Individual", "Análisis por Listas"])

listas_seguimiento = {
    "Tecnología": ["AAPL", "NVDA", "MSFT", "TSLA", "GOOGL"],
    "Semicond": ["ASML", "AMD", "AVGO", "ARM"],
    "Banca": ["JPM", "GS", "V", "MA"]
}

# --- MODO INDIVIDUAL ---
if modo == "Individual":
    st.title("🔍 Análisis Detallado")
    ticker_input = st.text_input("Introduce Ticker (ej: NVDA):", "TSLA").upper()
    
    if st.button("Analizar"):
        t = yf.Ticker(ticker_input)
        df = t.history(period="1y")
        m = calcular_metricas(df)
        
        if m:
            # Fila 1: Métricas principales
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Precio Actual", f"${m['Precio']:.2f}", f"{m['Cambio']:.2f}%")
            c2.metric("RSI (14d)", f"{m['RSI']:.2f}", "Sobrecompra >70" if m['RSI']>70 else "")
            c3.metric("Dist. Media 200", f"{((m['Precio']/m['SMA200'])-1)*100:.2f}%")
            c4.metric("Dist. Máximo 52s", f"{((m['Precio']/m['Max52w'])-1)*100:.2f}%")
            
            # Fila 2: Información Extra
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Gráfico de Precio")
                st.line_chart(df['Close'])
            with col_b:
                st.subheader("Datos Técnicos Extra")
                info_extra = {
                    "Media 50 días": f"${m['SMA50']:.2f}",
                    "Volumen Medio (20d)": f"{m['VolMedio']:,.0f}",
                    "Rango Día (Low-High)": f"${df['Low'].iloc[-1]:.2f} - ${df['High'].iloc[-1]:.2f}",
                    "Cierre Anterior": f"${df['Close'].iloc[-2]:.2f}"
                }
                st.json(info_extra)
        else:
            st.error("No se encontraron datos para ese Ticker.")

# --- MODO LISTAS ---
else:
    st.title("📊 Momentum de Listas")
    lista_sel = st.sidebar.selectbox("Elige tu lista:", list(listas_seguimiento.keys()))
    
    if st.button(f"Analizar Lista {lista_sel}"):
        resultados = []
        bar = st.progress(0)
        for i, t_name in enumerate(listas_seguimiento[lista_sel]):
            df_t = yf.Ticker(t_name).history(period="1y")
            m_t = calcular_metricas(df_t)
            if m_t:
                resultados.append({
                    "Ticker": t_name,
                    "Precio": round(m_t['Precio'], 2),
                    "RSI": round(m_t['RSI'], 2),
                    "vs Media 50": f"{((m_t['Precio']/m_t['SMA50'])-1)*100:.2f}%",
                    "vs Media 200": f"{((m_t['Precio']/m_t['SMA200'])-1)*100:.2f}%",
                    "Estado": "🔥 Fuerte" if m_t['RSI'] > 60 else ("❄️ Débil" if m_t['RSI'] < 40 else "⚖️ Neutro")
                })
            bar.progress((i+1)/len(listas_seguimiento[lista_sel]))
        
        st.table(pd.DataFrame(resultados))
