"""Clusteriza los productos de baño capturados y calcula métricas de demanda/competencia."""
import json, re, glob, statistics as st, importlib.util
from collections import defaultdict

spec = importlib.util.spec_from_file_location('po', 'parse_ofertas.py')
po = importlib.util.module_from_spec(spec); spec.loader.exec_module(po)

CATS = {
    'MLM1613': 'Baños (raíz)', 'MLM1616': 'Accesorios para Baño', 'MLM437239': 'Barrales y Cortinas',
    'MLM12269': 'Grifería para Baño', 'MLM31513': 'Lavabos', 'MLM412384': 'Sanitarios',
    'MLM151569': 'Tapetes de Baño', 'MLM443824': 'Tinas', 'MLM193786': 'Toallas y Batas',
    'MLM189241': 'Mobiliario para Baños',
}

# nicho -> (regex, peso_kg_estimado)
NICHOS = [
    ('Regaderas / cabezales de ducha', r'regadera|cabezal.*ducha|ducha.*lluvia|rociador', 1.0),
    ('Mezcladoras y llaves (grifería)', r'mezcladora|llave.*(lavabo|baño)|monomando|grifo|griferia|grifería', 1.5),
    ('Filtros y ahorradores de agua', r'filtro.*(ducha|regadera|agua)|ahorrador', 0.4),
    ('Organizadores / repisas de ducha', r'organizador|repisa|estante|canast|rack|esquiner', 1.2),
    ('Barras de seguridad / agarraderas', r'agarrader|barra de seguridad|barral de seguridad|antiderrapante.*barra', 1.0),
    ('Cortinas de baño y barras de cortina', r'cortina|barra telesc|barral', 0.9),
    ('Porta rollos / toalleros / ganchos', r'porta ?rollo|toaller|gancho|colgador|portapapel|dispensador de papel', 0.5),
    ('Dispensadores de jabón / sets de accesorios', r'dispensador|jabon|jabón|set.*accesorios|kit.*accesorios|4 piezas|16 piezas', 0.8),
    ('Coladeras / rejillas / antiolores', r'coladera|rejilla|antiolor|desag|trampa', 0.4),
    ('Espejos de baño (LED)', r'espejo', 3.0),
    ('Muebles y gabinetes de baño', r'mueble|gabinete|kit de lavabo|vanity|alacena', 12.0),
    ('Tapetes y alfombras de baño', r'tapete|alfombra|antiderrapante(?!.*barra)', 1.0),
    ('Toallas y batas', r'toalla|bata|toallon|toallón', 1.2),
    ('Sanitarios / WC / asientos', r'sanitario|inodoro|wc|taza de baño|asiento.*(wc|sanitario)|mingitorio|bidet', 20.0),
    ('Lavabos / ovalines', r'lavabo|ovalin|ovalín', 10.0),
    ('Tinas y hidromasaje', r'tina|jacuzzi|hidromasaje|bañera', 30.0),
    ('Calentadores / boiler / bombas', r'calentador|boiler|bomba|presuriza', 15.0),
]


def nicho_de(title):
    t = title.lower()
    for name, rx, w in NICHOS:
        if re.search(rx, t):
            return name, w
    return 'Otros', 1.0


def load():
    rows, seen = [], set()
    for cid in CATS:
        pat = f'sub/{cid}/p*.html' if glob.glob(f'sub/{cid}/p*.html') else 'bano_p*.html'
        for f in sorted(glob.glob(pat)):
            for it in po.cards(f):
                key = (it['link'] or it['title'])
                if key in seen:
                    continue
                seen.add(key)
                it['src_cat'] = CATS[cid]
                it['nicho'], it['peso_kg'] = nicho_de(it['title'])
                rows.append(it)
    return rows


# ---- modelo de rentabilidad (MX, 2026) ----
COMISION = {'clasica': 0.15, 'premium': 0.195}   # Hogar, Muebles y Jardín
ISR = 0.025  # retención a partir de 2026


def costo_fijo(precio):
    if precio >= 299:
        return 0
    if precio < 99:
        return 25
    if precio < 149:
        return 30
    return 37


def envio_estimado(precio, peso_kg):
    """Costo neto de envío gratis que absorbe el vendedor (estimación, reputación verde)."""
    if precio < 299:
        return 0  # envío no obligatorio; el comprador suele pagarlo
    if peso_kg <= 0.5:
        base = 105
    elif peso_kg <= 1:
        base = 120
    elif peso_kg <= 2:
        base = 145
    elif peso_kg <= 5:
        base = 175
    elif peso_kg <= 10:
        base = 230
    elif peso_kg <= 25:
        base = 380
    else:
        base = 650
    return round(base * 0.6)  # ~40% de subsidio/descuento efectivo con reputación verde


def margen(precio, costo, peso_kg, tipo='premium'):
    com = precio * COMISION[tipo]
    fijo = costo_fijo(precio) if tipo == 'clasica' else 0
    env = envio_estimado(precio, peso_kg)
    isr = precio * ISR
    neto = precio - com - fijo - env - isr - costo
    return neto, dict(comision=round(com), fijo=fijo, envio=env, isr=round(isr))


if __name__ == '__main__':
    rows = load()
    json.dump(rows, open('dataset_bano.json', 'w'), ensure_ascii=False, indent=1)
    g = defaultdict(list)
    for r in rows:
        g[r['nicho']].append(r)

    print(f"{'nicho':40}{'ofertas':>8}{'vendedores':>11}{'p50 $':>8}{'rango $':>14}{'uds med':>9}{'uds tot':>9}{'★':>5}{'desc%':>7}")
    resumen = []
    for n, v in sorted(g.items(), key=lambda x: -sum(y['sold'] or 0 for y in x[1])):
        pr = sorted(x['price'] for x in v if x['price'])
        so = [x['sold'] for x in v if x['sold']]
        ds = [int(re.sub(r'\D', '', x['discount'])) for x in v if x['discount']]
        ra = [x['rating'] for x in v if x['rating']]
        sellers = len({x['seller'] for x in v if x['seller']})
        row = dict(nicho=n, ofertas=len(v), vendedores=sellers,
                   p50=int(st.median(pr)) if pr else 0,
                   pmin=pr[0] if pr else 0, pmax=pr[-1] if pr else 0,
                   uds_med=int(st.median(so)) if so else 0, uds_tot=sum(so),
                   rating=round(st.mean(ra), 2) if ra else None,
                   desc=int(st.median(ds)) if ds else 0,
                   peso=v[0]['peso_kg'])
        resumen.append(row)
        print(f"{n:40}{row['ofertas']:8}{sellers:11}{row['p50']:8}{str(row['pmin'])+'-'+str(row['pmax']):>14}"
              f"{row['uds_med']:9}{row['uds_tot']:9}{str(row['rating']):>5}{row['desc']:6}%")
    json.dump(resumen, open('resumen_nichos.json', 'w'), ensure_ascii=False, indent=1)
    print('\ntotal productos:', len(rows))
