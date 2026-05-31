import streamlit as st
import pandas as pd
import yfinance as yf
import time

# --- FUNCIÓN OPTIMIZADA (SIN .info) ---
@st.cache_data(ttl=3600)
def obtener_datos_eficientes(lista_tickers):
    """
    Descarga datos de toda la lista en una sola petición.
    Es mucho más rápido y evita el error de rate limit.
    """
    # Descargamos solo lo necesario: el último precio de cierre
    datos = yf.download(lista_tickers, period="5d", group_by="ticker", progress=False)
    
    resultados = {}
    for tick in lista_tickers:
        try:
            # Si hay datos para el ticker, obtenemos el último precio
            if tick in datos.columns.levels[0]:
                precio = datos[tick]['Close'].iloc[-1]
            else:
                # Fallback simple si la descarga masiva falla para un ticker específico
                precio = yf.Ticker(tick).history(period="1d")['Close'].iloc[-1]
            
            resultados[tick] = float(precio)
        except:
            resultados[tick] = 0.0
            
    return resultados

# --- EN TU BUCLE DE LA CARTERA ---
# EN LUGAR DE LLAMAR A UNA FUNCIÓN POR TICKER:
# for ticker in lista:
#    p_live = obtener_info_financiera(ticker) -> ¡ESTO ES LO QUE DA ERROR!

# HAZ ESTO:
lista_tickers = df_mostrar["Ticker"].unique().tolist()
precios_vivos = obtener_datos_eficientes(lista_tickers)

# Y luego simplemente accedes al diccionario:
# p_live = precios_vivos.get(ticker, p_entrada)
