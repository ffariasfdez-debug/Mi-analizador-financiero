# ==========================================
# ... (Debajo de donde introduces el Ticker) ...
            
            precio_actual = float(hist['Close'].iloc[-1])
            
            # El sistema te pide tus datos reales en la propia pantalla
            st.write("🔧 **Introduce tus datos de compra para el análisis:**")
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                precio_compra = st.number_input("Tu Precio Medio de Compra (€):", value=precio_actual)
            with col_in2:
                cantidad_acciones = st.number_input("Cantidad de participaciones:", value=1, step=1)
            
            # A partir de aquí, el semáforo y las métricas calculan con TUS datos reales
            rendimiento_porcentaje = ((precio_actual - precio_compra) / precio_compra) * 100
            rendimiento_absoluto = (precio_actual - precio_compra) * cantidad_acciones
