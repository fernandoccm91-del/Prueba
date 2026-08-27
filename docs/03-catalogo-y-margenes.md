# Catálogo, costos e inversión

Todo lo de acá abajo está construido sobre los datos reales de
`02-datos-mercadolibre-chile.md`. El script que genera las tablas está en
`docs/datos/costeo.py` — cambia el dólar o los costos FOB y recalcula.

## Supuestos del modelo

| Variable | Valor usado | Nota |
|---|---|---|
| Tipo de cambio | **$950 CLP/USD** | Ajusta al dólar observado del día antes de decidir |
| Flete | **USD 2,20/kg** | Marítimo LCL consolidado. Aéreo consolidado ≈ USD 7/kg; DHL puerta a puerta USD 20–35/kg |
| Seguro | 1% del FOB | |
| Arancel | **0%** | China tiene TLC con Chile desde 2006. Requiere **Certificado de Origen Formulario F** emitido por el proveedor. Sin ese papel pagas 6% sobre CIF |
| IVA importación | 19% sobre CIF + arancel | **No lo cuento como costo**: si tienes empresa con iniciación de actividades es crédito fiscal contra el IVA de tus ventas. Sí es un desembolso de caja que tienes que financiar |
| Gastos de despacho | $400.000 por pedido | Handling del forwarder, almacenaje, transporte interno. Conservador |

> **Sobre el agente de aduanas:** bajo **USD 3.000 FOB** en régimen courier puedes
> hacer despacho simplificado sin agente. El pedido de prueba de abajo son USD 1.540
> FOB — queda cómodamente bajo el umbral. Ese es un motivo más para partir chico.

## Catálogo de lanzamiento — 7 SKU

| SKU | FOB USD | Peso | Unid. | CIF USD | **Landed CLP** | **PVP** | Margen | % | Múltiplo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Alfombra de diatomea 60x39 | 5,20 | 2,0 kg | 60 | 9,65 | $10.419 | **$27.990** | $17.571 | 62,8% | 2,7x |
| Set coordinado 4 piezas cerámica mate | 6,80 | 1,4 kg | 60 | 9,95 | $10.701 | **$37.990** | $27.289 | 71,8% | 3,6x |
| Dispensador de pared doble 2×400 ml | 4,10 | 0,7 kg | 50 | 5,68 | $6.647 | **$22.990** | $16.343 | 71,1% | 3,5x |
| Organizador de ducha adhesivo 2 niveles | 3,90 | 0,8 kg | 50 | 5,70 | $6.664 | **$21.990** | $15.326 | 69,7% | 3,3x |
| Bandeja organizadora de lavamanos | 2,90 | 0,6 kg | 40 | 4,25 | $5.287 | **$16.990** | $11.703 | 68,9% | 3,2x |
| Toallero-repisa de pared negro mate | 12,00 | 1,8 kg | 20 | 16,08 | $16.526 | **$69.990** | $53.464 | 76,4% | 4,2x |
| Set 4 ganchos adhesivos acero negro | 1,60 | 0,3 kg | 40 | 2,28 | $3.412 | **$9.990** | $6.578 | 65,8% | 2,9x |

**Totales del pedido 1:** 320 unidades · 351 kg · **USD 1.540 FOB**
**Inversión en inventario (landed):** **$2.611.220 CLP**
**Valor de venta del inventario completo:** **$8.686.800 CLP**

### Por qué cada SKU está en la lista

| SKU | Rol | Justificación con datos |
|---|---|---|
| **Alfombra de diatomea** | Héroe / captación | 1 sola oferta activa en ML a $11.441 vs 16 ofertas de alfombra común a $3.146. Producto visualmente distintivo, ideal para video corto |
| **Set coordinado 4 piezas** | Ancla de ticket | Los sets ya tienen mediana $25.219 en ML, la más alta de accesorios. Es el producto que define tu marca |
| **Dispensador de pared** | Volumen | 6 ofertas, 67% en Full — demanda de impulso comprobada. Objeto más visible del baño |
| **Organizador de ducha** | Volumen | 196 uds/publicación, demanda repartida entre 11 ofertas. Sin taladro = objeción cero para arrendatarios |
| **Bandeja de lavamanos** | Add-on | Precio de entrada bajo el umbral psicológico de $20.000. Sube unidades por pedido |
| **Toallero-repisa** | Ancla de precio | Mediana del nicho $82.440 con solo 2–3 competidores. Vende poco pero hace que el resto parezca barato |
| **Ganchos adhesivos** | Relleno de carrito | $9.990 es exactamente lo que le falta a alguien con $38.000 para llegar al envío gratis de $45.000 |

### Los bundles (donde está la plata de verdad)

| Bundle | Contiene | Suma individual | Precio bundle | Ahorro | Landed | Margen |
|---|---|---:|---:|---:|---:|---:|
| **El Lavamanos** | Set 4 piezas + bandeja | $54.980 | **$47.990** | 13% | $15.988 | 66,7% |
| **La Ducha** | Organizador + dispensador + ganchos | $54.970 | **$46.990** | 15% | $16.723 | 64,4% |
| **El Baño Completo** | Set + alfombra + dispensador + organizador | $110.960 | **$89.990** | 19% | $34.431 | 61,7% |

El margen porcentual baja, pero el margen **absoluto por pedido** sube muchísimo:
$27.289 en el set solo contra $55.559 en El Baño Completo. Con un costo de adquisición
fijo por cliente, lo que importa es el peso absoluto, no el porcentaje.

## Economía unitaria por pedido

Ticket promedio objetivo: **$48.000** (empujado por bundles y envío gratis sobre $45.000).

| Línea | CLP |
|---|---:|
| Ingreso | 48.000 |
| Costo de producto (landed) | −13.440 |
| Medios de pago + fee de Shopify (5,3%) | −2.544 |
| Despacho neto (lo que pones tú) | −3.200 |
| Packaging | −900 |
| **= Contribución antes de publicidad** | **27.916** |
| — con CPA $10.000 | 17.916 |
| — con CPA $15.000 | 12.916 |
| — con CPA $20.000 | 7.916 |

- **CPA máximo de equilibrio: $27.916**
- **ROAS mínimo para no perder: 1,72x**
- **ROAS objetivo de trabajo: 3,2x** (CPA $15.000, deja $12.916 por pedido)

> El 5,3% de medios de pago es alto y hay que entenderlo: **Shopify Payments no opera
> en Chile**, así que pagas la comisión de tu pasarela (Webpay 1,49–2,5%) **más** la
> tarifa por transacción de Shopify por usar una pasarela externa (2,0% en Basic,
> 1,0% en Shopify, 0,5% en Advanced). Cuando pases los ~60 pedidos al mes, subir al
> plan Shopify se paga solo.

## Inversión inicial completa

| Ítem | CLP | Nota |
|---|---:|---|
| Inventario pedido 1 (landed) | 2.611.220 | |
| IVA importación (recuperable) | ~500.000 | Crédito fiscal, pero hay que desembolsarlo |
| Muestras de proveedores (7 SKU) | 250.000 | **No lo saltes** |
| Fotografía de producto y ambiente | 450.000 | Ver nota abajo |
| Shopify 3 meses (plan Basic) | 111.000 | ~USD 39/mes |
| Apps (reseñas, envíos, DTE) | 90.000 | 3 meses |
| Dominio + email corporativo | 40.000 | |
| Packaging con marca (300 unidades) | 280.000 | Caja, sticker, tarjeta |
| Constitución + contador (3 meses) | 350.000 | Empresa en un día es gratis; el contador no |
| **Presupuesto de publicidad mes 1–2** | **900.000** | |
| **TOTAL** | **~5.080.000** | |

**Versión austera (~$3.500.000):** haces tú la fotografía con luz natural y un fondo
de microcemento, partes con 5 SKU en vez de 7, y bajas el presupuesto de ads a
$500.000 apoyándote en Pinterest orgánico.

> **Sobre la fotografía:** es el único ítem de esta lista donde ahorrar te sale caro.
> Toda la tesis de la tienda es "esto se ve mejor que lo de Sodimac". Si las fotos son
> del proveedor chino sobre fondo blanco, no hay tesis. Presupuesta al menos una
> sesión en un baño real bien iluminado.

## Punto de equilibrio

Costos fijos mensuales: Shopify + apps + contador + dominio ≈ **$180.000/mes**.
Con $12.916 de contribución neta por pedido (CPA $15.000):

**14 pedidos al mes cubren los fijos.** A partir del pedido 15 empiezas a ganar.
Con 60 pedidos/mes: **~$595.000 de utilidad mensual** antes de impuestos.

Es un negocio real, pero no es rápido: el pedido 1 completo vendido son $8,7 millones
de facturación, y a 60 pedidos/mes tardas unos 3 meses en rotarlo.
