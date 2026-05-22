# 1. Primero las importaciones y la configuración de página
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# 2. El título del sistema
st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# 3. La inicialización del diccionario de listas en segundo plano
if "mis_listas_limpias" not in st.session_state:
    st.session_state.mis_listas_limpias = {
        "Robótica": [
            "ISRG", "CGNX", "ADI", "AME", "ROCK", "ROK", "TER", "FTV", "NOW", "PTC", 
            "ANSS", "GWW", "SYM", "PATH", "AZTA", "ESTC", "NXPI", "TXN", "ON", "A",
            "SIE.DE", "SU.PA", "ABB", "SCHN.PA", "KRN.DE", "TRMB", "AZO", "GFL",
            "6361.T", "6594.T", "6645.T", "6954.T", "6758.T", "6762.T", "6501.T", 
            "7752.T", "4543.T", "7741.T", "4901.T", "6141.T", "6273.T"
        ],
        "Semiconductores": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "TSM", "AVGO", "LRCX", "AMAT"],
        "Fotónica": ["IPGP", "LITE", "COHR", "VNT", "FN", "MKSI", "NKTX", "LIMO"],
        "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR", "CGNX", "ISRG", "COHR"]
    }

# 4. CRUCIAL: Aquí se definen las pestañas antes de usarlas
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico y Fundamental", 
    "⚙️ Panel de Gestión de Listas Maestras"
])

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K
# =========================================================
with pestaña1:
    # (Aquí va tu código original del Bot de 30k con la tabla de ASM.AS, KLAC, etc.)
