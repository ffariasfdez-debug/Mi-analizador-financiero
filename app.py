if not hist.empty:
            precio_actual = float(hist['Close'].iloc[-1])
            
            # Si el activo está registrado en tu proyecto, calcula métricas, semáforo y consejo
            if ticker_input in datos_compra:
                precio_compra = datos_compra[ticker_input]["precio_medio"]
                cantidad_acciones = datos_compra[ticker_input]["cantidad"]
                
                rendimiento_porcentaje = ((precio_actual - precio_compra) / precio_compra) * 100
                rendimiento_absoluto = (precio_actual - precio_compra) * cantidad_acciones
                
                # Definición lógica del Semáforo y el Consejo Dinámico
                if rendimiento_porcentaje > 2.0:
                    semaforo_color, semaforo_texto = "🟢", "ÓPTIMO / GANANCIAS"
                    consejo_texto = f"El activo responde positivamente situándose un **{rendimiento_porcentaje:.2f}%** por encima de tu precio de entrada. Mantener para el objetivo del proyecto a largo plazo."
                elif -2.0 <= rendimiento_porcentaje <= 2.0:
                    semaforo_color, semaforo_texto = "🟡", "NEUTRAL / CONSOLIDACIÓN"
                    consejo_texto = "El activo se mantiene estable en zona de soporte lateral. Comportamiento en rango de consolidación esperado."
                else:
                    semaforo_color, semaforo_texto = "🔴", "ALERTA / PÉRDIDAS"
                    consejo_texto = f"Posición en pérdidas temporales (**{rendimiento_porcentaje:.2f}%**). Evaluar soportes clave por si el plan a largo plazo aconseja acumulación."
                
                # 1. INDICADORES VISUALES
                st.markdown(f"### {semaforo_color} Estado: {semaforo_texto}")
                st.info(f"💡 **Consejo Dinámico:** {consejo_texto}")
                st.write("---")
                
                # 2. MÉTRICAS NUMÉRICAS (KPIs)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Participaciones", f"{cantidad_acciones} ud")
                with col2:
                    st.metric("Precio Actual", f"{precio_actual:.2f} €", f"Tu coste: {precio_compra:.2f} €")
                with col3:
                    st.metric("Rendimiento (%)", f"{rendimiento_porcentaje:.2f} %")
                with col4:
                    st.metric("Beneficio Neto Total", f"{rendimiento_absoluto:.2f} €")
            else:
                st.warning("⚠️ Activo de mercado general (Fuera de cartera). Mostrando datos de cotización estándar.")
            
            st.write("---")
            
            # 3. EL GRÁFICO DE COTIZACIÓN REAL (Con escala perfecta y limpia)
            st.write(f"**Evolución del precio de {ticker_input} (Último mes):**")
            grafico_limpio = pd.DataFrame(hist['Close'])
            st.line_chart(grafico_limpio)
