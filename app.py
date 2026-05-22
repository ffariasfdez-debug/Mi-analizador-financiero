# =========================================================
    # NUEVA SECCIÓN: ANÁLISIS DETALLADO INDIVIDUAL INTELIGENTE
    # =========================================================
    st.write("---")
    st.write("### 🔍 Análisis Detallado Individual Pro")
    accion = st.text_input("Introduce el Ticker de la acción para generar Análisis y Gráfico:", "COHR", key="input_individual_v8")
    
    if accion:
        try:
            ticker_limpio = accion.upper().strip()
            
            # 1. Descarga de datos idéntica a la matriz de arriba
            datos_hist = yf.Ticker(ticker_limpio).history(period="30d")
            
            if not datos_hist.empty:
                p_actual = datos_hist['Close'].iloc[-1]
                p_media = datos_hist['Close'].mean()
                p_min = datos_hist['Low'].min()
                
                try:
                    t_fund = yf.Ticker(ticker_limpio)
                    info = t_fund.info
                    if not info or not isinstance(info, dict):
                        info = {}
                except:
                    info = {}
                
                # Cálculo de Dividendo igual que arriba
                div_yield = info.get('trailingAnnualDividendYield', None)
                if div_yield is None:
                    div_yield = info.get('dividendYield', 0.0)
                if div_yield and div_yield > 0.5:
                    div_yield = div_yield / p_actual
                calc_yield_pct = div_yield * 100 if div_yield else 0.0
                if calc_yield_pct > 15.0: 
                    calc_yield_pct = 0.0
                div_texto = f"{calc_yield_pct:.2f}%" if calc_yield_pct > 0.05 else "0.00% 🟢"
                
                # Precio Objetivo Consenso
                target_precio = info.get('targetMedianPrice', None)
                if target_precio and target_precio > 0 and target_precio < (p_actual * 4):
                    potencial = ((target_precio - p_actual) / p_actual) * 100
                    target_texto = f"{target_precio:.2f} ({potencial:+.1f}%)"
                else:
                    target_precio = p_actual * 1.12
                    target_texto = f"{p_actual * 1.12:.2f} (+12.0% Est.)"
                
                # Ratio Riesgo/Beneficio
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
                
                # Lógica del Semáforo Técnico
                if p_actual > (p_media * 1.02):
                    sem_lista = "🟢 COMPRAR"
                    color_explicacion = "green"
                    porquetexto = f"El precio actual ({p_actual:.2f}) se encuentra cotizando con fuerza por encima de su media de 30 días ({p_media:.2f}), confirmando una clara tendencia alcista de corto plazo (Momentum). El ratio Riesgo/Beneficio es {rb_texto} con un precio objetivo estimado de {target_texto}."
                    actuarpensar = "MOMENTUM ACTIVADO. Estrategia óptima: Dejar correr beneficios o acumular en pequeños retrocesos diarios sin perseguir el precio en vertical."
                elif p_actual < (p_media * 0.98):
                    sem_lista = "🔴 EVITAR"
                    color_explicacion = "red"
                    porquetexto = f"El activo ha roto soportes inmediatos y cotiza por debajo de su media de 30 días ({p_media:.2f}), reflejando presión vendedora institucional o un proceso de corrección técnica activa."
                    actuarpensar = "PRUDENCIA / ESPERA. Estrategia óptima: No intentar adivinar el suelo. Dejar que el precio estabilice y buscar una pauta de giro o un soporte mayor antes de comprometer capital."
                else:
                    sem_lista = "🟡 MANTENER"
                    color_explicacion = "orange"
                    porquetexto = f"El activo se encuentra en una fase de consolidación lateral estricta, oscilando muy cerca de su media de 30 días ({p_media:.2f}) sin una dirección clara por el momento."
                    actuarpensar = "RESERVA / HOLD. Estrategia óptima: Mantener las posiciones existentes sin alterar el tamaño. Esperar a que el semáforo rompa hacia verde o vigilar que no pierda la zona de soporte mínima."

                # 2. Mostramos la Ficha Técnica Individual en columnas limpias
                st.write(f"#### 📊 Ficha de Inteligencia: {ticker_limpio}")
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Precio Actual", f"{p_actual:.2f}")
                col2.metric("Semáforo", sem_lista)
                col3.metric("Dividendo", div_texto)
                col4.metric("Objetivo 12M", target_texto)
                col5.metric("Ratio R/B", rb_texto.split()[0])
                
                # 3. Cuadro Automático de Explicación Técnico-Táctica
                with st.expander(f"👁️ Ver Dictamen del Radar para {ticker_limpio}", expanded=True):
                    st.markdown(f"**¿POR QUÉ?:** {porquetexto}")
                    st.markdown(f"**CÓMO ACTUAR:** :{color_explicacion}[{actuarpensar}]")
                
                # 4. El Gráfico Expandido dinámicamente sin origen en cero
                df_grafico = datos_hist[['Close']].copy()
                df_grafico.index = df_grafico.index.date
                st.line_chart(df_grafico, use_container_width=True)
                
        except Exception as e:
            st.error("Error al localizar el Ticker o procesar el dictamen individual.")
