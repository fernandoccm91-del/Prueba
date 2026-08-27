# Instalación del tema

Las secciones de `theme/` están hechas para montarse **sobre Dawn**, el tema oficial
y gratuito de Shopify. No reemplazan el tema: se suman a él.

## Por qué Dawn y no un tema pagado

Dawn es rápido, lo mantiene Shopify, es Online Store 2.0 nativo y es gratis. Los temas
comerciales de US$300 vienen cargados de funciones que no vas a usar y que pesan —
y en este nicho la velocidad **es** conversión. Con las secciones de este repo encima,
Dawn queda igual de personalizado y bastante más liviano.

## Instalación

### 1. Instalar Dawn

Panel de Shopify → **Tienda online → Temas → Añadir tema → Buscar temas gratuitos** →
Dawn → Añadir.

### 2. Subir los archivos

**Temas → ⋯ → Editar código.**

| Archivo | Dónde va | Cómo |
|---|---|---|
| `theme/assets/bano-base.css` | Assets | Añadir un recurso nuevo → Crear archivo en blanco → `bano-base.css` |
| `theme/sections/*.liquid` | Sections | Añadir una sección nueva, con el mismo nombre de archivo |
| `theme/snippets/*.liquid` | Snippets | Añadir un fragmento nuevo, con el mismo nombre de archivo |

Copia y pega el contenido completo de cada archivo, incluidos los comentarios.

> **Más rápido con Shopify CLI:** si prefieres trabajar local,
> `shopify theme dev` levanta una vista previa en vivo y `shopify theme push`
> sube todo de una vez. Copia `theme/sections`, `theme/snippets` y `theme/assets`
> dentro de tu carpeta de Dawn y listo.

### 3. Cargar el CSS y las tipografías

En `layout/theme.liquid`, dentro de `<head>` y **antes** de `{{ content_for_header }}`:

```liquid
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Inter:wght@400;500&display=swap" rel="stylesheet">
{{ 'bano-base.css' | asset_url | stylesheet_tag }}
```

### 4. Armar la home

**Tienda online → Personalizar.** En la plantilla de inicio, elimina las secciones que
trae Dawn por defecto y añade en este orden:

1. Hero de portada
2. Barra de confianza
3. Sets completos
4. Producto héroe
5. Comprar por espacio
6. Reseñas con foto
7. Antes / después
8. Preguntas frecuentes

Cada sección viene con textos por defecto en español de Chile, ya escritos.

### 5. Configurar la ficha de producto

En la plantilla de **Producto**, añade la sección **Bundle en ficha** justo debajo del
bloque de información del producto, y asígnale 3 productos complementarios.

Para los dos snippets tienes que editar `sections/main-product.liquid` de Dawn a mano.
Busca el bloque del botón de compra (`{%- when 'buy_buttons' -%}`) y agrega
**inmediatamente después** del `</div>` que lo cierra:

```liquid
{% render 'bn-fecha-entrega', dias_min: 2, dias_max: 4, zona: 'Santiago' %}
{% render 'bn-insignias-ficha', producto: product %}
```

### 6. Configurar el carro lateral

En `snippets/cart-drawer.liquid`, justo después de la apertura del formulario del
carro:

```liquid
{% render 'bn-barra-envio-gratis', umbral: 4500000 %}
```

El umbral va **en centavos**, como todos los montos de Shopify: `$45.000 CLP = 4500000`.

## Referencia de las secciones

| Sección | Archivo | Para qué |
|---|---|---|
| Hero de portada | `bn-hero.liquid` | Imagen a sangre con texto superpuesto. Alto, oscurecido y alineación configurables |
| Barra de confianza | `bn-barra-confianza.liquid` | Hasta 4 garantías con ícono. Cinco íconos SVG incluidos |
| Sets completos | `bn-sets.liquid` | Los 3 bundles. Calcula y muestra el ahorro automáticamente desde el precio comparativo |
| Producto héroe | `bn-producto-heroe.liquid` | Un producto con media grande (imagen **o video en bucle**) y hasta 4 argumentos |
| Comprar por espacio | `bn-comprar-por-espacio.liquid` | Navegación por zona del baño en vez de por tipo de objeto |
| Reseñas con foto | `bn-resenas.liquid` | Hasta 6 reseñas con imagen, estrellas y comuna |
| Antes / después | `bn-antes-despues.liquid` | Deslizador de comparación. JS propio, sin librerías |
| Preguntas frecuentes | `bn-faq.liquid` | Acordeón con `<details>` (cero JS) + datos estructurados `FAQPage` para Google |
| Bundle en ficha | `bn-bundle-ficha.liquid` | "Se ve mejor con": agrega 3 productos al carro de una vez |

| Snippet | Archivo | Para qué |
|---|---|---|
| Fecha de entrega | `bn-fecha-entrega.liquid` | Calcula la fecha concreta saltando fines de semana, con corte a las 14:00 |
| Barra de envío gratis | `bn-barra-envio-gratis.liquid` | Progreso hacia el umbral, para el carro lateral |
| Insignias de ficha | `bn-insignias-ficha.liquid` | Devolución, pago seguro y stock bajo el botón de compra |

## Notas técnicas

- **CSS con alcance de sección.** Cada sección lleva su `<style>` dentro, con selector
  `#shopify-section-{{ section.id }}`. Puedes poner la misma sección dos veces en una
  página con configuraciones distintas y no chocan.
- **Cero dependencias.** No hay jQuery, ni Swiper, ni ninguna librería externa. El
  único JavaScript son 12 líneas en el deslizador de antes/después.
- **Accesibilidad.** Foco visible en todos los elementos interactivos, `role` y
  `aria-label` donde corresponde, y los SVG decorativos marcados `aria-hidden`.
- **Imágenes responsivas.** Todas usan `image_url` con `srcset`, `sizes`, `width` y
  `height` para evitar saltos de layout (CLS).

## Limitaciones conocidas

- **`bn-fecha-entrega` no conoce los feriados chilenos.** Salta sábados y domingos,
  nada más. En septiembre y en Fiestas Patrias va a prometer de menos. Si necesitas
  esa precisión, usa una app de fechas de entrega.
- **El desfase horario es manual.** El snippet asume UTC-4. Cámbialo a -3 en horario
  de verano (`desfase_horas: -3`) o déjalo en -4 y asume una hora de error, que en un
  rango de días no cambia nada.
- **`bn-bundle-ficha` no aplica el descuento.** Muestra el ahorro y agrega los tres
  productos al carro. El descuento real lo tienes que crear en **Descuentos** de
  Shopify (compra X + Y) o con una app de bundles. Si el porcentaje de la sección y la
  regla de descuento no coinciden, el cliente ve un precio en la ficha y otro en el
  carro — revísalo cada vez que cambies precios.
