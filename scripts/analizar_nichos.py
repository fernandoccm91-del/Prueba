#!/usr/bin/env python3
"""Agrega productos clasificados por nicho y calcula demanda, competencia,
margen disponible y un score de oportunidad. Escribe resumen_nichos.json.

Uso: python3 analizar_nichos.py productos_clasificados.json > resumen_nichos.json
"""
import json
import math
import statistics
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from unit_economics import margen, costo_maximo  # noqa: E402

PAIS = "CL"


def es_catalogo(link):
    return ("/p/MLC" in link) or ("/up/" in link)


def mediana(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else 0


def analizar(productos):
    nichos = {}
    for p in productos:
        nichos.setdefault(p["nicho"], []).append(p)

    filas = []
    for nicho, items in nichos.items():
        n = len(items)
        precios = [x["price"] for x in items if x.get("price")]
        pmed = mediana(precios)
        solds = [x["sold"] for x in items if x.get("sold")]
        uds_total = sum(solds)
        uds_por_pub = uds_total / n if n else 0

        # competidores: vendedores identificados unicos + publicaciones sin vendedor
        sellers = set()
        sin_seller = 0
        for x in items:
            s = x.get("seller")
            if s:
                sellers.add(s.strip().lower())
            else:
                sin_seller += 1
        competidores = len(sellers) + sin_seller

        pct_catalogo = sum(1 for x in items if es_catalogo(x["link"])) / n
        pct_full = sum(1 for x in items if x.get("full")) / n
        descuentos = []
        for x in items:
            d = x.get("discount")
            if d:
                m = "".join(ch for ch in d if ch.isdigit())
                if m:
                    descuentos.append(int(m))
        desc_med = mediana(descuentos) if descuentos else 0

        peso = mediana([x.get("peso_kg", 1.0) for x in items]) or 1.0
        neto, desg = margen(precio=pmed, costo=0, peso_kg=peso, pais=PAIS)
        pct_disponible = neto / pmed if pmed else 0
        cmax = costo_maximo(precio=pmed, peso_kg=peso, pais=PAIS)

        # score de oportunidad (formula validada en la skill)
        score = (
            math.log10(uds_por_pub + 10)
            * (1 / math.sqrt(competidores)) if competidores else 0
        )
        score = score * (1 - 0.35 * pct_catalogo) * max(pct_disponible, 0) * 100

        filas.append({
            "nicho": nicho,
            "ofertas": n,
            "competidores": competidores,
            "vendedores_ident": len(sellers),
            "uds_total": uds_total,
            "uds_por_pub": round(uds_por_pub, 1),
            "pct_catalogo": round(pct_catalogo, 3),
            "pct_full": round(pct_full, 3),
            "desc_mediano": desc_med,
            "peso_kg": peso,
            "precio_mediano": round(pmed),
            "precio_min": min(precios) if precios else 0,
            "precio_max": max(precios) if precios else 0,
            "disponible_tras_costos": round(neto),
            "pct_disponible": round(pct_disponible, 3),
            "costo_max_25pct": round(cmax),
            "desglose_costos": desg,
            "score": round(score, 1),
        })

    filas.sort(key=lambda r: r["score"], reverse=True)
    return filas


if __name__ == "__main__":
    productos = json.load(open(sys.argv[1]))
    filas = analizar(productos)
    json.dump(filas, sys.stdout, ensure_ascii=False, indent=1)
