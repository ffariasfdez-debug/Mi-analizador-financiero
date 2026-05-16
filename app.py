iimport streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuración de página
st.set_page_config(page_title="Terminal Financiero", layout="wide")

# =========================================================
# INICIALIZACIÓN COMPLETA Y SEGURA DE LA MEMORIA (SESSION STATE)
# =========================================================
if "listas_seguimiento" not in st.session_state:
    st.session_state.listas_seguimiento = {
        "Robótica/IA": ["ISRG", "ABB", "6861.T", "SYM", "SERV", "TER", "6954.T", "SYK", "CGNX", "AUR", "MBLY"],
        "Tecnología": ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"],
        "Semicond": ["ASML", "AVGO", "ARM", "SMCI", "MU"]
    }

# Universo del Bot en Session State para que sea dinámico y permita añadir tickers manualmente
if "universo_bot" not in st.session_state:
    st.session_state.universo_bot = {
        "Cerebro / Procesamiento": ["NVDA", "AMD", "QCOM", "INTC", "AVGO", "MRVL", "ADI", "TXN", "MU", "SMCI"],
        "Robótica Quirúrgica / Salud": ["ISRG", "SYK", "ZBH", "MDT", "BSX", "GMED", "TFX"],
        "Automatización / Logística": ["SYM", "ABB", "SIE.DE", "ROK", "GWW", "FAST", "AZO", "SNA", "GE"],
        "Fotónica / Sensórica / Visión": ["CGNX", "KEYS", "ROV", "PH", "AME", "TDY", "KYCCF"],
        "Software Industrial / EDA": ["CDNS", "SNPS", "ANSS", "PTC", "ADSK", "DSY.PA", "SAP.DE"],
        "Semiconductores Potencia / Energía": ["WOLF", "ON", "NXPI", "MPWR", "MCHP", "IFX.DE", "STM"],
        "Litografía / Equipos Sala Blanca": ["ASML", "ASM.AS", "AMAT", "LRCX", "KLAC", "TER", "ENTG", "MKSI", "COHR"],
        "Sistemas Autónomos / LiDAR": ["MBLY", "AUR", "LAZR", "APTIV"]
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
            
        return {"estado": estado, "precio": precio, "rsi": rsi, "yield": dividend_yield, "broker": broker_optimo, "motivo": motivo}
    except:
        return None

# =========================================================
# DISEÑO DE LA INTERFAZ DE TRES PESTAÑAS
# =========================================================
st.title("🎛️ Centro de Mando Financiero")
pestana1, pestana2, pestana3 = st.tabs([
    "🔍 Escáner Manual de Listas", 
    "🤖 Bot Masivo Robótica 30k",
    "⚙️ Configuración y Añadir Tickers"
])

# =========================================================
# PESTAÑA 1: ESCÁNER MANUAL
# =========================================================
with pestana1:
    st.header("🔍 Escáner Manual de Mercado")
    st.write("Analiza una acción suelta o revisa tus listas fijas de seguimiento.")
    st.markdown("---")
    
    col_individual, col_listas = st.columns(2)
    
    with col_individual:
        st.subheader("🔍 Opción 1: Análisis Individual")
        ticker_individual = st.text_input("Escribe el ticker (ej: TSLA, AAPL):", value="", key="manual_ind").upper().strip()
        btn_individual = st.button("📊 Analizar esta Acción Solamente", key="btn_ind")
        
        if btn_individual and ticker_individual:
            st.info(f"Analizando {ticker_individual}...")
            res_ind = analizar_activo(ticker_individual)
            if res_ind:
                st.success(f"**Resultado para: {ticker_individual}**")
                c_p, c_r, c_e = st.columns(3)
                c_p.metric("Precio Actual", f"{res_ind['precio']:.2f} $")
                c_r.metric("RSI (14 días)", f"{res_ind['rsi']:.1f}")
                c_e.metric("Estado Técnico", res_ind['estado'])
                st.info(f"**Bróker sugerido:** {res_ind['broker']}\n\n**Nota:** {res_ind['motivo']}")
            else:
                st.error("No se han encontrado datos. Revisa el ticker.")
                
    with col_listas:
        st.subheader("📋 Opción 2: Listas Predeterminadas")
        lista_sel = st.selectbox("Selecciona la lista:", list(st.session_state.listas_seguimiento.keys()), key="manual_lista")
        btn_listas = st.button("🚀 Ejecutar Análisis de la Lista", key="btn_lista")
        
        if btn_listas:
            st.info(f"Escaneando lista: {lista_sel}...")
            resultados = []
            for t in st.session_state.listas_seguimiento[lista_sel]:
                res = analizar_activo(t)
                if res:
                    resultados.append({
                        "Ticker": t, "Precio": f"{res['precio']:.2f}$", 
                        "RSI": round(res['rsi'], 1), "Estado": res['estado'], "Bróker Destino": res['broker'], "Nota": res['motivo']
                    })
            if resultados:
                st.table(pd.DataFrame(resultados))
            else:
                st.warning("Esta lista está vacía.")

# =========================================================
# PESTAÑA 2: EL BOT MASIVO CON MEMORIA DINÁMICA
# =========================================================
with pestana2:
    st.header("🤖 Bot de Gestión Activa (Radar Ampliado de Líderes)")
    st.write("Escanea el ecosistema global ejecutable en tus brókers y autogestiona un presupuesto de 30.000€.")
    st.markdown("---")
    
    st.subheader("🛡️ Exclusión de Cartera Real")
    exclusiones_input = st.text_input("Introduce las acciones que YA tienes compradas (separadas por comas, ej: NVDA, ASML):", value="", key="bot_excl").upper()
    lista_exclusiones = [t.strip() for t in exclusiones_input.split(",") if t.strip()]
    
    if lista_exclusiones:
        st.warning(f"🚫 Omitiendo automáticamente del radar del bot: {', '.join(lista_exclusiones)}")
        
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuesto Inicial", "30.000 €")
    c2.metric("Efectivo Disponible", f"{st.session_state.efectivo:,.2f} €")
    c3.metric("Posiciones Abiertas", f"{len(st.session_state.cartera_bot)} / 10")
    
    if st.button("🚀 Activar Escáner Diario", key="btn_run_bot"):
        reporte_movimientos = []
        
        conteo_industrias = {}
        for pos in st.session_state.cartera_bot:
            ind = pos["Industria"]
            conteo_industrias[ind] = conteo_industrias.get(ind, 0) + 1
            
        # Usa st.session_state.universo_bot en lugar del diccionario estático fijo anterior
        for industria, tickers in st.session_state.universo_bot.items():
            if conteo_industrias.get(industria, 0) >= 2:
                continue
                
            for ticker in tickers:
                if len(st.session_state.cartera_bot) >= 10 or st.session_state.efectivo < 3000:
                    break
                    
                if ticker in lista_exclusiones or any(p["Ticker"] == ticker for p in st.session_state.cartera_bot):
                    continue
                    
                ans = analizar_activo(ticker)
                
                if ans and ans["estado"] == "COMPRAR":
                    st.session_state.cartera_bot.append({
                        "Ticker": ticker,
                        "Industria": industria,
                        "Precio Entrada": f"{ans['precio']:.2f} $",
                        "RSI": round(ans['rsi'], 1),
                        "Bróker Destino": ans["broker"]
                    })
                    st.session_state.efectivo -= 3000
                    conteo_industrias[industria] = conteo_industrias.get(industria, 0) + 1
                    
                    reporte_movimientos.append({
                        "Acción": f"COMPRADO {ticker}",
                        "Subsector": industria,
                        "Destino Recomendado": ans["broker"],
                        "Motivo Técnico": ans["motivo"]
                    })
                    break
                    
        if reporte_movimientos:
            st.subheader("📝 Bitácora de Operaciones de Hoy")
            st.table(pd.DataFrame(reporte_movimientos))
        else:
            st.info("El escáner no ha encontrado nuevos activos que cumplan el patrón exacto hoy (o la cartera del bot está llena).")
            
    st.markdown("---")
    st.subheader("📊 Estado Actual de la Cartera del Bot (Simulada)")
    if st.session_state.cartera_bot:
        st.table(pd.DataFrame(st.session_state.cartera_bot))
        if st.button("🗑️ Reiniciar Cartera del Bot (Volver a 100% Liquidez)"):
            st.session_state.efectivo = 30000.0
            st.session_state.cartera_bot = []
            st.rerun()
    else:
        st.write("Cartera vacía. Pulsa el botón superior para poner al bot a escanear.")

# =========================================================
# PESTAÑA 3: GESTOR CENTRALIZADO (MANUAL Y BOT)
# =========================================================
with pestana3:
    st.header("⚙️ Panel de Control y Configuración")
    st.write("Gestiona tanto tus listas manuales como el universo de búsqueda del Bot Autónomo.")
    st.markdown("---")
    
    # SECCIÓN A: GESTIÓN DE LAS LISTAS MANUALES
    st.subheader("📋 1. Modificar Listas del Escáner Manual")
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        lista_a_modificar = st.selectbox("Selecciona lista manual:", list(st.session_state.listas_seguimiento.keys()), key="edit_lista")
    with col_m2:
        acciones_actuales = st.session_state.listas_seguimiento[lista_a_modificar]
        st.write(f"**Contenido actual:** {', '.join(acciones_actuales) if acciones_actuales else 'Vacía'}")
        
    c_add_m, c_del_m = st.columns(2)
    with c_add_m:
        nuevo_ticker = st.text_input("Añadir ticker a lista manual:", value="", key="add_t").upper().strip()
        if st.button("✅ Añadir a Lista Manual", key="btn_add"):
            if nuevo_ticker and nuevo_ticker not in acciones_actuales:
                st.session_state.listas_seguimiento[lista_a_modificar].append(nuevo_ticker)
                st.success(f"{nuevo_ticker} añadido a la lista manual.")
                st.rerun()
    with c_del_m:
        if acciones_actuales:
            ticker_a_borrar = st.selectbox("Quitar ticker de lista manual:", acciones_actuales, key="del_t")
            if st.button("🗑️ Borrar de Lista Manual", key="btn_del"):
                st.session_state.listas_seguimiento[lista_a_modificar].remove(ticker_a_borrar)
                st.success(f"{ticker_a_borrar} eliminado de la lista manual.")
                st.rerun()

    st.markdown("---")
    
    # SECCIÓN B: GESTIÓN DEL UNIVERSO DEL BOT (LA NUEVA OPCIÓN)
    st.subheader("🤖 2. Ampliar el Universo de Búsqueda del Bot")
    st.write("Si un nuevo componente entra en un índice sectorial, añádelo aquí para que el Bot lo vigile diariamente.")
    
    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        sector_bot_sel = st.selectbox("Selecciona a qué subsector pertenece:", list(st.session_state.universo_bot.keys()), key="sector_bot")
    with col_b2:
        tickers_bot_actuales = st.session_state.universo_bot[sector_bot_sel]
        st.write(f"**Empresas vigiladas en este subsector ({len(tickers_bot_actuales)}):**")
        st.write(f"{', '.join(tickers_bot_actuales)}")

    c_add_b, c_del_b = st.columns(2)
    with c_add_b:
        nuevo_ticker_bot = st.text_input("Escribe el nuevo ticker para el Bot (ej: PLTR, VRT):", value="", key="add_t_bot").upper().strip()
        if st.button("🚀 Inyectar al Radar del Bot", key="btn_add_bot"):
            if nuevo_ticker_bot:
                # Verificar que no esté ya en ese sector
                if nuevo_ticker_bot not in tickers_bot_actuales:
                    st.session_state.universo_bot[sector_bot_sel].append(nuevo_ticker_bot)
                    st.success(f"¡Brillante! {nuevo_ticker_bot} ha sido añadido al subsector '{sector_bot_sel}' del Bot.")
                    st.rerun()
                else:
                    st.warning(f"El ticker {nuevo_ticker_bot} ya está dentro de este subsector.")
    with c_del_b:
        if tickers_bot_actuales:
            ticker_bot_borrar = st.selectbox("Selecciona un ticker si deseas sacarlo del Bot:", tickers_bot_actuales, key="del_t_bot")
            if st.button("🗑️ Eliminar del Radar del Bot", key="btn_del_bot"):
                st.session_state.universo_bot[sector_bot_sel].remove(ticker_bot_borrar)
                st.success(f"{ticker_bot_borrar} retirado del universo del Bot.")
                st.rerun()
