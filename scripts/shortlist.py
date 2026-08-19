#!/usr/bin/env python3
"""Selecciona los 20 productos concretos: pequeños (<=1.5kg), demanda no
estacional, y con la economía unitaria calculada a precio de mercado real."""
import json, re, statistics as st, sys, collections
sys.path.insert(0, "/root/.claude/skills/synced/mercadolibre-market-research/scripts")
from unit_economics import margen, costo_maximo

d = [x for x in json.load(open("/home/user/Prueba/datos/productos.json")) if x["nicho"]]
nichos = json.load(open("/home/user/Prueba/datos/resumen_nichos.json"))
NM = {n["nicho"]: n for n in nichos}
por = collections.defaultdict(list)
for x in d: por[x["nicho"]].append(x)

# (nicho, producto de referencia -> regex, precio objetivo sugerido)
SEL = [
 ("Cuerdas de saltar",              r"cuerda.*salt"),
 ("Bidet ducha para WC",            r"bidet|árabe|arabe"),
 ("Hand grip / agarre",             r"hand ?grip|ejercitador de mano"),
 ("Bolsas para sellado al vacío",   r"rollo|bolsas"),
 ("Bandas elásticas resistencia",   r"set|kit|power"),
 ("Balanzas y grameras",            r"gramera|balanza"),
 ("Organizadores de ducha",         r"esquiner|repisa|estante"),
 ("Barras seguridad y movilidad",   r"barra|manilla"),
 ("Dispensador lavalozas/esponja",  r"dispensador"),
 ("Quita pelusas y pelo mascota",   r"rodillo|roller|cepillo"),
 ("Termómetros de cocina",          r"term[óo]metro"),
 ("Escobillas y limpieza WC",       r"escobilla|cepillo"),
 ("Antideslizantes y alfombras baño", r"antideslizante|tapete"),
 ("Cabezales y kits de ducha",      r"cabezal|tel[ée]fono|turbo"),
 ("Cortinas de baño",               r"cortina.*im[áa]n|cortina"),
 ("Organizadores de maquillaje",    r"espejo|led|giratori"),
 ("Cortadores y mandolinas",        r"mandolina|picador|rallador"),
 ("Accesorios crossfit textiles",   r"mu[ñn]equer|k.?tape"),
 ("Contenedores herméticos",        r"set|herm[ée]tic|contenedor"),
 ("Rejillas y desagües",            r"rejilla|anti.?olor|desag"),
 ("Paños de microfibra",            r"microfibra"),
 ("Cestos de ropa sucia",           r"plegable|cesto|canasto"),
 ("Colgadores y perchas de ropa",   r"terciopelo|antideslizante"),
 ("Toalleros y ganchos baño",       r"gancho|toaller"),
 ("Guantes desechables",            r"nitrilo|vinilo|caja"),
 ("Esponjas y estropajos",          r"esponja|set"),
 ("Cajas y bolsas organizadoras",   r"caja|bolsa|separador"),
 ("Bolsas de lavado",               r"bolsa|malla"),
]

filas = []
for nicho, pat in SEL:
    items = por.get(nicho, [])
    if not items: continue
    n = NM.get(nicho)
    # filtro de evidencia: muestra mínima y demanda mínima para sostener una apuesta
    if not n or n["peso_kg"] > 1.5: continue
    if n["ofertas"] < 4 or n["uds_pub"] < 200: continue
    # producto de referencia: el más vendido que matchea el patrón
    cand = [x for x in items if re.search(pat, x["title"], re.I)] or items
    ref = max(cand, key=lambda x: (x["sold"] or 0, -(x["price"] or 0)))
    precio = n["precio_mediano"]; peso = n["peso_kg"]
    neto, dg = margen(precio, 0, peso, "CL")
    cmax = costo_maximo(precio, peso, "CL")
    filas.append(dict(nicho=nicho, ref=ref["title"], ref_precio=ref["price"],
        ref_vendidos=ref["sold"], ref_link=ref["link"], ref_seller=ref["seller"],
        precio_mediano=precio, peso_kg=peso, ofertas=n["ofertas"],
        competidores=n["competidores"], uds_pub=n["uds_pub"], pct_full=n["pct_full"],
        desc_mediano=n["desc_mediano"], comision=dg["comision"], cargo_fijo=dg["cargo_fijo"],
        envio=dg["envio"], disponible=round(neto), pct_disponible=round(neto/precio*100),
        costo_max_25=round(cmax), multiplo=round(precio/max(cmax,1),1), score=n["score"]))

filas.sort(key=lambda r: -r["score"])
filas = filas[:20]
json.dump(filas, open("/home/user/Prueba/datos/shortlist20.json","w"), ensure_ascii=False, indent=1)

print(f"{'#':>2} {'PRODUCTO / NICHO':<32}{'kg':>5}{'p.med':>9}{'comp':>5}{'u/pub':>7}{'com':>7}{'fijo':>6}{'env':>6}{'disp':>8}{'%':>5}{'cmax25':>9}{'x':>5}")
print("-"*106)
for i,r in enumerate(filas,1):
    print(f"{i:>2} {r['nicho'][:31]:<32}{r['peso_kg']:>5}{r['precio_mediano']:>9,}{r['competidores']:>5}"
          f"{r['uds_pub']:>7}{r['comision']:>7,}{r['cargo_fijo']:>6,}{r['envio']:>6,}{r['disponible']:>8,}"
          f"{r['pct_disponible']:>5}{r['costo_max_25']:>9,}{r['multiplo']:>5}")
print("\n--- producto de referencia por nicho ---")
for i,r in enumerate(filas,1):
    print(f"{i:>2}. [{r['ref_vendidos'] or 0:>6} vend | ${r['ref_precio']:>7,}] {r['ref'][:80]}")
