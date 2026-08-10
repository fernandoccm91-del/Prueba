import re, html, json, sys

SOLD_RE = re.compile(r'\+?([\d.,]+)\s*(mil)?\s*vendidos?', re.I)

def norm_sold(txt):
    if not txt:
        return None
    m = SOLD_RE.search(txt)
    if not m:
        return None
    n = float(m.group(1).replace('.', '').replace(',', '.'))
    if m.group(2):
        n *= 1000
    return int(n)

def cards(path):
    s = open(path, encoding='utf-8', errors='ignore').read()
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
        seller = g(r'poly-component__seller"?[^>]*>(?:<span[^>]*>)?\s*([^<]+)')
        soldtxt = g(r'(Más de [\d.,]+ (?:mil )?productos vendidos|\+?[\d.,]+ ?(?:mil)? vendidos)')
        rating = g(r'Calificación ([\d.,]+) de 5')
        prices = re.findall(r'andes-money-amount__fraction[^>]*>([\d.,]+)', b)
        disc = g(r'polylabel-pill"[^>]*>(\d+% OFF)')
        out.append(dict(
            title=title, link=link, seller=seller,
            sold_txt=soldtxt, sold=norm_sold(soldtxt),
            rating=float(rating) if rating else None,
            price=int(prices[1].replace('.', '').replace(',', '')) if len(prices) > 1 and prices[1].replace('.', '').replace(',', '').isdigit() else (int(prices[0].replace('.', '').replace(',', '')) if prices and prices[0].replace('.', '').replace(',', '').isdigit() else None),
            list_price=int(prices[0].replace('.', '').replace(',', '')) if len(prices) > 1 and prices[0].replace('.', '').replace(',', '').isdigit() else None,
            discount=disc,
            free_ship=bool(re.search(r'Env[íi]o gratis|Llega gratis', b)),
            full=bool(re.search(r'Enviado por|full_icon', b)),
            top_seller=bool(re.search(r'MÁS VENDIDO', b)),
        ))
    return out

if __name__ == '__main__':
    items, seen = [], set()
    for p in sys.argv[1:]:
        for it in cards(p):
            key = it['link'] or it['title']
            if key in seen:
                continue
            seen.add(key)
            items.append(it)
    print(json.dumps(items, ensure_ascii=False, indent=1))
