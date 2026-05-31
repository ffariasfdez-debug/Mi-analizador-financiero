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
st.write(f"**Estado del Sistema:** Sincronización Inteligente | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# --- LÓGICA DE PERSISTENCIA ---
if "listas_guardadas" not in st.session_state:
    if os.path.exists(ARCHIVO_LISTAS):
        with open(ARCHIVO_LISTAS, "r") as f:
            st.session_state.listas_guardadas = json.load(f)
    else:
        st.session_state.listas_guardadas = {"Robótica Pura y Satélites": ["ARM", "AVGO", "MRVL"]}

if "cartera_compras" not in st.session_state:
    if os.path.exists(ARCHIVO_CARTERA):
        st.session_state.cartera_compras = pd.read_csv(ARCHIVO_CARTERA)
    else:
        st.session_state.cartera_compras = pd.DataFrame()

# --- FUNCIONES DE SOPORTE ---
def obtener_moneda(ticker):
    """Detecta la moneda basada en el sufijo del ticker o por defecto USD."""
    if ticker.endswith(('.AS', '.DE', '.PA', '.MC')): return "EUR"
    return "USD"

@st.cache_data(ttl=600)
def obtener_info_financiera(ticker):
    t = yf.Ticker(ticker)
    info = t.info
    # Fallback a último cierre si el precio actual falla
    hist = t.history(period="5d")
    p_actual = hist['Close'].iloc[-1] if not hist.empty else 0
    target = info.get('targetMedianPrice', p_actual * 1.2)
    dy = info.get('dividendYield', 0)
    return p_actual, target, dy if dy else 0

# --- PESTAÑAS ---
pestaña1, pestaña2, pestaña3 = st.tabs(["🤖 Bot Masivo", "🔍 Analizador", "⚙️ Configuración"])

with pestaña1:
    st.subheader("🤖 Ejecución y Seguimiento")
    
    if st.button("🔄 Ejecutar Análisis"):
        # Lógica de compra simplificada con moneda
        lista_activos = st.session_state.listas_guardadas.get("Robótica Pura y Satélites", [])
        nuevas_posiciones = []
        for tick in lista_activos:
            p_act, _, _ = obtener_info_financiera(tick)
            moneda = obtener_moneda(tick)
            nuevas_posiciones.append({
                "Ticker": tick,
                "Acciones": 1.0,
                "Precio Entrada": p_act,
                "Moneda": moneda,
                "Capital": p_act
            })
        st.session_state.cartera_compras = pd.DataFrame(nuevas_posiciones)
        st.session_state.cartera_compras.to_csv(ARCHIVO_CARTERA, index=False)
        st.rerun()

    # Muestra de Cartera Corregida
    if not st.session_state.cartera_compras.empty:
        df = st.session_state.cartera_compras.copy()
        
        # Calcular P&L con precio de cierre si mercado cerrado
        pnl_list = []
        for _, row in df.iterrows():
            ticker = row['Ticker']
            p_entrada = row['Precio Entrada']
            p_live, _, _ = obtener_info_financiera(ticker)
            
            # Si el mercado está cerrado, p_live ya es el último cierre gracias a yfinance
            ganancia = (p_live - p_entrada) * row['Acciones']
            pnl_list.append(f"{ganancia:.2f} {row['Moneda']}")
            
        df["Rendimiento (P&L)"] = pnl_list
        st.dataframe(df, use_container_width=True)

# [El resto de la lógica de las pestañas 2 y 3 permanece igual...]
