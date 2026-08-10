# ProductScout

Un comando que te busca productos para vender en **Mercado Libre Chile**.

Para cada producto de tu nicho revisa:

1. **Mercado Libre** — cuántos venden lo mismo, cuánto se vende y a qué precio.
2. **Amazon (EE.UU.)** — busca el mismo producto en inglés para confirmar que la demanda existe.
3. **Alibaba** — a cuánto sale traerlo y de qué proveedores.
4. **Las cuentas** — cuánto te queda después del costo, el flete, los impuestos, la comisión de
   Mercado Libre y el envío.

Y te entrega una lista ordenada: qué vale la pena, qué no, y por qué.

---

## Empezar (2 minutos)

```bash
pip install -e ".[web]"
python -m productscout buscar
```

Eso es todo. Por defecto busca el nicho **baño** (38 búsquedas: organizadores de ducha,
dispensadores, toalleros, etc.) en Mercado Libre Chile.

Al terminar te deja un archivo **`productos.html`** en la carpeta: ábrelo con doble clic y ahí
ves todos los productos con su ficha completa, sin tocar la terminal.

Otros comandos:

```bash
python -m productscout exportar                   # vuelve a generar productos.html
python -m productscout exportar --formato csv     # o productos.csv para Excel
python -m productscout buscar cocina              # otro nicho
python -m productscout buscar -t "filtro de ducha"  # un producto puntual
python -m productscout buscar --detalle           # ficha completa de todos
python -m productscout nichos                     # ver los nichos disponibles
python -m productscout serve                      # lo mismo pero en el navegador
```

## Cómo se ve

```
Buscando productos de Baño en Mercado Libre Chile (MLC)

   #  PUNTAJE  PRODUCTO                     PUBS   U/MES   PRECIO ML   ALIBABA   GANANCIA/U  MARGEN
   1 •   66.4  toallero adhesivo              56     252     $30.442   US$6.07       $9.406     31%
   2 ·   59.5  dispensador de jabon automat 1.249     107     $64.101  US$16.07      $22.665     35%

1. • 66.4 — TOALLERO ADHESIVO
   Mercado Libre   56 publicaciones · ~252 unidades/mes · precio típico $30.442
   Amazon (EE.UU.) ~235 unidades/mes · «Adhesive Towel Bar, No-Drill Aluminum» · 41 reseñas
   Alibaba         US$6.07/unidad · pedido mínimo 200 · Xiamen Adhesive Industrial Co.
   Cuentas         cuesta $8.862 puesto en Chile · comisión+envío $7.314 · ganas $9.406/u (31%)
   Inversión       $1.772.358 para traer 200 unidades
   Proveedores     https://www.alibaba.com/trade/search?SearchText=adhesive+towel+bar
     + Solo 56 publicaciones compitiendo: poca competencia
     + Los productos equivalentes en Amazon tienen pocas reseñas (mediana 41)
```

El **puntaje** va de 0 a 100 y resume cuatro cosas: cuánto se vende, cuánta competencia hay,
cuánto ganas y si Amazon confirma la demanda. Arriba de 75 es *vale la pena*, entre 60 y 75 es
*para investigar*, más abajo es *dudoso* o *descartar*.

---

## ⚠️ Importante: hoy estás viendo datos de ejemplo

Recién instalado, el programa usa **datos inventados** para que veas cómo funciona. Los números
que muestra no son reales todavía. Para que lo sean necesitas conectar las fuentes, y ahí hay una
diferencia grande entre las tres:

| Fuente | ¿Se puede conectar? | Qué hay que hacer |
|---|---|---|
| **Mercado Libre** | Sí, gratis | Crear una app en el portal de desarrolladores (15 min) |
| **Amazon** | Sí, pagando | Suscribirte a Keepa (~€20/mes). Es opcional: sirve para confirmar demanda |
| **Alibaba** | No hay forma automática | Pides las cotizaciones tú y las pegas en un archivo (5 min por producto) |

Sobre Alibaba: no existe una API pública para consultar precios, y copiar el sitio con un robot
va contra sus términos de servicio, así que el programa no lo hace. Lo que sí hace es dejarte el
link de búsqueda listo y calcular todo apenas le pases los precios reales.

### 1. Conectar Mercado Libre (lo más importante, y es gratis)

1. Entra a https://developers.mercadolibre.cl y crea una cuenta de desarrollador.
2. Crea una aplicación. Te va a dar un **Client ID** y un **Client Secret**.
3. En la carpeta del proyecto, copia el archivo de ejemplo y pega tus datos:

```bash
cp .env.example .env
```

Abre `.env` y déjalo así:

```
ML_SOURCE=api
ML_SITE=MLC
ML_CLIENT_ID=tu_client_id
ML_CLIENT_SECRET=tu_client_secret
```

Vuelve a correr `python -m productscout buscar`. Ahora las publicaciones, las ventas y los precios
son reales.

### 2. Conectar Amazon (opcional, de pago)

Amazon **no publica** cuántas unidades vende nadie. La forma práctica de saberlo es
[Keepa](https://keepa.com/#!api): entrega el ranking de ventas, las reseñas, el peso y —para
muchos productos— las unidades vendidas del último mes. Si te suscribes, agrega a tu `.env`:

```
AMAZON_SOURCE=keepa
KEEPA_API_KEY=tu_api_key
```

Sin esto el programa igual funciona: simplemente no va a poder confirmar la demanda en Amazon y
te lo va a avisar en cada producto.

### 3. Conectar Alibaba (manual, 5 minutos por producto)

Este es el flujo real, y es el que te va a dar los números que importan:

1. Corre `python -m productscout buscar` y mira los 2-3 primeros resultados.
2. Abre el link de Alibaba que aparece en cada uno.
3. Escríbele a tres proveedores y pregunta: **precio por unidad, pedido mínimo, peso por unidad y
   costo de envío a Chile**.
4. Anota las respuestas en `data/supplier_quotes.json`:

```json
[
  {
    "match": ["toallero adhesivo", "adhesive towel bar"],
    "supplier_name": "Xiamen Homeware Co., Ltd.",
    "unit_price_usd": 4.20,
    "moq": 200,
    "unit_weight_g": 310,
    "url": "https://www.alibaba.com/product-detail/...",
    "years_active": 7,
    "trade_assurance": true,
    "price_tiers": [
      {"min_qty": 200, "unit_price_usd": 4.20},
      {"min_qty": 1000, "unit_price_usd": 3.60}
    ]
  }
]
```

5. Pon `SUPPLIER_SOURCE=manual` en tu `.env` y vuelve a correr el comando. Ahí la ganancia deja de
   ser una estimación.

---

## Cómo calcula la ganancia (Chile)

```
precio de venta en Mercado Libre        $24.990
− IVA (19%, lo declaras)                −$3.990   → te quedan $21.000
− comisión de Mercado Libre (14,5%)     −$3.624
− cargo fijo (productos bajo $9.990)         $0
− envío (obligatorio sobre $19.990)     −$2.900
− costo puesto en Chile                 −$5.980   (Alibaba + flete aéreo + 6% arancel)
= ganancia por unidad                    $8.496   (34% del precio)
```

Todos esos supuestos se pueden cambiar en el archivo `.env`: tipo de cambio, comisión, costo de
envío, si el flete es aéreo o marítimo, arancel, y si vendes con empresa o como persona natural.
**Son aproximaciones** de tarifas públicas que cambian cada año — antes de comprar, verifica la
comisión exacta en tu cuenta de vendedor y el arancel de tu producto con tu agente de aduana.

## Cambiar el nicho o agregar búsquedas

Todo vive en `data/nichos.json`, y es texto plano:

```json
{
  "bano": {
    "nombre": "Baño",
    "descripcion": "Accesorios y organización de baño.",
    "terminos": ["organizador de ducha", "filtro de ducha", "..."]
  }
}
```

Agrega los términos que se te ocurran y vuelve a correr el comando. Si un término tuyo es raro,
agrega también su traducción al inglés en `data/traducciones.json` para que la búsqueda en Amazon
y Alibaba sea buena.

## Lo que el programa no puede ver

Antes de comprar, revisa a mano:

- **Marcas y patentes** — que el producto no esté registrado por otro.
- **Certificaciones** — cosas eléctricas, que tocan agua potable o de uso infantil suelen pedirlas.
- **Estacionalidad** — un mes bueno no es un año bueno.
- **La calidad real** — pide siempre una muestra antes del pedido grande.
- **Las publicaciones que ya venden** — mira sus fotos, su precio y sus preguntas: ahí está lo que
  puedes hacer mejor.

---

## Para el que quiera mirar el código

```
productscout/
  cli.py            los comandos (buscar, nichos, scan, serve…)
  ideas.py          el flujo principal: ML → Amazon → Alibaba → cuentas
  scoring.py        cómo se arma el puntaje
  fees.py           costo puesto en el país, comisión ML, envío, ganancia
  estimators.py     estimación de ventas de Amazon a partir del ranking
  keywords.py       traducción español ↔ inglés de las búsquedas
  niches.py         paquetes de búsquedas por nicho
  db.py             historial en SQLite
  api.py + web/     el dashboard
  sources/          adaptadores: Amazon (mock/Keepa/PA-API), ML (mock/API),
                    proveedores (mock/manual/HTTP)
data/               nichos, traducciones, cotizaciones y datos de ejemplo
tests/              80 pruebas
```

El motor no tiene dependencias (solo la librería estándar de Python 3.10+); FastAPI y uvicorn se
usan únicamente para el dashboard. Agregar una fuente nueva es implementar una de las tres clases
de `sources/base.py`.

```bash
python -m unittest discover -s tests
```

También queda un flujo alternativo centrado en **Amazon FBA** (`python -m productscout scan`), por
si algún día quieres vender allá: mismo motor, pero descubriendo productos desde Amazon y
calculando tarifas de FBA en vez de comisiones de Mercado Libre.
