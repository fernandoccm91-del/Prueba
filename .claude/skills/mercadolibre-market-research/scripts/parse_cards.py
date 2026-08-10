#!/usr/bin/env python3
"""Extrae productos estructurados desde páginas de ofertas de MercadoLibre ya descargadas.

Cada tarjeta de producto en /ofertas?category=... trae título, precio, precio de
lista, descuento, vendedor (cuando la tarjeta lo muestra), calificación,
unidades vendidas acumuladas (en cubos: +100, +1.000, +5.000, +10.000...), y si
usa envío Full. Este parser trabaja sobre el HTML crudo con regex porque la
página no expone una API JSON limpia; probado sobre MercadoLibre México y Chile.

Uso:
    python3 parse_cards.py archivo1.html archivo2.html ... > productos.json

Nota sobre robustez: MercadoLibre cambia nombres de clase CSS de tanto en tanto
(ej. "poly-card", "poly-component__*"). Si este script de repente devuelve 0
productos sobre un HTML que sí tiene tarjetas visibles, es señal de que cambió
el markup: abre el HTML, busca a mano el bloque de una tarjeta y actualiza los
patrones de abajo en vez de asumir que la categoría está vacía.
"""
import html
import json
import re
import sys

SOLD_RE = re.compile(r"\+?([\d.,]+)\s*(mil)?\s*vendidos?", re.I)


def norm_sold(txt):
    if not txt:
        return None
    m = SOLD_RE.search(txt)
    if not m:
        return None
    n = float(m.group(1).replace(".", "").replace(",", "."))
    if m.group(2):
        n *= 1000
    return int(n)


def norm_money(txt):
    if not txt:
        return None
    digits = txt.replace(".", "").replace(",", "")
    return int(digits) if digits.isdigit() else None


def cards(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        s = f.read()
    blocks = re.split(r'<div class="poly-card__portada', s)[1:]
    out = []
    for b in blocks:
        def g(pat, grp=1, flags=re.S):
            m = re.search(pat, b, flags)
            return html.unescape(m.group(grp)).strip() if m else None

        title = g(r'class="poly-component__title"[^>]*>([^<]+)')
        if not title:
            continue
        link = g(r'<a href="([^"#?]+)[^"]*"[^>]*class="poly-component__title"')
        # El vendedor solo aparece en una parte de las tarjetas; None es normal.
        seller = g(r'poly-component__seller"?[^>]*>(?:<span[^>]*>)?\s*([^<]+)')
        soldtxt = g(r"(Más de [\d.,]+ (?:mil )?productos vendidos|\+?[\d.,]+ ?(?:mil)? vendidos)")
        rating = g(r"Calificación ([\d.,]+) de 5")
        prices = re.findall(r"andes-money-amount__fraction[^>]*>([\d.,]+)", b)
        disc = g(r'polylabel-pill"[^>]*>(\d+% OFF)')
        out.append(
            dict(
                title=title,
                link=link,
                seller=seller,
                sold_txt=soldtxt,
                sold=norm_sold(soldtxt),
                rating=float(rating.replace(",", ".")) if rating else None,
                # cuando hay precio de lista tachado, el 2do número es el precio actual
                price=norm_money(prices[1]) if len(prices) > 1 else norm_money(prices[0] if prices else None),
                list_price=norm_money(prices[0]) if len(prices) > 1 else None,
                discount=disc,
                free_ship=bool(re.search(r"Env[íi]o gratis|Llega gratis", b)),
                full=bool(re.search(r"Enviado por|full_icon", b)),
                top_seller=bool(re.search(r"MÁS VENDIDO", b)),
            )
        )
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: parse_cards.py archivo.html [archivo2.html ...]", file=sys.stderr)
        sys.exit(1)
    items, seen = [], set()
    for path in sys.argv[1:]:
        for it in cards(path):
            key = it["link"] or it["title"]
            if key in seen:
                continue
            seen.add(key)
            items.append(it)
    print(json.dumps(items, ensure_ascii=False, indent=1))
