<div class="card shadow mb-4">
    <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
        <h6 class="m-0 font-weight-bold text-primary">
            <i class="fas fa-book-open mr-2"></i>Libro de Registro de Posiciones (Simulación 30k)
        </h6>
        <span class="badge badge-success">Fondos Disponibles: 22.000 €</span>
    </div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-bordered table-hover" id="tablaPosiciones" width="100%" cellspacing="0">
                <thead class="thead-light">
                    <tr>
                        <th>Fecha/Hora</th>
                        <th>Ticker</th>
                        <th>Cantidad (Títulos)</th>
                        <th>Precio Compra</th>
                        <th>Precio Actual</th>
                        <th>Capital Invertido</th>
                        <th>Rendimiento (%)</th>
                        <th>Bróker Asignado</th>
                    </tr>
                </thead>
                <tbody id="cuerpoPosiciones">
                    <tr>
                        <td>18/05/2026 15:45</td>
                        <td><strong class="text-dark">ASM.AS</strong></td>
                        <td class="font-weight-bold">2.3474</td>
                        <td>852.00 €</td>
                        <td class="text-primary font-weight-bold" id="act-asm">855.10 €</td>
                        <td>2.000 €</td>
                        <td><span class="badge badge-pill badge-success font-weight-bold">+0.36%</span></td>
                        <td><span class="text-secondary">Bolero</span></td>
                    </tr>
                    <tr>
                        <td>18/05/2026 15:45</td>
                        <td><strong class="text-dark">KLAC</strong></td>
                        <td class="font-weight-bold">2.4154</td>
                        <td>828.00 €</td>
                        <td class="text-primary font-weight-bold" id="act-klac">824.70 €</td>
                        <td>2.000 €</td>
                        <td><span class="badge badge-pill badge-danger font-weight-bold">-0.40%</span></td>
                        <td><span class="text-secondary">Revolut Be</span></td>
                    </tr>
                    <tr>
                        <td>18/05/2026 15:45</td>
                        <td><strong class="text-dark">MPWR</strong></td>
                        <td class="font-weight-bold">2.4301</td>
                        <td>823.00 €</td>
                        <td class="text-primary font-weight-bold" id="act-mpwr">818.50 €</td>
                        <td>2.000 €</td>
                        <td><span class="badge badge-pill badge-danger font-weight-bold">-0.54%</span></td>
                        <td><span class="text-secondary">ING España</span></td>
                    </tr>
                    <tr>
                        <td>18/05/2026 15:45</td>
                        <td><strong class="text-dark">AME</strong></td>
                        <td class="font-weight-bold">5.8139</td>
                        <td>172.00 €</td>
                        <td class="text-primary font-weight-bold" id="act-ame">172.80 €</td>
                        <td>1.000 €</td>
                        <td><span class="badge badge-pill badge-success font-weight-bold">+0.46%</span></td>
                        <td><span class="text-secondary">ING España</span></td>
                    </tr>
                    <tr>
                        <td>18/05/2026 15:45</td>
                        <td><strong class="text-dark">TFX</strong></td>
                        <td class="font-weight-bold">4.7169</td>
                        <td>212.00 €</td>
                        <td class="text-primary font-weight-bold" id="act-tfx">212.15 €</td>
                        <td>1.000 €</td>
                        <td><span class="badge badge-pill badge-success font-weight-bold">+0.07%</span></td>
                        <td><span class="text-secondary">Bolero</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
// Función lógica automatizada para refrescar los rendimientos dinámicamente
function actualizarRendimientosSimulacion() {
    const posiciones = [
        { id: 'asm', compra: 852.00 },
        { id: 'klac', compra: 828.00 },
        { id: 'mpwr', compra: 823.00 },
        { id: 'ame', compra: 172.00 },
        { id: 'tfx', compra: 212.00 }
    ];

    posiciones.forEach(pos => {
        const celdaActual = document.getElementById(`act-${pos.id}`);
        if (celdaActual) {
            const precioActual = parseFloat(celdaActual.innerText);
            const rendimiento = ((precioActual - pos.compra) / pos.compra) * 100;
            const celdaPorcentaje = celdaActual.nextElementSibling.firstElementChild;
            
            // Actualizar texto del porcentaje
            celdaPorcentaje.innerText = (rendimiento >= 0 ? '+' : '') + rendimiento.toFixed(2) + '%';
            
            // Cambiar clase de color según el semáforo de momentum
            if (rendimiento >= 0) {
                celdaPorcentaje.className = "badge badge-pill badge-success font-weight-bold";
            } else {
                celdaPorcentaje.className = "badge badge-pill badge-danger font-weight-bold";
            }
        }
    });
}
</script>
