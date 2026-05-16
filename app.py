import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="🤖 Bot Gestor Autónomo 30k", layout="wide")

# --- CONFIGURACIÓN DEL UNIVERSO DE INVERSIÓN (10 SLOTS UNIQUE) ---
ESTRUCTURA_CARTERA = {
    "Slot 1: Cómputo IA (Líder)": {"tickers": ["NVDA", "AMD"], "broker": "ING (0% Div)"},
    "Slot 2: Litografía/Equipos": {"tickers": ["ASML", "AMAT", "LRCX"], "broker": "Bolero/Revolut"},
    "Slot 3: Robótica Quirúrgica": {"tickers": ["ISRG", "SYK"], "broker": "Bolero/Revolut"},
    "Slot 4: Automatización Logística": {"tickers": ["SYM", "AZO"], "broker": "ING (0% Div)"},
    "Slot 5: Fotónica y Sensores": {"tickers": ["6861.T", "CGNX"], "broker": "Bolero/Revolut"},
    "Slot 6: Ciberseguridad IA": {"tickers": ["CRWD", "PANW", "NET"], "broker": "ING (0% Div)"},
    "Slot 7: Software de Diseño (EDA)": {"tickers": ["CDNS", "SNPS"], "broker": "ING (0% Div)"},
    "Slot 8: Semiconductores Potencia": {"tickers": ["WOLF", "ON"], "broker": "ING (0% Div)"},
    "Slot 9: Infraestructura Cloud": {"tickers": ["MSFT", "AMZN", "GOOGL"], "broker": "ING (0% Div)"},
    "Slot 10: Especulativo / Autónomo": {"tickers": ["SERV", "AUR", "MBLY"], "broker": "Bolero/Revolut"}
}

# --- MOTOR DE ANÁLISIS TÉCNICO Y FISCAL ---
def analizar_activo(ticker, regla_broker):
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        df = tk.history(period="2y")
        
        if df.empty or len(df) < 200: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Filtro de Dividendos
        dividend_yield = info.get('dividendYield', 0)
        if dividend_yield is None: dividend_yield = 0
        
        # Si es para ING, el dividendo DEBE ser 0%
        if "ING" in regla_broker and dividend_yield > 0:
            return {"estado": "DESCARTADO", "motivo": "Filtro estricto ING: Paga dividendos."}
            
        precio = df['Close'].iloc[-1]
        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # Calcular RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        # Lógica de Compra Exigente
        if precio > sma200 and 45 <= rsi <= 55:
            return {
                "estado": "COMPRAR", "precio": precio, "rsi": rsi, "yield": dividend_yield,
                "motivo": f"Punto óptimo detectado. RSI sano ({rsi:.1f}) y tendencia alcista a largo plazo."
            }
        else:
            return {
                "estado": "ESPERAR", "precio": precio, "rsi": rsi, "yield": dividend_yield,
                "motivo": "Precio extendido o sin fuerza de momentum clara."
            }
    except:
        return None

# --- INTERFAZ DEL USUARIO (CENTRO DE MANDO) ---
st.title("🤖 Tu Asesor Autónomo de Inversión")
st.write("Estrategia de Gestión Activa para un presupuesto maestro de **30.000€** (Max. 3.000€ por posición).")

# Simulación de Estado de Cartera (Esto luego vendrá de la Base de Datos automática)
if 'efectivo' not in st.session_state:
    st.session_state.efectivo = 30000.0
    st.session_state.cartera = {}

# Cuadro de Mandos Superior
c1, c2, c3 = st.columns(3)
c1.metric("Presupuesto Inicial", "30.000 €")
c2.metric("Efectivo Disponible", f"{st.session_state.efectivo:,.2f} €")
c3.metric("Posiciones Activas", f"{len(st.session_state.cartera)} / 10")

st.markdown("---")

# Botón para que el bot empiece a trabajar solo
if st.button("🚀 Activar Escáner Diario del Bot"):
    st.info("El Bot está buceando en los mercados internacionales y aplicando tus reglas...")
    
    reporte_movimientos = []
    
    for slot, configuracion in ESTRUCTURA_CARTERA.items():
        # Si el slot ya está ocupado en nuestra cartera, el bot lo salta (Anti-solape)
        if slot in st.session_state.cartera:
            continue
            
        comprado_en_este_slot = False
        for ticker in configuracion["tickers"]:
            if comprado_en_este_slot: break
            
            analisis = analizar_activo(ticker, configuracion["broker"])
            
            if analisis and analisis["estado"] == "COMPRAR":
                if st.session_state.efectivo >= 3000:
                    # Ejecutar compra virtual
                    precio_compra = analisis["precio"]
                    acciones_compradas = 3000 / precio_compra
                    
                    st.session_state.cartera[slot] = {
                        "Ticker": ticker,
                        "Precio Entrada": precio_compra,
                        "Acciones": round(acciones_compradas, 2),
                        "Broker": configuracion["broker"]
                    }
                    st.session_state.efectivo -= 3000
                    
                    reporte_movimientos.append({
                        "Slot": slot, "Acción": f"COMPRADO {ticker}", 
                        "Broker Destino": configuracion["broker"], "Reseña Técnica": analisis["motivo"]
                    })
                    comprado_en_este_slot = True
            
            elif analisis and analisis["estado"] == "DESCARTADO":
                reporte_movimientos.append({
                    "Slot": slot, "Acción": f"Ignorar {ticker}", 
                    "Broker Destino": configuracion["broker"], "Reseña Técnica": analisis["motivo"]
                })

    if reporte_movimientos:
        st.subheader("📝 Bitácora de Movimientos de Hoy")
        st.table(pd.DataFrame(reporte_movimientos))
    else:
        st.success("💤 El Bot ha analizado el mercado: Todo está muy caro o no cumple los filtros fiscales. Mantenemos el efectivo a salvo.")

# Mostrar Cartera Actual
st.markdown("---")
st.subheader("📊 Mi Cartera Virtual en Tiempo Real")
if st.session_state.cartera:
    df_cartera = pd.DataFrame.from_dict(st.session_state.cartera, orient='index')
    st.table(df_cartera)
else:
    st.write("Tu cartera está en 100% liquidez. Pulsa el botón de arriba para que el Bot busque las primeras entradas.")
