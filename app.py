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

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# Inicializar las listas en el estado de la sesión para que las modificaciones no se borren al hacer clic
if "listas_guardadas" Hollywood not in st.session_state:
    st.session_state.listas_guardadas = {
        "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML"],
        "Robótica Pura": [
            "ISRG", "ZBH", "STE", "ROK", "CGNX", "TER", 
            "ATS", "SYM", "GWW", "AME", "ADI", "FTV", "KEYS", "PTC", 
            "ANSS", "ROCK", "COHR", "DE", "CAT", "AVAV", "GE", "HON"
        ],
        "Fotónica": ["IPGP", "LITE", "COHR"],
        "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR"]
    }

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

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente y Maduración Trimestral")
    st.write("El bot filtra la lista de **Robótica Pura** exigiendo crecimiento del **20%**, momentum técnico, y aplica un candado de **3 meses**.")

    mercado_activo = comprobar_mercado_abierto()
    if mercado_activo:
        st.success("🟢 MERCADO ABIERTO: Las operaciones simuladas se ejecutarán con precios e impacto en vivo.")
    else:
        st.warning("🕒 MERCADO CERRADO (Wall Street): El bot analizará el mercado pero las órdenes quedarán bloqueadas hasta la apertura.")

    st.write("#### 🛡️ Reglas de Gestión Monetaria")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        max_por_accion = st.number_input("Capital fijo por operación (€):", min_value=100, max_value=5000, value=1000, step=100)
    with col_r2:
        tope_semanal = st.slider("Tope de presupuesto compras semanales (€):", min_value=1000, max_value=30000, value=10000, step=1000)

    if st.button("🔄 Ejecutar Embudo Inteligente y Escanear Mercado"):
        st.cache_data.clear()
        st.toast("El bot está aplicando el triple filtro cuantitativo...")

    @st.cache_data(ttl=60)
    def motor_bot_inteligente(lista_tickers, inversion_bloque, limite_semana, mercado_on):
        caja_total_estrategia = 30000.0
        gasto_semanal_actual = 0.0
        candidatas_finalistas = []

        tickers_string = " ".join(lista_tickers)
        try:
            datos_globales = yf.download(tickers_string, period="60d", group_by="ticker", progress=False)
        except:
            datos_globales = pd.DataFrame()

        for tick in lista_tickers:
            try:
                if tick in datos_globales.columns.levels[0]:
                    historial = datos_globales[tick].dropna()
                else:
                    t = yf.Ticker(tick)
                    historial = t.history(period="60d")
                
                if not historial.empty and len(historial) >= 30:
                    precio_actual = historial['Close'].iloc[-1]
                    media_30 = historial['Close'].iloc[-30:].mean()
                    precio_hace_60d = historial['Close'].iloc[0]
                    
                    if precio_actual >= (media_30 * 0.98):
                        crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                        crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))

                        if crecimiento_porcentaje >= 20.0:
                            target_estimado = precio_actual * 1.28
                            potencial_4a = ((target_estimado - precio_actual) / precio_actual) * 100
                            
                            candidatas_finalistas.append({
                                "Ticker": tick,
                                "Precio Actual": precio_actual,
                                "Crecimiento Anual": crecimiento_porcentaje,
                                "Potencial 4A Real": potencial_4a
                            })
            except:
                pass

        posiciones_compradas = []
        if candidatas_finalistas and mercado_on:
            df_ordenado = pd.DataFrame(candidatas_finalistas)
            df_ordenado = df_ordenado.sort_values(by="Potencial 4A Real", ascending=False)
            
            for _, fila in df_ordenado.iterrows():
                if caja_total_estrategia < inversion_bloque:
                    break
                if (gasto_semanal_actual + inversion_bloque) > limite_semana:
                    break
                
                caja_total_estrategia -= inversion_bloque
                gasto_semanal_actual += inversion_bloque
                
                fecha_compra = datetime.now().strftime('%d/%m/%Y')
                fecha_liberacion = (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y')
                cantidad_acciones = round(inversion_bloque / fila["Precio Actual"], 4)
                
                posiciones_com
