import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuración de página con el menú lateral forzado a estar abierto por si acaso
st.set_page_config(page_title="Terminal Financiero", layout="wide", initial_sidebar_state="expanded")

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
        
        # Filtro estricto para ING: 0% dividendos obligatorio
        if "ING" in regla_broker and dividend_yield > 0:
            return {"estado": "DESCARTADO", "motivo": "Filtro ING: Paga dividendos."}
            
        precio = df['Close'].iloc[-1]
        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # Calcular RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        if precio > sma200 and 45 <= rsi <= 55:
            estado = "COMPRAR"
            motivo = f"Punto óptimo. RSI sano ({rsi:.1f}) y tendencia alcista a largo plazo."
        else:
            estado = "ESPERAR"
            motivo = "Precio extendido o sin fuerza clara de momentum."
            
        return {"estado": estado, "precio": precio, "rsi": rsi, "yield": dividend_yield, "motivo": motivo}
    except:
        return None

# =========================================================
# NUEVOS BOTONES SUPERIORES (PESTAÑAS CENTRALES EN PANTALLA)
# =========================================================
st.title("🎛️ Centro de Mando Financiero")
pestana1, pestana2 = st.tabs(["🔍 Escáner Manual de Listas", "🤖 Bot Autónomo Robótica 30k"])

# ==========================================
# PESTAÑA 1: EL ESCÁNER MANUAL (ORIGINAL)
# ==========================================
with pestana1:
    st.header("🔍 Escáner Manual de Mercado")
    st.write("Revisa tus listas de seguimiento predeterminadas y analiza puntos de entrada.")
    
    # Listas originales restauradas por completo
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
# PESTAÑA 2: EL BOT AUTÓNOMO DE 30K (ROBÓTICA)
# ==========================================
with pestana2:
    st.header("🤖 Tu Asesor Autónomo de Inversión")
    st.write("Estrategia de Gestión Activa centrada en Robótica y su cadena de valor física (Excluida IA Pura).")
    
    # 10 Slots limpios reorientados a hardware de robótica y potencia
    ESTRUCTURA_CARTERA = {
        "Slot 1: Robótica Quirúrgica/Médica": {"tickers": ["ISRG", "SYK"], "broker": "Bolero/Revolut"},
        "Slot 2: Automatización y Almacén": {"tickers": ["SYM", "ABB"], "broker": "ING (0% Div)"},
        "Slot 3: Fotónica y Visión Artificial": {"tickers": ["6861.T", "CGNX"], "broker": "Bolero/Revolut"},
        "Slot 4: Litografía (Chips de Robots)": {"tickers": ["ASML"], "broker": "Bolero/Revolut"},
        "Slot 5: Procesamiento Gráfico/Edge": {"tickers": ["NVDA", "AMD"], "broker": "ING (0% Div)"},
        "Slot 6: Sensores e Infraestructura": {"tickers": ["FANUC.F", "TER"], "broker": "Bolero/Revolut"},
        "Slot 7: Software de Diseño de Hardware": {"tickers": ["CDNS", "SNPS"], "broker": "ING (0% Div)"},
        "Slot 8: Semiconductores de Potencia": {"tickers": ["WOLF", "ON"], "broker": "ING (0% Div)"},
        "Slot 9: Vehículos Autónomos y LiDAR": {"tickers": ["MBLY", "AUR"], "broker": "Bolero/Revolut"},
        "Slot 10: Componentes Críticos/Líderes": {"tickers": ["AMAT", "LRCX"], "broker": "Bolero/Revolut"}
    }
    
    # El filtro de exclusión real ahora está integrado aquí abajo para que no se pierda en ningún menú lateral
    st.markdown("### 🛡️ Filtro de Cartera Real")
    exclusiones_input = st.text_input("Introduce los tickers que YA tienes en la realidad (ej: NVDA, ASML):", value="").upper()
    lista_exclusiones = [t.strip() for t in exclusiones_input.split(",") if t.strip()]
    
    if lista_exclusiones:
        st.warning(f"Omitiendo de los análisis automáticos: {', '.join(lista_exclusiones)}")
    
    if 'efectivo' not in st.session_state:
        st.session_state.efectivo = 30000.0
        st.session_state.cartera = {}
        
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuesto Inicial", "30.000 €")
    c2.metric("Efectivo Disponible", f"{st.session_state.efectivo:,.2f} €")
    c3.metric("Slots Ocupados", f"{len(st.session_state.cartera)} / 10")
    
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
                        "Broker Destino": configuracion["broker"], "Reseña Técnica": "Ya en posesión en cartera real."
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
            st.subheader("📝 Bitácora de Movimientos del Bot")
            st.table(pd.DataFrame(reporte_movimientos))
            
    st.markdown("---")
    st.subheader("📊 Estado de la Cartera Autónoma (Simulada)")
    if st.session_state.cartera:
        st.table(pd.DataFrame.from_dict(st.session_state.cartera, orient='index'))
    else:
        st.write("Tu cartera está en 100% liquidez esperando el momento óptimo de entrada.")
