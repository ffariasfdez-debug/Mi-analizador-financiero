import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Terminal Financiero", layout="wide")

# --- MENÚ LATERAL DE NAVEGACIÓN ---
st.sidebar.title("🎛️ Centro de Mando")
menu = st.sidebar.radio("Selecciona herramienta:", ["🔍 Escáner Manual", "🤖 Bot Autónomo 30k"])

# --- CÓDIGO COMÚN: ANALÍTICA TÉCNICA ---
def analizar_activo(ticker, regla_broker="Bolero/Revolut"):
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        df = tk.history(period="2y")
        
        if df.empty or len(df) < 200: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        dividend_yield = info.get('dividendYield', 0)
        if dividend_yield is None: dividend_yield = 0
        
        # Filtro estricto para ING
        if "ING" in regla_broker and dividend_yield > 0:
            return {"estado": "DESCARTADO", "motivo": "Filtro ING: Paga dividendos."}
            
        precio = df['Close'].iloc[-1]
        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        if precio > sma200 and 45 <= rsi <= 55:
            estado = "COMPRAR"
            motivo = f"Punto óptimo. RSI sano ({rsi:.1f}) y tendencia alcista."
        else:
            estado = "ESPERAR"
            motivo = "Precio extendido o sin fuerza clara."
            
        return {"estado": estado, "precio": precio, "rsi": rsi, "yield": dividend_yield, "motivo": motivo, "sma200": sma200}
    except:
        return None

# ==========================================
# PASTA 1: EL ESCÁNER MANUAL (TU APP ORIGINAL)
# ==========================================
if menu == "🔍 Escáner Manual":
    st.title("🔍 Escáner Manual de Mercado")
    st.write("Revisa tus listas de seguimiento y analiza puntos de entrada manualmente.")
    
    listas_seguimiento = {
        "Robótica/IA": ["ISRG", "ABB", "6861.T", "SYM", "SERV", "TER", "6954.T", "SYK", "CGNX", "AUR", "MBLY"],
        "Tecnología": ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"],
        "Semicond": ["ASML", "AVGO", "ARM", "SMCI", "MU"]
    }
    
    lista_sel = st.selectbox("Selecciona la lista a escanear:", list(listas_seguimiento.keys()))
    
    if st.button("Ejecutar Análisis de Lista"):
        resultados = []
        for t in listas_seguimiento[lista_sel]:
            res = analizar_activo(t)
            if res:
                resultados.append({
                    "Ticker": t, "Precio": f"{res['precio']:.2f}$", 
                    "RSI": round(res['rsi'], 1), "Estado": res['estado'], "Nota": res['motivo']
                })
        st.table(pd.DataFrame(resultados))

# ==========================================
# PESTAÑA 2: EL BOT AUTÓNOMO DE 30K
# ==========================================
elif menu == "🤖 Bot Autónomo 30k":
    st.title("🤖 Tu Asesor Autónomo de Inversión")
    st.write("Estrategia de Gestión Activa para un presupuesto maestro de **30.000€**.")
    
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
    
    st.sidebar.markdown("---")
    st.sidebar.header("🛡️ Filtro de Cartera Real")
    exclusiones_input = st.sidebar.text_input("Tickers a excluir (ej: NVDA, ASML):", value="").upper()
    lista_exclusiones = [t.strip() for t in exclusiones_input.split(",") if t.strip()]
    
    if 'efectivo' not in st.session_state:
        st.session_state.efectivo = 30000.0
        st.session_state.cartera = {}
        
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuesto Inicial", "30.000 €")
    c2.metric("Efectivo Disponible", f"{st.session_state.efectivo:,.2f} €")
    c3.metric("Posiciones Activas", f"{len(st.session_state.cartera)} / 10")
    
    if st.button("🚀 Activar Escáner Diario del Bot"):
        reporte_movimientos = []
        for slot, configuracion in ESTRUCTURA_CARTERA.items():
            if slot in st.session_state.cartera: continue
            
            comprado_en_este_slot = False
            for ticker in configuracion["tickers"]:
                if comprado_en_este_slot: break
                
                if ticker in lista_exclusiones:
                    reporte_movimientos.append({
                        "Slot": slot, "Acción": f"EXCLUIDO {ticker}", 
                        "Broker Destino": configuracion["broker"], "Reseña Técnica": "Ya en cartera real."
                    })
                    continue
                
                ans = analizar_activo(ticker, configuracion["broker"])
                if ans and ans["estado"] == "COMPRAR":
                    if st.session_state.efectivo >= 3000:
                        st.session_state.cartera[slot] = {
                            "Ticker": ticker, "Precio Entrada": ans["precio"], 
                            "Acciones": round(3000 / ans["precio"], 2), "Broker": configuracion["broker"]
                        }
                        st.session_state.efectivo -= 3000
                        reporte_movimientos.append({
                            "Slot": slot, "Acción": f"COMPRADO {ticker}", 
                            "Broker Destino": configuracion["broker"], "Reseña Técnica": ans["motivo"]
                        })
                        comprado_en_este_slot = True
                elif ans and ans["estado"] == "DESCARTADO":
                    reporte_movimientos.append({
                        "Slot": slot, "Acción": f"Ignorar {ticker}", 
                        "Broker Destino": configuracion["broker"], "Reseña Técnica": ans["motivo"]
                    })
                    
        if reporte_movimientos:
            st.subheader("📝 Bitácora de Movimientos")
            st.table(pd.DataFrame(reporte_movimientos))
            
    st.markdown("---")
    st.subheader("📊 Mi Cartera Virtual en Tiempo Real")
    if st.session_state.cartera:
        st.table(pd.DataFrame.from_dict(st.session_state.cartera, orient='index'))
    else:
        st.write("Tu cartera está en 100% liquidez.")
