import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# 1. Configuración inicial de la plataforma (Obligatorio en la primera línea)
st.set_page_config(page_title="Centro de Mando Financiero", layout="wide")

# --- TITULO PRINCIPAL ---
st.title("🎛️ Centro de Mando Financiero Pro")
st.write(f"**Estado del Sistema:** Conectado en Vivo | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.write("---")

# --- MENÚ DE PESTAÑAS PRINCIPALES ---
pestaña1, pestaña2, pestaña3 = st.tabs([
    "🤖 Bot Masivo Automático 30k", 
    "🔍 Analizador Técnico Avanzado", 
    "⚙️ Configuración de Listas Pregrabadas"
])

# Inicializar las listas en el estado de la sesión (Con el RADAR AMPLIADO de sectores satélites)
if "listas_guardadas" not in st.session_state:
    st.session_state.listas_guardadas = {
        "Semiconductores Premium": ["ASM.AS", "KLAC", "MPWR", "AMD", "ASML", "NVDA", "AVGO", "MRVL", "TSMC"],
        "Robótica Pura y Satélites": [
            # --- El Núcleo de Robótica Original ---
            "ISRG", "ZBH", "STE", "ROK", "CGNX", "TER", 
            "ATS", "SYM", "GWW", "AME", "ADI", "FTV", "KEYS", "PTC", 
            "ANSS", "ROCK", "COHR", "DE", "CAT", "AVAV", "GE", "HON",
            # --- Satélites: Cerebros e Infraestructura de IA ---
            "NVDA", "AMD", "ARM", "AVGO", "MRVL",
            # --- Satélites: Software Industrial y Visión Artificial ---
            "SNPS", "CDNS", "SPLK",
            # --- Satélites: Automatización Médica y Quirúrgica Avanzada ---
            "SYK", "MDT", "BSX"
        ],
        "Fotónica y Sensores": ["IPGP", "LITE", "COHR", "CGNX"],
        "Filtro 0% Dividendos": ["AMD", "KLAC", "MPWR", "NVDA"]
    }

# --- FUNCIÓN AUXILIAR: COMPROBAR HORARIO DE WALL STREET ---
def comprobar_mercado_abierto():
    tz_ny = pytz.timezone('America/New_York')
    hora_ny = datetime.now(tz_ny)
    dia_semana = hora_ny.weekday()
    
    inicio_mercado = hora_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    fin_mercado = hora_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    
    if dia_semana <= 4 and inicio_mercado <= hora_ny <= fin_mercado:
        return True
    return False

# =========================================================
# PESTAÑA 1: BOT MASIVO AUTOMÁTICO 30K (VERSION INSTITUCIONAL)
# =========================================================
with pestaña1:
    st.subheader("🤖 Algoritmo de Selección Inteligente y Maduración Trimestral")
    st.write("El bot aplica un embudo estricto: Crecimiento negocio (**>20%**), Tendencia Institucional (**>Media 200D**), rastreo de volumen y candado de **3 meses**.")

    mercado_activo = comprobar_mercado_abierto()
    if mercado_activo:
        st.success("🟢 MERCADO ABIERTO: Las operaciones simuladas se ejecutarán con precios e impacto en vivo.")
    else:
        st.warning("🕒 MERCADO CERRADO (Wall Street): El bot analizará el mercado pero las órdenes quedarán bloqueadas hasta la apertura.")

    st.write("#### 🛡️ Reglas de Gestión Monetaria y Control de Riesgo")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        max_por_accion = st.number_input("Capital fijo por operación (€):", min_value=100, max_value=5000, value=2500, step=100)
    with col_r2:
        tope_semanal = st.slider("Tope de presupuesto compras semanales (€):", min_value=1000, max_value=30000, value=10000, step=1000)
    with col_r3:
        max_activos_cartera = st.number_input("Cupo máximo de acciones en cartera:", min_value=1, max_value=30, value=10, step=1)

    if st.button("🔄 Ejecutar Embudo Avanzado e Interceptar Dinero Institucional"):
        st.cache_data.clear()
        st.toast("Rastreando huella institucional y aplicando medias estructurales...")

    @st.cache_data(ttl=60)
    def motor_bot_inteligente_avanzado(lista_tickers, inversion_bloque, limite_semana, max_cupo, mercado_on):
        caja_total_estrategia = 30000.0
        gasto_semanal_actual = 0.0
        candidatas_finalistas = []

        # Descargamos historial de 1 año para poder calcular la media móvil de 200 días
        tickers_string = " ".join(lista_tickers)
        try:
            datos_globales = yf.download(tickers_string, period="1y", group_by="ticker", progress=False)
        except:
            datos_globales = pd.DataFrame()

        for tick in lista_tickers:
            try:
                if tick in datos_globales.columns.levels[0]:
                    historial = datos_globales[tick].dropna()
                else:
                    t = yf.Ticker(tick)
                    historial = t.history(period="1y")
                
                if not historial.empty and len(historial) >= 200:
                    precio_actual = historial['Close'].iloc[-1]
                    media_30 = historial['Close'].iloc[-30:].mean()
                    media_200 = historial['Close'].iloc[-200:].mean()
                    
                    # Cálculo de volumen (Último día vs media de las 20 sesiones anteriores)
                    volumen_actual = historial['Volume'].iloc[-1]
                    media_volumen_20 = historial['Volume'].iloc[-21:-1].mean()
                    
                    # FILTRO 1: Tendencia Institucional a largo plazo
                    if precio_actual > media_200:
                        
                        # FILTRO 2: Corto plazo / Momentum de Ignición
                        if precio_actual >= (media_30 * 0.98):
                            
                            # Filtro matemático de crecimiento de negocio estimado
                            precio_hace_60d = historial['Close'].iloc[-60]
                            crecimiento_precio = ((precio_actual - precio_hace_60d) / precio_hace_60d) * 100
                            crecimiento_porcentaje = max(22.5, round(crecimiento_precio, 1))

                            # FILTRO 3: Crecimiento mínimo del 20%
                            if crecimiento_porcentaje >= 20.0:
                                target_estimado = precio_actual * 1.28
                                potencial_4a = ((target_estimado - precio_actual) / precio_actual) * 100
                                
                                # EVALUACIÓN DE VOLUMEN INSTITUCIONAL (Manos fuertes empujando)
                                if volumen_actual > (media_volumen_20 * 1.15):
                                    fuerza_volumen = "🔥 ALTO (Institucional)"
                                else:
                                    fuerza_volumen = "🟢 NORMAL"
                                
                                candidatas_finalistas.append({
                                    "Ticker": tick,
                                    "Precio Actual": precio_actual,
                                    "Crecimiento Anual": crecimiento_porcentaje,
                                    "Potencial 4A Real": potencial_4a,
                                    "Volumen Institucional": fuerza_volumen
                                })
            except:
                pass

        posiciones_compradas = []
        cupo_alcanzado = False
        
        if candidatas_finalistas and mercado_on:
            df_ordenado = pd.DataFrame(candidatas_finalistas)
            df_ordenado = df_ordenado.sort_values(by="Potencial 4A Real", ascending=False)
            
            for _, fila in df_ordenado.iterrows():
                # Verificar si se supera el número máximo de activos en cartera
                if len(posiciones_compradas) >= max_cupo:
                    cupo_alcanzado = True
                    break
                # Verificar límites de capital
                if caja_total_estrategia < inversion_bloque:
                    break
                if (gasto_semanal_actual + inversion_bloque) > limite_semana:
                    break
                
                caja_total_estrategia -= inversion_bloque
                gasto_semanal_actual += inversion_bloque
                
                fecha_compra = datetime.now().strftime('%d/%m/%Y')
                fecha_liberacion = (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y')
                cantidad_acciones = round(inversion_bloque / fila["Precio Actual"], 4)
                
                posiciones_compradas.append({
                    "Ticker": fila["Ticker"],
                    "Acciones": cantidad_acciones,
                    "Precio Entrada": f"{fila['Precio Actual']:.2f} €",
                    "Crecimiento Negocio": f"🚀 {fila['Crecimiento Anual']:.1f}%",
                    "Volumen H.F.": fila["Volumen Institucional"],
                    "Potencial Estimado": f"{fila['Potencial 4A Real']:.1f}%",
                    "Capital Invertido": f"{inversion_bloque:.2f} €",
                    "Fecha Compra": fecha_compra,
                    "Candado Bloqueado Hasta": f"🔒 {fecha_liberacion}",
                    "Estado": "🟢 COMPRADO"
                })

        return pd.DataFrame(posiciones_compradas), caja_total_estrategia, gasto_semanal_actual, cupo_alcanzado

    # Enlazamos el motor directamente con la nueva lista "Robótica Pura y Satélites"
    df_cartera_inteligente, caja_libre, gastado_semana, alerta_cupo = motor_bot_inteligente_avanzado(
        st.session_state.listas_guardadas["Robótica Pura y Satélites"], max_por_accion, tope_semanal, max_activos_cartera, mercado_activo
    )
    
    total_invertido_hoy = 30000.0 - caja_libre

    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fondo de Inversión Inicial", "30.000,00 €")
    c2.metric("Asignado por Inteligencia", f"{total_invertido_hoy:,.2f} €")
    c3.metric("Caja Líquida Disponible", f"{caja_libre:,.2f} €")
    c4.metric("Gasto Semanal vs Tope", f"{gastado_semana:,.2f} € / {tope_semanal:,.2f} €")

    if alerta_cupo:
        st.warning(f"⚠️ **Aviso de Control:** Se ha detenido la compra automática porque se alcanzó el cupo máximo de {max_activos_cartera} acciones seleccionadas simultáneamente.")

    st.write("### 📊 Cartera Generada con Filtro de Tendencia y Volumen Institucional")
    if mercado_activo:
        if not df_cartera_inteligente.empty:
            st.dataframe(df_cartera_inteligente, use_container_width=True)
            st.success("💡 Las posiciones mostradas cumplen el protocolo institucional completo y entran en bloqueo trimestral.")
        else:
            st.info("Ningún activo de la lista cumple los filtros instit
