import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# 1. Configuración inicial de la plataforma (Obligatorio en la primera línea)
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# --- TITULO PRINCIPAL ---
st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# Inicializar las listas y el almacenamiento de la cartera en el estado de la sesión
if "listas_guardadas" not in st.session_state:
    st.session_state.listas_guardadas = {
        "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "AVGO", "MRVL", "TSMC"],
        "Robótica Pura y Satélites": [
            "ISRG", "ZBH", "STE", "ROK", "CGNX", "TER", 
            "ATS", "SYM", "GWW", "AME", "ADI", "FTV", "KEYS", "PTC", 
            "ANSS", "ROCK", "COHR", "DE", "CAT", "AVAV", "GE", "HON",
            "NVDA", "AMD", "ARM", "AVGO", "MRVL",
            "SNPS", "CDNS", "ANSS", "SPLK",
            "SYK", "MDT", "BSX"
        ],
        "Fotónica y Sensores": ["IPGP", "LITE", "COHR", "CGNX"],
        "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR", "NVDA"]
    }

if "cartera_compras" not in st.session_state:
    st.session_state.cartera_compras = pd.DataFrame()

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# --- FUNCIÓN AUXILIAR: COMPROBAR HORARIO DE WALL STREET ---
def comprobar_mercado_abierto():
    tz_ny = pytz.timezone('America/New_York')
    hora_ny = datetime.now(tz_ny)
    dia_semana = hora_ny.weekday()
    inicio_mercado = hora_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    fin_mercado = hora_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    if dia_semana <= 4 and inicio_mercado <= hora_ny <= fin_mercado:
        return True
    return False

# --- FUNCIÓN OPTIMIZADA CON CACHÉ PARA OBTENER INFO CLAVE DE YFINANCE ---
@st.cache_data(ttl=300)  # Guarda la info 5 minutos para evitar bloqueos de IP
def obtener_info_segura(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        target = info.get('targetMedianPrice', None)
        dy = info.get('dividendYield', None)
        return target, dy
    except:
        return None, None

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente y Maduración Trimestral")
    st.write("El bot aplica un embudo estricto: Crecimiento negocio (**>20%**), Tendencia Institucional (**>Media 200D**), rastreo de volumen y candado de **3 meses**.")

    mercado_activo = comprobar_mercado_abierto()
    if mercado_activo:
        st.success("🟢 MERCADO ABIERTO: Las operaciones simuladas se ejecutarán con precios e impacto en vivo.")
    else:
        st.warning("🕒 MERCADO CERRADO (Wall Street): El bot analizará el mercado con los últimos precios vivos disponibles.")

    st.write("#### 🛡️ Reglas de Gestión Monetaria y Control de Riesgo")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        max_por_accion = st.number_input("Capital fijo por operación (€):", min_
