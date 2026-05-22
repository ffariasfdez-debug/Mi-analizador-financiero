# =========================================================
# PESTAÑA 2: ANALIZADOR TÉCNICO Y FUNDAMENTAL (INTEGRADO)
# =========================================================
with pestaña2:
    st.subheader("🔍 Matriz de Inteligencia de Mercado (Horizonte 4 Años)")
    lista_sel = st.selectbox("Selecciona una lista:", list(mis_listas_limpias.keys()))
    
    if lista_sel:
        tickers_lista = mis_listas_limpias[lista_sel]
        datos_lista = []
        mkt_data = yf.download(tickers_lista, period="30d", group_by='ticker', progress=False)
            
        for tick in tickers_lista:
            tick = tick.strip().upper()
            t_ind = yf.Ticker(tick)
            hist = t_ind.history(period="30d")
            info = t_ind.info
            
            if not hist.empty:
                p_act = hist['Close'].iloc[-1]
                p_med = hist['Close'].mean()
                target = info.get('targetMedianPrice', p_act * 1.15)
                
                # --- NUEVA LÓGICA DE DECISIÓN A 4 AÑOS ---
                potencial_4a = ((target - p_act) / p_act) * 100
                
                # Semáforo de Inteligencia: Combinamos Tendencia + Valor
                if p_act > p_med and potencial_4a > 10:
                    sem = "🟢 COMPRAR (Alcista + Valor)"
                elif p_act < p_med and potencial_4a > 20:
                    sem = "🟡 ACUMULAR (Barata)"
                else:
                    sem = "🔴 ESPERAR (Sobrevalorada)"
                
                datos_lista.append({
                    "Ticker": tick,
                    "Precio": round(p_act, 2),
                    "Estado": sem,
                    "Potencial 12M": f"{potencial_4a:.1f}%",
                    "Target": round(target, 2)
                })
        
        st.dataframe(pd.DataFrame(datos_lista), use_container_width=True)

    st.write("---")
    st.subheader("🔍 Ficha de Inteligencia Individual")
    accion = st.text_input("Ticker:", "COHR")
    
    if accion:
        t = yf.Ticker(accion.upper())
        df = t.history(period="30d")
        
        # Presentación limpia en 3 columnas
        col1, col2, col3 = st.columns(3)
        col1.metric("Precio Actual", f"${df['Close'].iloc[-1]:.2f}")
        
        # Aquí calculamos el dictamen basado en la nueva lógica
        p_act = df['Close'].iloc[-1]
        target = t.info.get('targetMedianPrice', p_act * 1.15)
        
        if ((target - p_act)/p_act) > 0.10:
            col2.success("ACCIÓN: COMPRAR")
        else:
            col2.warning("ACCIÓN: MANTENER / ESPERAR")
            
        col3.metric("Potencial", f"{((target - p_act)/p_act)*100:.1f}%")
        
        # Gráfico sin eje en cero
        st.line_chart(df['Close'], use_container_width=True)
