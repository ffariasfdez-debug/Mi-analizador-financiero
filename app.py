import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuración de página
st.set_page_config(page_title="Terminal Financiero", layout="wide")

# =========================================================
# INICIALIZACIÓN COMPLETA Y DINÁMICA DE LA MEMORIA
# =========================================================
if "listas_seguimiento" not in st.session_state:
    st.session_state.listas_seguimiento = {
        "Robótica/IA": [
            "NVDA", "AMD", "QCOM", "INTC", "AVGO", "MRVL", "ADI", "TXN", "MU", "SMCI",
            "ISRG", "SYK", "ZBH", "MDT", "BSX", "GMED", "TFX",
            "SYM", "ABB", "SIE.DE", "ROK", "GWW", "FAST", "AZO", "SNA", "GE",
            "CGNX", "KEYS", "ROV", "PH", "AME", "TDY", "KYCCF",
            "CDNS", "SNPS", "ANSS", "PTC", "ADSK", "DSY.PA", "SAP.DE",
            "WOLF", "ON", "NXPI", "MPWR", "MCHP", "IFX.DE", "STM",
            "ASML", "ASM.AS", "AMAT", "LRCX", "KLAC", "TER", "ENTG", "MKSI", "COHR",
            "MBLY", "AUR", "LAZR", "APTIV"
        ],
        "Tecnología (Manual)": ["TSLA", "AAPL", "MSFT"],
    }

if "efectivo" not in st.session_state:
    st.session_state.efectivo = 30000.0

if "cartera_bot" not in st.session_state:
    st.session_state.cartera_bot = []

# --- MOTOR DE ANALÍTICA TÉCNICA Y FILTRO DE BRÓKER ---
def analizar_activo(ticker, forzar_ing=False):
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        df = tk.history(period="2y")
        
        if df.empty or len(df) < 200: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        dividend_yield = info.get('dividendYield', 0)
        if dividend_yield is None: dividend_yield = 0
        
        precio = df['Close'].iloc[-1]
        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # Cálculo de RSI (14 días)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        if dividend_yield == 0:
            broker_optimo = "ING (0% Div) o Bolero/Revolut"
            es_apto_ing = True
        else:
            broker_optimo = "Bolero / Revolut (Paga Dividendo)"
            es_apto_ing = False
            
        if forzar_ing and not es_apto_ing:
            return {"estado": "DESCARTADO", "motivo": "Filtro estricto ING: Paga dividendos."}
            
        if precio > sma200 and 45 <= rsi <= 55:
            estado = "COMPRAR"
            motivo = f"Punto óptimo. RSI sano ({rsi:.1f}) en tendencia alcista principal."
        else:
            estado = "ESPERAR"
            motivo = f"RSI en {rsi:.1f}. Precio extendido o sin momentum claro."
            
        industry = info.get('industry', 'General')
        return {"estado": estado, "precio": precio, "rsi": rsi, "yield": dividend_yield, "broker": broker_optimo, "motivo": motivo, "industria": industry}
    except:
        return None

# =========================================================
# DISEÑO DE LA INTERFAZ DE TRES PESTAÑAS
# =========================================================
st.title("🎛️ Centro de Mando Financiero")
pestana1, pestana2, pestana3 = st.tabs([
    "🔍 Escáner Manual de Listas", 
    "🤖 Bot Dinámico Robótica 30k",
    "⚙️ Configuración de Listas del Bot"
])

# =========================================================
# PESTAÑA 1: ESCÁNER MANUAL (RESTAURADA COMPROBACIÓN DE LISTAS)
# =========================================================
with pestana1:
    col_individual, col_listas = st.columns(2)
    
    with col_individual:
        st.subheader("🔍 Opción 1: Análisis Individual")
        ticker_individual = st.text_input("Escribe el ticker (ej: TSLA, AAPL):", value="", key="manual_ind").upper().strip()
        btn_individual = st.button("📊 Analizar esta Acción Solamente", key="btn_ind")
        
        if btn_individual and ticker_individual:
            res_ind = analizar_activo(ticker_individual)
            if res_ind:
                st.success(f"**Resultado para: {ticker_individual}**")
                c_p, c_r, c_e = st.columns(3)
                c_p.metric("Precio Actual", f"{res_ind['precio']:.2f} $")
                c_r.metric("RSI (14 días)", f"{res_ind['rsi']:.1f}")
                c_e.metric("Estado Técnico", res_ind['estado'])
                st.info(f"**Bróker:** {res_ind['broker']}\n\n**Nota:** {res_ind['motivo']}")
            else:
                st.error("No se han encontrado datos. Revisa el ticker.")
                
    with col_listas:
        st.subheader("📋 Opción 2: Listas Completas")
        lista_sel = st.selectbox("Selecciona la lista a escanear:", list(st.session_state.listas_seguimiento.keys()), key="manual_lista")
        
        # RESTAURADO: Muestra los componentes en tiempo real en el modo manual al seleccionar la lista
        acciones_de_la_lista = st.session_state.listas_seguimiento[lista_sel]
        st.write(f"**Componentes en '{lista_sel}':** {', '.join(acciones_de_la_lista) if acciones_de_la_lista else 'Lista vacía'}")
        
        btn_listas = st.button("🚀 Ejecutar Análisis de la Lista", key="btn_lista")
        
        if btn_listas:
            st.info(f"Escaneando lista: {lista_sel}...")
            resultados = []
            for t in acciones_de_la_lista:
                res = analizar_activo(t)
                if res:
                    resultados.append({
                        "Ticker": t, "Precio": f"{res['precio']:.2f}$", 
                        "RSI": round(res['rsi'], 1), "Estado": res['estado'], "Bróker Destino": res['broker'], "Nota": res['motivo']
                    })
            if resultados:
                st.table(pd.DataFrame(resultados))

# =========================================================
# PESTAÑA 2: EL BOT DINÁMICO
# =========================================================
with pestana2:
    st.header("🤖 Bot de Gestión Activa (Radar Editable)")
    st.write("Escanea la lista 'Robótica/IA' modificada por ti. Autogestiona 30.000€ distribuidos en un máximo de 10 posiciones.")
    st.markdown("---")
    
    exclusiones_input = st.text_input("🛡️ Exclusión de Cartera Real (Acciones que ya tienes separadas por comas):", value="", key="bot_excl").upper()
    lista_exclusiones = [t.strip() for t in exclusiones_input.split(",") if t.strip()]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuesto Inicial", "30.000 €")
    c2.metric("Efectivo Disponible", f"{st.session_state.efectivo:,.2f} €")
    c3.metric("Posiciones Abiertas", f"{len(st.session_state.cartera_bot)} / 10")
    
    if st.button("🚀 Activar Escáner Diario del Bot", key="btn_run_bot"):
        reporte_movimientos = []
        conteo_industrias = {}
        
        for pos in st.session_state.cartera_bot:
            ind = pos["Industria"]
            conteo_industrias[ind] = conteo_industrias.get(ind, 0) + 1
            
        universo_bot = st.session_state.listas_seguimiento["Robótica/IA"]
        
        for ticker in universo_bot:
            if len(st.session_state.cartera_bot) >= 10 or st.session_state.efectivo < 3000:
                break
                
            if ticker in lista_exclusiones or any(p["Ticker"] == ticker for p in st.session_state.cartera_bot):
                continue
                
            ans = analizar_activo(ticker)
            if ans and ans["estado"] == "COMPRAR":
                industria_activo = ans["industria"]
                
                if conteo_industrias.get(industria_activo, 0) >= 2:
                    continue
                    
                st.session_state.cartera_bot.append({
                    "Ticker": ticker, 
                    "Industria": industria_activo, 
                    "Precio Entrada": f"{ans['precio']:.2f} $", 
                    "RSI": round(ans['rsi'], 1), 
                    "Bróker Destino": ans["broker"]
                })
                st.session_state.efectivo -= 3000
                conteo_industrias[industria_activo] = conteo_industrias.get(industria_activo, 0) + 1
                
                reporte_movimientos.append({
                    "Acción": f"COMPRADO {ticker}", 
                    "Subsector": industria_activo, 
                    "Destino Recomendado": ans["broker"], 
                    "Motivo Técnico": ans["motivo"]
                })
                
        if reporte_movimientos:
            st.subheader("📝 Bitácora de Operaciones de Hoy")
            st.table(pd.DataFrame(reporte_movimientos))
        else:
            st.info("El escáner ha revisado tu lista actual y ninguna nueva cumple las condiciones de entrada hoy.")
            
    st.markdown("---")
    st.subheader("📊 Estado Actual de la Cartera del Bot")
    if st.session_state.cartera_bot:
        st.table(pd.DataFrame(st.session_state.cartera_bot))
        if st.button("🗑️ Reiniciar Cartera del Bot"):
            st.session_state.efectivo = 30000.0
            st.session_state.cartera_bot = []
            st.rerun()
    else:
        st.write("Cartera en 100% liquidez.")

# =========================================================
# PESTAÑA 3: GESTOR DE LISTAS (MÁXIMA FLEXIBILIDAD)
# =========================================================
with pestana3:
    st.header("⚙️ Configuración y Modificación del Universo del Bot")
    st.write("Desde aquí controlas los componentes que el bot y el escáner manual rastrearán. Cualquier cambio impacta en ambas herramientas.")
    
    lista_a_modificar = st.selectbox("Selecciona la lista a gestionar (Elige 'Robótica/IA' para alterar el Bot):", list(st.session_state.listas_seguimiento.keys()), key="edit_lista")
    acciones_actuales = st.session_state.listas_seguimiento[lista_a_modificar]
    
    st.write(f"**Valores monitorizados en este momento ({len(acciones_actuales)}):**")
    st.info(", ".join(acciones_actual
