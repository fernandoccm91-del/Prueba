---
name: mercadolibre-market-research
description: 'Investiga oportunidades de negocio en MercadoLibre — busca productos de una categoría con demanda comprobada, mide cuánta competencia tienen y calcula qué margen real queda después de comisión, cargo fijo y despacho. Úsala siempre que pidan "buscar productos en MercadoLibre", "qué se vende bien en MercadoLibre", "productos rentables para vender", "oportunidad de negocio", "nicho para vender", "qué vender en MercadoLibre Chile/México/etc.", o que mencionen analizar demanda, competencia o margen de una categoría de producto en MercadoLibre — incluso si no dicen la palabra "skill" o "investigación" explícitamente. El usuario de esta cuenta vive y vende en Chile: por defecto usa MercadoLibre Chile (mercadolibre.cl) y precios en CLP, salvo que pida explícitamente otro país.'
---

# Investigación de mercado en MercadoLibre

Esta skill responde una pregunta muy concreta: **de todo lo que se vende en
una categoría de MercadoLibre, ¿qué conviene vender?** No es solo "qué es
popular" — combina demanda comprobada, cuánta competencia tiene cada nicho, y
cuánto margen real queda después de que MercadoLibre se queda con su
comisión, cargo fijo y despacho. El resultado es un ranking accionable, no
una lista de productos.

Antes de escribir una sola línea de código, **lee
`references/mercadolibre-notes.md` completo**. Documenta qué endpoints están
bloqueados, cuál es la única superficie que sí responde, por qué un navegador
headless no sirve en la mayoría de estos entornos, y las cifras de costos ya
investigadas por país. Reinventar esa investigación desde cero desperdicia
tiempo y hace que el usuario espere sin necesidad.

## 0. Definir el alcance

Necesitas dos cosas antes de empezar: **qué categoría de producto** y **en
qué sitio/moneda**.

- Si el usuario no especifica país, y no hay ningún `CLAUDE.md` u otro
  contexto del proyecto que lo diga, asume **Chile (mercadolibre.cl, CLP)** —
  es donde vive y vende el usuario de esta cuenta. No asumas México ni
  Argentina por defecto.
- Si el proyecto donde estás trabajando ya tiene una investigación previa de
  este tipo (carpetas `scripts/`, `datos/`, `informe/` con un patrón
  parecido), sigue esa misma convención de nombres y estructura en vez de
  inventar una nueva.

## 1. Descubrir las categorías relevantes

Usa `scripts/fetch_ofertas.sh` y `scripts/discover_categories.py` en pares:
descarga la página de ofertas de una categoría amplia, extrae sus
subcategorías con conteo de ofertas activas, y baja un nivel más si hace
falta hasta llegar a las categorías hoja que de verdad importan para lo que
pidió el usuario.

```bash
scripts/fetch_ofertas.sh "https://www.mercadolibre.cl/ofertas?category=MLC1574" home.html
python3 scripts/discover_categories.py home.html
```

No hace falta bajar hasta el fondo del árbol completo — apunta a las 5-15
categorías hoja con más ofertas activas que correspondan al rubro pedido.

## 2. Descargar los datos

Para cada categoría hoja relevante, descarga 2-3 páginas
(`&page=1`, `&page=2`, `&page=3`) con `fetch_ofertas.sh`. Cada página trae
~40-50 productos, así que 2-3 páginas por categoría hoja suelen ser
suficientes para una muestra sólida (en sesiones anteriores, 170-270
productos totales fue un tamaño de muestra que permitió sacar conclusiones
confiables). Guarda los HTML en una carpeta organizada por ID de categoría.

## 3. Extraer los productos

```bash
python3 scripts/parse_cards.py categoria1/*.html categoria2/*.html ... > productos.json
```

El script ya deduplica por enlace/título. Revisa que el conteo de salida
tenga sentido (si descargaste ~250 tarjetas y el script devuelve 5, algo se
rompió — ver la nota sobre markup cambiante en `references/mercadolibre-notes.md`
antes de asumir que la categoría está vacía).

## 4. Clasificar en nichos (la parte que requiere criterio)

Esto **no está automatizado a propósito** — clasificar bien un nicho requiere
entender qué es el producto, no solo hacer *pattern matching* de palabras.
Lee los títulos de `productos.json` y agrupa en 10-20 nichos con sentido de
negocio real (ej. "barras de seguridad para baño" es un nicho; "productos que
contienen la palabra baño" no lo es). Para cada producto, asigna:

- **`nicho`**: el nombre del grupo al que pertenece.
- **`peso_kg`**: un peso estimado razonable del producto físico (necesario
  para el modelo de envío del paso siguiente). No hace falta precisión
  perfecta — una coladera pesa ~0.4kg, un mueble de baño ~12kg, un sanitario
  ~25kg; usa criterio de sentido común sobre qué es el objeto.
- **`src_cat`** (opcional): la subcategoría de origen, si la guardaste al
  recorrer categorías en el paso 2. Si no la tienes, déjala en `null` — no es
  obligatoria.

Guarda el resultado enriquecido (mismo `productos.json`, con `nicho` y
`peso_kg` agregados a cada registro) **usando exactamente esos nombres de
clave**. `scripts/build_report_xlsx.py` lee `productos.json` buscando esas
claves literales — si en vez de `peso_kg` escribes `peso` o `pesoKg`, la
columna correspondiente sale vacía sin ningún error visible en pantalla.

## 5. Calcular demanda, competencia y margen por nicho

Para cada nicho, calcula:

- **Ofertas**: cuántas publicaciones distintas hay.
- **Competidores**: vendedores identificados + publicaciones sin vendedor
  visible en la tarjeta (cada una tratada como un competidor propio — es una
  cota superior razonable, ver notas de dominio).
- **Uds/publicación**: unidades vendidas totales del nicho ÷ número de
  ofertas. Es la señal de demanda más confiable que tienes.
- **% en catálogo**: fracción de links con patrón `/p/MLC...`, `/p/MLM...` o
  `/up/...` — indica cuánto del nicho es ficha compartida (gana el precio)
  vs. publicación propia (se puede diferenciar con marca).
- **% Full, descuento mediano, precio mediano/mín/máx.**
- **Margen disponible**: usa `scripts/unit_economics.py` con el precio
  mediano del nicho y el peso estimado, para el país correspondiente:

  ```python
  from unit_economics import margen, costo_maximo
  neto, desglose = margen(precio=24990, costo=0, peso_kg=2.0, pais="CL")
  cmax = costo_maximo(precio=24990, peso_kg=2.0, pais="CL")  # costo máx. para 25% de margen neto
  ```

- **Score de oportunidad** (ajusta si tiene sentido, pero esta fórmula ya se
  validó en sesiones anteriores y produce rankings sensatos):

  ```
  score = log10(uds_por_publicación + 10)
          × (1 / √competidores)
          × (1 − 0.35 × %en_catálogo)
          × %disponible_tras_costos
          × 100
  ```

**Guarda cada nicho con exactamente estas claves** — no un subconjunto, no
sinónimos. `scripts/build_report_xlsx.py` valida esto y avisa si detecta que
una columna quedó vacía en (casi) todas las filas, pero es mucho mejor
evitarlo desde el origen:

```json
{
  "nicho": "Barras de seguridad para baño",
  "score": 80.4,
  "ofertas": 7,
  "vendedores": 6,
  "uds_publ": 1729,
  "uds_tot": 12100,
  "p50": 33666,
  "pmin": 7590,
  "pmax": 48180,
  "peso": 2.5,
  "catalogo": 29,
  "full": 29,
  "desc": 24,
  "disp": 67
}
```

Un error real que ya pasó: en una sesión se calcularon bien todas estas
métricas como variables intermedias (el `score` salió correcto), pero al
armar el diccionario final para guardar en `resumen_nichos.json` solo se
incluyeron `nicho`, `score` y `ofertas` — el resto de las claves nunca se
escribió. El Excel se generó sin errores (`build_report_xlsx.py` no inventa
datos que no recibió) pero la hoja "Resumen por nicho" quedó prácticamente
vacía. Desde entonces el script detecta este patrón y estampa una fila de
alerta roja bien visible en el archivo — si la ves, no es un problema del
Excel, es que `resumen_nichos.json` no tiene las claves de arriba. Antes de
entregar el archivo al usuario, revisa la salida de la consola: si
`build_report_xlsx.py` imprimió una `ADVERTENCIA`, arregla el JSON y vuelve
a correrlo — no entregues un archivo con esa advertencia.

  La intuición detrás de cada factor: `log10` porque la demanda importa pero
  con rendimientos decrecientes (10.000 ventas no es 100x mejor que 1.000);
  `1/√competidores` castiga la saturación sin aplastar nichos con algo de
  competencia sana; `%en_catálogo` penaliza los nichos donde ya no se puede
  diferenciar, solo bajar precio; `%disponible` descarta nichos que se ven
  bien en demanda pero cuya logística se come el margen.

## 6. Escribir el informe

Usa siempre esta estructura — se validó con el usuario y funcionó bien:

1. **Resumen ejecutivo**: 4-6 hallazgos concretos, numerados, con cifras
   reales (no genéricos).
2. **Cómo se obtuvieron los datos y qué NO cubren**: siempre, con
   transparencia. Menciona explícitamente: (a) la muestra es de productos
   con oferta activa, no el catálogo completo; (b) "vendidos" es acumulado
   histórico en cubos (+100, +1.000, +5.000...), no venta mensual; (c) el
   conteo de competidores es una cota superior; (d) los costos de envío son
   estimaciones que hay que confirmar en el simulador oficial de
   MercadoLibre antes de comprometer inventario real.
3. **Mapa de la categoría**: tabla de subcategorías con conteo de ofertas.
4. **Ranking de oportunidad por nicho**: tabla completa ordenada por score,
   con ofertas, competidores, %catálogo, %Full, precio mediano, descuento.
5. **Las apuestas concretas** (4-5 productos específicos, no solo nichos):
   para cada uno — por qué (evidencia concreta de la muestra), economía
   unitaria (comisión, envío/cargo fijo, disponible, costo máximo de compra,
   múltiplo precio/costo), y el riesgo específico de ese producto.
6. **El "acantilado" del umbral de envío gratis**: tabla mostrando cómo cae
   la contribución al cruzar el umbral de envío gratis del país (en Chile,
   $19.990 CLP; en México, $299 MXN) — es casi siempre el hallazgo más
   accionable del informe porque le dice al usuario exactamente dónde NO
   poner el precio.
7. **Qué evitar**: nichos con mala economía (peso alto, mucha competencia
   madura, márgenes negativos).
8. **Cómo validar antes de comprar inventario**: pasos concretos (confirmar
   comisión y envío real en el simulador, verificar peso volumétrico, pedir
   muestra física, arrancar con volumen chico).
9. **Anexo**: los 10-15 productos más vendidos de toda la muestra, con
   precio, descuento, calificación y vendedor.

## 7. Entregables — siempre en tres formatos

- **Informe visual**: si tienes acceso a la herramienta `Artifact`, carga la
  skill `artifact-design` antes de construir el HTML (define paleta, tipografía
  y layout específicos del tema, no una plantilla genérica) y publícalo. Si no
  tienes esa herramienta, un `.md` bien estructurado es suficiente.
- **Excel, nunca solo CSV**: un CSV abierto en el celular se ve como texto
  plano ilegible. Usa siempre `scripts/build_report_xlsx.py` para producir un
  `.xlsx` de dos hojas (resumen por nicho + detalle de productos) con formato
  de moneda, encabezados congelados y enlaces:

  ```bash
  python3 scripts/build_report_xlsx.py resumen_nichos.json productos.json \
      salida.xlsx --moneda CLP --titulo "Productos de baño en MercadoLibre Chile"
  ```

  Envíalo con `SendUserFile` si la tienes disponible.
- **Si estás dentro de un repositorio git**: guarda los datos crudos y el
  informe en la estructura del proyecto. No hagas commit ni push a menos que
  el usuario lo pida explícitamente.

## Notas finales

- Si el usuario pide repetir el estudio para otro país, revisa si
  `scripts/unit_economics.py` ya tiene ese perfil de costos. Si no, hay que
  investigarlo (comisión, cargo fijo, umbral de envío gratis) antes de poder
  calcular márgenes confiables — no inventes cifras.
- Si el usuario pide comparar dos países que ya investigaste antes en la
  misma conversación o proyecto, agrega una sección comparativa al final del
  informe (fue un agregado que funcionó bien: Full%, %catálogo, descuento
  mediano y umbral de envío gratis lado a lado).
