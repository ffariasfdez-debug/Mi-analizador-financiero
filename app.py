import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# 1. Configuración obligatoria de la página (Siempre al principio)
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# 2. Título Principal
st.title("📊 Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# 3. Tu Diccionario Maestro de Activos
mis_listas_limpias = {
    "Robótica": [
        "ISRG", "CGNX", "ADI", "AME", "ROCK", "ROK", "TER", "FTV", "NOW", "PTC",
        "ANSS", "GWW", "SYM", "PATH", "AZTA", "ESTC", "NXPI", "TXN", "ON", "A",
        "SIE.DE", "SU.PA", "ABB", "SCHN.PA", "KRN.DE", "TRMB", "AZO", "GFL"
    ]
}

# 4. Datos de tus posiciones para el Proyecto (Precios medios y cantidades)
datos_compra = {
    "NOW": {"precio_medio": 85.0, "cantidad": 10},
    # Aquí puedes ir añadiendo tus otros activos comprados siguiendo el mismo formato
}

# 5. Sección de Análisis Individual
st.header("🔍 Análisis Detallado Individual")
st.write("Introduce el Ticker de la acción para generar Gráficos y Diagnósticos:")

# Cuadro de texto fijo para buscar el activo
ticker_input = st.text_input("Ticker del Activo:", value="NOW").upper().strip()

if ticker_input:
    try:
        # Descarga de datos históricos de mercado (Último mes)
        datos_ticker = yf.Ticker(ticker_input)
        hist = datos_ticker.history(period="1mo")
        
        if not hist.empty:
            precio_actual = float(hist['Close'].iloc[-1])
            
            # Si el activo está en tu cartera, calcula semáforo, consejo y KPIs
            if ticker_input in datos_compra:
                precio_compra = datos_compra[ticker_input]["precio_medio"]
                cantidad_acciones = datos_compra[ticker_input]["cantidad"]
                
                rendimiento_porcentaje = ((precio_actual - precio_compra) / precio_compra) * 100
                rendimiento_absoluto = (precio_actual - precio_compra) * cantidad_acciones
                
                # Lógica del Semáforo y el Consejo Dinámico
                if rendimiento_porcentaje > 2.0:
                    semaforo_color, semaforo_texto = "🟢", "ÓPTIMO / GANANCIAS"
                    consejo_texto = f"El activo responde positivamente situándose un **{rendimiento_porcentaje:.2f}%** por encima de tu precio de entrada. Mantener para el objetivo del proyecto a largo plazo."
                elif -2.0 <= rendimiento_porcentaje <= 2.0:
                    semaforo_color, semaforo_texto = "🟡", "NEUTRAL / CONSOLIDACIÓN"
                    consejo_texto = "El activo se mantiene estable en zona de soporte lateral. Comportamiento en rango de consolidación esperado."
                else:
                    semaforo_color, semaforo_texto = "🔴", "ALERTA / PÉRDIDAS"
                    consejo_texto = f"Posición en pérdidas temporales (**{rendimiento_porcentaje:.2f}%**). Evaluar soportes clave por si el plan a largo plazo aconseja acumulación."
                
                # Renderizado de Tarjetas de Estado
                st.markdown(f"### {semaforo_color} Estado: {semaforo_texto}")
                st.info(f"💡 **Consejo Dinámico:** {consejo_texto}")
                st.write("---")
                
                # Renderizado de Métricas Numéricas (KPIs)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Participaciones", f"{cantidad_acciones} ud")
                with col2:
                    st.metric("Precio Actual", f"{precio_actual:.2f} €", f"Tu coste: {precio_compra:.2f} €")
                with col3:
                    st.metric("Rendimiento (%)", f"{rendimiento_porcentaje:.2f} %")
                with col4:
                    st.metric("Beneficio Neto Total", f"{rendimiento_absoluto:.2f} €")
            else:
                st.warning("⚠️ Activo de mercado general (Fuera de cartera). Mostrando datos de cotización estándar.")
            
            st.write("---")
            
            # El Gráfico de Cotización con escala real e intacta
            st.write(f"**Evolución del precio de {ticker_input} (Último mes):**")
            grafico_limpio = pd.DataFrame(hist['Close'])
            st.line_chart(grafico_limpio)
            
        else:
            st.error(f"No se han encontrado datos en Yahoo Finance para el ticker: {ticker_input}")
            
    except Exception as e:
        st.error(f"Error al procesar el activo: {e}")
