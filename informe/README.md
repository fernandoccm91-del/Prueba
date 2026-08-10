# Productos de baño en MercadoLibre México: dónde hay demanda y margen

**Fecha de captura:** 10 de agosto de 2026 · **Sitio:** MercadoLibre México (MLM) · **Muestra:** 173 productos únicos de las categorías de baño

---

## 1. Resumen ejecutivo

1. **La demanda del baño se concentra en piezas baratas y ligeras, no en muebles.** Los 10 productos más vendidos de la muestra son coladeras, toallas, organizadores, regaderas y sets de accesorios entre **$89 y $488 MXN**. El 68% de la oferta activa está por debajo de $299.
2. **El mejor equilibrio demanda/competencia está en tres nichos:** barras de seguridad para baño, coladeras antiolores y cortinas + barras telescópicas. Son nichos con **625–1,200 unidades vendidas por publicación** y solo **4–6 vendedores** compitiendo.
3. **Existe un acantilado de rentabilidad en $299.** A ese precio el envío gratis se vuelve obligatorio y el costo de envío (~$72 netos para 1 kg) borra de golpe el 24% del precio. Un producto a **$289 deja $225** libres de comisiones; el mismo a **$299 deja $161**. Hay que vender por debajo de $299 o por encima de ~$400, nunca en medio.
4. **Mercado Envíos Full ya es requisito de entrada:** el 92% de los productos con oferta activa en baño se envían por Full.
5. **El 65% de las publicaciones compite en catálogo** (una sola ficha, varios vendedores, gana el precio). Los nichos con poca ficha de catálogo — porta-rollos y toalleros (27%), coladeras (50%), cortinas (50%) — son los que aún permiten construir una publicación propia con marca y contenido.

---

## 2. Cómo se obtuvieron los datos (y qué NO cubren)

MercadoLibre bloquea el acceso automatizado a las páginas de búsqueda y a la API pública (`api.mercadolibre.com` devuelve 403 sin token de aplicación). La superficie que sí resultó accesible es la de **ofertas por categoría** (`/ofertas?category=...`), que expone para cada producto: título, precio, precio de lista, descuento, vendedor, calificación, unidades vendidas acumuladas y tipo de envío.

Se recorrieron 10 categorías de baño (Baños y sus 8 subcategorías + Mobiliario para Baños de Construcción), se deduplicaron los resultados y se clasificaron en 17 nichos por reglas sobre el título.

**Limitaciones que hay que tener presentes:**

- La muestra es de **productos con oferta/descuento activo**, no del catálogo completo. Está sesgada hacia productos que el vendedor está empujando: sirve muy bien para medir *qué se mueve*, y subestima la oferta total de cada nicho.
- **"Vendidos" es acumulado histórico y viene en cubos** (+100, +1,000, +5,000, +10,000), no es venta mensual. Sirve para comparar nichos entre sí, no para proyectar facturación.
- El **número de vendedores** es el de la muestra, no el total del nicho: es un indicador de concentración, no un censo.
- Los **costos de envío del modelo son estimaciones** basadas en rangos públicos; hay que confirmarlos en el simulador de costos de MercadoLibre con las medidas y el peso reales antes de comprometer inventario.

Los datos crudos están en [`../datos/mercadolibre_bano_mx.csv`](../datos/mercadolibre_bano_mx.csv) y los scripts en [`../scripts/`](../scripts).

---

## 3. Mapa de la categoría

Ofertas activas por subcategoría al momento de la captura (Hogar › Baños):

| Subcategoría | Ofertas activas |
|---|---:|
| Accesorios para Baño | 75 |
| Grifería para Baño | 44 |
| Toallas, Toallones y Batas | 30 |
| Barrales y Cortinas de Baño | 24 |
| Lavabos para Baño | 11 |
| Sanitarios | 3 |
| Tapetes de Baño | 3 |
| Tinas de Baño | 2 |
| Generadores de Vapor | 1 |
| **Total categoría Baños** | **190** |

El grueso del movimiento vive en *Accesorios* y *Grifería*. Sanitarios, lavabos, tinas y muebles casi no tienen actividad promocional: son productos pesados, de baja rotación y con logística cara.

---

## 4. Ranking de oportunidad por nicho

Score = demanda por publicación × (1 / √vendedores) × penalización por catálogo × margen disponible después de comisión, ISR y envío.

| # | Nicho | Score | Uds/publicación | Vendedores | % catálogo | Precio mediano | Peso típico | % del precio que se va en envío | % disponible |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Barras de seguridad / agarraderas | **55.6** | 625 | 4 | 80% | $315 | 1.0 kg | 23% | 55% |
| 2 | Coladeras / rejillas antiolores | **51.1** | 1,200 | 6 | 50% | $219 | 0.4 kg | 29% | 49% |
| 3 | Cortinas y barras de cortina | **44.5** | 593 | 5 | 50% | $208 | 0.9 kg | 35% | 43% |
| 4 | Mezcladoras y llaves | **39.4** | 316 | 8 | 70% | $452 | 1.5 kg | 19% | 59% |
| 5 | Porta-rollos / toalleros / ganchos | **38.2** | 230 | 7 | 27% | $203 | 0.5 kg | 31% | 47% |
| 6 | Toallas y batas | 37.4 | 832 | 4 | 68% | $196 | 1.2 kg | 44% | 34% |
| 7 | Organizadores / repisas de ducha | 36.7 | 900 | 8 | 79% | $294 | 1.2 kg | 30% | 48% |
| 8 | Dispensadores / sets de accesorios | 34.1 | 1,352 | 7 | 67% | $178 | 0.8 kg | 40% | 38% |
| 9 | Regaderas / cabezales de ducha | 33.3 | 1,312 | 12 | 79% | $266 | 1.0 kg | 27% | 51% |
| 10 | Sanitarios / WC / asientos | 2.3 | 204 | 1 | 0% | $207 | 20 kg | 110% | −32% |

"% disponible" es lo que queda del precio para pagar el producto y la utilidad, después de comisión Premium (19.5%), retención de ISR (2.5%) y envío estimado.

---

## 5. Las cinco apuestas concretas

### 1. Kit de 2 barras de seguridad para baño, acero inox 50 cm — precio objetivo $349

- **Por qué:** es el nicho con menos competencia de toda la categoría (4 vendedores en la muestra) y con demanda probada: las tres publicaciones principales acumulan +1,000 unidades cada una, con calificación 4.8. Los precios van de $212 a $694 para un producto casi idéntico, lo que indica que el nicho todavía no está exprimido por precio.
- **Demanda estructural:** población que envejece + accesibilidad. Es una compra por necesidad, poco sensible a la moda.
- **Economía a $349:** comisión $68 · envío estimado $72 · ISR $9 → quedan **$200**. Para 25% de margen neto el costo puesto en almacén debe ser **≤ $113** (múltiplo 3.1×).
- **Riesgo:** 80% de las publicaciones son de catálogo; hay que entrar con una ficha propia (medida, acabado o kit distinto) o ganar el buy box con Full + precio.

### 2. Coladera antiolores de acero inoxidable, pack de 2 — precio objetivo $249

- **Por qué:** el producto individual más vendido de toda la muestra es una coladera antiolores de $92 con +10,000 unidades y 4.7 estrellas. El nicho promedia **1,200 unidades por publicación** con solo 6 vendedores, y la mitad de las publicaciones no son de catálogo.
- **Economía a $249:** por debajo de $299 no hay envío gratis obligatorio, así que la carga logística no aplica. Comisión $49 · ISR $6 → quedan **$194**. Costo objetivo **≤ $132** (múltiplo 1.9×).
- **La jugada:** el mercado está anclado en $92–$120 por pieza. Vender **pack de 2 o de 4** sube el ticket sin cruzar los $299 y saca la comparación directa de precio unitario.
- **Riesgo:** producto genérico y ligero; entra competencia nueva rápido. La defensa es la ficha propia y las reseñas.

### 3. Cortina de baño impermeable de tela + barra telescópica sin taladro — $289 y $199

- **Por qué:** la cortina de tela de $272 lleva +5,000 unidades y 4.9 estrellas; las barras telescópicas de $112–$159 llevan +500 a +1,000 cada una. Solo 5 vendedores en la muestra y la mitad de las publicaciones son propias, no de catálogo.
- **Economía:** ambos precios quedan bajo el umbral de $299. La cortina a $289 deja **$225** después de comisión e ISR (costo objetivo ≤ $153); la barra a $199 deja **$155** (costo objetivo ≤ $105).
- **La jugada:** venderlos como conjunto y como recambio. Es consumible: la cortina se reemplaza cada 12–18 meses, así que hay recompra.
- **Riesgo:** descuentos medianos del 48% en el nicho — es un espacio donde ya se pelea con promoción. Hay que entrar con precio de lista realista, no inflado.

### 4. Set de toallero + porta-rollo + ganchos adhesivos (5–15 piezas) — precio objetivo $279

- **Por qué:** es el nicho **menos dominado por catálogo de todos: solo 27%**. Un porta-rollo adhesivo de $89 lleva +1,000 unidades; un juego de 15 piezas de $249 también. Se puede construir marca propia sin pelear el buy box.
- **Economía a $279:** comisión $54 · ISR $7 → quedan **$218**. Costo objetivo **≤ $148**.
- **La jugada:** "sin taladro" es el ángulo de venta (rentas, departamentos, azulejo). Empaque de kit completo en vez de piezas sueltas.
- **Riesgo:** el adhesivo que falla es la principal fuente de reseñas de 1 estrella en este nicho. Hay que validar el pegamento antes de comprar volumen.

### 5. Regadera de alta presión con filtro y tubo extensor — precio objetivo $449

- **Por qué:** es el nicho de mayor demanda absoluta (36,750 unidades acumuladas en 28 publicaciones), y demuestra que **el precio alto sí vende**: HOMELYA a $349 y SKBE a $488 llevan +5,000 unidades cada una.
- **Economía a $449:** comisión $88 · envío $72 · ISR $11 → quedan **$278**. Costo objetivo **≤ $166** (múltiplo 2.7×).
- **La jugada:** arriba de $400 el envío pesa solo 16% y la comparación deja de ser puramente de precio. Diferenciar con filtro de sedimentos, tubo extensor y acabado negro mate.
- **Riesgo:** el nicho más competido (12 vendedores, 79% catálogo) y con un incumbente fuerte (HAWOO, 7 publicaciones). Es la apuesta de mayor volumen y menor facilidad.

---

## 6. Economía unitaria: el acantilado de los $299

Modelo aplicado (MercadoLibre México, categoría Hogar, Muebles y Jardín):

| Concepto | Valor usado |
|---|---|
| Comisión publicación Clásica | 15% |
| Comisión publicación Premium | 19.5% |
| Costo fijo por unidad (solo Clásica, precio < $299) | $25 / $30 / $37 según el rango |
| Retención de ISR (2026) | 2.5% |
| Envío gratis | Obligatorio desde $299; el vendedor lo absorbe con subsidio por reputación (hasta 60% con reputación verde) |

Cómo se comporta un producto de 1 kg al cruzar el umbral:

| Precio | Envío que absorbe el vendedor | % del precio | Queda tras comisión + ISR + envío |
|---:|---:|---:|---:|
| $249 | $0 | 0% | **$194** |
| $289 | $0 | 0% | **$225** |
| $299 | $72 | 24% | **$161** |
| $349 | $72 | 21% | $200 |
| $399 | $72 | 18% | $239 |
| $449 | $72 | 16% | $278 |
| $549 | $72 | 13% | $356 |

**Conclusión operativa:** subir un producto de $289 a $299 destruye $64 de contribución por unidad. Hay que recuperar hasta ~$390 para volver al punto de partida. Las dos zonas sanas son **$150–$289** (ticket bajo, sin carga logística, se compensa con volumen y packs) y **$400 en adelante** (la logística se diluye). La franja $299–$390 es tierra quemada.

---

## 7. Qué evitar

- **Sanitarios, lavabos, tinas y muebles de baño.** El envío de un producto de 20–30 kg supera el 100% del precio mediano de la muestra. Solo funcionan con venta local, recolección en tienda o tickets de $3,000+.
- **Toallas.** Demanda alta (832 unidades por publicación) pero es el nicho con el descuento mediano más agresivo (50%) y el envío pesa 44% del precio mediano. Es un negocio de volumen y capital, no de margen.
- **Entrar sin Full.** Con 92% de los competidores en Full, una publicación sin él pierde posición y el badge de envío rápido.
- **Competir por precio en fichas de catálogo maduras.** Regaderas y organizadores tienen 79% de catálogo: ahí la única palanca es bajar el precio, y el incumbente ya tiene mejor costo.

---

## 8. Cómo validar antes de comprar inventario

1. Confirmar comisión exacta por subcategoría y el costo de envío real con peso y medidas en el simulador de costos de MercadoLibre (el modelo de arriba usa estimaciones públicas).
2. Verificar el peso volumétrico: largo × ancho × alto ÷ 5,000. En organizadores y cortinas suele mandar el volumen, no la báscula.
3. Pedir muestra física y probar el punto de falla del nicho (adhesivo en toalleros, sello de la coladera, presión real de la regadera).
4. Arrancar con 50–100 piezas por SKU en Full, medir 3–4 semanas de venta orgánica y solo después decidir el volumen.
5. Repetir esta captura en 30 días y comparar la variación de unidades vendidas por publicación: es la única forma de convertir el acumulado en tasa de venta.

---

## 9. Anexo: los 15 productos más vendidos de la muestra

| Uds. acumuladas | Precio | Desc. | ★ | Vendedor | Producto |
|---:|---:|---:|---:|---|---|
| +10,000 | $92 | 6% | 4.7 | VARMI | Coladera redonda antiolores de acero inoxidable |
| +10,000 | $109 | 54% | 4.5 | SHENDY VENDY | Toalla de baño grande 100% algodón |
| +10,000 | $158 | 36% | 4.4 | MXGAA | Organizador de baño con 3 estantes de plástico |
| +10,000 | $189 | 33% | 4.8 | HAWOO | Regadera cuadrada tipo lluvia 20×20 + tubo |
| +5,000 | $169 | 43% | 4.8 | FSY FASILYT | Set de accesorios de baño 4 piezas con bambú |
| +5,000 | $175 | 26% | 4.8 | HAWOO | Regadera cuadrada alta presión 20 cm |
| +5,000 | $209 | 52% | 4.6 | TORISE | Set accesorios de baño 16 piezas acero inox |
| +5,000 | $272 | 61% | 4.9 | — | Cortina de baño impermeable tela lino 200×200 |
| +5,000 | $349 | 41% | 4.6 | HOMELYA | Regadera cuadrada con ducha de mano alta presión |
| +5,000 | $488 | 40% | 4.8 | SKBE | Regadera cuadrada de lujo acero inoxidable |
| +1,000 | $89 | 47% | 4.9 | EDECOR | Porta-rollo autoadhesivo acero inoxidable negro |
| +1,000 | $112 | 50% | 4.8 | HALMAN | Barra retráctil para cortina 70–120 cm |
| +1,000 | $120 | 48% | 4.7 | PATHOO | Coladera redonda inox 12 cm antiolores |
| +1,000 | $218 | 53% | 4.8 | HAIMO | Barra de seguridad inox 50 cm, 2 piezas |
| +1,000 | $315 | 35% | 4.8 | HALMAN | 4 agarraderas / barras de seguridad para baño |

---

### Fuentes de costos y comisiones

- [Comisiones de Mercado Libre México 2026 — ProfitOS](https://www.profitosapp.com/blog/cuanto-cobra-mercado-libre-por-vender-mexico-2026)
- [¿Cuánto cobra de comisión Mercado Libre? — Tiendanube](https://www.tiendanube.com/blog/comision-mercado-libre-mexico/)
- [Costos por ofrecer envíos gratis — Ayuda de Mercado Libre](https://www.mercadolibre.com.mx/ayuda/costos-de-envios_3667)
- Datos de productos: superficie de ofertas de MercadoLibre México, capturada el 10/08/2026.
