import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Scanner de Listas", page_icon="🗂️", layout="wide")

st.title("📂 Mis Listas de Seguimiento")
st.markdown("Selecciona una pestaña para analizar todos los activos de esa lista al instante.")

# 2. Definición de tus listas pregrabadas (Edita los tickers aquí)
listas = {
    "🚀 Tecnología": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META"],
    "💰 Dividendos": ["KO", "PEP", "JNJ", "PG", "MMM"],
    "🌐 Cripto & Otros": ["BTC-USD", "ETH-USD", "TSLA", "AMD"]
}

# 3. Creación de las pestañas en la interfaz
tabs = st.tabs(listas.keys())

# Lógica para cada pestaña
for i, (nombre_lista, tickers) in enumerate(listas.items()):
    with tabs[i]:
        st.subheader(f"Analizando: {nombre_lista}")
        
        if st.button(f"Ejecutar Análisis de {nombre_lista}", key=f"btn_{i}"):
            resultados = []
            progreso = st.progress(0)
            
            for index, ticker in enumerate(tickers):
                try:
                    df = yf.download(ticker, period="1y", interval="1d", progress=False)
                    
                    if not df.empty and len(df) > 50:
                        # Limpiar columnas para evitar errores de Yahoo
                        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
                        
                        # Cálculos Técnicos
                        df['SMA50'] = df['Close'].rolling(window=50).mean()
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi_act = 100 - (100 / (1 + rs.iloc[-1]))
                        
                        precio_act = float(df['Close'].iloc[-1])
                        sma50_act = float(df['SMA50'].iloc[-1])
                        
                        # Lógica de Veredicto
                        if precio_act > sma50_act:
                            if rsi_act > 70: veredicto = "🟡 MANTENER (Sobrecompra)"
                            else: veredicto = "🟢 COMPRA"
                        else:
                            veredicto = "🔴 ESPERAR (Bajista)"
                        
                        resultados.append({
                            "Activo": ticker,
                            "Precio": f"${precio_act:.2f}",
                            "RSI": f"{rsi_act:.2f}",
                            "Estado": veredicto
                        })
                except:
                    continue
                progreso.progress((index + 1) / len(tickers))
            
            # Mostrar Tabla de Resultados
            if resultados:
                df_resumen = pd.DataFrame(resultados)
                
                # Aplicar color a la columna Estado
                def color_estado(val):
                    if "🟢" in val: return 'background-color: #d4edda; color: #155724'
                    if "🔴" in val: return 'background-color: #f8d7da; color: #721c24'
                    return 'background-color: #fff3cd; color: #856404'

                st.table(df_resumen)
                st.success(f"Análisis de {nombre_lista} completado.")
            else:
                st.error("No se pudieron cargar los datos.")
