import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import json

# 1. Configuración inicial
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

ARCHIVO_CARTERA = "cartera_guardada.csv"
ARCHIVO_LISTAS = "listas_permanentes.json"

# --- DEFINICIÓN DE PESTAÑAS (DEBE ESTAR AL NIVEL PRINCIPAL) ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Configuración de Listas"
])

# --- LÓGICA DE PERSISTENCIA ---
if "listas_guardadas" not in st.session_state:
    if os.path.exists(ARCHIVO_LISTAS):
        with open(ARCHIVO_LISTAS, "r") as f:
            st.session_state.listas_guardadas = json.load(f)
    else:
        st.session_state.listas_guardadas = {"Robótica": ["ARM", "AVGO", "MRVL"]}

if "cartera_compras" not in st.session_state:
    if os.path.exists(ARCHIVO_CARTERA):
        st.session_state.cartera_compras = pd.read_csv(ARCHIVO_CARTERA)
    else:
        st.session_state.cartera_compras = pd.DataFrame()

# --- FUNCIÓN DE DESCARGA MASIVA (Solución al RateLimitError) ---
@st.cache_data(ttl=3600)
def obtener_precios_masivos(lista_tickers):
    if not lista_tickers: return {}
    # Descarga todos los tickers en UNA sola petición
    datos = yf.download(lista_tickers, period="5d", group_by="ticker", progress=False)
    precios = {}
    for tick in lista_tickers:
        try:
            # Obtiene el último precio de cierre disponible
            if tick in datos.columns.levels[0]:
                precios[tick] = float(datos[tick]['Close'].iloc[-1])
            else:
                precios[tick] = 0.0
        except:
            precios[tick] = 0.0
    return precios

# --- PESTAÑA 1 ---
with pestaña1:
    st.subheader("🤖 Bot Masivo")
    
    if st.button("🔄 Ejecutar Análisis de Cartera"):
        lista_activos = st.session_state.listas_guardadas.get("Robótica", [])
        # Ejemplo: lógica simple de llenado
        nuevas_posiciones = []
        for tick in lista_activos:
            nuevas_posiciones.append({
                "Ticker": tick,
                "Acciones": 1.0,
                "Precio Entrada Base": 100.0, # Ajusta según tu lógica
                "Moneda": "USD" if not tick.endswith(('.AS', '.DE')) else "EUR"
            })
        st.session_state.cartera_compras = pd.DataFrame(nuevas_posiciones)
        st.session_state.cartera_compras.to_csv(ARCHIVO_CARTERA, index=False)
        st.rerun()

    # Visualización con datos masivos
    if not st.session_state.cartera_compras.empty:
        df = st.session_state.cartera_compras.copy()
        lista_tickers = df["Ticker"].unique().tolist()
        precios_vivos = obtener_precios_masivos(lista_tickers)
        
        pnl_list = []
        for _, row in df.iterrows():
            p_live = precios_vivos.get(row['Ticker'], row['Precio Entrada Base'])
            ganancia = (p_live - row['Precio Entrada Base']) * row['Acciones']
            pnl_list.append(f"{ganancia:.2f} {row['Moneda']}")
            
        df["Rendimiento (P&L)"] = pnl_list
        st.dataframe(df, use_container_width=True)
    else:
        st.info("La cartera está vacía.")

# --- PESTAÑA 2 Y 3 ---
with pestaña2:
    st.write("Analizador Técnico...")

with pestaña3:
    st.write("Configuración de listas...")
