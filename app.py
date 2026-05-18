import streamlit as st
import pandas as pd

# Configuración principal de la aplicación
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

st.title("🎛️ Centro de Mando Financiero")
st.subheader("🤖 Bot Masivo Automático 30k")
st.write("### 📊 Algoritmo de Gestión Autónoma por Momentum Técnico")

# Exclusiones
exclusiones = st.text_input("Acciones a excluir del radar de compra (ej: NVDA, ASML):", "")

# --- DATOS DE LA SIMULACIÓN ---
if 'caja' not in st.session_state:
    st.session_state.caja = 22000.00
if 'capital_invertido' not in st.session_state:
    st.session_state.capital_invertido = 8000.00

# Base de datos de las compras del 18-05-2026
# Añadimos los Precios Actuales ficticios para el cálculo del rendimiento en vivo
datos_compras = [
    {"Fecha/Hora": "2026-05-18 14:38:46", "Ticker": "ASM.AS", "Precio Ejecución": 852.00, "Precio Actual": 855.10, "Capital Invertido": 2000.0, "RSI": 53.1000, "Motivo Tipo": "MOMENTUM MÁXIMO (2k)", "Canal": "Bolero / Rev"},
    {"Fecha/Hora": "2026-05-18 14:38:52", "Ticker": "KLAC", "Precio Ejecución": 1755.30, "Precio Actual": 1748.20, "Capital Invertido": 2000.0, "RSI": 45.9000, "Motivo Tipo": "MOMENTUM MÁXIMO (2k)", "Canal": "Bolero / Rev"},
    {"Fecha/Hora": "2026-05-18 14:39:01", "Ticker": "TFX", "Precio Ejecución": 133.32, "Precio Actual": 134.10, "Capital Invertido": 1000.0, "RSI": 47.1000, "Motivo Tipo": "PRUDENTE (Freno de Mano 1k)", "Canal": "Bolero / Rev"},
    {"Fecha/Hora": "2026-05-18 14:39:07", "Ticker": "AME", "Precio Ejecución": 227.10, "Precio Actual": 228.30, "Capital Invertido": 1000.0, "RSI": 47.7000, "Motivo Tipo": "PRUDENTE BASE (1k)", "Canal": "Bolero / Rev"},
    {"Fecha/Hora": "2026-05-18 14:39:16", "Ticker": "MPWR", "Precio Ejecución": 1514.83, "Precio Actual": 1502.10, "Capital Invertido": 2000.0, "RSI": 50.8000, "Motivo Tipo": "MOMENTUM MÁXIMO (2k)", "Canal": "ING España"}
]

# Crear el cuadro con los nuevos cálculos automáticos
df = pd.DataFrame(datos_compras)

# MATEMÁTICAS AUTOMÁTICAS:
# 1. Cantidad de títulos comprados
df["Cantidad (Títulos)"] = (df["Capital Invertido"] / df["Precio Ejecución"]).round(4)
# 2. Rendimiento porcentual
df["Rendimiento (%)"] = (((df["Precio Actual"] - df["Precio Ejecución"]) / df["Precio Ejecución"]) * 100).round(2)

# Formatear el rendimiento para mostrarlo visualmente con flechas
df["Rendimiento (%)"] = df["Rendimiento (%)"].apply(lambda x: f"🔼 +{x}%" if x >= 0 else f"🔽 {x}%")

# Reordenar columnas para que queden perfectas en pantalla
columnas_ordenadas = [
    "Fecha/Hora", "Ticker", "Cantidad (Títulos)", "Precio Ejecución", 
    "Precio Actual", "Capital Invertido", "Rendimiento (%)", "RSI", "Motivo Tipo", "Canal"
]
df = df[columnas_ordenadas]

# --- RENDERIZADO EN LA PÁGINA WEB ---
st.write("### 📋 Libro de Registro de Posiciones")
col1, col2, col3 = st.columns(3)
col1.metric("Fondo Estrategia", "30.000 €")
col2.metric("Caja Líquida", f"{st.session_state.caja:,.2f} €")
col3.metric("Posiciones Abiertas", "5")

# Mostrar la tabla estilizada en tu pantalla
st.dataframe(df.style.set_properties(**{'background-color': '#1e293b', 'color': 'white'}), use_container_width=True)

if st.button("Resetear Cuenta de Simulación"):
    st.success("Simulación reiniciada.")
                     
     
