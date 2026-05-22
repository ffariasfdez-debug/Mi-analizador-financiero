# =========================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO Y FUNDAMENTAL AVANZADO
# =========================================================
with pestaña2:
    st.subheader("🔍 Matriz de Inteligencia de Mercado")
    
    st.write("### 📁 Cargar una Lista de Seguimiento Completa")
    lista_sel = st.selectbox("Selecciona una lista pregrabada para proyectar:", list(st.session_state.mis_listas_limpias.keys()), key="selector_analisis_v8")
    
    if lista_sel:
        tickers_lista = st.session_state.mis_listas_limpias[lista_sel]
        
        with st.spinner(f"Sincronizando flujos institucionales..."):
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
                            "Ticker": tick, "Precio Actual": 0.0, "Semáforo Técnico": "❔ SIN DATOS",
                            "Filtro Fiscal (Destino Seguro)": "N/A", "Dividendo": "0.00%", 
                            "Objetivo 12M": "No disp.", "Ratio R/B": "N/A", "Beta": "1.00"
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
                    
                    # --- AUDITORÍA DE DIVIDENDOS EXIGENTE ---
                    div_yield = info.get('trailingAnnualDividendYield', None)
                    if div_yield is None:
                        div_yield = info.get('dividendYield', 0.0)
                        
                    if div_yield and div_yield > 0.5:
                        div_yield = div_yield / p_actual
                        
                    calc_yield_pct = div_yield * 100 if div_yield else 0.0
                    if calc_yield_pct > 15.0: 
                        calc_yield_pct = 0.0
                    
                    # --- AUDITORÍA FISCAL DE DIVIDENDOS ---
                    if calc_yield_pct == 0.0:
                        filtro_fiscal = "🟢 APTO: ING España (0% Absoluto)"
                        div_texto = "0.00% 🟢"
                    else:
                        filtro_fiscal = "🚫 PROHIBIDO EN ING -> Solo Revolut"
                        div_texto = f"{calc_yield_pct:.2f}% ⚠️"
                    
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

                    # CONFIGURACIÓN DEL MOMENTUM TÉCNICO DE CORTO PLAZO
                    if p_actual >= (p_media * 1.01):
                        sem_lista = "🟢 COMPRAR"
                    elif p_actual <= (p_media * 0.99):
                        sem_lista = "🔴 EVITAR"
                    else:
                        sem_lista = "🟡 MANTENER"
                        
                    datos_lista.append({
                        "Ticker": tick, 
                        "Precio Actual": round(p_actual, 2), 
                        "Semáforo Técnico": sem_lista,
                        "Filtro Fiscal (Destino Seguro)": filtro_fiscal,
                        "Dividendo": div_texto,
                        "Objetivo 12M (Potencial)": target_texto,
                        "Ratio Riesgo/Beneficio": rb_texto,
                        "Volatilidad (Beta)": beta_texto
                    })
                except:
                    datos_lista.append({
                        "Ticker": tick, "Precio Actual": 0.0, "Semáforo Técnico": "❔ ERROR FILA",
                        "Filtro Fiscal (Destino Seguro)": "Error", "Dividendo": "N/A",
                        "Objetivo 12M (Potencial)": "No disp.", "Ratio Riesgo/Beneficio": "N/A", "Volatilidad (Beta)": "1.00"
                    })
            
            if datos_lista:
                df_mostrar = pd.DataFrame(datos_lista)
                st.dataframe(df_mostrar, use_container_width=True)
                st.caption(f"📊 Control de volumen total: {len(df_mostrar)} activos proyectados.")
            else:
                st.warning("Descargando datos...")

    st.write("---")
    st.write("### 🔍 Análisis Detallado Individual")
    accion = st.text_input("Introduce el Ticker de la acción para generar Gráficos:", "COHR", key="input_individual_v8")
    if accion:
        try:
            datos_hist = yf.Ticker(accion.upper().strip()).history(period="30d")
            if not datos_hist.empty:
                df_grafico = datos_hist[['Close']].copy()
                df_grafico.index = df_grafico.index.date
                st.line_chart(df_grafico, use_container_width=True)
        except:
            st.error("Error al localizar el Ticker.")
