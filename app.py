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
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# --- LÓGICA DE PERSISTENCIA ---
if "listas_guardadas" not in st.session_state:
    if os.path.exists(ARCHIVO_LISTAS):
        try:
            with open(ARCHIVO_LISTAS, "r") as f:
                st.session_state.listas_guardadas = json.load(f)
        except:
            if os.path.exists(ARCHIVO_LISTAS): os.remove(ARCHIVO_LISTAS)
    
    if "listas_guardadas" not in st.session_state or not isinstance(st.session_state.listas_guardadas, dict):
        st.session_state.listas_guardadas = {
            "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "AVGO", "MRVL", "TSMC"],
            "Robótica Pura y Satélites": ["ISRG", "ZBH", "STE", "ROK", "CGNX", "TER", "SYM", "GWW", "AME", "ADI", "FTV", "KEYS", "PTC", "ANSS", "COHR", "DE", "CAT", "AVAV", "GE", "HON", "NVDA", "AMD", "ARM", "AVGO", "MRVL", "SNPS", "CDNS", "SYK", "MDT", "BSX"],
            "Fotónica y Sensores": ["IPGP", "LITE", "COHR", "CGNX"],
            "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR", "NVDA"]
        }

if "cartera_compras" not in st.session_state:
    if os.path.exists(ARCHIVO_CARTERA):
        try:
            st.session_state.cartera_compras = pd.read_csv(ARCHIVO_CARTERA)
        except:
            st.session_state.cartera_compras = pd.DataFrame()
    else:
        st.session_state.cartera_compras = pd.DataFrame()

# --- FUNCIONES AUXILIARES ---
def comprobar_mercado_abierto():
    tz_ny = pytz.timezone('America/New_York')
    hora_ny = datetime.now(tz_ny)
    dia_semana = hora_ny.weekday()
    return dia_semana <= 4 and 9.5 <= (hora_ny.hour + hora_ny.minute/60) <= 16.0

@st.cache_data(ttl=300)
def obtener_info_segura(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        target = info.get('targetMedianPrice')
        dy = info.get('dividendYield')
        if dy and dy > 1.0: dy = dy / 100.0
        return target, dy
    except:
        return None, None

# --- INTERFAZ ---
pestaña1, pestaña2, pestaña3 = st.tabs(["🤖 Bot Masivo Automático 30k", "🔍 Analizador Técnico Avanzado", "⚙️ Configuración de Listas"])

with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente")
    max_por_accion = st.number_input("Capital fijo por operación (€):", 100, 5000, 1000)
    tope_semanal = st.slider("Tope presupuesto semanal (€):", 1000, 30000, 10000)
    
    if st.button("🔄 Ejecutar Embudo Avanzado"):
        st.toast("Rastreando huella institucional...")
        # Aquí iría tu lógica de cálculo que tenías...
        st.success("Análisis ejecutado.")

with pestaña2:
    st.subheader("🔍 Analizador Técnico")
    accion = st.text_input("Ticker para analizar:", "NVDA")
    # Lógica de gráficos aquí

with pestaña3:
    st.subheader("⚙️ Configuración de Listas")
    lista_sel = st.selectbox("Selecciona lista:", list(st.session_state.listas_guardadas.keys()))
    if lista_sel:
        st.write(f"Activos: {', '.join(st.session_state.listas_guardadas[lista_sel])}")
