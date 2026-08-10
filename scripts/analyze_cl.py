"""Clasifica los productos de baño de MercadoLibre Chile (MLC) y calcula demanda, competencia y margen."""
import json, re, glob, math, statistics as st, importlib.util
from collections import defaultdict

spec = importlib.util.spec_from_file_location('po', 'scripts/parse_ofertas.py')
po = importlib.util.module_from_spec(spec); spec.loader.exec_module(po)

CATS = {
    'MLC1613': 'Baños', 'MLC1616': 'Accesorios para Baño', 'MLC175577': 'Alfombras de Baño',
    'MLC440088': 'Barras y Cortinas', 'MLC175583': 'Espejos de Baño', 'MLC412368': 'Grifería',
    'MLC412391': 'Lavamanos', 'MLC414062': 'Platos de Ducha', 'MLC412384': 'Sanitarios',
    'MLC416214': 'Sifones de Desagüe', 'MLC1614': 'Toallas y Batas',
    'MLC180881': 'Mobiliario para Baños', 'MLC435273': 'Gasfitería',
}

# nicho -> (regex sobre el título, peso estimado en kg). El orden importa: gana la primera regla
# que calce, así que las categorías específicas van antes que las genéricas.
NICHOS = [
    ('Ducha bidet árabe / bidet para WC', r'bidet|bidé|ducha (arabe|árabe|turca)', 0.8),
    ('Accesibilidad: barras, alzabaño, sillas', r'barra[s]? de seguridad|pasamanos|manilla[s]? de seguridad|alzaba|silla de ducha|adulto mayor|discapacitad|agarrader|baranda|apoyo.*(baño|inodoro)', 2.5),
    ('Asientos y tapas de WC', r'tapa (wc|de baño|asiento)|asiento (y tapa|wc)|tapa.*(inodoro|wc)|cierre (lento|suave)|soft close', 2.5),
    ('Bombas y presurizadoras', r'bomba|presuriza|calefont|calef[oó]n', 12.0),
    ('Grifería: monomando y llaves', r'monomando|griferia|grifería|grifo|llave.*(lavatorio|ducha|tina|monomando)|mezcladora', 1.5),
    ('Kits de ducha, teléfonos y columnas', r'kit (de )?ducha|ducha tel|columna (de )?ducha|ducha moderna|brazo ducha|rociador|ducha el[eé]ctrica|regadera|alcachofa', 2.0),
    ('Cortinas de baño y barras', r'cortina|barra telesc|barral', 1.0),
    ('Ganchos y colgadores adhesivos', r'gancho|colgador|perchero|adhesiv', 0.4),
    ('Cestos de ropa sucia', r'cesto|cesta.*ropa|canasto', 1.5),
    ('Dispensadores e higiene institucional', r'dispensador|secador de mano|papel higi[eé]nico|toalla de papel|jabon|jabón|esponja', 1.5),
    ('Organizadores, estantes y repisas', r'organizador|estante|repisa|mueble.*(baño|organizador)|esquiner', 2.5),
    ('Antideslizantes y alfombras de baño', r'antideslizante|alfombra|piso de ducha|goma.*(tina|ducha)|tapete', 1.2),
    ('Sanitarios, lavamanos y receptáculos', r'recept[aá]culo|vanitorio|sanitario|taza (wc|de baño)|inodoro|wc (one piece|corto|largo)|lavamanos(?!.*(desag|pop up|sif))|tina\b', 25.0),
    ('Sifones, desagües y antiolor', r'sif[oó]n|desag[uü]e|anti-?olor|coladera|rejilla|drenaje', 0.6),
    ('Sets de accesorios de baño', r'(set|juego|kit).{0,20}(de )?(accesorios|ba(ñ|n)o)|\d+ ?(piezas|pzas)|toallero|jabonera|porta ?cepillo|escobilla|cepillo wc', 1.2),
    ('Toallas y batas', r'toalla(?! de papel)|bata|toall[oó]n', 1.2),
    ('Espejos de baño', r'espejo', 3.0),
    ('Extractores y ventilación', r'extractor|ventilaci[oó]n', 2.0),
]

# ---- modelo de costos: MercadoLibre Chile (CLP) ----
COMISION = {'clasica': 0.14, 'premium': 0.17}   # Hogar y Muebles, rango referencial 14-17%
UMBRAL_ENVIO = 19990                            # envío gratis obligatorio desde este precio
CARGO_FIJO = 600                                # por unidad, bajo el umbral
DESC_REPUTACION = 0.55                          # paga el 55% del costo de lista (reputación verde)

TARIFA_ENVIO = [(0.5, 5200), (1, 6200), (2, 7500), (5, 9500), (10, 13000), (25, 22000), (1e9, 38000)]


def envio_estimado(precio, peso_kg):
    """Costo de envío que absorbe el vendedor al ofrecer envío gratis."""
    if precio < UMBRAL_ENVIO:
        return 0                                # el comprador paga el despacho
    for tope, tarifa in TARIFA_ENVIO:
        if peso_kg <= tope:
            return round(tarifa * DESC_REPUTACION / 10) * 10
    return 0


def margen(precio, costo, peso_kg, tipo='premium'):
    com = precio * COMISION[tipo]
    fijo = CARGO_FIJO if precio < UMBRAL_ENVIO else 0
    env = envio_estimado(precio, peso_kg)
    neto = precio - com - fijo - env - costo
    return neto, dict(comision=round(com), fijo=fijo, envio=env)


def nicho_de(title):
    t = title.lower()
    for name, rx, w in NICHOS:
        if re.search(rx, t):
            return name, w
    return 'Otros', 1.5


def load(base='subcl'):
    rows, seen = [], set()
    for cid, cname in CATS.items():
        for f in sorted(glob.glob(f'{base}/{cid}/p*.html')):
            for it in po.cards(f):
                key = it['link'] or it['title']
                if key in seen:
                    continue
                seen.add(key)
                it['src_cat'] = cname
                it['nicho'], it['peso_kg'] = nicho_de(it['title'])
                rows.append(it)
    return rows


if __name__ == '__main__':
    rows = load()
    json.dump(rows, open('datos/dataset_bano_cl.json', 'w'), ensure_ascii=False, indent=1)
    g = defaultdict(list)
    for r in rows:
        g[r['nicho']].append(r)

    resumen = []
    for n, v in g.items():
        pr = sorted(x['price'] for x in v if x['price'])
        so = [x['sold'] for x in v if x['sold']]
        ds = [int(re.sub(r'\D', '', x['discount'])) for x in v if x['discount']]
        ra = [x['rating'] for x in v if x['rating']]
        cat = sum(1 for x in v if x['link'] and '/p/MLC' in x['link']) / len(v)
        p50 = int(st.median(pr)) if pr else 0
        peso = v[0]['peso_kg']
        env = envio_estimado(max(p50, UMBRAL_ENVIO), peso)
        disp = 1 - COMISION['premium'] - env / max(p50, 1)
        dpo = sum(so) / len(v)
        # Solo la mitad de las tarjetas muestra vendedor: se cuenta cada publicación
        # sin vendedor visible como un competidor propio (cota superior uniforme).
        vend = len({x['seller'] for x in v if x['seller']}) + sum(1 for x in v if not x['seller'])
        score = round(math.log10(dpo + 10) * (1 / math.sqrt(max(vend, 1)))
                      * (1 - 0.35 * cat) * max(disp, 0.01) * 100, 1) if pr else 0
        resumen.append(dict(nicho=n, ofertas=len(v), vendedores=vend,
                            p50=p50, pmin=pr[0] if pr else 0, pmax=pr[-1] if pr else 0,
                            uds_tot=sum(so), uds_publ=round(dpo), catalogo=round(100 * cat),
                            rating=round(st.mean(ra), 2) if ra else None, desc=int(st.median(ds)) if ds else 0,
                            peso=peso, envio_pct=round(100 * env / max(p50, 1)), disp=round(100 * disp),
                            full=round(100 * sum(x['full'] for x in v) / len(v)), score=score))
    resumen.sort(key=lambda r: -r['score'])
    json.dump(resumen, open('datos/resumen_nichos_cl.json', 'w'), ensure_ascii=False, indent=1)

    print(f"{'score':>6}  {'nicho':42}{'ofert':>6}{'vend':>5}{'uds/publ':>9}{'%cat':>6}{'p50 CLP':>9}{'kg':>6}{'%envío':>7}{'%disp':>6}")
    for r in resumen:
        if r['nicho'] == 'Otros' or r['ofertas'] < 4:
            continue
        print(f"{r['score']:6}  {r['nicho']:42}{r['ofertas']:6}{r['vendedores']:5}{r['uds_publ']:9}{r['catalogo']:5}%"
              f"{r['p50']:9}{r['peso']:6}{r['envio_pct']:6}%{r['disp']:5}%")
    print('\ntotal productos:', len(rows))
