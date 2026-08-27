# Arquitectura de la tienda

## Principio de diseño

Minimalista de verdad significa **jerarquía brutal**, no "poco contenido". Cada
pantalla tiene una sola cosa que quieres que el visitante haga. Todo lo que no
empuja hacia ahí, se va.

Tres reglas que no se rompen:

1. **Una acción primaria por sección.** Un solo botón lleno por bloque.
2. **Máximo dos niveles de navegación.** Si el cliente necesita tres clics para
   llegar al producto, perdiste.
3. **El producto siempre en contexto.** Nada de fondo blanco de catálogo en la home:
   el objeto tiene que estar en un baño real, con luz real.

## Sistema visual

```
Colores
  --arena-clara   #F5F1EC   fondo principal
  --arena         #E8E0D6   fondo alterno de sección
  --tinta         #1C1917   texto y botón primario
  --tinta-suave   #57534E   texto secundario
  --piedra        #A8A29E   bordes y detalles
  --acento        #8A7F6D   solo para precio de oferta y foco de teclado
  --blanco        #FFFFFF   tarjetas de producto

Tipografía
  Títulos:  serif humanista con contraste bajo (Fraunces, Instrument Serif)
  Cuerpo:   sans geométrica neutra (Inter, Manrope) — 16 px mínimo
  Escala:   1,25 en móvil / 1,333 en escritorio

Espaciado
  Ritmo base 8 px. Secciones a 96 px en escritorio, 64 px en móvil.
  Aire generoso: es el 80% de la sensación "profesional".

Bordes y sombras
  Radio 2 px (casi recto — el radio grande se lee barato en este nicho)
  Sombras: casi ninguna. Separa con espacio y línea de 1 px, no con sombra.
```

Sin degradados, sin animaciones de entrada, sin carruseles automáticos. El lujo
percibido viene del espacio en blanco y de la fotografía, no de los efectos.

## Mapa del sitio

```
Home
├── Colecciones
│   ├── Lavamanos          (set, bandeja, dispensador)
│   ├── Ducha              (organizador, alfombra, ganchos)
│   ├── Orden y pared      (toallero-repisa, ganchos)
│   └── Sets completos     ← la colección más importante, primera en el menú
├── Producto (ficha)
├── Arma tu set            ← configurador, el diferenciador de conversión
├── Nuestra historia
├── Guías
│   ├── Cómo ordenar un baño chico
│   ├── Cómo elegir tu alfombra de baño
│   └── Baño de arriendo: todo sin taladro
├── Envíos y devoluciones
├── Preguntas frecuentes
└── Contacto
```

**Navegación superior (5 ítems máximo):**
`Sets · Lavamanos · Ducha · Orden · Arma tu set`
"Nuestra historia" y "Guías" van en el pie, no en el menú principal.

## Estructura de la home, bloque por bloque

| # | Bloque | Qué contiene | Por qué |
|---|---|---|---|
| 1 | **Barra de anuncio** | "Envío gratis sobre $45.000 · Despacho en 48 h en RM" | La objeción de envío se responde antes de que aparezca |
| 2 | **Hero** | Foto de baño completo con tus productos. Título, una línea de apoyo, un botón | Vende el resultado, no el objeto |
| 3 | **Barra de confianza** | 4 íconos: envío gratis · 30 días de devolución · pago seguro · despacho 48 h | Reduce el riesgo percibido en el primer scroll |
| 4 | **Sets completos** | 3 bundles con precio tachado y ahorro visible | El bloque que más factura. Va **antes** que los productos sueltos |
| 5 | **El héroe** | Alfombra de diatomea: foto grande, 3 argumentos, video de 8 s del agua absorbiéndose | Un producto memorable enseña de qué se trata la marca |
| 6 | **Comprar por espacio** | 3 tarjetas: Lavamanos / Ducha / Orden | Navegación por espacio, no por tipo de objeto (como Dorai Home) |
| 7 | **Prueba social** | 3 reseñas con foto real de cliente + nota promedio | Reseñas con foto convierten mucho más que reseñas de texto |
| 8 | **Antes / después** | Un baño desordenado y el mismo baño ordenado | El argumento más potente del nicho, y casi nadie lo usa |
| 9 | **Instagram / UGC** | 6 fotos con tu hashtag | Prueba social de bajo costo |
| 10 | **Pie** | Menús, medios de pago, botón de arrepentimiento, datos de la empresa | Obligaciones legales + confianza |

## Estructura de la ficha de producto

Esta es la página que gana o pierde la venta. Orden exacto:

1. **Galería** — 6 imágenes mínimo, en este orden:
   1. El producto en un baño real (no fondo blanco)
   2. Detalle de material a 20 cm
   3. Escala con referencia humana (una mano sosteniéndolo)
   4. Vista completa sobre fondo neutro
   5. Diagrama con medidas en centímetros
   6. El producto en uso / video corto en bucle
2. **Título + precio + nota de reseñas** (las estrellas hacen scroll al bloque de reseñas)
3. **Variantes** como muestras de color, no como menú desplegable
4. **Botón de compra a ancho completo**, en `--tinta`, texto "Agregar al carro — $27.990"
5. **Microcopy de envío**: "Llega entre el 3 y el 5 de septiembre a Santiago"
   (fecha concreta, no "3 a 5 días hábiles")
6. **Insignias de confianza en línea**: 30 días de devolución · pago con Webpay · stock real
7. **Bundle sugerido**: "Se ve mejor con..." — el producto + 2 complementos, con ahorro
8. **Tres argumentos con ícono** — no una lista de características, tres razones
9. **Acordeón**: Medidas y materiales / Cuidado y limpieza / Envío y devoluciones
10. **Reseñas con foto**
11. **También te puede gustar** — máximo 4 productos

### Lo que NO va en la ficha

- Contadores de cuenta regresiva falsos
- "17 personas están viendo esto ahora"
- Alertas de stock inventadas
- Ruedas de descuento

Todo eso sube la conversión un punto y te destruye la marca premium que estás
construyendo. En este nicho el cliente compra porque confía en tu criterio estético;
los trucos de urgencia gritan "dropshipping" y matan exactamente esa confianza.
Si vas a usar escasez, que sea real: stock verdadero, plazo verdadero.

## "Arma tu set" — el configurador

Tu diferenciador de conversión, copiando el mecanismo de MirrorMate.

```
Paso 1 · Elige tu paleta        → Arena · Blanco hueso · Negro mate
Paso 2 · Elige tus piezas       → grilla con casillas, mínimo 3
Paso 3 · Tu set                 → resumen en vivo, precio bajando por volumen
                                   3 piezas −10% · 4 piezas −15% · 5+ piezas −20%
```

Se puede construir con la sección `arma-tu-set.liquid` de este repo más una app de
bundles (Fast Bundle, Bundler o Rebuy) para el descuento en el carro. Déjalo para la
semana 3–4: primero valida que la tienda vende.

## Rendimiento (esto es conversión, no tecnicismo)

| Métrica | Objetivo | Por qué |
|---|---|---|
| LCP móvil | < 2,5 s | Cada segundo extra cuesta ~7% de conversión |
| Peso de la home | < 1,5 MB | Fotografía de calidad **no** significa archivos pesados |
| Imágenes | WebP, `loading="lazy"` salvo el hero | |
| Apps instaladas | Máximo 6 | Cada app inyecta JS y te frena |

Usa el tema **Dawn** (gratis, oficial, rápido) con las secciones de este repo encima.
No compres un tema de $300 USD del Theme Store: los temas comerciales vienen cargados
de funciones que no vas a usar y que pesan.
