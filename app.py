import streamlit as st
import pandas as pd
import yfinance as yf

# --- FUNCIÓN DE DESCARGA MASIVA (Evita RateLimitError) ---
@st.cache_data(ttl=3600)
def obtener_precios_masivos(lista_tickers):
    if not lista_tickers: return {}
    # Descarga todos los tickers en UNA sola petición HTTP
    datos = yf.download(lista_tickers, period="5d", group_by="ticker", progress=False)
    precios = {}
    for tick in lista_tickers:
        try:
            # Extrae el precio de cierre del último día disponible
            if tick in datos.columns.levels[0]:
                precios[tick] = float(datos[tick]['Close'].iloc[-1])
            else:
                precios[tick] = 0.0
        except:
            precios[tick] = 0.0
    return precios

# --- PESTAÑA 1 (Integración de la corrección) ---
with pestaña1:
    # ... (tu lógica de botones de arriba)

    # 1. Aseguramos que df_mostrar exista SIEMPRE
    if "cartera_compras" in st.session_state and not st.session_state.cartera_compras.empty:
        df_mostrar = st.session_state.cartera_compras.copy()
    else:
        df_mostrar = pd.DataFrame()

    # 2. Solo si hay datos, procedemos a calcular
    if not df_mostrar.empty:
        lista_tickers = df_mostrar["Ticker"].unique().tolist()
        
        # Llamada única a Yahoo Finance para toda la cartera
        precios_vivos = obtener_precios_masivos(lista_tickers)

        lista_pnl = []
        for _, fila in df_mostrar.iterrows():
            ticker = fila["Ticker"]
            p_entrada = fila["Precio Entrada Base"]
            n_acciones = fila["Acciones"]
            
            # Obtenemos precio de nuestro diccionario masivo
            p_live = precios_vivos.get(ticker, p_entrada)
            
            # Cálculo de rendimiento
            ganancia_euros = (p_live - p_entrada) * n_acciones
            ganancia_pct = ((p_live - p_entrada) / p_entrada) * 100 if p_entrada > 0 else 0
            
            if ganancia_euros > 0:
                lista_pnl.append(f"🟩 +{ganancia_euros:.2f} € (+{ganancia_pct:.2f}%)")
            elif ganancia_euros < 0:
                lista_pnl.append(f"🟥 {ganancia_euros:.2f} € ({ganancia_pct:.2f}%)")
            else:
                lista_pnl.append(f"⬜ 0.00 € (0.00%)")

        df_mostrar["Rendimiento Actual (P&L)"] = lista_pnl
        # ... (resto de tu código de visualización)
        st.dataframe(df_mostrar)
    else:
        st.info("La cartera está vacía o no hay datos para mostrar.")
