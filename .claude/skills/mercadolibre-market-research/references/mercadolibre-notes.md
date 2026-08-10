# Notas de dominio: acceso a datos de MercadoLibre

Conocimiento acumulado de sesiones anteriores investigando MercadoLibre Chile
(y México, como referencia). Léelo antes de improvisar un enfoque nuevo — la
mayoría de los caminos obvios ya se probaron y no funcionan.

## Qué NO funciona

- **`api.mercadolibre.com`**: devuelve 403 sin token de aplicación OAuth. No
  hay forma de sortear esto sin registrar una app y autenticar.
- **`listado.mercadolibre.<tld>/...` y `/search`**: redirigen a un muro de
  verificación de cuenta (`.../gz/account-verification?go=...`) cuando el
  cliente no parece un navegador logueado. Pasa incluso con headers de
  navegador completos.
- **Navegador headless (Playwright/Chromium)**: en varios entornos con proxy
  de salida (sandboxes, agent proxy) la conexión del browser se corta con
  `ERR_CONNECTION_RESET`, incluso apuntando `proxy: {server: ...}` al mismo
  proxy que usa curl. No pierdas tiempo depurando esto primero — prueba curl
  antes. Si de verdad hace falta JavaScript (raro para esta tarea), recién
  ahí vale la pena instalar Playwright y pelear con la config de proxy.
- **Endpoints de autosuggest** (`http2.mlstatic.com/resources/sites/.../autosuggest`):
  403 también.

## Qué SÍ funciona

**La superficie de ofertas por categoría:**
```
https://www.mercadolibre.<tld>/ofertas?category=<ID>&page=<N>
```
responde 200 con curl + headers de navegador (ver `scripts/fetch_ofertas.sh`).
Trae hasta ~1000 productos por categoría raíz, paginados de a ~40-50 por
página, con precio, descuento, vendedor (a veces), calificación, unidades
vendidas acumuladas y tipo de envío.

**Limitación importante de esta superficie**: solo muestra productos con
*oferta o descuento activo*, no el catálogo completo de la categoría. Es una
buena muestra de "qué se está moviendo" pero subestima la oferta total. Dilo
siempre explícitamente en el informe final.

También sirve `https://tendencias.mercadolibre.<tld>/<ID_categoria>` para una
lista de búsquedas en tendencia, aunque en la práctica devuelve una lista
genérica de keywords de toda la plataforma (celulares, electrodomésticos,
etc.), no específica de la categoría — útil como referencia cruzada, no como
fuente principal.

## Cómo descubrir IDs de categoría

No hace falta adivinarlos. Cada página de ofertas trae embebido el árbol de
subcategorías con conteo de ofertas activas:
```json
{"id":"category","name":"Categorías","values":[
  {"id":"MLC1616","name":"Accesorios para Baño","results":99}, ...
]}
```
Usa `scripts/discover_categories.py` sobre el HTML descargado para extraerlo.
Flujo típico: fetch de una categoría raíz amplia (ej. Hogar) → discover →
fetch de la subcategoría que interesa → discover otra vez si tiene más
subniveles → fetch de las hojas finales con varias páginas cada una.

IDs raíz conocidos de Hogar, Muebles y Jardín (verifica que sigan vigentes,
MercadoLibre reorganiza categorías de tanto en tanto):

| Sitio | ID raíz Hogar | Ejemplo hoja usada en sesión previa |
|---|---|---|
| Chile (MLC) | `MLC1574` | `MLC1613` = Baños |
| México (MLM) | `MLM1574` | `MLM1613` = Baños |

## Parsing de tarjetas de producto

`scripts/parse_cards.py` funciona sobre el markup `poly-card` / `poly-component__*`
que usa MercadoLibre en agosto de 2026. Si un día devuelve 0 resultados sobre
un HTML que visiblemente tiene productos, es porque MercadoLibre cambió las
clases CSS — abre el HTML, busca a mano el bloque de una tarjeta (`grep -o
'class="poly-card[^"]*"'` es un buen punto de partida) y actualiza los
patrones del script en vez de asumir que la categoría está vacía o que el
scraping "ya no funciona".

Notas sobre los campos que devuelve:
- `sold` viene en **cubos**, no es un número exacto: +100, +1.000, +5.000,
  +10.000, etc. Es un acumulado histórico de toda la vida de la publicación,
  no venta mensual. Sirve para comparar nichos entre sí y para ordenar por
  popularidad, no para proyectar facturación.
- `seller` solo aparece en una fracción de las tarjetas (en la sesión de
  Chile, ~51%). Cuando falta, no asumas que no tiene vendedor — trátalo como
  informacion faltante. Para contar competidores por nicho, una cota superior
  razonable es: vendedores identificados + publicaciones sin vendedor visible
  (cada una tratada como un competidor propio).
- `link` con `/p/MLC...` o `/p/MLM...` (o `/up/MLCU...`) indica que el
  producto vive en una **ficha de catálogo compartida** entre varios
  vendedores (gana quien tenga mejor precio/reputación/stock). Un link sin
  ese patrón es una publicación propia de un solo vendedor. El % de
  productos en catálogo por nicho es una señal fuerte de cuánto se puede
  diferenciar con marca propia vs. cuánto es pura guerra de precio.
- `full` se detecta por la presencia de "Enviado por" o el ícono `full_icon`
  en el markup — no hay un flag limpio y explícito en el HTML.

## Modelo de costos por país

`scripts/unit_economics.py` trae perfiles investigados para Chile (por
defecto) y México (referencia). Si el usuario pide otro país, tienes que
investigar de cero: busca "comisiones Mercado Libre <país> <año>",
"costos de envío gratis Mercado Libre <país>" y el umbral de envío gratis
vigente. Guarda lo que encuentres siguiendo el mismo formato de perfil (ver
el diccionario `PERFILES` en el script) para no tener que rehacer la
búsqueda la próxima vez.

**Fuentes usadas para Chile (agosto 2026)**:
- Comisión referencial 14%–17% para Hogar y Muebles: Wivo Analytics, Rapiboy.
- Cargo fijo ~$600 CLP bajo el umbral, umbral de envío gratis $19.990 CLP,
  descuento por reputación verde hasta 50-60%: Ayuda de MercadoLibre Chile
  (`mercadolibre.cl/ayuda/Costos-de-envios_3667`) y las mismas fuentes de
  comisión. Ninguna fuente publicó una tabla completa de tarifas de envío por
  peso — la tabla en el script es una interpolación razonable a partir de
  ejemplos sueltos, **no una cifra oficial**. Confírmala siempre en el
  simulador de MercadoLibre antes de fijar precios reales.

Estas cifras cambian. Si ha pasado más de un par de meses desde la fecha de
arriba, vale la pena rebuscar antes de confiar ciegamente en los números.
