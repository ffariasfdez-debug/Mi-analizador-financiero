import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Analizador de Inversión", layout="wide")

def obtener_datos(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="2y", interval="1d") # 2 años para mejor contexto
        if df.empty: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Indicadores de Largo Plazo
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        
        # RSI para Momentum
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    except:
        return None

# --- SIDEBAR COMPACTO ---
st.sidebar.header("Configuración")
ticker_input = st.sidebar.text_input("Ticker:", "TSLA").upper()
btn = st.sidebar.button("Actualizar Análisis")

if btn:
    data = obtener_datos(ticker_input)
    if data is not None:
        precio_act = data['Close'].iloc[-1]
        sma200 = data['SMA200'].iloc[-1]
        rsi_act = data['RSI'].iloc[-1]

        st.title(f"🔍 Evaluación de Inversión: {ticker_input}")

        # --- FILA DE MÉTRICAS (Pequeñas) ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precio", f"${precio_act:.2f}")
        c2.metric("RSI (Fuerza)", f"{rsi_act:.1f}")
        c3.metric("Media 200d", f"${sma200:.2f}")
        distancia_sma200 = ((precio_act - sma200) / sma200) * 100
        c4.metric("Sobre Media 200", f"{distancia_sma200:.1f}%")

        # --- LÓGICA DE INVERSIÓN (Sustituye al cartel de trading) ---
        if precio_act > sma200:
            estado = "Tendencia de Fondo Alcista (Sólida)"
            color = "#1E88E5" # Azul Inversión
            if rsi_act > 70:
                consejo = "Activo en zona de euforia. Para medio plazo: MANTENER, pero evitar nuevas compras hasta que el RSI baje de 50."
            else:
                consejo = "Buen momento para mantener o buscar entradas si el precio se acerca a la Media 50."
        else:
            estado = "Tendencia de Fondo Bajista"
            color = "#E53935" # Rojo
            consejo = "El activo cotiza bajo su media de 200 días. Riesgo elevado para largo plazo hasta que recupere los niveles actuales."

        st.info(f"**Estado:** {estado} \n\n **Nota:** {consejo}")

        # --- GRÁFICOS (Tamaño reducido) ---
        st.subheader("Gráfico de Largo Plazo (Precio vs Medias 50 y 200)")
        st.line_chart(data[['Close', 'SMA50', 'SMA200']], height=300)

        # Explicación del Momentum (RSI) para inversores
        with st.expander("¿Cómo leer el Momentum (RSI) en tu caso?"):
            st.write("""
            Para un inversor de largo plazo, el RSI no es para vender, sino para **gestionar el tiempo de entrada**:
            - **RSI > 70:** El mercado está muy optimista. Si quieres comprar más, espera a que se enfríe.
            - **RSI < 30:** Hay miedo. Suelen ser las mejores ventanas para entradas de largo plazo si los fundamentales son buenos.
            """)
            st.area_chart(data['RSI'], height=150)
    else:
        st.error("Error al cargar datos.")


