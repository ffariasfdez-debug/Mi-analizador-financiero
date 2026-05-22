# ==========================================
# SECCIÓN: ANÁLISIS DETALLADO INDIVIDUAL
# ==========================================

st.header("🔍 Análisis Detallado Individual")
st.write("Introduce el Ticker de la acción para generar Gráficos y Diagnósticos:")

# Diccionario con tus datos de compra reales/simulados para el proyecto a 4 años
# (Puedes ajustar estos valores con tus datos exactos)
datos_compra = {
    "NOW": {"precio_medio": 85.0, "cantidad": 10},
    "VVSM": {"precio_medio": 100.0, "cantidad": 15},
    "AMD": {"precio_medio": 150.0, "cantidad": 8},
}

# 1. Buscador / Selector de Ticker (Evita que desaparezca el texto al escribir)
ticker_input = st.text_input("Ticker del Activo:", value="NOW").upper().strip()

if ticker_input:
    try:
        # Descarga de datos históricos para el gráfico (últimos 30 días)
        datos_ticker = yf.Ticker(ticker_input)
        hist = datos_ticker.history(period="1mo")
        
        if not hist.empty:
            # Obtener el precio de cierre más reciente
            precio_actual = float(hist['Close'].iloc[-1])
            
            # Verificar si tenemos este activo en cartera para activar las métricas y el semáforo
            if ticker_input in datos_compra:
                precio_compra = datos_compra[ticker_input]["precio_medio"]
                cantidad_acciones = datos_compra[ticker_input]["cantidad"]
                
                # Cálculos de rendimiento
                rendimiento_porcentaje = ((precio_actual - precio_compra) / precio_compra) * 100
                rendimiento_absoluto = (precio_actual - precio_compra) * cantidad_acciones
                valor_total_posicion = precio_actual * cantidad_acciones
                
                # --- DETECCIÓN DEL SEMÁFORO Y EL CONSEJO (Lógica blindada) ---
                if rendimiento_porcentaje > 2.0:
                    semaforo_color = "🟢"
                    semaforo_texto = "ÓPTIMO / GANANCIAS"
                    consejo_texto = f"El activo responde positivamente situándose un **{rendimiento_porcentaje:.2f}%** por encima de tu precio de entrada. Mantener la posición para maximizar el rendimiento del proyecto a largo plazo."
                elif -2.0 <= rendimiento_porcentaje <= 2.0:
                    semaforo_color = "🟡"
                    semaforo_texto = "NEUTRAL / CONSOLIDACIÓN"
                    consejo_texto = "El activo se encuentra en un rango lateral estable cerca de tu precio medio. Comportamiento esperado de consolidación, monitorizar sin necesidad de ejecutar movimientos."
                else:
                    semaforo_color = "🔴"
                    semaforo_texto = "ALERTA / PÉRDIDAS"
                    consejo_texto = f"Posición actualmente en pérdidas (**{rendimiento_porcentaje:.2f}%**). Evaluar si el activo se acerca a soportes históricos importantes para considerar una acumulación estratégica a largo plazo."
                
                # 2. RENDERIZADO DE INDICADORES (Semáforo y Consejo)
                st.subheader(f"{semaforo_color} Estado: {semaforo_texto}")
                st.info(f"💡 **Consejo Dinámico:** {consejo_texto}")
                
                st.write("---")
                
                # 3. RENDERIZADO DE MÉTRICAS NUMÉRICAS (KPIs)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Participaciones", f"{cantidad_acciones} ud")
                with col2:
                    st.metric("Precio Compra vs Actual", f"{precio_compra:.2f}€", f"{precio_actual:.2f}€")
                with col3:
                    st.metric("Rendimiento (%)", f"{rendimiento_porcentaje:.2f}%")
                with col4:
                    st.metric("Beneficio Neto Total", f"{rendimiento_absoluto:.2f}€", delta_color="normal")
            
            else:
                # Si el activo no está en cartera, avisa pero permite ver el gráfico general
                st.warning("⚠️ Este activo no se encuentra registrado en tu cartera. Mostrando solo datos generales de mercado.")
                precio_compra = None

            # 4. PREPARACIÓN Y MEJORA DEL GRÁFICO DE TENDENCIA
            # Añadimos la columna de Precio Medio de Compra como una línea recta si existe
            grafico_data = pd.DataFrame(hist['Close'])
            if precio_compra:
                grafico_data['Mi Precio de Compra'] = precio_compra
            
            # Renderizado del gráfico en el panel
            st.write(f"**Evolución del precio de {ticker_input} (Último mes):**")
            st.line_chart(grafico_data)
            
        else:
            st.error(f"No se han encontrado datos disponibles para el ticker: {ticker_input}")
            
    except Exception as e:
        st.error(f"Error al conectar con la base de datos financiera: {e}")
