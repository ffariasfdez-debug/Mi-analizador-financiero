import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# Configuración de la página completa
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# --- TITULO PRINCIPAL ---
st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# --- DICCIONARIO MAESTRO AMPLIADO A 40 ACTIVOS AUDITADOS ---
mis_listas_limpias = {
    "Robótica": [
        # --- Estados Unidos y Europa ---
        "ISRG", "CGNX", "ADI", "AME", "ROCK", "ROK", "TER", "FTV", "NOW", "PTC", 
        "ANSS", "GWW", "SYM", "PATH", "AZTA", "ESTC", "NXPI", "TXN", "ON", "A",
        "SIE.DE", "SU.PA", "ABB", "SCHN.PA", "KRN.DE", "TRMB", "AZO", "GFL",
        # --- Japón (Extensiones nativas .T para evitar bloqueos) ---
        "6361.T", "6594.T", "6645.T", "6954.T", "6758.T", "6762.T", "6501.T", 
        "7752.T", "4543.T", "7741.T", "4901.T", "6141.T", "6273.T"
    ],
    "Semiconductores": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "TSM", "AVGO", "LRCX", "AMAT"],
    "Fotónica": ["IPGP", "LITE", "COHR", "VNT", "FN", "MKSI", "NKTX", "LIMO"],
    "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR", "CGNX", "ISRG", "COHR"]
}

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico y Fundamental", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K (INTACTA)
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Gestión Autónoma por Momentum Técnico")
    
    compras_fijas = [
        {"Ticker": "ASM.AS", "Precio Compra": 852.00, "Capital Invertido": 2000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "KLAC", "Precio Compra": 1755.30, "Capital Invertido": 2000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "TFX", "Precio Compra": 133.32, "Capital Invertido": 1000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "AME", "Precio Compra": 227.10, "Capital Invertido": 1000.0, "Broker": "Bolero / Rev"},
        {"Ticker": "MPWR", "Precio Compra": 1514.83, "Capital Invertido": 2000.0, "Broker": "ING España"}
    ]
    
    @st.cache_data(ttl=60)
    def cargar_posiciones_con_previsiones(lista):
        tabla_final = []
        tickers_bot = [c["Ticker"] for c in lista]
        try:
            datos_bloque = yf.download(tickers_bot, period="30d", group_by='ticker', progress=False)
        except:
            datos_bloque = pd.DataFrame()

        for c in lista:
            tick = c["Ticker"]
            try:
                if not datos_bloque.empty and tick in datos_bloque:
                    historial = datos_bloque[tick]
                    precio_actual = historial['Close'].dropna().iloc[-1]
                    media_tendencia = historial['Close'].dropna().mean()
                else:
                    precio_actual = c["Precio Compra"]
                    media_tendencia = c["Precio Compra"]
            except:
                precio_actual = c["Precio Compra"]
                media_tendencia = c["Precio Compra"]
                
            cantidad = round(c["Capital Invertido"] / c["Precio Compra"], 4)
            rendimiento = round(((precio_actual - c["Precio Compra"]) / c["Precio Compra"]) * 100, 2)
            flecha = "🔼 +" if rendimiento >= 0 else "🔽 "
            
            if precio_actual > (media_tendencia * 1.02):
                semaforo_tabla = "🟢 COMPRAR / AÑADIR"
                prev_medio = "📈 Tendencia Alcista Fuerte"
                accion_sugerida = "Dejar correr beneficios."
            elif precio_actual < (media_tendencia * 0.98):
                semaforo_tabla = "🔴 EVITAR / RECORTE"
                prev_medio = "📉 Corrección de Corto"
                accion_sugerida = "Esperar soporte de giro."
            else:
                semaforo_tabla = "🟡 MANTENER"
                prev_medio = "↔️ Lateral / Consolidación"
                accion_sugerida = "Mantener posición."

            tabla_final.append({
                "Ticker": tick,
                "Cantidad": cantidad,
                "Precio Compra": f"{c['Precio Compra']:.2f}",
                "Precio Actual": f"{precio_actual:.2f}",
                "Rendimiento": f"{flecha}{rendimiento}%",
                "Semáforo Corto Plazo": semaforo_tabla,
                "Previsión Medio Plazo": prev_medio,
                "Consejo del Radar": accion_sugerida,
                "Broker": c["Broker"]
            })
        return pd.DataFrame(tabla_final)

    df_bot = cargar_posiciones_con_previsiones(compras_fijas)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Fondo Estrategia", "30.000 €")
    c2.metric("Caja Líquida", "22.000,00 €")
    c3.metric("Posiciones Abiertas", "5")
    
    st.dataframe(df_bot, use_container_width=True)

# =========================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO Y FUNDAMENTAL
# =========================================================
with pestaña2:
    st.subheader("🔍 Matriz de Inteligencia de Mercado (Flujos y Valoración)")
    
    st.write("### 📁 Cargar una Lista de Seguimiento Completa")
    lista_sel = st.selectbox("Selecciona una lista pregrabada para proyectar:", list(mis_listas_limpias.keys()), key="selector_analisis_v8")
    
    if lista_sel:
        tickers_lista = mis_listas_limpias[lista_sel]
        
        with st.spinner(f"Sincronizando flujos institucionales para {lista_sel}..."):
            datos_lista = []
            
            try:
                mkt_data = yf.download(tickers_lista, period="30d", group_by='ticker', progress=False)
            except:
                mkt_data = pd.DataFrame()
                
            for tick in tickers_lista:
                tick = tick.strip().upper()
                try:
                    if not mkt_data.empty and tick in mkt_data:
                        h = mkt_data[tick].dropna(subset=['Close'])
                    else:
                        t_individual = yf.Ticker(tick)
                        h = t_individual.history(period="30d")
                        
                    if h.empty:
                        datos_lista.append({
                            "Ticker": tick, 
                            "Precio Actual": 0.0, 
                            "Semáforo Técnico": "❔ SIN DATOS",
                            "Dividendo Anual": "0.00% 🟢", 
                            "Objetivo 12M (Potencial)": "No disp.",
                            "Ratio Riesgo/Beneficio": "N/A", 
                            "Volatilidad (Beta)": "1.00"
                        })
                        continue
                        
                    p_actual = h['Close'].iloc[-1]
                    p_media = h['Close'].mean()
                    p_min = h['Low'].min()
                    
                    try:
                        t_fund = yf.Ticker(tick)
                        info = t_fund.info
                        if not info or not isinstance(info, dict):
                            info = {}
                    except:
                        info = {}
                    
                    # FILTRO DE DIVIDENDOS AUDITADO
                    div_yield = info.get('trailingAnnualDividendYield', None)
                    if div_yield is None:
                        div_yield = info.get('dividendYield', 0.0)
                        
                    if div_yield and div_yield > 0.5:
                        div_yield = div_yield / p_actual
                        
                    calc_yield_pct = div_yield * 100 if div_yield else 0.0
                    if calc_yield_pct > 15.0: 
                        calc_yield_pct = 0.0
                        
                    div_texto = f"{calc_yield_pct:.2f}%" if calc_yield_pct > 0.05 else "0.00% 🟢"
                    
                    # PRECIO OBJETIVO CONSENSO 12 MESES
                    target_precio = info.get('targetMedianPrice', None)
                    if target_precio and target_precio > 0 and target_precio < (p_actual * 4):
                        potencial = ((target_precio - p_actual) / p_actual) * 100
                        target_texto = f"{target_precio:.2f} ({potencial:+.1f}%)"
                    else:
                        target_precio = p_actual * 1.12
                        target_texto = f"{p_actual * 1.12:.2f} (+12.0% Est.)"
                    
                    # RATIO RIESGO / BENEFICIO TÁCTICO
                    riesgo_bajada = max(0.5, ((p_actual - p_min) / p_actual) * 100)
                    beneficio_subida = max(0.5, ((target_precio - p_actual) / p_actual) * 100)
                    ratio_rb = beneficio_subida / riesgo_bajada
                    
                    if ratio_rb >= 1.8:
                        rb_texto = f"{ratio_rb:.1f}x 🔥 Excelente"
                    elif ratio_rb >= 1.0:
                        rb_texto = f"{ratio_rb:.1f}x 📊 Favorable"
                    else:
                        rb_texto = f"{ratio_rb:.1f}x ⚠️ Riesgo Alto"
                        
                    beta = info.get('beta', 1.0)
                    beta_texto = f"{beta:.2f}" if beta else "1.00"

                    if p_actual > (p_media * 1.02):
                        sem_lista = "🟢 COMPRAR"
                    elif p_actual < (p_media * 0.98):
                        sem_lista = "🔴 EVITAR"
                    else:
                        sem_lista = "🟡 MANTENER"
                        
                    datos_lista.append({
                        "Ticker": tick, 
                        "Precio Actual": round(p_actual, 2), 
                        "Semáforo Técnico": sem_lista,
                        "Dividendo Anual": div_texto,
                        "Objetivo 12M (Potencial)": target_texto,
                        "Ratio Riesgo/Beneficio": rb_texto,
                        "Volatilidad (Beta)": beta_texto
                    })
                except:
                    datos_lista.append({
                        "Ticker": tick, 
                        "Precio Actual": 0.0, 
                        "Semáforo Técnico": "❔ ERROR FILA",
                        "Divid
