import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuración de página principal
st.set_page_config(page_title="Terminal Financiero", layout="wide")

# =========================================================
# INICIALIZACIÓN DE VARIABLES EN MEMORIA (SESSION STATE)
# =========================================================
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

if "cartera_real_comprada" not in st.session_state:
    st.session_state.cartera_real_comprada = []

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
        
        # RSI estándar de 14 períodos
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        # Enrutamiento fiscal estricto de activos
        if dividend_yield == 0:
            broker_optimo = "ING España (0% Dividendo - Eficiente)"
        else:
            broker_optimo = "Bolero / Revolut (Acción con Dividendo)"
            
        # Condición matemática estricta de entrada
        if precio > sma200 and 45 <= rsi <= 55:
            estado = "COMPRAR"
            motivo = f"RSI óptimo en zona de acumulación ({rsi:.1f}) y cotizando sobre la SMA 200."
        else:
            estado = "ESPERAR"
            motivo = f"RSI en {rsi:.1f}. No se encuentra en la ventana técnica de entrada."
            
        return {"estado": estado, "precio": precio, "rsi": rsi, "broker": broker_optimo, "motivo": motivo, "yield": dividend_yield}
    except:
        return None

# =========================================================
# COMPONENTE VISUAL: CONTROL DE PESTAÑAS
# =========================================================
st.title("🎛️ Centro de Mando Financiero")
pestana1, pestana2, pestana3 = st.tabs([
    "🔍 Escáner Manual de Listas", 
    "🤖 Bot Masivo Robótica 30k",
    "⚙️ Configuración de Listas"
])

# =========================================================
# PESTAÑA 1: PANEL MANUAL
# =========================================================
with pestana1:
    col_individual, col_listas = st.columns(2)
    
    with col_individual:
        st.subheader("🔍 Opción 1: Análisis Individual")
        ticker_individual = st.text_input("Escribe el ticker:", value="", key="manual_ind").upper().strip()
        btn_individual = st.button("📊 Analizar Ticker", key="btn_ind")
        
        if btn_individual and ticker_individual:
            res_ind = analizar_activo(ticker_individual)
            if res_ind:
                st.success(f"**Resultado para: {ticker_individual}**")
                c_p, c_r, c_e = st.columns(3)
                c_p.metric("Precio Actual", f"{res_ind['precio']:.2f} $")
                c_r.metric("RSI", f"{res_ind['rsi']:.1f}")
                c_e.metric("Filtro", res_ind['estado'])
                st.info(f"**Destino Sugerido:** {res_ind['broker']}\n\n**Nota:** {res_ind['motivo']}")
            else:
                st.error("Ticker no válido o sin datos históricos suficientes.")
                
    with col_listas:
        st.subheader("📋 Opción 2: Listas de Seguimiento")
        lista_sel = st.selectbox("Selecciona la lista:", list(st.session_state.listas_seguimiento.keys()), key="manual_lista")
        btn_listas = st.button("🚀 Escanear Lista Completa", key="btn_lista")
        
        if btn_listas:
            resultados = []
            for t in st.session_state.listas_seguimiento[lista_sel]:
                res = analizar_activo(t)
                if res:
                    resultados.append({
                        "Ticker": t, 
                        "Precio": f"{res['precio']:.2f}$", 
                        "RSI": round(res['rsi'], 1), 
                        "Estado": res['estado'], 
                        "Asignación Bróker": res['broker'], 
                        "Análisis": res['motivo']
                    })
            if resultados:
                st.table(pd.DataFrame(resultados))

# =========================================================
# PESTAÑA 2: RADAR ALGORÍTMICO CON BOTÓN DE ENTRADA REAL
# =========================================================
with pestana2:
    st.subheader("🤖 Simulación del Universo de Inversión (65 Líderes)")
    
    UNIVERSO_EXPANDIDO = {
        "Cerebro / Procesamiento": ["NVDA", "AMD", "QCOM", "INTC", "AVGO", "MRVL", "ADI", "TXN", "MU", "SMCI"],
        "Robótica Quirúrgica / Salud": ["ISRG", "SYK", "ZBH", "MDT", "BSX", "GMED", "TFX"],
        "Automatización / Logística": ["SYM", "ABB", "SIE.DE", "ROK", "GWW", "FAST", "AZO", "SNA", "GE"],
        "Fotónica / Sensórica / Visión": ["CGNX", "KEYS", "ROV", "PH", "AME", "TDY", "KYCCF"],
        "Software Industrial / EDA": ["CDNS", "SNPS", "ANSS", "PTC", "ADSK", "DSY.PA", "SAP.DE"],
        "Semiconductores Potencia / Energía": ["WOLF", "ON", "NXPI", "MPWR", "MCHP", "IFX.DE", "STM"],
        "Litografía / Equipos Sala Blanca": ["ASML", "ASM.AS", "AMAT", "LRCX", "KLAC", "TER", "ENTG", "MKSI", "COHR"],
        "Sistemas Autónomos / LiDAR": ["MBLY", "AUR", "LAZR", "APTIV"]
    }
    
    exclusiones_input = st.text_input("🛡️ Excluir de la simulación (Acciones que ya tienes en cartera real, ej: NVDA, ASML):", value="", key="bot_excl").upper()
    lista_exclusiones = [t.strip() for t in exclusiones_input.split(",") if t.strip()]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuesto Estrategia", "30.000 €")
    c2.metric("Efectivo Libre Simulado", f"{st.session_state.efectivo:,.2f} €")
    c3.metric("Posiciones Ocupadas", f"{len(st.session_state.cartera_bot)} / 10")
    
    # Botón principal de ejecución del escáner
    ejecutar_escaneo = st.button("🔌 Ejecutar Escáner de Mercado Masivo", key="btn_run_bot")
    
    if ejecutar_escaneo:
        st.session_state.oportunidades_detectadas = []
        
        # Control estricto de diversificación por sectores (Máx 2 por subsector)
        sectores_activos = {}
        for pos in st.session_state.cartera_bot:
            sec = pos["Subsector"]
            sectores_activos[sec] = sectores_activos.get(sec, 0) + 1
            
        for sector, tickers in UNIVERSO_EXPANDIDO.items():
            if sectores_activos.get(sector, 0) >= 2:
                continue
                
            for ticker in tickers:
                if len(st.session_state.cartera_bot) >= 10 or st.session_state.efectivo < 3000:
                    break
                if ticker in lista_exclusiones or any(p["Ticker"] == ticker for p in st.session_state.cartera_bot):
                    continue
                    
                ans = analizar_activo(ticker)
                # Si cumple con las condiciones técnicas de COMPRA, se captura
                if ans and ans["estado"] == "COMPRAR":
                    st.session_state.oportunidades_detectadas.append({
                        "Ticker": ticker,
                        "Subsector": sector,
                        "Precio": ans["precio"],
                        "RSI": ans["rsi"],
                        "Broker": ans["broker"],
                        "Motivo": ans["motivo"]
                    })
                    break # Saltamos al siguiente subsector para asegurar diversificación lineal

    # DESPLIEGUE DE ALERTAS CON OPCIÓN DE ADICIÓN DIRECTA
    if "oportunidades_detectadas" in st.session_state and st.session_state.oportunidades_detectadas:
        st.markdown("### 🚨 Oportunidades Técnicas Encontradas Hoy")
        st.write("Revisa los parámetros técnicos antes de enviarlas a tu sección de órdenes:")
        
        for op in st.session_state.oportunidades_detectadas:
            with st.container():
                col_info, col_accion = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**⚡ COMPRA SUGERIDA: {op['Ticker']}** ({op['Subsector']})")
                    st.write(f"• Precio: {op['Precio']:.2f}$ | RSI: {op['RSI']:.1f}")
                    st.write(f"• **Asignación Fiscal:** {op['Broker']}")
                    st.caption(f"Motivo técnico: {op['Motivo']}")
                with col_accion:
                    # Este botón ejecuta la adición a tu radar de compras reales aprobadas
                    if st.button(f"➕ Añadir {op['Ticker']}", key=f"add_real_{op['Ticker']}"):
                        if not any(p["Ticker"] == op["Ticker"] for p in st.session_state.cartera_bot):
                            st.session_state.cartera_bot.append({
                                "Ticker": op["Ticker"],
                                "Subsector": op["Subsector"],
                                "Precio Entrada": f"{op['Precio']:.2f} $",
                                "RSI": round(op['RSI'], 1),
                                "Canal Recomendado": op["Broker"]
                            })
                            st.session_state.efectivo -= 3000
                            st.success(f"¡{op['Ticker']} integrada en el panel!")
                            st.rerun()
            st.markdown("---")

    st.subheader("📊 Panel de Posiciones del Bot (Simulación Activa)")
    if st.session_state.cartera_bot:
        st.table(pd.DataFrame(st.session_state.cartera_bot))
        if st.button("🗑️ Liquidar y Reiniciar Cartera"):
            st.session_state.efectivo = 30000.0
            st.session_state.cartera_bot = []
            if "oportunidades_detectadas" in st.session_state:
                st.session_state.oportunidades_detectadas = []
            st.rerun()
    else:
        st.info("El bot está al 100% en liquidez. Pulsa el botón de arriba para rastrear entradas.")

# =========================================================
# PESTAÑA 3: EDITOR DE LISTAS MANUALES
# =========================================================
with pestana3:
    st.subheader("⚙️ Panel de Control de Listas")
    
    lista_a_modificar = st.selectbox("Elige lista a editar:", list(st.session_state.listas_seguimiento.keys()), key="edit_lista")
    acciones_actuales = st.session_state.listas_seguimiento[lista_a_modificar]
    
    if acciones_actuales:
        st.info(f"Componentes actuales de la lista: {', '.join(acciones_actuales)}")
    else:
        st.warning("La lista seleccionada no contiene tickers actualmente.")
    
    st.markdown("---")
    col_add, col_del = st.columns(2)
    
    with col_add:
        st.markdown("### ➕ Añadir Activo")
        nuevo_ticker = st.text_input("Introduce Ticker:", value="", key="add_t").upper().strip()
        if st.button("✅ Añadir a Lista", key="btn_add"):
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
        else:
            st.write("No hay activos disponibles para borrar.")
