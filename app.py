import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import os
import json

# 1. Configuración inicial
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

ARCHIVO_CARTERA = "cartera_guardada.csv"
ARCHIVO_LISTAS = "listas_permanentes.json"

st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado:** Conectado | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# --- LÓGICA DE PERSISTENCIA ---
if "listas_guardadas" not in st.session_state:
    if os.path.exists(ARCHIVO_LISTAS):
        with open(ARCHIVO_LISTAS, "r") as f:
            st.session_state.listas_guardadas = json.load(f)
    else:
        st.session_state.listas_guardadas = {
            "Semiconductores": ["ASM.AS", "NVDA", "AMD"],
            "Robótica": ["ISRG", "DE", "ROK"]
        }

if "cartera_compras" not in st.session_state:
    if os.path.exists(ARCHIVO_CARTERA):
        st.session_state.cartera_compras = pd.read_csv(ARCHIVO_CARTERA)
    else:
        st.session_state.cartera_compras = pd.DataFrame()

# --- FUNCIONES ---
def identificar_mercado_y_divisa(ticker):
    t = str(ticker).upper()
    if t.endswith(".AS"): return "Euronext Ámsterdam", "EUR (€)"
    if t.endswith(".DE"): return "Xetra Alemania", "EUR (€)"
    if t.endswith(".MC"): return "Bolsa Madrid", "EUR (€)"
    return "Wall Street (EE.UU.)", "USD ($)"

# --- PESTAÑAS ---
pestaña1, pestaña2, pestaña3 = st.tabs(["🤖 Bot", "🔍 Análisis", "⚙️ Listas"])

with pestaña1:
    st.subheader("🤖 Bot Masivo")
    
    # Parámetros simplificados
    max_por_accion = st.number_input("Capital por operación (€):", 100, 5000, 1000)
    tope_semanal = st.slider("Tope semanal (€):", 1000, 30000, 10000)
    
    if st.button("🔄 Ejecutar"):
        nombre_lista = list(st.session_state.listas_guardadas.keys())[0]
        lista_tickers = st.session_state.listas_guardadas[nombre_lista]
        
        posiciones = []
        for tick in lista_tickers:
            # Aquí está la línea 237 corregida de forma compacta
            mercado, divisa = identificar_mercado_y_divisa(tick)
            
            # Simulamos un precio y guardamos
            posiciones.append({
                "Ticker": tick,
                "Plaza Cotización": mercado,
                "Divisa": divisa,
                "Capital Invertido Base": max_por_accion
            })
            
        st.session_state.cartera_compras = pd.DataFrame(posiciones)
        st.session_state.cartera_compras.to_csv(ARCHIVO_CARTERA, index=False)
        st.rerun()

    # --- RENDERIZADO SEGURO ---
    if not st.session_state.cartera_compras.empty:
        df = st.session_state.cartera_compras
        # Filtro de columnas para que no rompa si el CSV es antiguo
        columnas_ideales = ["Ticker", "Plaza Cotización", "Divisa", "Capital Invertido Base"]
        cols = [c for c in columnas_ideales if c in df.columns]
        st.dataframe(df[cols], use_container_width=True)

with pestaña2:
    st.write("Analizador Técnico...")

with pestaña3:
    st.write("Configuración de Listas...")
