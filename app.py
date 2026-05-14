import streamlit as st
import yfinance as yf
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Analizador Financiero", layout="wide")

# --- FUNCIÓN MAESTRA DE CÁLCULO ---
def obtener_datos(ticker):
    try:
        # Usamos Ticker + history porque es el método más estable actualmente
        t = yf.Ticker(ticker)
        df = t.history(period="1y", interval="1d")
        
        if df.empty or len(df) < 50:
            return None
            
        # Limpieza de columnas (importante para evitar errores de visualización)
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Cálculo de Indicadores Básicos
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        
        return df
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return None

# --- BARRA LATERAL ---
st.sidebar.title("🚀 Menú Principal")
modo = st.sidebar.radio("Ir a:", ["🔍 Análisis Individual", "📁 Mis Listas"])
ticker_input = st.sidebar.text_input("Introduce un Ticker (ej: TSLA, AAPL):", "TSLA").upper()
boton = st.sidebar.button("Analizar Ahora")

# --- CUERPO PRINCIPAL ---
st.title("📊 Análisis de Mercado Detallado")

if boton:
    datos = obtener_datos(ticker_input)
    
    if datos is not None:
        st.success(f"Datos de {ticker_input} cargados correctamente")
        st.line_chart(datos['Close'])
        st.subheader("Últimos registros")
        st.dataframe(datos.tail(10))
    else:
        st.error("No se pudo analizar este Ticker. Revisa el nombre o intenta más tarde.")
