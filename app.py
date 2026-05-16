import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuración de página
st.set_page_config(page_title="Terminal Financiero", layout="wide")

# --- INITIALIZATION OF LISTS IN SESSION STATE (Para que sean editables) ---
if "listas_seguimiento" not in st.session_state:
    st.session_state.listas_seguimiento = {
        "Robótica/IA": ["ISRG", "ABB", "6861.T", "SYM", "SERV", "TER", "6954.T", "SYK", "CGNX", "AUR", "MBLY"],
        "Tecnología": ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"],
        "Semicond": ["ASML", "AVGO", "ARM", "SMCI", "MU"]
    }

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
            motivo = "Precio extendido o sin fuerza."
            
        return {"estado": estado, "precio": precio, "rsi": rsi, "yield": dividend_yield, "motivo": motivo}
    except:
        return None

# =========================================================
# CREACIÓN DE LAS TRES PESTAÑAS PRINCIPALES
# =========================================================
st.title("🎛️ Centro de Mando Financiero")
pestana1, pestana2, pestana3 = st.tabs([
    "🔍 Escáner Manual de Listas", 
    "🤖 Bot Autónomo Robótica 30k",
    "⚙️ Configuración de Listas"
])

# =========================================================
# CONTENIDO DE LA PESTAÑA 1: ESCÁNER MANUAL
# =========================================================
with pestana1:
    st.header("🔍 Escáner Manual de Mercado")
    st.write("Analiza una acción suelta o revisa tus listas fijas de seguimiento.")
    st.markdown("---")
    
    col_individual, col_listas = st.columns(2)
    
    with col_individual:
        st.subheader("🔍 Opción 1: Análisis Individual")
        ticker_individual = st.text_input("Escribe el ticker (ej: TSLA, AAPL):", value="", key="input_manual_ind").upper().strip()
        btn_individual = st.button("📊 Analizar esta Acción Solamente", key="btn_manual_ind")
        
        if btn_individual and ticker_individual:
            st.info(f"Analizando {ticker_individual}...")
            res_ind = analizar_activo(ticker_individual)
            if res_ind:
                st.success(f"**Resultado para: {ticker_individual}**")
                c_p, c_r, c_e = st.columns(3)
                c_p.metric("Precio Actual", f"{res_ind['precio']:.2f} $")
                c_r.metric("RSI (14 días)", f"{res_ind['rsi']:.1f}")
                c_e.metric("Estado Técnico", res_ind['estado'])
                st.info(f"**Nota:** {res_ind['motivo']}")
            else:
                st.error("No se han encontrado datos. Revisa el ticker.")
                
    with col_listas:
        st.subheader("📋 Opción 2: Listas Predeterminadas")
        lista_sel = st.selectbox("Selecciona la lista:", list(st.session_state.listas_seguimiento.keys()), key="select_manual_lista")
        btn_listas = st.button("🚀 Ejecutar Análisis de la Lista", key="btn_manual_lista")
        
        if btn_listas:
            st.info(f"Escaneando lista: {lista_sel}...")
            resultados = []
            for t in st.session_state.listas_seguimiento[lista_sel]:
                res = analizar_activo(t)
                if res:
                    resultados.append({
                        "Ticker": t, "Precio": f"{res['precio']:.2f}$", 
                        "RSI": round(res['rsi'], 1), "Estado": res['estado'], "Nota": res['motivo']
                    })
            if resultados:
                st.table(pd.DataFrame(resultados))
            else:
                st.warning("Esta lista está vacía actualmente.")

# =========================================================
# CONTENIDO DE LA PESTAÑA 2: BOT AUTÓNOMO 30K
# =========================================================
with pestana2:
    st.header("🤖 Bot Autónomo de Inversión (Ecosistema Robótica)")
    st.write("Gestión simulada de 30.000€ centrada en el hardware y cadena de valor de la Robótica.")
    st.markdown("---")
    
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
    
    st.subheader("🛡️ Filtro de Cartera Real")
    exclusiones_input = st.text_input("Introduce los tickers que YA tienes en la realidad (separados por comas):", value="", key="input_bot_exclusiones").upper()
    lista_exclusiones = [t.strip() for t in exclusiones_input.split(",") if t.strip()]
    
    if lista_exclusiones:
        st.warning(f"Omitiendo de las compras del bot: {', '.join(lista_exclusiones)}")
        
    if 'efectivo' not in st.session_state:
        st.session_state.efectivo = 30000.0
        st.session_state.cartera = {}
        
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuesto Inicial", "30.000 €")
    c2.metric("Efectivo Disponible", f"{st.session_state.efectivo:,.2f} €")
    c3.metric("Slots Ocupados", f"{len(st.session_state.cartera)} / 10")
    
    if st.button("🚀 Activar Escáner Diario del Bot", key="btn_activar_bot"):
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
        st.write("Tu cartera está en 100% liquidez esperando oportunidades.")

# =========================================================
# NUEVA PESTAÑA 3: CONFIGURACIÓN Y EDICIÓN DE LISTAS
# =========================================================
with pestana3:
    st.header("⚙️ Gestor de Listas de Seguimiento")
    st.write("Añade o elimina acciones de tus listas predeterminadas fácilmente.")
    st.markdown("---")
    
    # 1. Selector de la lista a editar
    lista_a_modificar = st.selectbox("Selecciona la lista que deseas gestionar:", list(st.session_state.listas_seguimiento.keys()), key="select_edicion")
    
    # Mostrar componentes actuales de la lista
    acciones_actuales = st.session_state.listas_seguimiento[lista_a_modificar]
    st.write(f"**Acciones actuales en '{lista_a_modificar}':** {', '.join(acciones_actuales) if acciones_actuales else 'Lista vacía'}")
    
    st.markdown("---")
    col_add, col_del = st.columns(2)
    
    # Bloque para AÑADIR Tickers
    with col_add:
        st.subheader("➕ Añadir Acción")
        nuevo_ticker = st.text_input("Escribe el ticker a añadir (ej: AMD, PLTR):", value="", key="input_add_ticker").upper().strip()
        if st.button("✅ Añadir a la Lista", key="btn_add_ticker"):
            if nuevo_ticker:
                if nuevo_ticker not in st.session_state.listas_seguimiento[lista_a_modificar]:
                    st.session_state.listas_seguimiento[lista_a_modificar].append(nuevo_ticker)
                    st.success(f"¡{nuevo_ticker} se ha añadido correctamente a '{lista_a_modificar}'!")
                    st.rerun()  # Recarga la app para aplicar el cambio visual inmediato
                else:
                    st.warning(f"El ticker {nuevo_ticker} ya existe en esta lista.")
            else:
                st.error("Por favor, escribe un ticker válido.")
                
    # Bloque para BORRAR Tickers
    with col_del:
        st.subheader("❌ Eliminar Acción")
        if acciones_actuales:
            ticker_a_borrar = st.selectbox("Selecciona qué ticker quieres quitar:", acciones_actuales, key="select_del_ticker")
            if st.button("🗑️ Borrar de la Lista", key="btn_del_ticker"):
                st.session_state.listas_seguimiento[lista_a_modificar].remove(ticker_a_borrar)
                st.success(f"¡{ticker_a_borrar} eliminado de '{lista_a_modificar}'!")
                st.rerun()  # Recarga la app para aplicar el cambio visual inmediato
        else:
            st.write("No hay acciones para borrar en esta lista.")
