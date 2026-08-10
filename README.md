# Investigación: productos de baño con demanda y margen en MercadoLibre

Análisis de la categoría de baño en MercadoLibre para identificar qué productos tienen demanda
comprobada y cuáles dejan margen después de comisiones y despacho.

**Chile (MLC) — mercado principal**

- **Informe:** [`informe/chile.md`](informe/chile.md) · [versión web](informe/chile.html)
- **Datos:** [`datos/mercadolibre_bano_cl.csv`](datos/mercadolibre_bano_cl.csv) — 273 productos
- **Análisis:** [`scripts/analyze_cl.py`](scripts/analyze_cl.py)

**México (MLM) — referencia comparativa**

- **Informe:** [`informe/README.md`](informe/README.md) · [versión web](informe/index.html)
- **Datos:** [`datos/mercadolibre_bano_mx.csv`](datos/mercadolibre_bano_mx.csv) — 173 productos
- **Análisis:** [`scripts/analyze.py`](scripts/analyze.py)

## Reproducir la captura

```bash
# 1. Descargar las páginas de ofertas por categoría de baño (Chile)
for c in MLC1613 MLC1616 MLC175577 MLC440088 MLC175583 MLC412368 MLC412391 \
         MLC414062 MLC412384 MLC416214 MLC1614 MLC180881 MLC435273; do
  mkdir -p subcl/$c
  for p in 1 2 3; do
    scripts/fetch.sh "https://www.mercadolibre.cl/ofertas?category=$c&page=$p" subcl/$c/p$p.html
  done
done

# 2. Clasificar en nichos y calcular demanda, competencia y margen
python3 scripts/analyze_cl.py
```

`scripts/analyze_cl.py` genera `datos/dataset_bano_cl.json` (productos clasificados) y
`datos/resumen_nichos_cl.json` (métricas por nicho), e imprime la tabla comparativa.
Para México el equivalente es `scripts/analyze.py` sobre `sub/MLM*`.

## Alcance y limitaciones

La API pública de MercadoLibre y las páginas de búsqueda rechazan el acceso automatizado, así que
los datos provienen de la superficie de **ofertas por categoría**. Eso implica una muestra de
productos con descuento activo —buena para medir qué se mueve, incompleta como censo de oferta— y
un conteo de "vendidos" que es acumulado histórico y viene en cubos (+100, +1,000, +5,000, +10,000).
Los costos de envío del modelo de rentabilidad son estimaciones y deben confirmarse en el simulador
de costos de MercadoLibre. El detalle está en la sección de método del informe.
