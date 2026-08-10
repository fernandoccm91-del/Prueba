# Productos de baño en MercadoLibre Chile: dónde hay demanda y margen

**Fecha de captura:** 10 de agosto de 2026 · **Sitio:** MercadoLibre Chile (MLC) · **Muestra:** 273 productos únicos de 13 categorías de baño · **Moneda:** CLP

---

## 1. Resumen ejecutivo

1. **Chile está mucho menos saturado que México.** Solo el **49% de las publicaciones usa Full** (en México es 92%) y apenas el **38% compite en ficha de catálogo** (en México, 65%). El descuento mediano por nicho va de 10% a 24%, frente a 35%–50% en México. Traducción: todavía se puede entrar con publicación propia, y Full es una ventaja competitiva real, no un requisito de supervivencia.
2. **El nicho más desatendido es accesibilidad** —barras de seguridad, alzabaño, sillas de ducha—: **1.729 unidades por publicación** con solo 7 publicaciones en oferta, 29% de Full y 24% de descuento mediano. Es el mejor ratio demanda/competencia de toda la categoría.
3. **La ducha bidet árabe es un producto característicamente chileno con demanda masiva.** Una sola publicación de $8.714 acumula más de 10.000 unidades, y el nicho promedia 1.736 unidades por publicación con 9 competidores. Pesa 0,8 kg y se vende bajo el umbral de envío gratis: la combinación logística más limpia de la muestra.
4. **El escalón de los $19.990 castiga menos que en México, pero existe.** Un producto de 2 kg a $19.490 deja $15.577 después de comisión; el mismo a $19.990 deja $12.472. Hay que llegar a ~$24.000 para recuperar la diferencia.
5. **La grifería monomando es el nicho grande con menos catálogo (22%)**: 1.067 unidades por publicación, precio mediano $24.656 y solo 33% de los competidores en Full. Es donde más se puede construir marca propia con ticket medio.

---

## 2. Cómo se obtuvieron los datos (y qué NO cubren)

La API pública de MercadoLibre responde 403 sin token de aplicación y las páginas de búsqueda (`listado.mercadolibre.cl`) redirigen a un muro de verificación. La superficie accesible es la de **ofertas por categoría** (`mercadolibre.cl/ofertas?category=...`), que expone por producto: título, precio, precio de lista, descuento, vendedor, calificación, unidades vendidas acumuladas y tipo de envío.

Se recorrieron 13 categorías —Baños y sus 10 subcategorías, más Mobiliario para Baños y Gasfitería de Construcción—, se deduplicaron los resultados y se clasificaron en 17 nichos por reglas sobre el título. 45 de los 273 productos (16%) quedaron en "Otros" por no calzar con ninguna regla.

**Limitaciones:**

- La muestra es de **productos con oferta activa**, no del catálogo completo: mide bien qué se mueve, subestima la oferta total.
- **"Vendidos" es acumulado histórico en cubos** (+100, +1.000, +5.000, +10.000), no venta mensual.
- Solo el 51% de las tarjetas muestra el nombre del vendedor. El conteo de competidores suma los vendedores identificados más cada publicación sin vendedor visible, tratada como competidor propio: es una **cota superior**.
- Los **costos de envío del modelo son estimaciones**. Hay que confirmarlos en el simulador de MercadoLibre con peso y medidas reales.

Datos crudos en [`../datos/mercadolibre_bano_cl.csv`](../datos/mercadolibre_bano_cl.csv); scripts en [`../scripts/analyze_cl.py`](../scripts/analyze_cl.py).

---

## 3. Mapa de la categoría

Ofertas activas por subcategoría al momento de la captura:

| Subcategoría | Ofertas |
|---|---:|
| Accesorios para Baño | 99 |
| Mobiliario para Baños (Construcción) | 83 |
| Gasfitería | 58 |
| Toallas, Sábanas y Batas | 38 |
| Grifería para Baño | 36 |
| Barras y Cortinas de Baño | 10 |
| Alfombras de Baño | 6 |
| Sifones de Desagüe | 5 |
| Sanitarios | 4 |
| Lavamanos para Baño | 3 |
| Espejos de Baño | 2 |
| Platos de Ducha | 1 |
| **Total categoría Baños** | **206** |

---

## 4. Ranking de oportunidad por nicho

Score = demanda por publicación × (1 / √competidores) × penalización por catálogo × margen disponible después de comisión y envío.

| # | Nicho | Score | Uds/publ. | Ofertas | Compet. | % catálogo | % Full | Precio mediano | Desc. mediano |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Accesibilidad: barras, alzabaño, sillas | **80.4** | 1.729 | 7 | 6 | 29% | 29% | $33.666 | 24% |
| 2 | Dispensadores e higiene institucional | **60.1** | 1.085 | 12 | 8 | 33% | 83% | $20.979 | 14% |
| 3 | Ducha bidet árabe / bidet para WC | **53.2** | 1.736 | 9 | 9 | 44% | 78% | $13.774 | 27% |
| 4 | Asientos y tapas de WC | **51.7** | 1.500 | 6 | 6 | 83% | 50% | $19.494 | 22% |
| 5 | Grifería: monomando y llaves | **45.0** | 1.067 | 18 | 17 | 22% | 33% | $24.656 | 19% |
| 6 | Bombas y presurizadoras | 38.6 | 872 | 19 | 16 | 58% | 37% | $69.990 | 18% |
| 7 | Sets de accesorios de baño | 38.5 | 94 | 17 | 12 | 18% | 65% | $32.990 | 32% |
| 8 | Cortinas de baño y barras | 37.5 | 107 | 14 | 12 | 36% | 43% | $30.571 | 13% |
| 9 | Kits de ducha, teléfonos y columnas | 36.0 | 395 | 14 | 13 | 36% | 71% | $15.782 | 23% |
| 10 | Cestos de ropa sucia | 33.6 | 331 | 12 | 9 | 67% | 58% | $13.280 | 16% |
| 11 | Ganchos y colgadores adhesivos | 33.2 | 909 | 11 | 10 | 45% | 91% | $6.990 | 12% |
| 12 | Antideslizantes y alfombras | 32.7 | 197 | 9 | 8 | 22% | 67% | $10.377 | 15% |
| 13 | Sifones, desagües y antiolor | 31.4 | 181 | 8 | 8 | 25% | 75% | $8.439 | 21% |
| 14 | Organizadores, estantes y repisas | 24.3 | 662 | 20 | 18 | 45% | 40% | $13.157 | 15% |
| 15 | Sanitarios, lavamanos y receptáculos | 21.2 | 182 | 17 | 16 | 18% | 41% | $27.890 | 10% |
| 16 | Toallas y batas | 17.2 | 144 | 29 | 18 | 76% | 66% | $10.990 | 37% |

---

## 5. Las cinco apuestas concretas

### 1. Accesibilidad: pack x2 barras de seguridad y silla de ducha — $24.990 y $39.990

- **Por qué:** el mejor ratio demanda/competencia de la categoría. Solo 7 publicaciones en oferta, 1.729 unidades por publicación, calificación 4.8 y apenas 24% de descuento mediano: nadie está peleando precio. El alzabaño de $31.620 lleva +10.000 unidades y la silla de ducha de $39.148 lleva +1.000, ambas de un mismo vendedor (YAA) que aún no tiene contrapeso.
- **Señal fuerte:** solo 29% del nicho usa Full. Entrar con Full es ventaja inmediata en posicionamiento y plazo de entrega.
- **Economía a $24.990 (pack x2 barras, 2 kg):** comisión $4.248 · envío $4.120 → quedan **$16.622**. Costo puesto en bodega **≤ $10.374** para 25% de margen neto (múltiplo 2,4×).
- **Economía a $39.990 (silla de ducha, 3,5 kg):** quedan **$27.972**; costo objetivo **≤ $17.974**.
- **Riesgo:** producto de uso clínico-doméstico. Una barra que se suelta es un accidente, no una devolución. Exigir certificación de carga al proveedor y publicar la capacidad en kilos.

### 2. Ducha bidet árabe de acero inoxidable, kit completo — $14.990

- **Por qué:** demanda característicamente chilena y masiva. La publicación líder de $8.714 acumula +10.000 unidades con 4.7 estrellas, y hay al menos cinco publicaciones más sobre las 1.000 unidades. El nicho promedia 1.736 unidades por publicación.
- **La mejor logística de la muestra:** 0,8 kg y precio bajo el umbral de $19.990, así que el vendedor no absorbe despacho. A $14.990 quedan **$11.842** (79% del precio) y el costo objetivo es **≤ $8.094** (múltiplo 1,9×).
- **La jugada:** el rango está partido entre el genérico de $6.600–$8.900 y el bidet "de marca" de $18.900–$28.500. Entrar en la mitad con kit completo (manguera trenzada, soporte y llave de paso incluidos) y armado sin gasfíter.
- **Riesgo:** 78% del nicho ya está en Full, así que la ventaja logística está tomada. La diferenciación tiene que venir del kit y de las fotos de instalación.

### 3. Grifería monomando para lavatorio, negro mate — $26.990

- **Por qué:** es el nicho grande con **menos catálogo (22%)**, lo que permite publicación propia con marca. 1.067 unidades por publicación, y el líder —un monomando de $10.640— lleva +10.000 unidades. Solo 33% de los competidores usa Full.
- **Economía a $26.990 (1,5 kg):** comisión $4.588 · envío $4.120 → quedan **$18.282**. Costo objetivo **≤ $11.534** (múltiplo 2,3×).
- **La jugada:** el tramo $20.000–$30.000 en acabado negro mate y cascada está poco cubierto; abajo hay cromo genérico y arriba marcas de tienda. Vender con flexibles incluidos.
- **Riesgo:** 17 competidores, el número más alto del top 5. Es el nicho donde más importa la ficha: fotos de instalación, medidas y garantía del cartucho.

### 4. Dispensadores e higiene institucional — $22.990

- **Por qué:** 1.085 unidades por publicación con solo 12 publicaciones y 14% de descuento mediano, el segundo más bajo de la categoría. El comprador no es sólo el hogar: oficinas, restaurantes y clínicas compran dispensador de papel jumbo, secador de manos y jabonera de pared. El secador de manos de $23.390 lleva +5.000 unidades.
- **Economía a $22.990 (1,5 kg):** comisión $3.908 · envío $4.120 → quedan **$14.962**. Costo objetivo **≤ $9.214** (múltiplo 2,5×).
- **La jugada:** venta B2B recurrente. Quien compra el dispensador vuelve por el consumible; conviene publicar ambos y ofrecer packs.
- **Riesgo:** 83% del nicho ya usa Full y son productos voluminosos respecto a su peso, así que manda el peso volumétrico. Calcular largo × ancho × alto ÷ 4.000 antes de fijar precio.

### 5. Asiento y tapa de WC con cierre suave, reforzada — $17.990

- **Por qué:** 1.500 unidades por publicación con solo 6 publicaciones en oferta. Es compra de reposición pura —la tapa se rompe y se reemplaza— y el mercado está partido entre el plástico universal de $3.870 (3.9 estrellas, mal calificado) y el Bemis de madera de $40.704. El tramo intermedio de calidad está abierto.
- **Economía a $17.990 (2,5 kg):** queda bajo el umbral, así que no hay despacho a cargo del vendedor: comisión $3.058 · cargo fijo $600 → quedan **$14.332** (80% del precio). Costo objetivo **≤ $9.834**.
- **La jugada:** cierre suave, bisagra metálica y formato universal, atacando explícitamente la mala calificación del genérico barato.
- **Riesgo:** **83% del nicho es catálogo**, el más alto de la muestra. Hay que llegar con un modelo que no tenga ficha creada o resignarse a pelear el buy box.

**Alternativa de entrada de bajo capital:** ganchos y colgadores adhesivos, con 909 unidades por publicación y ticket de $6.990. El margen absoluto por unidad es chico ($6.862 disponibles, costo objetivo ≤ $4.614), pero es el nicho más liviano (0,4 kg) y sirve para levantar reputación rápido antes de subir de ticket.

---

## 6. Economía unitaria: el escalón de los $19.990

Modelo aplicado (MercadoLibre Chile, categoría Hogar y Muebles):

| Concepto | Valor usado |
|---|---|
| Comisión por venta | 14% clásica / 17% premium (rango referencial 14%–17% para Hogar) |
| Cargo fijo por unidad (precio < $19.990) | ~$600 |
| Envío gratis | Obligatorio desde **$19.990**; el vendedor absorbe el costo con descuento por reputación de hasta 50%–60% |
| Costo de envío de referencia | ~$6.200 por 1 kg antes de descuento |
| IVA | Las comisiones se facturan con IVA. Si eres contribuyente lo recuperas; si no, súmale 19% sobre la comisión |

Comportamiento de un producto de 2 kg al cruzar el umbral:

| Precio | Cargo fijo | Envío que absorbe el vendedor | Queda tras comisión, cargo fijo y envío |
|---:|---:|---:|---:|
| $14.990 | $600 | $0 | **$11.842** (79%) |
| $17.990 | $600 | $0 | **$14.332** (80%) |
| $19.490 | $600 | $0 | **$15.577** (80%) |
| $19.990 | $0 | $4.120 | **$12.472** (62%) |
| $22.990 | $0 | $4.120 | $14.962 (65%) |
| $26.990 | $0 | $4.120 | $18.282 (68%) |
| $32.990 | $0 | $4.120 | $23.262 (71%) |

**Conclusión operativa:** cruzar de $19.490 a $19.990 cuesta **$3.105 de contribución por unidad**, y hay que llegar a ~$24.000 para recuperarla. El escalón es más suave que en México porque el ticket chileno es más alto en relación al despacho, pero sigue definiendo dos zonas de precio: **hasta $19.490** y **desde $24.000**.

---

## 7. Qué evitar

- **Sanitarios, lavamanos y receptáculos.** A 25 kg el despacho se come el 61% del precio mediano del nicho, con la peor rotación de la muestra (182 unidades por publicación). Solo funciona con retiro en tienda o tickets sobre $100.000.
- **Toallas y batas.** El nicho más poblado (29 publicaciones), con 76% de catálogo y 37% de descuento mediano: es el único donde ya hay guerra de precios abierta, y la rotación por publicación es la más baja (144 unidades).
- **Organizadores y estantes.** Demanda decente (662 unidades por publicación) pero 2,5 kg de puro volumen: el envío se lleva 40% del precio mediano. Solo con diseño plegable o desarmable.
- **Precios entre $19.990 y $24.000.** Es la franja donde el escalón de envío ya se activó pero el ticket todavía no lo absorbe.

---

## 8. Cómo validar antes de comprar inventario

1. Confirmar la comisión exacta de la subcategoría y el costo real de despacho con peso y medidas en el simulador de MercadoLibre. El modelo de arriba usa rangos públicos referenciales.
2. Calcular el peso volumétrico antes de fijar precio; en dispensadores, organizadores y cestos casi siempre manda el volumen.
3. Definir si vas a operar con o sin Full por nicho. En accesibilidad (29% Full) y grifería (33% Full) el Full es palanca de posicionamiento; en ganchos (91%) ya es requisito.
4. Pedir muestra y probar el punto de falla del nicho: carga real de la barra de seguridad, cartucho del monomando, bisagra de la tapa de WC, sello del bidet.
5. Partir con 50 a 100 unidades por SKU, medir tres o cuatro semanas de venta orgánica y recién ahí decidir volumen.
6. Repetir esta captura en 30 días: la variación de unidades por publicación es la única forma de convertir el acumulado en tasa de venta real.

---

## 9. Anexo: los 16 productos más vendidos de la muestra

| Uds. acumuladas | Precio | Desc. | ★ | Vendedor | Producto |
|---:|---:|---:|---:|---|---|
| +10.000 | $8.714 | 27% | 4.7 | — | Ducha bidet árabe acero inoxidable para WC |
| +10.000 | $10.640 | 5% | 4.7 | — | Grifería PMB monomando lavatorio Cincinnati cromo |
| +10.000 | $31.620 | 38% | 4.7 | YAA | Asiento WC portátil plegable alzabaño |
| +5.000 | $3.286 | 7% | 4.5 | — | Ganchos adhesivos colgador perchero acero inox |
| +5.000 | $3.870 | 29% | 3.9 | — | Tapa de baño asiento WC universal redondo plástico |
| +5.000 | $7.990 | 20% | 4.8 | BathLand | Pack x2 estante de baño organizador esquinero |
| +5.000 | $9.479 | 52% | 4.6 | — | Grifo monomando mezcladora inoxidable negro |
| +5.000 | $13.850 | 13% | 4.4 | — | Estante mueble organizador de baño 3 niveles |
| +5.000 | $18.675 | 25% | 4.9 | BIOMED CHILE | Pack esponja jabonosa desechable Begobaño 144 un |
| +5.000 | $23.390 | 13% | 4.6 | Vaelora | Secador de mano eléctrico con sensor 1800 W |
| +5.000 | $32.990 | 17% | 4.5 | GDPLUS | Bomba presurizadora para calefont |
| +5.000 | $81.470 | 18% | 4.8 | Ferretería Mimbral | Bomba sumergible 17.000 L 630 W Einhell |
| +1.000 | $3.141 | 10% | 5.0 | — | Brazo de ducha cromado Täumm con difusor |
| +1.000 | $5.648 | 36% | 4.8 | — | 30 ganchos montados en la pared |
| +1.000 | $5.810 | 35% | 4.7 | Ravera | Restaurador de esmalte cerámico Ceys para tinas |
| +1.000 | $5.890 | 46% | 4.9 | — | 10 piezas ganchos perchero acero inox doble |

---

## 10. Chile frente a México

Para referencia, comparado con [el mismo estudio en México](README.md):

| Indicador | Chile | México |
|---|---:|---:|
| Publicaciones en Full | 49% | 92% |
| Publicaciones en catálogo | 38% | 65% |
| Descuento mediano por nicho | 10%–24% | 26%–50% |
| Umbral de envío gratis | $19.990 CLP (~US$21) | $299 MXN (~US$16) |
| Nicho estrella | Accesibilidad y ducha bidet | Barras de seguridad y coladeras |

El patrón común es la accesibilidad —barras de seguridad y apoyos de baño— que aparece arriba en los dos países. La diferencia es que en Chile el mercado todavía no está copado por Full ni por fichas de catálogo, así que hay más espacio para construir publicación propia.

---

### Fuentes de costos y comisiones

- [Cuánto cobra Mercado Libre por venta en 2026 — Wivo Analytics](https://www.wivoanalytics.com/blog/cuanto-cobra-mercado-libre-por-venta-en-2025-guia-completa-de-comisiones-envios-y-mas)
- [Guía 2026 de comisiones por venta en Mercado Libre — Rapiboy](https://blog.rapiboy.com/comisiones-sobre-ventas-en-la-plataforma-meli/)
- [Costos por ofrecer envíos gratis — Ayuda de Mercado Libre Chile](https://www.mercadolibre.cl/ayuda/Costos-de-envios_3667)
- Datos de productos: superficie de ofertas de MercadoLibre Chile, capturada el 10/08/2026.
