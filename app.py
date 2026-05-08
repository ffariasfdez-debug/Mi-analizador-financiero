import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Scanner de Listas", page_icon="🗂️", layout="wide")

st.title("📂 Mis Listas de Seguimiento")
st.markdown("Selecciona una lista en el menú lateral para analizar todos sus activos.")

# 2. Definición de tus listas pregrabadas
listas = {
    "🚀 Tecnología": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META"],
    "💰 Dividendos": ["KO", "PEP", "JNJ", "PG", "MMM"],
    "🌐 Cripto & Otros": ["BTC-USD", "ETH-USD", "TSLA", "AMD"]
}

# 3. Selector lateral para las listas
seleccion = st.sidebar.selectbox("Selecciona una lista para analizar:", list(listas.keys()))
tickers = listas[seleccion]
boton = st.sidebar.button(f"Analizar {seleccion}")

if boton:
    resultados = []
    progreso = st.progress(0)
    
    with st.spinner(f'Analizando activos de {seleccion}...'):
        for index, ticker in enumerate(tickers):
            try:
                # Descarga con limpieza de columnas incluida
                df = yf.download(ticker, period="1y", interval="1d", progress=False)
                
                if not df.empty and len(df) > 50:
                    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
                    
                    # Cálculos Técnicos
                    df['SMA50'] = df['Close'].rolling(window=50).mean()
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi_act = 100 - (100 / (1 + rs.iloc[-1]))
                    
                    precio_act = float(df['Close'].iloc[-1])
                    sma50_act = float(df['SMA50'].iloc[-1])
                    
                    # Lógica de Veredicto
                    if precio_act > sma50_act:
                        if rsi_act > 70: veredicto = "🟡 MANTENER (Caro)"
                        else: veredicto = "🟢 COMPRA"
                    else:
                        veredicto = "🔴 ESPERAR (Bajista)"
                    
                    resultados.append({
                        "Activo": ticker,
                        "Precio": f"${precio_act:.2f}",
                        "RSI": f"{rsi_act:.2f}",
                        "Veredicto": veredicto
                    })
            except Exception as e:
                continue
            progreso.progress((index + 1) / len(tickers))
    
    # 4. Mostrar Resultados
    if resultados:
        st.subheader(f"📋 Resultados para {seleccion}")
        df_resumen = pd.DataFrame(resultados)
        st.table(df_resumen)
    else:
        st.error("No se pudieron obtener datos para esta lista.")
