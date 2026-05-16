import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuración de la interfaz de usuario
st.set_page_config(page_title="Terminal Financiero", layout="wide")

# =========================================================
# INICIALIZACIÓN DE VARIABLES EN MEMORIA (SESSION STATE)
# =========================================================
# Universo base del Bot (Se almacena en session_state para permitir modificaciones dinámicas)
if "universo_bot" not in st.session_state:
    st.session_state.universo_bot = {
        "Cerebro / Procesamiento": ["NVDA", "AMD", "QCOM", "INTC", "AVGO", "MRVL", "ADI", "TXN", "MU", "SMCI"],
        "Robótica Quirúrgica / Salud": ["ISRG", "SYK", "ZBH", "MDT", "BSX", "GMED", "TFX"],
        "Automatización / Logística": ["SYM", "ABB", "SIE.DE", "ROK", "GWW", "FAST", "AZO", "SNA", "GE"],
        "Fotónica / Sensórica / Visión": ["CGNX", "KEYS", "ROV", "PH", "AME", "TDY", "KYCCF"],
        "Software Industrial / EDA": ["CDNS", "SNPS", "ANSS", "PTC", "ADSK", "DSY.PA", "SAP.DE"],
        "Semiconductores Potencia / Energía": ["WOLF", "ON", "NXPI", "MPWR", "MCHP", "IFX.DE", "STM"],
        "Litografía / Equipos Sala Blanca": ["ASML", "ASM.AS", "AMAT", "LRCX", "KLAC", "TER", "ENTG", "MKSI", "COHR"],
        "Sistemas Autónomos / LiDAR": ["MBLY", "AUR", "LAZR", "APTIV"],
        "Selección Manual / Extras": []  # <--- Aquí es donde se guardarán tus incorporaciones personalizadas
    }

if "listas_seguimiento" not in st.session_state:
    st.session_state.listas_seguimiento = {
        "Robótica/IA": ["ISRG", "ABB", "6861.T", "SYM", "SERV", "TER", "6954.T", "SYK", "CGNX", "AUR", "MBLY"],
        "Tecnología": ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"],
        "Semicond": ["ASML", "AVGO", "ARM", "SMCI", "MU"]
    }

if "efectivo" not in st.session_state:
    st.session_state.efectivo = 30000.0

if "cartera_bot" not in st.session_state:
    st.session_state.cartera_bot = []

if "oportunidades_bot" not in st.session_state:
    st.session_state.oportunidades_bot = []

# --- MOTOR DE CÁLCULO TÉCNICO ---
def analizar_activo(ticker):
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        df = tk.history(period="2y")
        
        if df.empty or len(df) < 200: 
            return None
            
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        dividend_yield = info.get('dividendYield', 0)
        if dividend_yield is None: 
            dividend_yield = 0
        
        precio = df['Close'].iloc[-1]
        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # Filtro RSI estándar (14 sesiones)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        # Análisis fiscal estricto de flujos (Bélgica vs España)
        if dividend_yield == 0:
            broker_optimo = "ING España (0% Dividendo - Eficiente)"
        else:
            broker_optimo = "Bolero / Revolut"
            
        if precio > sma200 and 45 <= rsi <= 55:
            estado = "COMPRAR (Filtro OK)"
        else:
            estado = "ESPERAR"
            
        return {
            "estado": estado, "precio": precio, "rsi": rsi, "broker": broker_optimo, "yield": dividend_yield
        }
    except:
        return None

# =========================================================
# ENTORNO VISUAL: DISEÑO DE PESTAÑAS
# =========================================================
st.title("🎛️ Centro de Mando Financiero")
pestana1, pestana2, pestana3 = st.tabs([
    "🔍 Escáner Manual de Listas Fijas", 
    "🤖 Bot Algorítmico + Control de Radares",
    "⚙️ Configuración de Listas Visuales"
])

# =========================================================
# PESTAÑA 1: PANEL TRADICIONAL
# =========================================================
with pestana1:
    col_individual, col_listas = st.columns(2)
    with col_individual:
        st.subheader("🔍 Opción 1: Análisis Individual Rápido")
        ticker_individual = st.text_input("Escribe el ticker:", value="", key="manual_ind").upper().strip()
        if st.button("📊 Analizar Ticker", key="btn_ind") and ticker_individual:
            res_ind = analizar_activo(ticker_individual)
            if res_ind:
                st.success(f"**Resultado para: {ticker_individual}**")
                c_p, c_r, c_e = st.columns(3)
                c_p.metric("Precio Actual", f"{res_ind['precio']:.2f} $")
                c_r.metric("RSI", f"{res_ind['rsi']:.1f}")
                c_e.metric("Filtro", res_ind['estado'])
                st.info(f"**Destino Sugerido:** {res_ind['broker']}")
            else:
                st.error("Ticker sin datos históricos suficientes en Yahoo Finance.")
                
    with col_listas:
        st.subheader("📋 Opción 2: Listas de Seguimiento")
        lista_sel = st.selectbox("Selecciona la lista:", list(st.session_state.listas_seguimiento.keys()), key="manual_lista")
        if st.button("🚀 Escanear Lista Completa", key="btn_lista"):
            resultados = []
            for t in st.session_state.listas_seguimiento[lista_sel]:
                res = analizar_activo(t)
                if res:
                    resultados.append({
                        "Ticker": t, "Precio": f"{res['precio']:.2f}$", "RSI": round(res['rsi'], 1), "Filtro": res['estado'], "Bróker": res['broker']
                    })
            if resultados:
                st.table(pd.DataFrame(resultados))

# =========================================================
# PESTAÑA 2: EL BOT MÁS LA POTENCIA DE INTEGRAR EN EL RADAR
# =========================================================
with pestana2:
    st.subheader("🤖 Cuadro de Mando del Bot de Robótica y Tecnología")
    
    # KPIs unificados de gestión monetaria
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuesto Estrategia", "30.000 €")
    c2.metric("Líquido Libre Simulado", f"{st.session_state.efectivo:,.2f} €")
    c3.metric("Posiciones Ocupadas", f"{len(st.session_state.cartera_bot)} / 10")
    
    st.markdown("---")
    
    # Bloques en paralelo: Izquierda Automático, Derecha Tu Inyección a Radar
    col_bot, col_manual_extra = st.columns([2, 1])
    
    with col_bot:
        st.markdown("### 🛰️ Bloque 1: Escáner Automático del Universo")
        # Mostrar cuántos tickers extras has metido tú en la base de datos
        total_extras = len(st.session_state.universo_bot["Selección Manual / Extras"])
        st.caption(f"Rastrea los subsectores industriales preconfigurados + ({total_extras}) activos inyectados por ti.")
        
        if st.button("🔌 Lanzar Rastreo Automático", key="btn_run_bot"):
            with st.spinner("Buscando ventanas técnicas óptimas..."):
                temp_sug = []
                sectores_activos = {}
                for pos in st.session_state.cartera_bot:
                    sec = pos.get("Subsector", "Selección Manual / Extras")
                    sectores_activos[sec] = sectores_activos.get(sec, 0) + 1
                    
                for sector, tickers in st.session_state.universo_bot.items():
                    # Mantenemos control de diversificación para los sectores base
                    if sector != "Selección Manual / Extras" and sectores_activos.get(sector, 0) >= 2:
                        continue
                    for ticker in tickers:
                        if any(p["Ticker"] == ticker for p in st.session_state.cartera_bot):
                            continue
                        ans = analizar_activo(ticker)
                        if ans and ans["estado"] == "COMPRAR (Filtro OK)":
                            temp_sug.append({
                                "Ticker": ticker, "Subsector": sector, "Precio": ans["precio"], "RSI": ans["rsi"], "Broker": ans["broker"]
                            })
                            # Rompemos flujo si el sector base ya se satura
                            if sector != "Selección Manual / Extras":
                                break
                st.session_state.oportunidades_bot = temp_sug
                
        # Mostrar alertas automáticas descubiertas
        if st.session_state.oportunidades_bot:
            st.markdown("##### 🚨 Entradas Técnicas Detectadas:")
            for op in st.session_state.oportunidades_bot:
                if any(p["Ticker"] == op["Ticker"] for p in st.session_state.cartera_bot):
                    continue
                with st.container():
                    cb_inf, cb_act = st.columns([3, 1])
                    cb_inf.write(f"**{op['Ticker']}** ({op['Subsector']}) — Precio: {op['Precio']:.2f}$ | RSI: {op['RSI']:.1f}\n`Asignación: {op['Broker']}`")
                    if cb_act.button(f"➕ Comprar", key=f"add_bot_{op['Ticker']}"):
                        if len(st.session_state.cartera_bot) < 10 and st.session_state.efectivo >= 3000:
                            st.session_state.cartera_bot.append({
                                "Ticker": op["Ticker"], "Subsector": op["Subsector"], "Precio Entrada": f"{op['Precio']:.2f} $", "RSI": round(op['RSI'], 1), "Bróker Destino": op["Broker"]
                            })
                            st.session_state.efectivo -= 3000
                            st.rerun()
            st.markdown("---")

    with col_manual_extra:
        st.markdown("### 👑 Bloque 2: Forzar Tickers Externos")
        st.caption("Introduce cualquier acción que no esté en las listas fijas del robot.")
        
        ticker_manual_libre = st.text_input("Ticker Nuevo (Ej: PLTR, GOOG, TSLA):", value="", key="t_libre_bot").upper().strip()
        
        if ticker_manual_libre:
            res_libre = analizar_activo(ticker_manual_libre)
            if res_libre:
                st.write(f"**Precio:** {res_libre['precio']:.2f}$ | **RSI:** {res_libre['rsi']:.1f}")
                st.write(f"**Filtro Técnico:** `{res_libre['estado']}`")
                st.caption(f"Fiscalidad Bróker: {res_libre['broker']}")
                
                # COMPROBACIÓN DE SI YA EXISTE EN EL RADAR AUTOMÁTICO
                ya_en_radar = False
                for sec, t_list in st.session_state.universo_bot.items():
                    if ticker_manual_libre in t_list:
                        ya_en_radar = True
                
                # BOTÓN 1: METERLO DENTRO DE LA LISTA DEL BOT PARA SIEMPRE
                if ya_en_radar:
                    st.success(f"ℹ️ {ticker_manual_libre} ya forma parte del radar permanente del Bot.")
                else:
                    if st.button(f"📌 Inyectar {ticker_manual_libre} en Radar Fijo", key="btn_radar_inject"):
                        st.session_state.universo_bot["Selección Manual / Extras"].append(ticker_manual_libre)
                        st.success(f"¡{ticker_manual_libre} guardado en la lista del bot! Ahora se analizará de forma automática.")
                        st.rerun()
                
                st.markdown("---")
                
                # BOTÓN 2: COMPRA INMEDIATA
                if st.button(f"🚀 Forzar Entrada Directa en Cartera", key="btn_force_libre"):
                    if len(st.session_state.cartera_bot) >= 10:
                        st.error("Límite de cartera lleno (máx 10 posiciones).")
                    elif st.session_state.efectivo < 3000:
                        st.error("Falta presupuesto (mínimo 3.000 €).")
                    elif any(p["Ticker"] == ticker_manual_libre for p in st.session_state.cartera_bot):
                        st.warning("Ese activo ya consta comprado abajo.")
                    else:
                        st.session_state.cartera_bot.append({
                            "Ticker": ticker_manual_libre,
                            "Subsector": "Selección Manual / Extras",
                            "Precio Entrada": f"{res_libre['precio']:.2f} $",
                            "RSI": round(res_libre['rsi'], 1),
                            "Bróker Destino": res_libre['broker']
                        })
                        st.session_state.efectivo -= 3000
                        st.success(f"¡{ticker_manual_libre} añadido a la cartera simulación!")
                        st.rerun()
            else:
                st.error("No se encuentra en la base de datos mundial de Yahoo Finance.")

    # Registro único unificado abajo
    st.markdown("---")
    st.subheader("📊 Tabla Consolidada de Posiciones en Cartera (30k)")
    if st.session_state.cartera_bot:
        st.table(pd.DataFrame(st.session_state.cartera_bot))
        if st.button("🗑️ Vaciar Cartera y Reiniciar Parámetros"):
            st.session_state.efectivo = 30000.0
            st.session_state.cartera_bot = []
            st.session_state.oportunidades_bot = []
            st.rerun()
    else:
        st.caption("Cartera actual en liquidez líquida. Inyecta posiciones desde el escáner automático o la columna derecha.")

# =========================================================
# PESTAÑA 3: EDITOR DE LISTAS VISUALES
# =========================================================
with pestana3:
    st.subheader("⚙️ Panel de Control de Listas Fijas")
    lista_a_modificar = st.selectbox("Elige lista a editar:", list(st.session_state.listas_seguimiento.keys()), key="edit_lista")
    acciones_actuales = st.session_state.listas_seguimiento[lista_a_modificar]
    
    if acciones_actuales:
        st.info(f"Componentes actuales de la lista: {', '.join(acciones_actuales)}")
    
    st.markdown("---")
    col_add, col_del = st.columns(2)
    with col_add:
        st.markdown("### ➕ Añadir Activo")
        nuevo_ticker = st.text_input("Introduce Ticker para guardar:", value="", key="add_t").upper().strip()
        if st.button("✅ Guardar en Lista", key="btn_add"):
            if nuevo_ticker and nuevo_ticker not in acciones_actuales:
                st.session_state.listas_seguimiento[lista_a_modificar].append(nuevo_ticker)
                st.success(f"Añadido {nuevo_ticker} correctamente.")
                st.rerun()
                
    with col_del:
        st.markdown("### ❌ Eliminar Activo")
        if acciones_actuales:
            ticker_a_borrar = st.selectbox("Selecciona Ticker a retirar:", acciones_actuales, key="del_t")
            if st.button("🗑️ Eliminar de Lista", key="btn_del"):
                st.session_state.listas_seguimiento[lista_a_modificar].remove(ticker_a_borrar)
                st.success(f"Retirado {ticker_a_borrar} correctamente.")
                st.rerun()
