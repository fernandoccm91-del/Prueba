# Investigación: productos de baño con demanda y margen en MercadoLibre México

Análisis de la categoría de baño en MercadoLibre México (MLM) para identificar qué productos
tienen demanda comprobada y cuáles dejan margen después de comisiones, retención de ISR y envío.

- **Informe:** [`informe/README.md`](informe/README.md)
- **Versión web:** [`informe/index.html`](informe/index.html)
- **Datos crudos:** [`datos/mercadolibre_bano_mx.csv`](datos/mercadolibre_bano_mx.csv) — 173 productos
  con precio, descuento, unidades vendidas acumuladas, calificación, vendedor y envío.
- **Scripts:** [`scripts/`](scripts) — captura, parseo y análisis.

## Reproducir la captura

```bash
# 1. Descargar las páginas de ofertas por categoría de baño
for c in MLM1613 MLM1616 MLM437239 MLM12269 MLM31513 MLM412384 MLM151569 MLM443824 MLM193786 MLM189241; do
  mkdir -p sub/$c
  for p in 1 2 3; do
    scripts/fetch.sh "https://www.mercadolibre.com.mx/ofertas?category=$c&page=$p" sub/$c/p$p.html
  done
done

# 2. Clasificar en nichos y calcular métricas de demanda, competencia y margen
python3 scripts/analyze.py
```

`scripts/analyze.py` genera `dataset_bano.json` (productos clasificados) y `resumen_nichos.json`
(métricas por nicho), e imprime la tabla comparativa.

## Alcance y limitaciones

La API pública de MercadoLibre y las páginas de búsqueda rechazan el acceso automatizado, así que
los datos provienen de la superficie de **ofertas por categoría**. Eso implica una muestra de
productos con descuento activo —buena para medir qué se mueve, incompleta como censo de oferta— y
un conteo de "vendidos" que es acumulado histórico y viene en cubos (+100, +1,000, +5,000, +10,000).
Los costos de envío del modelo de rentabilidad son estimaciones y deben confirmarse en el simulador
de costos de MercadoLibre. El detalle está en la sección de método del informe.
