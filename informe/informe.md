# Oportunidades en el nicho Hogar — MercadoLibre Chile

**Fecha:** 13 de agosto de 2026 · **Sitio:** mercadolibre.cl · **Moneda:** CLP
**Muestra:** 988 publicaciones únicas con oferta activa, en 14 categorías hoja del árbol Hogar, clasificadas en 52 nichos.

---

## 1. Resumen ejecutivo

1. **Los nichos con mejor relación demanda/competencia/margen no son los más grandes.** Cámaras de seguridad (78 ofertas) y baterías de cocina (53) están saturadas y compiten por precio; los ganadores por *score* son nichos chicos y específicos: **cubrecolchón impermeable, molinillos de café, selladoras al vacío, gramera de cocina y alfombras antideslizantes de baño**.

2. **Existe un "acantilado" brutal en $19.990.** Justo bajo el umbral de envío gratis pagas solo el cargo fijo de ~$600 y te queda ~80% del precio; un peso por encima ($19.990) MercadoLibre te cobra el despacho (~$4.100 para 2 kg) y caes a ~62%. **Vender a $19.990 exacto es el peor precio posible.** Varios vendedores ya lo saben: la selladora al vacío líder está fijada en **$19.980**, un peso bajo el umbral.

3. **Casi todo el nicho Hogar vive en fichas de catálogo compartidas** (`/p/` y `/up/`): 96% de la muestra. Eso significa que en la mayoría de los nichos compites por la "compra ganadora" (precio + reputación + stock), no por diferenciación de marca. Los pocos nichos con menor % de catálogo —alfombras de baño (14%), limpieza (20%), cortinas (23%)— son donde una publicación propia bien hecha puede destacar.

4. **La demanda liviana y barata rinde más.** Productos de <1 kg y precio bajo el umbral (gramera $7.990, molinillo $10.990, cubrecolchón $8.607) dejan 75-80% disponible y toleran un costo de compra alto. El peso mata el margen: WC/sanitarios (peso ~22 kg) cae a 41% disponible pese a buena demanda.

5. **Hay productos de recompra (consumibles) escondidos en Hogar.** Rollos de sellado al vacío (+10.000 vendidos, $4.950), bolsas de basura (+10.000, ~$1.200), paños/traperos (+50.000, $1.690). Margen unitario chico pero recompra frecuente y ticket de envío que se diluye si se vende en pack.

6. **Competencia "débil" concreta:** cubrecolchón (7 competidores para +10.000 ventas de un solo modelo dominante), molinillos (9), gramera (8), selladoras (8), alfombra de baño (6). Son nichos con demanda comprobada donde todavía caben pocos jugadores más.

---

## 2. Cómo se obtuvieron los datos y qué NO cubren

- **Fuente:** superficie pública de *ofertas por categoría* (`mercadolibre.cl/ofertas?category=<ID>`), descargada con `curl` + headers de navegador. Es la única superficie estable: la API oficial exige token OAuth (403) y las páginas de listado/búsqueda redirigen a un muro de verificación.
- **(a) La muestra es de productos con oferta/descuento activo, no el catálogo completo.** Es una buena señal de "qué se está moviendo", pero subestima la oferta total de cada nicho.
- **(b) "Vendidos" es acumulado histórico en cubos** (+100, +1.000, +5.000, +10.000…), de toda la vida de la publicación, **no venta mensual**. Sirve para comparar nichos entre sí y ordenar por popularidad, no para proyectar facturación.
- **(c) El conteo de competidores es una cota superior:** el vendedor solo aparece en ~55% de las tarjetas; cada publicación sin vendedor visible se contó como un competidor propio.
- **(d) Los costos de envío y comisión son ESTIMACIONES.** Comisión referencial 14-17% (Hogar/Muebles), cargo fijo ~$600 bajo umbral, umbral de envío gratis $19.990, tabla de despacho por peso interpolada. **Confírmalos en el simulador oficial de MercadoLibre con el peso y medidas reales antes de comprometer inventario.**
- **(e) La clasificación en nichos y el peso por producto** son heurísticos (reglas sobre el título + criterio). El 8,7% quedó en "Otros / sin clasificar".

---

## 3. Mapa de la categoría Hogar (ofertas activas)

| Subcategoría | ID | Ofertas activas |
|---|---|---:|
| Cocina y Menaje | MLC1592 | 570 |
| Textiles de Hogar y Decoración | MLC436246 | 370 |
| Muebles para el Hogar | MLC436380 | 340 |
| Adornos y Decoración | MLC1631 | 254 |
| Camas, Colchones y Accesorios | MLC433403 | 250 |
| Cuidado del Hogar y Lavandería | MLC174455 | 232 |
| Seguridad para el Hogar | MLC177170 | 224 |
| Jardín y Aire Libre | MLC1621 | 218 |
| Organización para el Hogar | MLC436414 | 195 |
| Baños | MLC1613 | 192 |
| Iluminación para el Hogar | MLC1582 | 190 |

*(Categorías hoja efectivamente muestreadas: almacenamiento y vajilla de cocina, utensilios, cocción, ropa de cama, almohadas, alfombras, cortinas, monitoreo, herrajes, accesorios de limpieza, lámparas, organizadores de ropa y baños.)*

---

## 4. Ranking de oportunidad por nicho

`score = log10(uds/pub + 10) × (1/√competidores) × (1 − 0,35·%catálogo) × %disponible × 100`

> ⚠️ Los nichos con **≤5 ofertas** (marcados con \*) tienen muestra chica y score inflado/ruidoso — trátalos como pistas a validar, no como conclusiones. La tabla completa de 52 nichos está en el Excel.

| # | Nicho | Ofertas | Comp. | Uds/pub | %cat | %Full | Desc. | Precio med. | %disp | Score |
|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | Aromas / home spray / difusores \* | 1 | 1 | 500 | 100 | 100 | 25 | $19.990 | 69 | 120,9 |
| 2 | Toallero eléctrico / secatoallas \* | 2 | 2 | 550 | 100 | 50 | 23 | $53.492 | 73 | 92,5 |
| 3 | Lámpara de sal / decorativas mesa \* | 1 | 1 | 50 | 100 | 100 | 16 | $7.232 | 75 | 86,3 |
| 4 | Secaplatos / escurridores \* | 3 | 2 | 533 | 100 | 100 | 24 | $24.990 | 66 | 83,6 |
| 5 | Dispensadores de papel (baño) \* | 5 | 3 | 540 | 100 | 100 | 28 | $16.911 | 80 | 81,7 |
| 6 | **Cubrecolchón / protectores** | 12 | 7 | 1.698 | 100 | 67 | 29 | $10.797 | 77 | **61,5** |
| 7 | **Molinillos de café** | 10 | 9 | 3.180 | 100 | 100 | 14 | $16.916 | 80 | **60,3** |
| 8 | **Selladoras al vacío / conservación** | 9 | 8 | 1.789 | 100 | 89 | 35 | $19.980 | 80 | **59,8** |
| 9 | Guantes / protectores térmicos \* | 4 | 4 | 256 | 100 | 75 | 16 | $6.352 | 74 | 58,0 |
| 10 | **Alfombras baño/cocina antidesl.** | 7 | 6 | 725 | 100 | 14 | 10 | $8.174 | 76 | **57,5** |
| 11 | **Termos y mates** | 16 | 8 | 1.094 | 100 | 88 | 31 | $16.142 | 79 | **55,4** |
| 12 | **Básculas / gramera de cocina** | 10 | 8 | 880 | 100 | 80 | 8 | $8.146 | 76 | **51,3** |
| 13 | Accesorios de baño (sets) | 9 | 8 | 667 | 100 | 100 | 19 | $11.224 | 78 | 50,5 |
| 14 | Contenedores herméticos cocina | 8 | 8 | 466 | 100 | 75 | 14 | $11.490 | 78 | 47,9 |
| 15 | Carritos y repisas organizadoras | 14 | 10 | 691 | 93 | 86 | 34 | $12.990 | 78 | 47,6 |
| 16 | Cajas y canastos organizadores | 14 | 11 | 789 | 93 | 71 | 22 | $13.357 | 78 | 46,4 |
| 17 | Basureros / papeleras | 8 | 8 | 306 | 100 | 75 | 12 | $16.490 | 79 | 45,6 |
| 18 | Lámparas de techo / colgantes | 17 | 14 | 698 | 71 | 53 | 24 | $12.475 | 78 | 44,8 |
| 19 | Limpieza: traperos / mopas / cepillos | 20 | 18 | 4.115 | 100 | 20 | 18 | $8.462 | 76 | 42,0 |
| 20 | Toallas de baño | 13 | 7 | 133 | 100 | 77 | 32 | $10.980 | 78 | 41,0 |
| … | *(37 nichos más — ver Excel)* | | | | | | | | | |
| 48 | Baterías de cocina / ollas / sartenes | 53 | 33 | 441 | 100 | 51 | 20 | $42.492 | 71 | 21,2 |
| 49 | WC / sanitarios / mamparas | 19 | 15 | 854 | 100 | 47 | 24 | $28.759 | **41** | 20,2 |

---

## 5. Las apuestas concretas

### 🥇 Cubrecolchón impermeable 2 plazas
- **Por qué:** un solo modelo (Okaeri, $8.607) acumula +10.000 vendidos y hay clones de +5.000 y +1.000. Nicho de solo **12 ofertas / 7 competidores** → demanda comprobada con competencia baja. Liviano (~1,4 kg) y bajo el umbral de envío gratis.
- **Economía unitaria** (P=$8.607): comisión ~$1.463, cargo fijo $600 → **disponible ~$6.544 (76%)**. Costo máximo para 25% de margen neto: **~$4.392** → múltiplo precio/costo ~2×.
- **Riesgo:** producto muy indiferenciado; se compite por precio dentro de la ficha de catálogo. Necesitas buen precio de importación y reputación verde.

### 🥈 Molinillo de café eléctrico
- **Por qué:** **3.180 uds/publicación** (la demanda más alta entre los nichos sanos), 2 modelos con +10.000 vendidos ($10.990 y $6.291). Solo 10 ofertas / 9 competidores. Precio mediano bajo el umbral.
- **Economía unitaria** (P=$10.990, 0,8 kg): comisión ~$1.868, fijo $600 → **disponible ~$8.522 (78%)**. Costo máx. 25%: **~$5.774**.
- **Riesgo:** es un electrodoméstico → postventa, garantía y devoluciones. Verifica certificación SEC y voltaje 220V.

### 🥉 Selladora al vacío + rollos (consumible)
- **Por qué:** 1.789 uds/pub, la máquina líder a **$19.980 — un peso bajo el umbral** (pricing ya optimizado por el mercado). El verdadero negocio es el **consumible**: rollos de sellado con +10.000 vendidos a $4.950 → recompra recurrente.
- **Economía unitaria** — máquina (P=$19.980, 1,5 kg): disponible **~$15.983 (80%)**, costo máx. 25% **~$10.988**. Rollos (P=$4.950, 0,6 kg): disponible ~$3.508 (71%).
- **Riesgo:** si subes la máquina $10 a $19.990 pierdes ~$3.100 de contribución (ver §6). El descuento mediano del nicho es alto (35%) → hay guerra de precio en la máquina; compénsalo con margen del consumible.

### Básculas / gramera de cocina
- **Por qué:** 880 uds/pub, gramera líder a $7.990 (+5.000). Producto **liviano (0,5 kg) y barato** → 76% disponible y logística trivial. Solo 8 competidores. Descuento mediano bajísimo (8%) → poca guerra de precio.
- **Economía unitaria** (P=$7.990): disponible **~$6.032 (75%)**, costo máx. 25% **~$4.034**.
- **Riesgo:** ticket bajo → necesitas volumen o venta en pack para que valga la operación logística.

### Alfombra de baño antideslizante
- **Por qué:** el nicho con **menor % de catálogo (14%)** de toda la muestra → aquí SÍ se puede diferenciar con publicación y marca propia, no es pura guerra de ficha compartida. Líder a $2.702 con +5.000 vendidos.
- **Economía unitaria** (P=$2.702, 0,6 kg): disponible ~$1.643 (61%). **A este precio el cargo fijo de $600 se come el 22% del ticket** → hay que vender en set/pack para que rinda (los sets a $7.000-8.000 dejan 76%).
- **Riesgo:** ticket unitario muy bajo; solo funciona en pack o con venta cruzada de accesorios de baño.

---

## 6. El "acantilado" del envío gratis ($19.990 CLP)

Para un producto de **2 kg**, cómo cae la contribución al cruzar el umbral:

| Precio venta | Comisión | Cargo fijo / envío | Disponible | % disponible |
|---:|---:|---:|---:|---:|
| $15.990 | $2.718 | $600 | $12.672 | 79% |
| $17.990 | $3.058 | $600 | $14.332 | 80% |
| $18.990 | $3.228 | $600 | $15.162 | 80% |
| **$19.490** | $3.313 | **$600** | **$15.577** | **80%** |
| **$19.990** | $3.398 | **$4.125** | **$12.467** | **62%** |
| $20.990 | $3.568 | $4.125 | $13.297 | 63% |
| $22.990 | $3.908 | $4.125 | $14.957 | 65% |
| $24.990 | $4.248 | $4.125 | $16.617 | 66% |

**Lectura:** cruzar de $19.490 a $19.990 te hace **perder ~$3.100 de contribución** (de $15.577 a $12.467), y no recuperas el mismo monto absoluto hasta ~$23.500. **Regla práctica:** si tu producto pesa poco, fija el precio en **$19.490-$19.890**, nunca en $19.990 exacto; si necesitas subir, salta directo a ~$23.500+ donde el envío ya está amortizado.

---

## 7. Qué evitar

- **WC, sanitarios, receptáculos y mamparas** (peso ~22 kg): buena demanda (854 uds/pub) pero el despacho hunde el margen a **41% disponible**. Solo viable con logística propia o retiro en tienda.
- **Baterías de cocina / ollas** (53 ofertas, 33 competidores, peso ~4,5 kg, ticket $42.492): nicho maduro, saturado y pesado. Guerra de marcas establecidas.
- **Cámaras de seguridad WiFi** (78 ofertas, 32 competidores, 83% Full, descuento 35%): mucha demanda pero mercado saturado, dominado por marcas (EZVIZ) y con Full casi obligatorio. Difícil entrar sin capital.
- **Alfombras decorativas de living** (peso ~5 kg, 25 competidores): pesadas y muy competidas; el envío se come la ventaja.
- **Cualquier producto fijado en $19.990 exacto.**

---

## 8. Cómo validar antes de comprar inventario

1. **Confirma la comisión exacta** de la subcategoría hoja en tu cuenta de vendedor (varía 14-17% y según Clásica/Premium).
2. **Simula el despacho real** en el simulador de costos de MercadoLibre con el **peso y medidas reales** (ojo con el peso volumétrico: una alfombra liviana pero voluminosa puede tarifar como si pesara más).
3. **Pide muestra física** antes de comprometer volumen — calidad y peso reales suelen diferir de la ficha del proveedor.
4. **Arranca con volumen chico** (10-20 unidades) para medir tasa de conversión y reputación antes de escalar.
5. **Fija el precio respetando el acantilado** (§6): idealmente bajo $19.990, o bien arriba de ~$23.500.
6. **Para consumibles** (rollos, bolsas, paños): arma packs para diluir el cargo de envío y fomentar recompra.

---

## 9. Anexo — Top 15 más vendidos de la muestra

| Vendidos (acum.) | Precio | ★ | Nicho | Producto |
|---:|---:|:--:|---|---|
| +50.000 | $5.595 | 4,8 | Cortinas | Cortina Velo Liso 140x220cm 2 Paño Blanco |
| +50.000 | $1.690 | 4,9 | Limpieza | Paño limpieza Virginia Trapero Húmedo (pack) |
| +10.000 | $10.490 | 4,6 | Almohadas | Almohadas Cannon (set de 2) |
| +10.000 | $17.290 | 4,7 | Almohadas | Almohadas Cannon American Family 50x70 (set 4) |
| +10.000 | $27.990 | 4,5 | Almohada cervical | Almohada Emma Memory Adapt |
| +10.000 | $31.620 | 4,7 | WC/sanitarios | Asiento WC Portátil Plegable / Alzabaño |
| +10.000 | $12.990 | 4,7 | Vajilla/servir | Secaplatos de mesa EOLAND 2 niveles acero inox |
| +10.000 | $1.190 | 4,8 | Bolsas de basura | Bolsa de Basura Grande 80x110 (10 u) |
| +10.000 | $2.460 | 4,8 | Bolsas plásticas | Bolsas Plásticas tipo Camiseta 50x60 (100 u) |
| +10.000 | $4.950 | 4,8 | Selladoras (consumible) | Rollo Bolsas Sellado al Vacío 28cm×10m |
| +10.000 | $1.183 | 4,9 | Bolsas de basura | Aileda Bolsa de Basura con Cordón 70x90 |
| +10.000 | $10.990 | 4,8 | Molinillos café | Molinillo Eléctrico Café Sindelen 12 tazas |
| +10.000 | $6.291 | 4,7 | Molinillos café | Moledor Molinillo Eléctrico E-roca |
| +10.000 | $12.990 | 4,8 | Cortinas | Cortina Roller Tipo Zebra 120x180 Día/Noche |
| +10.000 | $7.590 | 4,8 | Cortinas | Cortina Velo Liso 140x220 con Argollas |

---

*Datos crudos y detalle completo de las 988 publicaciones y los 52 nichos: ver `datos/` y el Excel `informe/oportunidades_hogar_mercadolibre_cl.xlsx`.*
