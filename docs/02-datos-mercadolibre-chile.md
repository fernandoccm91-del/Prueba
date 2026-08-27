# Demanda real del nicho baño en Chile — datos de MercadoLibre

Investigación propia sobre **179 publicaciones con oferta activa** en las categorías
de baño de MercadoLibre Chile (agosto 2026). Datos crudos en `docs/datos/`.

## Resumen: 6 hallazgos que cambian el plan

**1. El precio mediano del nicho baño en Chile es bajísimo.** Alfombras de baño
absorbentes: **$3.146**. Jaboneras: **$2.771**. Portacepillos: **$5.104**.
Dispensadores de jabón: **$9.063**. Si entras a competir en esos precios, no hay
negocio: con un ticket de $5.000 no financias ni el costo de adquisición.

**2. El 100% de las publicaciones está en ficha de catálogo compartida.** En 29 de
los 31 nichos medidos, el 100% de los links son `/p/MLC...` o `/up/...`. Eso
significa que en MercadoLibre **no puedes diferenciarte con marca — solo bajar el
precio**, porque compartes ficha con todos los demás vendedores del mismo producto.
Es la confirmación más dura de por qué tu tienda propia en Shopify es el canal
correcto, no un marketplace.

**3. El diferencial de material multiplica el precio por 3,6x.** Alfombra de baño
absorbente común: mediana **$3.146**. Alfombra de **piedra de diatomea** (secado
rápido): **$11.441**, con una sola oferta activa en toda la muestra. Mismo problema
del cliente ("el piso queda mojado"), 3,6 veces el precio, casi sin competencia. Este
es exactamente el mecanismo que tu tienda tiene que explotar en todo el catálogo.

**4. El segmento de alto ticket existe y está desatendido.** Repisas y toalleros:
mediana **$82.440**. Espejos de baño: mediana **$65.691** con solo 5 ofertas activas
y 20 unidades por publicación. Hay gente en Chile pagando $80.000 por un toallero.
No todos compiten en el piso.

**5. Los "sets de accesorios" ya validan el ticket alto: mediana $25.219**, el precio
más alto de toda la zona de accesorios, con 67% en Full. La demanda por comprar
coordinado existe; lo que no existe es alguien vendiéndola bien.

**6. Toallas y drenajes están quemados por descuento** (39% de descuento mediano en
ambos). Toallas además tiene 17 ofertas y solo 64,7 unidades por publicación: mucha
oferta persiguiendo poca demanda. **No entres a toallas como producto ancla.**

---

## Cómo se obtuvieron estos datos y qué NO cubren

- **Muestra**: 179 publicaciones **con oferta o descuento activo** en 8 categorías
  hoja de baño y organización de MercadoLibre Chile. No es el catálogo completo —
  subestima la oferta total. Es una buena lectura de "qué se está moviendo ahora".
- **"Vendidos" es acumulado histórico en cubos** (+100, +1.000, +5.000, +10.000),
  no venta mensual. Sirve para comparar nichos entre sí y ordenar por popularidad,
  **no** para proyectar facturación.
- **El conteo de competidores es una cota superior**: vendedores identificados más
  cada publicación sin vendedor visible contada como competidor propio. MercadoLibre
  solo muestra el vendedor en ~51% de las tarjetas.
- **Los costos de envío y comisión son estimaciones** (comisión referencial 14–17%
  para Hogar, cargo fijo ~$600 bajo el umbral, umbral de envío gratis $19.990).
  Confírmalos en el simulador oficial de MercadoLibre antes de comprometer inventario.
- **Nichos con 1–3 ofertas tienen muestra insuficiente.** "Secadores de manos"
  encabeza el ranking con score 145,9 sobre una sola publicación con +5.000 vendidos.
  Es una señal interesante, no una conclusión. Lo mismo para diatomea (1 oferta).

---

## Mapa de la categoría (ofertas activas)

| Categoría | ID | Ofertas activas |
|---|---|---|
| Accesorios para Baño | MLC1616 | 83 |
| Grifería para Baño | MLC412368 | 33 |
| Toallas, Sábanas y Batas | MLC1614 | 22 |
| Alfombras de Baño | MLC175577 | 16 |
| Barras y Cortinas de Baño | MLC440088 | 12 |
| Espejos de Baño | MLC175583 | 5 |
| Sanitarios | MLC412384 | 4 |
| Lavamanos | MLC412391 | 2 |

Baños completo (MLC1613): 177 ofertas activas, décimo de doce subcategorías de Hogar.
Es un nicho **de tamaño medio**: suficiente demanda para vivir, no tan grande como
para atraer a los grandes operadores de e-commerce.

---

## Ranking de oportunidad por nicho

`Uds/pub` = unidades vendidas acumuladas ÷ ofertas (señal de demanda).
`%Cat` = % en ficha de catálogo compartida (100% = imposible diferenciarse en ML).
`Disp%` = % del precio que queda tras comisión, cargo fijo y despacho de ML.

| Nicho | Ofertas | Comp. | Uds/pub | %Cat | %Full | Precio med. | Desc. med. | Disp% | Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Secadores de manos eléctricos ⚠️ | 1 | 1 | 5.000 | 100 | 0 | $23.390 | 13% | 60,7 | 145,9 |
| Alfombras antideslizantes de ducha ⚠️ | 2 | 2 | 2.750 | 100 | 50 | $8.033 | 12% | 75,5 | 119,5 |
| Ducha bidet / bidet árabe | 4 | 4 | 3.000 | 50 | 50 | $11.268 | 23% | 77,7 | 111,5 |
| **Alfombras de diatomea (secado rápido)** ⚠️ | 1 | 1 | 100 | 100 | 0 | **$11.441** | 18% | 77,8 | 103,2 |
| **Repisas flotantes y toalleros** | 3 | 2 | 333 | 100 | 0 | **$82.440** | 25% | 78,9 | 91,9 |
| Tapas y asientos de WC | 3 | 3 | 1.000 | 100 | 67 | $16.901 | 16% | 79,4 | 89,6 |
| Cestos de ropa sucia | 4 | 4 | 1.875 | 100 | 75 | $12.332 | 11% | 78,1 | 83,2 |
| Ganchos adhesivos de pared | 4 | 4 | 288 | 100 | 25 | $6.765 | 5% | 74,1 | 59,6 |
| Porta papel higiénico | 4 | 4 | 144 | 100 | 25 | $17.435 | 12% | 79,6 | 56,5 |
| Toalleros eléctricos / calefactores | 3 | 2 | 25 | 100 | 0 | $149.990 | 25% | 78,2 | 55,5 |
| Drenajes y coladeras de piso | 6 | 6 | 225 | 100 | 50 | $13.603 | 39% | 78,6 | 49,4 |
| Columnas de ducha | 7 | 6 | 214 | 100 | 0 | $49.990 | 23% | 72,5 | 45,3 |
| Cajas organizadoras (no baño) | 14 | 11 | 598 | 100 | 21 | $9.980 | 14% | 77,0 | 42,0 |
| **Dispensadores de jabón** | 6 | 6 | 104 | 100 | 67 | $9.063 | 14% | 76,4 | 41,7 |
| Cabezales y kits de ducha | 10 | 10 | 605 | 100 | 20 | $5.514 | 16% | 72,1 | 41,3 |
| Organizadores de maquillaje | 11 | 10 | 459 | 100 | 36 | $4.290 | 13% | 69,0 | 37,9 |
| Cortinas de baño y barras | 10 | 9 | 165 | 100 | 20 | $6.899 | 16% | 74,3 | 36,1 |
| Toallas y sets de toalla ❌ | 17 | 7 | 65 | 100 | 29 | $10.650 | **39%** | 77,4 | 35,6 |
| Organizadores de ducha y repisas | 11 | 11 | 196 | 100 | 18 | $7.990 | 16% | 75,5 | 34,2 |
| Grifería monomando | 9 | 9 | 81 | 100 | 33 | $17.450 | 17% | 79,6 | 33,7 |
| Portacepillos y portavasos | 2 | 2 | 0 | 100 | 0 | $5.104 | 20% | 71,2 | 32,7 |
| **Espejos de baño** | 5 | 5 | 20 | 100 | 0 | **$65.691** | 10% | 75,0 | 32,2 |
| **Sets de accesorios de baño** | 6 | 6 | 38 | 100 | 67 | **$25.219** | 14% | 66,6 | 29,7 |
| Barras y apoyos de seguridad | 5 | 5 | 15 | 100 | 20 | $35.991 | 14% | 71,5 | 29,1 |
| Soportes para secador de pelo | 2 | 2 | 0 | 100 | 0 | $1.978 | 16% | 52,7 | 24,2 |
| Soportes de ducha sin taladro | 3 | 3 | 0 | 100 | 0 | $3.104 | 0% | 63,7 | 23,9 |
| Jaboneras ❌ | 3 | 3 | 0 | 100 | 0 | $2.771 | 16% | 61,3 | 23,0 |
| Alfombras de baño absorbentes ❌ | 16 | 16 | 53 | 100 | 12 | $3.146 | 16% | 63,9 | 18,7 |

⚠️ = muestra de 1–2 publicaciones, tratar como señal, no como conclusión.
❌ = evitar como producto ancla.

---

## Las apuestas concretas

### 1. Alfombra de piedra de diatomea — el producto héroe

- **Evidencia**: 1 sola oferta activa a $11.441 en toda la muestra, contra 16 ofertas
  de alfombra absorbente común a mediana $3.146. El mercado chileno todavía no lo
  conoce y quien lo vende no tiene competencia.
- **Por qué funciona en tu tienda**: es visualmente distinto (piedra mate, se ve de
  diseño), resuelve un problema real ("el piso del baño queda mojado y con olor"),
  y se explica en 10 segundos de video. Es el producto perfecto para Pinterest y Reels.
- **Precio sugerido en tu tienda**: $27.990–29.990 con marca, packaging y fotografía
  de ambiente. Sí, muy por sobre los $11.441 de ML — ese es el punto: no compites en
  la misma ficha, compites en otra categoría mental.
- **Riesgo específico**: es frágil (se quiebra en el envío si no va bien embalada) y
  la calidad varía muchísimo entre proveedores chinos. **Pide muestra física
  obligatoriamente** y prueba la absorción y la resistencia a la caída.

### 2. Set de accesorios coordinado — el ancla de ticket

- **Evidencia**: mediana $25.219, la más alta de la zona de accesorios, con 67% en
  Full (la gente los compra por impulso con envío rápido). Solo 6 ofertas activas.
- **Precio sugerido**: $34.990–39.990 el set de 4–5 piezas coordinadas.
- **Riesgo**: es el producto más copiable del catálogo. Tu defensa es la curaduría de
  paleta y la fotografía, no el objeto.

### 3. Repisa / toallero de alto ticket — el producto de prestigio

- **Evidencia**: mediana $82.440 en el nicho, con solo 2–3 competidores.
- **Función en la tienda**: aunque venda poco, **ancla el precio de todo lo demás**.
  Un catálogo donde el producto más caro vale $89.990 hace que un set de $34.990
  parezca razonable. Es psicología de precio, no volumen.
- **Riesgo**: capital inmovilizado alto y rotación lenta. Compra 15–20 unidades, no más.

### 4. Dispensador de jabón de pared rellenable

- **Evidencia**: 6 ofertas, mediana $9.063, 67% en Full, demanda constante.
- **Por qué**: es el objeto más visible del baño y el que más "afea" cuando es el
  envase original del supermercado. Argumento de venta directo.
- **Precio sugerido**: $22.990 el doble de pared.

### 5. Organizador de ducha sin taladro

- **Evidencia**: 11 ofertas, 196 uds/publicación — demanda sólida y repartida.
  Mediana $7.990.
- **Por qué**: objeción cero (no hay que perforar, sirve para arrendatarios, que son
  muchísimos en Santiago).
- **Precio sugerido**: $18.990–21.990 en versión aluminio negro mate.

---

## El acantilado del umbral de envío gratis

Este es el hallazgo más accionable si además vendes en MercadoLibre como canal
secundario. En Chile el umbral es **$19.990**: sobre ese precio, el envío lo pagas tú.

**Producto de 0,8 kg:**

| Precio de venta | Comisión | Cargo fijo | Envío | Te queda | % |
|---:|---:|---:|---:|---:|---:|
| $18.990 | $3.228 | $600 | $0 | **$15.161** | 79,8% |
| $19.890 | $3.381 | $600 | $0 | **$15.908** | 80,0% |
| **$19.990** | $3.398 | $0 | $3.410 | **$13.181** | 65,9% |
| $21.990 | $3.738 | $0 | $3.410 | $14.841 | 67,5% |
| $24.990 | $4.248 | $0 | $3.410 | $17.331 | 69,4% |

**Subir el precio de $19.890 a $19.990 te hace perder $2.727 por unidad.** Necesitas
llegar a **$23.900** solo para recuperar lo que ganabas a $19.890.

**Producto de 2,0 kg** (alfombra de diatomea): el mismo salto de $19.490 a $19.990 te
quita $3.110 por unidad ($15.576 → $12.466).

**Regla operativa**: en MercadoLibre, o te quedas en **$19.890** o saltas directo a
**$24.990+**. La franja $19.990–$23.900 es tierra quemada.

> En tu tienda Shopify este acantilado no existe — tú defines el umbral. Por eso
> conviene poner el envío gratis en **$45.000**, justo sobre el ticket de un set, para
> empujar el bundle.

---

## Qué evitar

| Nicho | Por qué no |
|---|---|
| **Alfombras de baño absorbentes** | 16 competidores, mediana $3.146, score 18,7 — el peor del ranking. Guerra de precio pura |
| **Toallas** | 17 ofertas, 39% de descuento mediano, solo 65 uds/pub. Sobreoferta con márgenes destruidos |
| **Jaboneras sueltas** | Mediana $2.771. No financia ni el costo de picking |
| **Grifería y columnas de ducha** | Alto peso (1,5–4,5 kg), instalación técnica, postventa complicada, y compites con Sodimac en su terreno |
| **Espejos con luz LED** | Precio atractivo ($65.691) pero frágiles, voluminosos y con componente eléctrico — riesgo de quiebre y de SEC |
| **Cajas organizadoras genéricas** | No son baño, 11 competidores, mediana $9.980 |

---

## Cómo validar antes de comprar inventario

1. **Confirma comisión y envío reales** en el simulador de MercadoLibre con el peso y
   las medidas exactas — la comisión de tu subcategoría puede diferir del 14–17%.
2. **Verifica el peso volumétrico**, no solo el físico. Una alfombra de diatomea de
   2 kg puede facturar como 4 kg por volumen y eso cambia todo el cálculo.
3. **Pide muestra física de cada SKU antes del pedido grande.** Sin excepción. En
   diatomea y cerámica, la diferencia entre proveedores es abismal.
4. **Parte con volumen chico**: 40–60 unidades por SKU en el primer pedido, sobre 6
   SKU. Total 250–350 unidades. Ver `docs/03-catalogo-y-margenes.md`.
5. **Cruza con Google Trends CL y Pinterest Trends** para confirmar estacionalidad
   antes de comprometerte con un producto de temporada.

---

## Anexo: los 16 productos más vendidos de la muestra

| Vendidos | Precio | Desc. | ★ | Vendedor | Producto |
|---|---:|---:|---:|---|---|
| +10.000 | $8.762 | 27% | 4,7 | n/d | Ducha bidet árabe acero inoxidable |
| +5.000 | $23.390 | 13% | 4,7 | Vaelora | Secador de manos eléctrico con sensor 1800W |
| +5.000 | $10.535 | 5% | 4,7 | n/d | Canasto ropa sucia plegable look bambú con tapa |
| +5.000 | $7.145 | 45% | 4,2 | GJG IMPORT | Cabezal de ducha turbo con masajeador 4 en 1 |
| +5.000 | $6.440 | 7% | 4,2 | HD HOGAR SPA | Pack 6 organizadores de zapatos transparentes |
| +5.000 | $5.690 | 5% | 4,9 | WakesHome | Alfombra antideslizante con ventosas de silicona |
| +5.000 | $4.290 | 38% | 4,8 | n/d | Caja de almacenamiento de cosméticos blanca |
| +1.000 | $48.677 | 16% | 4,7 | n/d | Tapa WC Bemis madera blanca cuadrada |
| +1.000 | $16.901 | 11% | 4,9 | n/d | Asiento Fanaloza Victoria redondo softclose |
| +1.000 | $16.577 | 7% | 4,8 | n/d | Caja organizadora 100 L con ruedas |
| +1.000 | $15.990 | 5% | 4,1 | n/d | Canaleta de piso drenaje acero inoxidable |
| +1.000 | $14.990 | 28% | 4,8 | AZ AURAZEUS | Cortina de baño rayada con 12 ganchos 180x180 |
| +1.000 | $13.774 | 24% | 4,4 | n/d | Ducha bidet árabe acero inoxidable |
| +1.000 | $13.496 | 55% | 4,9 | n/d | 4 repisas flotantes de acrílico |
| +1.000 | $12.990 | 13% | 4,7 | Telotenemos | Canasto ropa sucia rectangular bambú plegable |
| +1.000 | $11.675 | 59% | 4,9 | n/d | Cesto de ropa plegable 80 L con asas |

**Lectura del anexo**: fíjate que casi todos los superventas son **soluciones a un
problema concreto** (el piso mojado, la ropa sucia tirada, la ducha desordenada), no
objetos decorativos. La decoración vende el clic; el problema resuelto vende la unidad.
Tu copy tiene que hacer las dos cosas: entrar por la estética, cerrar por el problema.

---

Datos completos: `docs/datos/mercadolibre-bano-chile.xlsx` (resumen por nicho +
detalle de los 179 productos con enlace), `productos.json` y `resumen_nichos.json`.
