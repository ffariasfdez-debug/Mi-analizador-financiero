import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import os
import json

# Configuración inicial
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

ARCHIVO_CARTERA = "cartera_guardada.csv"
ARCHIVO_LISTAS = "listas_permanentes.json"

# --- LÓGICA DE PERSISTENCIA ---
if "listas_guardadas" not in st.session_state:
    if os.path.exists(ARCHIVO_LISTAS):
        with open(ARCHIVO_LISTAS, "r") as f:
            st.session_state.listas_guardadas = json.load(f)
    else:
        st.session_state.listas_guardadas = {
            "Semiconductores": ["ASM.AS", "NVDA", "AMD", "ASML"],
            "Robótica": ["ISRG", "DE", "ROK", "CGNX"]
        }

# --- FUNCIONES DE MERCADO ---
def identificar_mercado(ticker):
    t = str(ticker).upper()
    if t.endswith(".AS"): return "Euronext Ámsterdam", "EUR (€)"
    if t.endswith(".DE"): return "Xetra Alemania", "EUR (€)"
    if t.endswith(".MC"): return "Bolsa Madrid", "EUR (€)"
    return "Wall Street (EE.UU.)", "USD ($)"

def obtener_datos(tickers_list):
    """Obtiene datos de Yahoo Finance para una lista de tickers."""
    datos = yf.download(" ".join(tickers_list), period="1y", group_by="ticker", progress=False)
    return datos

# --- INTERFAZ ---
st.title("🎛️ Centro de Mando Financiero Pro")

tab1, tab2, tab3 = st.tabs(["🤖 Bot Masivo", "🔍 Analizador Técnico", "⚙️ Configuración"])

with tab1:
    st.subheader("🤖 Ejecución de Embudo")
    cap = st.number_input("Capital por operación (€):", 100, 5000, 1000)
    
    if st.button("🔄 Ejecutar Análisis"):
        lista_activos = st.session_state.listas_guardadas.get(list(st.session_state.listas_guardadas.keys())[0], [])
        
        # Procesamiento
        resultados = []
        for tick in lista_activos:
            mercado, divisa = identificar_mercado(tick)
            # Aquí podrías añadir la lógica de medias móviles (SMA 50/200)
            resultados.append({
                "Ticker": tick,
                "Plaza": mercado,
                "Divisa": divisa,
                "Inversión": cap
            })
            
        st.session_state.cartera_compras = pd.DataFrame(resultados)
        st.success("Análisis completado")
        st.dataframe(st.session_state.cartera_compras)

with tab2:
    st.subheader("🔍 Análisis Estructural")
    # Aquí incluirías el gráfico de líneas y las medias móviles
    st.write("Selecciona un activo para ver su estructura técnica.")

with tab3:
    st.subheader("⚙️ Configuración de Listas")
    # Panel de edición de tickers
    lista_edit = st.selectbox("Lista a editar:", list(st.session_state.listas_guardadas.keys()))
    nuevo_t = st.text_input("Añadir ticker:")
    if st.button("Guardar"):
        st.session_state.listas_guardadas[lista_edit].append(nuevo_t.upper())
        with open(ARCHIVO_LISTAS, "w") as f:
            json.dump(st.session_state.listas_guardadas, f)
        st.rerun()
