#!/usr/bin/env python3
"""Calcula demanda, competencia, catálogo y margen disponible por nicho, y los
rankea con el score de oportunidad."""
import json, math, re, statistics as st, sys, collections
sys.path.insert(0, "/root/.claude/skills/synced/mercadolibre-market-research/scripts")
from unit_economics import margen, costo_maximo

PAIS = "CL"
d = [x for x in json.load(open("/home/user/Prueba/datos/productos.json")) if x["nicho"]]
por = collections.defaultdict(list)
for x in d: por[x["nicho"]].append(x)

CAT_RE = re.compile(r"/(p/ML|up/ML)")
filas = []
for nicho, items in por.items():
    if len(items) < 3:            # muestra demasiado chica para concluir
        continue
    precios = [x["price"] for x in items if x["price"]]
    if not precios: continue
    pmed = int(st.median(precios))
    peso = items[0]["peso_kg"]

    vendidos = sum(x["sold"] or 0 for x in items)
    uds_pub  = vendidos / len(items)

    sellers = {x["seller"] for x in items if x["seller"]}
    sin_seller = sum(1 for x in items if not x["seller"])
    competidores = max(len(sellers) + sin_seller, 1)

    en_cat = sum(1 for x in items if x["link"] and CAT_RE.search(x["link"])) / len(items)
    full   = sum(1 for x in items if x["full"]) / len(items)
    descs  = [int(m.group(1)) for x in items if x["discount"]
              for m in [re.match(r"(\d+)", x["discount"])] if m]
    desc_med = int(st.median(descs)) if descs else 0

    neto, desg = margen(precio=pmed, costo=0, peso_kg=peso, pais=PAIS)
    disp = neto / pmed
    cmax = costo_maximo(precio=pmed, peso_kg=peso, pais=PAIS)

    score = (math.log10(uds_pub + 10) * (1/math.sqrt(competidores))
             * (1 - 0.35*en_cat) * max(disp, 0) * 100)

    filas.append(dict(nicho=nicho, ofertas=len(items), competidores=competidores,
        uds_pub=round(uds_pub), vendidos=vendidos, pct_catalogo=round(en_cat*100),
        pct_full=round(full*100), desc_mediano=desc_med, precio_mediano=pmed,
        precio_min=min(precios), precio_max=max(precios), peso_kg=peso,
        comision=desg["comision"], cargo_fijo=desg["cargo_fijo"], envio=desg["envio"],
        disponible=round(neto), pct_disponible=round(disp*100),
        costo_max_25=round(cmax), score=round(score,1)))

filas.sort(key=lambda r: -r["score"])
json.dump(filas, open("/home/user/Prueba/datos/resumen_nichos.json","w"), ensure_ascii=False, indent=1)

hdr = f"{'#':>2} {'NICHO':<34}{'ofr':>4}{'comp':>5}{'u/pub':>7}{'%cat':>5}{'%Full':>6}{'%dto':>5}{'p.med':>9}{'kg':>6}{'disp%':>6}{'cmax25':>9}{'score':>7}"
print(hdr); print("-"*len(hdr))
for i,r in enumerate(filas,1):
    print(f"{i:>2} {r['nicho'][:33]:<34}{r['ofertas']:>4}{r['competidores']:>5}{r['uds_pub']:>7}"
          f"{r['pct_catalogo']:>5}{r['pct_full']:>6}{r['desc_mediano']:>5}{r['precio_mediano']:>9,}"
          f"{r['peso_kg']:>6}{r['pct_disponible']:>6}{r['costo_max_25']:>9,}{r['score']:>7}")
