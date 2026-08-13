#!/usr/bin/env python3
"""Extrae el árbol de categorías/subcategorías desde una página de ofertas ya descargada.

Cada página https://www.mercadolibre.<tld>/ofertas?category=<ID> incluye, embebido
en el HTML, el bloque de filtros disponibles con el conteo de ofertas activas por
subcategoría. Este script lo extrae sin necesidad de adivinar IDs a mano.

Uso:
    python3 discover_categories.py archivo.html
    python3 discover_categories.py archivo1.html archivo2.html ...

Salida: JSON con [{"id": "MLC1616", "name": "Accesorios para Baño", "results": 99}, ...]

Flujo recomendado:
    1. fetch_ofertas.sh "https://www.mercadolibre.cl/ofertas?category=MLC1574" home.html
       (MLC1574 = Hogar, Muebles y Jardín; cambia el ID raíz según el rubro que
       te pidan — ver references/mercadolibre-chile-notes.md para IDs conocidos,
       o parte de la categoría raíz del sitio si no la conoces).
    2. python3 discover_categories.py home.html   -> lista subcategorías del rubro
    3. Repite fetch + discover en la subcategoría que interese hasta llegar a
       categorías hoja con pocas ofertas (ahí ya no hay más "values" del filtro).
"""
import json
import re
import sys


def extract(path: str):
    with open(path, encoding="utf-8", errors="ignore") as f:
        html = f.read()
    return [
        {"id": cid, "name": name, "results": int(count)}
        for cid, name, count in re.findall(
            r'"id":"([A-Z]{2,4}\d+)","name":"([^"]+)","results":(\d+)', html
        )
    ]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: discover_categories.py archivo.html [archivo2.html ...]", file=sys.stderr)
        sys.exit(1)
    seen = {}
    for path in sys.argv[1:]:
        for cat in extract(path):
            seen[cat["id"]] = cat  # dedup, última página gana en empate
    print(json.dumps(sorted(seen.values(), key=lambda c: -c["results"]), ensure_ascii=False, indent=1))
