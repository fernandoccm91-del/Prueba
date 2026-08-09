# ProductScout

App de investigación de productos: encuentra artículos **nuevos, pequeños, con demanda y poca
competencia** en Amazon, cruza cada uno contra **Mercado Libre** para ver cuánta competencia y
cuánta venta hay en LATAM, y cotiza **proveedores en Alibaba** para calcular costo puesto en
bodega, margen y ROI.

```
Amazon ──► demanda (u/día, u/mes, $/mes) ─┐
   │       competencia (reseñas, vendedores, antigüedad)
   │                                       ├──► score 0-100 ──► ranking + veredicto
Mercado Libre ──► publicaciones, ventas ──┤
   │                                       │
Alibaba ──► precio FOB, MOQ, proveedores ─┘──► landed cost, margen, ROI
```

Funciona **sin credenciales** desde el primer minuto usando fuentes `mock` (datos de ejemplo
realistas), para que puedas ver el flujo completo y decidir qué API vale la pena pagar.

---

## Instalación

```bash
git clone <este-repo> && cd Prueba
pip install -e ".[web]"      # el motor no tiene dependencias; [web] agrega el dashboard
cp .env.example .env         # opcional, para credenciales
```

Requiere Python 3.10+.

## Uso

```bash
# Buscar (con datos de ejemplo, sin API keys)
python -m productscout scan --small-only --top 15

# Buscar por palabras clave y categoría
python -m productscout scan -k "cable organizer" -k "pill organizer" -c "Office Products"

# Solo lo que valga la pena revisar
python -m productscout scan --min-score 65 --small-only

# Ficha completa de un producto
python -m productscout show B0D3F8W7RK

# Historial y exportación
python -m productscout runs
python -m productscout list --verdict perseguir
python -m productscout export --format csv --out oportunidades.csv

# Dashboard web en http://127.0.0.1:8000
python -m productscout serve
```

Salida típica:

```
   SCORE  ASIN         PRODUCTO                                    U/DÍA   U/MES      $/MES  UTIL/U    ROI  ML
•   67.3  B0D3F8W7RK   Stainless Steel Herb Stripper Tool            4.1     122  $1,575.70   $5.02   177%  163 pub / 41 u-mes
•   65.5  B0DKQ2N4SW   Beard Growth Roller Kit with Storage Case     5.7     171  $4,457.37  $11.22   161%  132 pub / 54 u-mes
```

---

## Qué se puede saber de verdad (y qué no)

Esto es lo primero que conviene tener claro, porque define qué API necesitas:

| Dato que pediste | ¿Existe? | Cómo lo resuelve la app |
|---|---|---|
| Unidades que vende un producto en Amazon | **No hay API oficial.** Amazon nunca publica ventas de terceros | Keepa entrega el *"bought in past month"* para muchos ASIN (dato real); si no está, se estima con la curva BSR→ventas por categoría |
| Antigüedad del listing ("producto nuevo") | Sí, vía Keepa (`listedSince`) | Se usa tal cual; el score de novedad castiga listings viejos |
| Competencia en Amazon | Parcial | Reseñas del listing, reseñas medianas de los rivales de la misma búsqueda, número de vendedores en la oferta y si Amazon vende directo |
| Competencia y ventas en Mercado Libre | **Sí, API oficial** | Total de publicaciones, `sold_quantity`, precio mediano, % de tiendas oficiales |
| Precios y proveedores en Alibaba | **No hay API pública abierta** | La app genera la búsqueda lista para Alibaba y tú pegas las cotizaciones en un JSON; o conectas tu propio gateway/proveedor de datos |

Las estimaciones de venta son **señal de orden, no contabilidad**. Sirven para comparar productos
entre sí, no para proyectar tu facturación al centavo.

### Fuentes de datos

Cada bloque es intercambiable por configuración (`AMAZON_SOURCE`, `ML_SOURCE`, `SUPPLIER_SOURCE`):

**Amazon**
- `mock` — datos de ejemplo, sin credenciales. Default.
- `keepa` — [Keepa API](https://keepa.com/#!api), de pago (~€/mes por tokens). **La opción
  recomendada**: es la única accesible que da BSR, reseñas, ofertas, dimensiones, peso, fecha de
  alta del listing y unidades vendidas del último mes. Incluye el *Product Finder* para filtrar
  directamente por rango de BSR, precio, reseñas y peso.
- `paapi` — Product Advertising API 5.0 de Amazon. Gratis pero exige cuenta de Afiliados activa
  con ventas, y **no** entrega reseñas ni antigüedad. Sirve para precio, dimensiones y ofertas.
  (La firma AWS SigV4 está implementada a mano, sin SDK.)

**Mercado Libre**
- `mock` — mercado sintético determinista.
- `api` — API oficial. Crea una app en el portal de desarrolladores y pon `ML_CLIENT_ID` /
  `ML_CLIENT_SECRET`: la app pide el token con `client_credentials`, no requiere login de usuario.
  Ojo: `sold_quantity` es acumulado histórico de la publicación, así que se amortiza sobre una
  ventana configurable (`ML_SOLD_WINDOW_MONTHS`, 12 meses por defecto) para llegar a u/mes.

**Alibaba / proveedores**
- `mock` — cotizaciones sintéticas ancladas al precio de venta.
- `manual` — **el flujo realista**. La app te arma la búsqueda de Alibaba sin marca ni adjetivos
  de marketing; pides cotizaciones, y pegas precio, MOQ, escalas de precio, años del proveedor y
  Trade Assurance en `data/supplier_quotes.json`. De ahí en adelante el margen y el ROI se
  calculan con datos reales.
- `http` — apunta `SUPPLIER_HTTP_ENDPOINT` a lo que tengas derecho a usar (Alibaba Open Platform
  si te aprueban, un proveedor de datos B2B, o tu propio servicio). El mapeador acepta los
  nombres de campo más comunes.

> Alibaba no tiene API abierta y hacer scraping del sitio va contra sus términos de servicio, así
> que la app no lo hace. Por eso el modo `manual` es el camino soportado.

---

## Cómo se calcula el score

Seis sub-scores de 0 a 100 que se combinan con pesos (ver `WEIGHTS` en `productscout/scoring.py`):

| Sub-score | Peso | Qué mide |
|---|---|---|
| `demand` | 25% | Unidades y facturación mensual estimada en Amazon |
| `competition` | 25% | Reseñas del listing y de sus rivales, vendedores en la oferta, si Amazon compite, rating bajo como hueco de calidad |
| `margin` | 20% | Margen y ROI sobre el costo puesto en bodega |
| `novelty` | 10% | Días desde que el listing existe |
| `size` | 10% | Categoría de tamaño FBA y peso — premia lo pequeño |
| `mercadolibre` | 10% | Demanda vs. saturación en ML, penalizando dominio de tiendas oficiales |

Veredicto: **≥75 perseguir · ≥60 investigar · ≥45 dudoso · <45 descartar**.

Cada oportunidad guarda además las razones a favor y las advertencias en texto plano, para que el
número nunca sea una caja negra.

### Economía unitaria

```
costo unitario (según escala de precio del MOQ)
+ flete            (peso facturable = max(real, volumétrico) × tarifa aérea/marítima)
+ arancel          (DUTY_RATE sobre FOB)
+ prep             (INBOUND_PREP_USD)
= landed cost
− comisión Amazon  (AMAZON_REFERRAL_RATE, 15% por defecto)
− tarifa FBA       (según small/large standard u oversize)
= utilidad por unidad, margen y ROI
```

Todas las tarifas y supuestos viven en `.env` y en `productscout/fees.py`. Las tablas FBA son
aproximaciones del tarifario de EE.UU. y cambian cada año: revísalas antes de confiar en los
números absolutos.

---

## Ajustes que probablemente quieras hacer

- **Curvas BSR→ventas** por categoría: `data/bsr_curves.json` (`{"Home & Kitchen": [16560, 0.809]}`)
  sobreescribe los valores de `productscout/estimators.py`. Si tienes ventas reales de algún
  producto, calibra con eso: es la mejora de precisión más grande disponible.
- **Diccionario español** para las búsquedas en Mercado Libre: `data/ml_terms.json`
  (`{"tumbler": "termo"}`). Los títulos de Amazon vienen en inglés y ML busca en español.
- **Pesos del score**: `WEIGHTS` en `productscout/scoring.py`.
- **Filtros de tamaño y precio**: variables `MAX_WEIGHT_G`, `MIN_PRICE_USD`, `MAX_PRICE_USD`.

## Estructura

```
productscout/
  cli.py            comandos scan / list / show / runs / export / serve
  api.py            API HTTP + dashboard (FastAPI, opcional)
  pipeline.py       orquestación: Amazon → demanda → ML → proveedores → score
  scoring.py        los seis sub-scores y el veredicto
  estimators.py     curva BSR→ventas y demanda de ML
  fees.py           tamaño FBA, tarifas, flete, landed cost, margen, ROI
  keywords.py       título de Amazon → búsqueda en ML (español) y en Alibaba (genérica)
  models.py         modelos de dominio
  db.py             persistencia SQLite (historial de corridas)
  http.py           cliente HTTP con reintentos, solo stdlib
  sources/          adaptadores: amazon_{mock,keepa,paapi}, ml_{mock,api}, alibaba_{mock,manual,http}
  web/index.html    dashboard
data/               datos de ejemplo y archivos de ajuste
tests/              46 pruebas (unittest, sin dependencias)
```

Agregar una fuente nueva = implementar una de las tres clases de `sources/base.py` y registrarla
en las funciones `get_*_source`. Nada más cambia.

```bash
python -m unittest discover -s tests
```

## Flujo de trabajo sugerido

1. `scan --small-only --min-score 60` con Keepa para sacar una lista corta.
2. Revisar la ficha (`show ASIN`) de los 5-10 mejores: mirar las advertencias, no solo el score.
3. Abrir la URL de Alibaba que genera la app, pedir 3-5 cotizaciones reales por producto.
4. Pegarlas en `data/supplier_quotes.json`, cambiar a `SUPPLIER_SOURCE=manual` y volver a correr:
   ahora el margen y el ROI son de verdad.
5. Validar a mano lo que la herramienta no puede ver: patentes y marcas registradas, restricciones
   de categoría, certificaciones (FDA, FCC, CPSIA), estacionalidad y calidad real de la muestra.
