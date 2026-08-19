#!/usr/bin/env python3
"""Genera el informe visual en HTML inyectando las cifras reales del estudio."""
import json, html

D = "/home/user/Prueba/datos/"
short = json.load(open(D+"shortlist20.json"))
nichos = json.load(open(D+"resumen_nichos.json"))
cliff  = json.load(open(D+"acantilado_envio.json"))
anexo  = json.load(open(D+"anexo_top.json"))
prods  = json.load(open(D+"productos.json"))

clp = lambda v: f"${v:,.0f}".replace(",", ".")
miles = lambda v: f"{v:,.0f}".replace(",", ".")
esc = html.escape

# --- por qué cada apuesta: nota específica por nicho ---
NOTA = {
 "Cuerdas de saltar": ("Solo 2 vendedores en toda la muestra y la referencia acumula +5.000 unidades. Es el nicho menos disputado de los 20.", "Producto commodity: si entran 3 vendedores más, la única palanca es el precio. Diferénciate con el rodamiento y el cable de acero recubierto."),
 "Bidet ducha para WC": ("2.008 unidades por publicación con 4 competidores. La referencia lleva +10.000 ventas a $8.762 y hay espacio hasta $17.990.", "Producto de instalación: una fuga genera reclamo y daña reputación. Exige muestra y prueba de presión antes de comprar volumen."),
 "Cestos de ropa sucia": ("Demanda pareja todo el año, 4 competidores y 79% del precio disponible tras costos.", "Es voluminoso aunque liviano: el peso volumétrico puede encarecer el despacho más de lo que dice la tabla por kilo. Confírmalo plegado y sin plegar."),
 "Bolsas para sellado al vacío": ("El mayor ratio de la muestra: 3.333 unidades por publicación. Es consumible — el cliente vuelve a comprar.", "Margen por unidad bajo ($5.104). Solo funciona con rotación alta y compra por volumen; no sirve para vender de a una."),
 "Hand grip / agarre": ("1.512 uds/publicación con 4 competidores y solo 0,3 kg. Envío casi gratis para ti.", "Ticket bajo y producto muy copiable. Sube el ticket vendiéndolo en kit (grip + banda + cuerda) en vez de suelto."),
 "Antideslizantes y alfombras baño": ("3 competidores, 75% del precio disponible y demanda que no depende de la estación.", "Muestra chica (4 publicaciones): confirma la demanda en el buscador antes de comprometer inventario."),
 "Barras seguridad y movilidad": ("Demanda estructural por envejecimiento de la población, no por temporada. 79% disponible tras costos.", "Producto de seguridad: si se suelta del muro hay riesgo real. Pide certificación de carga al proveedor."),
 "Guantes desechables": ("850 uds/publicación, consumible puro y 0% de las publicaciones usa Full — hay espacio para ganar por logística.", "Guerra de precio por caja. El margen sale del volumen de compra, no del producto."),
 "Quita pelusas y pelo mascota": ("Consumible con recompra (repuestos adhesivos) y 5 competidores. Demanda sostenida por tenencia de mascotas.", "El repuesto es donde está el margen; véndelo como sistema rodillo + recambios, no como pieza suelta."),
 "Organizadores de maquillaje": ("743 uds/publicación con 6 competidores y 71% en Full — el nicho premia la entrega rápida.", "Es el más sensible a moda de los 20: el modelo con espejo LED puede quedar obsoleto en una temporada."),
 "Esponjas y estropajos": ("Consumible de recompra constante y solo 12% de las publicaciones usa Full.", "Ticket muy bajo por unidad: obliga a vender en pack grande para que el cargo fijo no se coma el margen."),
 "Cajas y bolsas organizadoras": ("100% de las publicaciones usa Full y hay 383 uds/publicación con 6 competidores.", "Compite contra el mismo producto genérico importado. Diferénciate por set y medidas, no por el artículo suelto."),
 "Paños de microfibra": ("788 uds/publicación y 0% usa Full: puedes ganar visibilidad solo despachando más rápido que el resto.", "Producto sin barrera de entrada. El pack de 20 unidades es el formato que ya validó el mercado."),
 "Cortinas de baño": ("Reemplazo periódico garantizado y solo 6 competidores, con descuento mediano de apenas 8% — poca guerra de precio.", "218 uds/publicación es la demanda más baja de los 20. Entra con volumen chico."),
 "Termómetros de cocina": ("0,2 kg — el producto más liviano de la lista — y demanda estable por cocina casera y repostería.", "A $2.694 el cargo fijo de $600 se lleva el 22% del precio. Solo funciona vendiéndolo sobre $6.000 o en kit."),
 "Cabezales y kits de ducha": ("731 uds/publicación, 83% en Full y reemplazo por desgaste. 78% del precio queda disponible.", "10 competidores: es el más disputado del grupo de baño. Necesitas un ángulo (filtro, presión, materiales)."),
 "Balanzas y grameras": ("938 uds/publicación con demanda cruzada de cocina, repostería y fitness. 83% en Full.", "Producto electrónico: la tasa de devolución por calibración es real. Compra con garantía del proveedor."),
 "Accesorios crossfit textiles": ("0,3 kg, consumible por desgaste y 334 uds/publicación con 8 competidores.", "Ticket bajo. Funciona como complemento de un catálogo fitness, no como producto único."),
 "Bandas elásticas resistencia": ("525 uds/publicación y el set completo se vende a $12.980 con 78% disponible.", "14 competidores — el más saturado de los 20. Entra solo si consigues un costo claramente mejor."),
 "Cortadores y mandolinas": ("692 uds/publicación y demanda constante de cocina casera. 77% del precio disponible.", "13 competidores y producto con riesgo de corte: una mala reseña por filo suelto pesa mucho."),
}

def bar(v, mx, cls="bar"):
    return f'<span class="{cls}"><span style="width:{max(3,round(v/mx*100))}%"></span></span>'

mx_score = max(r["score"] for r in short)
mx_uds   = max(r["uds_pub"] for r in short)

# --- tabla ranking 20 ---
filas20 = "".join(
 f'<tr><td class="n">{i}</td><td class="prod"><strong>{esc(r["nicho"])}</strong>'
 f'<span class="ref">{esc(r["ref"][:70])}</span></td>'
 f'<td class="num">{r["peso_kg"]:.1f}</td><td class="num">{clp(r["precio_mediano"])}</td>'
 f'<td class="num">{r["competidores"]}</td>'
 f'<td class="num">{r["uds_pub"]:,}'.replace(",",".") + f'{bar(r["uds_pub"], mx_uds, "bar sm")}</td>'
 f'<td class="num">{clp(r["disponible"])}</td><td class="num pct">{r["pct_disponible"]}%</td>'
 f'<td class="num">{clp(r["costo_max_25"])}</td>'
 f'<td class="num score">{r["score"]:.0f}{bar(r["score"], mx_score)}</td></tr>'
 for i, r in enumerate(short, 1))

# --- apuestas detalladas (top 6) ---
def apuesta(i, r):
    por, riesgo = NOTA.get(r["nicho"], ("", ""))
    return f'''<article class="bet">
 <header><span class="rank">{i:02d}</span><div><h3>{esc(r["nicho"])}</h3>
 <p class="ref">Referencia en la muestra: {esc(r["ref"])} — {miles(r["ref_vendidos"] or 0)} vendidos a {clp(r["ref_precio"])}</p></div></header>
 <p class="why">{esc(por)}</p>
 <div class="econ">
  <div><span>Precio mediano</span><b>{clp(r["precio_mediano"])}</b></div>
  <div><span>Comisión 17%</span><b class="neg">−{clp(r["comision"])}</b></div>
  <div><span>Cargo fijo</span><b class="neg">−{clp(r["cargo_fijo"])}</b></div>
  <div><span>Despacho</span><b class="neg">−{clp(r["envio"])}</b></div>
  <div class="hl"><span>Queda disponible</span><b>{clp(r["disponible"])}</b></div>
  <div class="hl"><span>Costo máx. de compra</span><b>{clp(r["costo_max_25"])}</b></div>
 </div>
 <p class="risk"><span>Riesgo</span>{esc(riesgo)}</p>
</article>'''.replace("{:,}", "")
apuestas = "".join(apuesta(i, r) for i, r in enumerate(short[:6], 1))

# --- acantilado ---
mxc = max(c["contrib"] for c in cliff)
cliff_rows = "".join(
 f'<tr class="{"peak" if c["precio"]==19890 else ("drop" if c["precio"]==19990 else "")}">'
 f'<td class="num">{clp(c["precio"])}</td><td class="num">−{clp(c["comision"])}</td>'
 f'<td class="num">{"−"+clp(c["fijo"]) if c["fijo"] else "—"}</td>'
 f'<td class="num">{"−"+clp(c["envio"]) if c["envio"] else "—"}</td>'
 f'<td class="num"><b>{clp(c["contrib"])}</b>{bar(c["contrib"], mxc)}</td>'
 f'<td class="num pct">{c["pct"]}%</td></tr>' for c in cliff)

# --- evitar ---
NM = {n["nicho"]: n for n in nichos}
def ev(nicho, motivo):
    n = NM[nicho]
    return (f'<tr><td><strong>{esc(nicho)}</strong></td><td class="num">{n["peso_kg"]:.1f}</td>'
            f'<td class="num">{clp(n["precio_mediano"])}</td><td class="num">{n["competidores"]}</td>'
            f'<td class="num pct {"bad" if n["pct_disponible"]<60 else ""}">{n["pct_disponible"]}%</td>'
            f'<td>{esc(motivo)}</td></tr>')
evitar = "".join([
 ev("Paños y traperos húmedos", "15.250 uds/publicación — la demanda más alta de todo el estudio. Pero a $1.690 el cargo fijo de $600 se lleva un tercio del precio: solo queda el 47%."),
 ev("Pesas y mancuernas", "12 kg de despacho contra un precio mediano de $28.601: el envío deja apenas el 41% disponible."),
 ev("Sartenes, ollas y baterías", "42 competidores, 98% en ficha de catálogo compartida y 6 kg de peso. Guerra de precio sin diferenciación posible."),
 ev("Suplementos deportivos", "El mayor volumen absoluto del estudio, pero 77 competidores y requiere registro sanitario del ISP para importar y vender."),
 ev("Máquinas de gimnasio", "35 kg: el despacho es prohibitivo salvo con logística propia. Descuento mediano del 49% indica márgenes ya destruidos."),
 ev("Termómetros de cocina", "Aparece en los 20 por su demanda, pero a $2.694 solo queda el 61%. Súbelo de precio o véndelo en kit."),
])

# --- anexo ---
anexo_rows = "".join(
 f'<tr><td class="prod"><a href="{esc(a["link"] or "#")}" target="_blank" rel="noopener">{esc(a["title"][:78])}</a>'
 f'<span class="ref">{esc(a["nicho"] or "—")}</span></td>'
 f'<td class="num">{clp(a["price"])}</td><td class="num">+{a["sold"]:,}'.replace(",",".") +
 f'</td><td class="num">{a["rating"] or "—"}</td><td class="num">{esc(a["seller"] or "no visible")}</td>'
 f'<td class="num">{a["disc"] or "—"}</td></tr>' for a in anexo)

# --- mapa de categorías ---
CATS = [("Cocina y Menaje","MLC1592",583),("Muebles para el Hogar","MLC436380",370),
 ("Textiles de Hogar y Decoración","MLC436246",323),("Adornos y Decoración","MLC1631",284),
 ("Cuidado del Hogar y Lavandería","MLC174455",262),("Iluminación","MLC1582",235),
 ("Jardín y Aire Libre","MLC1621",225),("Camas y Colchones","MLC433403",222),
 ("Seguridad para el Hogar","MLC177170",219),("Baños","MLC1613",175),
 ("Organización para el Hogar","MLC436414",174)]
FIT = [("Suplementos y Shakers","MLC438178",378),("Zapatillas","MLC3724",315),
 ("Camping, Caza y Pesca","MLC1362",177),("Fitness y Musculación","MLC1338",175),
 ("Ropa Deportiva","MLC1339",156),("Ciclismo","MLC1292",93),("Pilates y Yoga","MLC440636",20)]
mxh = max(c[2] for c in CATS)
def catrows(lst):
    return "".join(f'<tr><td>{esc(n)}</td><td class="mono muted">{i}</td>'
                   f'<td class="num">{v}{bar(v,mxh)}</td></tr>' for n,i,v in lst)

# --- ranking completo de nichos ---
mxs = max(n["score"] for n in nichos)
full_rows = "".join(
 f'<tr><td class="n">{i}</td><td>{esc(n["nicho"])}</td><td class="num">{n["ofertas"]}</td>'
 f'<td class="num">{n["competidores"]}</td><td class="num">{n["uds_pub"]:,}'.replace(",",".") +
 f'</td><td class="num">{n["pct_full"]}%</td><td class="num">{n["desc_mediano"]}%</td>'
 f'<td class="num">{clp(n["precio_mediano"])}</td><td class="num">{n["peso_kg"]:.1f}</td>'
 f'<td class="num pct">{n["pct_disponible"]}%</td>'
 f'<td class="num score">{n["score"]:.0f}{bar(n["score"], mxs)}</td></tr>'
 for i, n in enumerate(nichos, 1))

HTML = f'''<title>Veinte Apuestas Chicas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root{{
  --paper:#F4F7F5; --surface:#FFFFFF; --sunk:#EBF0ED;
  --ink:#141E1C; --body:#31403C; --muted:#68776F;
  --line:#D6DEDA; --hair:#E5EBE7;
  --accent:#14574F; --accent-soft:#DCEBE6;
  --warn:#A55D06; --warn-soft:#F6E8D2;
  --good:#33704A; --bad:#9C3B2E;
  --shadow:0 1px 2px rgba(20,30,28,.05), 0 8px 24px -16px rgba(20,30,28,.18);
}}
@media (prefers-color-scheme:dark){{
  :root:not([data-theme="light"]){{
    --paper:#0D1514; --surface:#151F1D; --sunk:#111A18;
    --ink:#E9F0EC; --body:#BAC8C2; --muted:#869890;
    --line:#26332F; --hair:#1E2A27;
    --accent:#5FBCAC; --accent-soft:#16302C;
    --warn:#D99A3C; --warn-soft:#2E2415;
    --good:#63AE7C; --bad:#D47563;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
  }}
}}
:root[data-theme="dark"]{{
  --paper:#0D1514; --surface:#151F1D; --sunk:#111A18;
  --ink:#E9F0EC; --body:#BAC8C2; --muted:#869890;
  --line:#26332F; --hair:#1E2A27;
  --accent:#5FBCAC; --accent-soft:#16302C;
  --warn:#D99A3C; --warn-soft:#2E2415;
  --good:#63AE7C; --bad:#D47563;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
}}
*{{box-sizing:border-box}}
body{{
  margin:0; background:var(--paper); color:var(--body);
  font-family:"Source Serif 4",Georgia,serif; font-size:17px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
}}
.wrap{{max-width:1120px; margin:0 auto; padding:0 24px 96px}}
h1,h2,h3,h4{{font-family:"Bricolage Grotesque",system-ui,sans-serif; color:var(--ink); text-wrap:balance; margin:0}}
.mono,.num,.eyebrow,th,.tag,.rank,.econ span,.risk span{{font-family:"IBM Plex Mono",ui-monospace,monospace}}
.num{{font-variant-numeric:tabular-nums}}
a{{color:var(--accent)}}
:focus-visible{{outline:2px solid var(--accent); outline-offset:3px; border-radius:3px}}

/* ---------- encabezado ---------- */
header.top{{border-bottom:1px solid var(--line); padding:64px 0 40px; margin-bottom:56px}}
.eyebrow{{font-size:11.5px; letter-spacing:.16em; text-transform:uppercase; color:var(--accent); font-weight:600}}
h1{{font-size:clamp(38px,6.4vw,68px); line-height:1.02; font-weight:800; letter-spacing:-.025em; margin:18px 0 0; max-width:16ch}}
.lede{{font-size:20px; max-width:62ch; margin:22px 0 0; color:var(--body)}}
.scope{{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1px;
  background:var(--line); border:1px solid var(--line); border-radius:10px; overflow:hidden; margin-top:40px}}
.scope div{{background:var(--surface); padding:16px 18px}}
.scope b{{font-family:"IBM Plex Mono",monospace; font-size:26px; font-weight:600; color:var(--ink); display:block; font-variant-numeric:tabular-nums; line-height:1.2}}
.scope span{{font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted)}}

/* ---------- secciones ---------- */
section{{margin:0 0 72px}}
h2{{font-size:clamp(25px,3.4vw,34px); font-weight:700; letter-spacing:-.02em; margin-bottom:6px}}
.sub{{color:var(--muted); font-size:15.5px; max-width:70ch; margin:0 0 26px}}
h3{{font-size:20px; font-weight:700; letter-spacing:-.01em}}
p{{max-width:70ch}}

/* ---------- hallazgos ---------- */
ol.finds{{list-style:none; counter-reset:f; padding:0; margin:0; display:grid; gap:2px;
  background:var(--line); border:1px solid var(--line); border-radius:10px; overflow:hidden}}
ol.finds li{{counter-increment:f; background:var(--surface); padding:20px 24px 20px 62px; position:relative}}
ol.finds li::before{{content:counter(f,decimal-leading-zero); position:absolute; left:22px; top:21px;
  font-family:"IBM Plex Mono",monospace; font-size:12px; font-weight:600; color:var(--accent)}}
ol.finds strong{{color:var(--ink); font-weight:600}}

/* ---------- tablas ---------- */
.scroll{{overflow-x:auto; border:1px solid var(--line); border-radius:10px; background:var(--surface); box-shadow:var(--shadow)}}
table{{width:100%; border-collapse:collapse; font-size:14px}}
th{{font-size:10.5px; letter-spacing:.07em; text-transform:uppercase; font-weight:600; color:var(--muted);
  text-align:right; padding:13px 12px; border-bottom:1px solid var(--line); white-space:nowrap; background:var(--sunk)}}
th:first-child,th.l{{text-align:left}}
td{{padding:12px; border-bottom:1px solid var(--hair); vertical-align:middle}}
td.num{{text-align:right; white-space:nowrap; font-family:"IBM Plex Mono",monospace; font-size:13px}}
tr:last-child td{{border-bottom:0}}
td.n{{color:var(--muted); font-family:"IBM Plex Mono",monospace; font-size:12px; width:34px; text-align:right}}
.prod strong{{color:var(--ink); font-weight:600; font-family:"Bricolage Grotesque",sans-serif; display:block; font-size:14.5px}}
.ref{{display:block; font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); margin-top:3px; line-height:1.45}}
.pct{{color:var(--good); font-weight:500}} .pct.bad{{color:var(--bad)}}
.bar{{display:block; height:3px; border-radius:2px; background:var(--hair); margin-top:5px; min-width:52px}}
.bar>span{{display:block; height:100%; border-radius:2px; background:var(--accent)}}
.bar.sm>span{{background:var(--muted); opacity:.55}}
td.score{{font-weight:600; color:var(--ink)}}
tbody tr:hover td{{background:var(--sunk)}}
.two{{display:grid; grid-template-columns:1fr 1fr; gap:24px}}
@media(max-width:760px){{.two{{grid-template-columns:1fr}}}}

/* ---------- apuestas ---------- */
.bets{{display:grid; gap:20px}}
.bet{{background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:26px 28px; box-shadow:var(--shadow)}}
.bet header{{display:flex; gap:16px; align-items:flex-start; margin-bottom:14px}}
.rank{{flex:none; width:34px; height:34px; border-radius:8px; background:var(--accent-soft); color:var(--accent);
  display:grid; place-items:center; font-size:13px; font-weight:600}}
.bet .ref{{margin-top:5px}}
.why{{margin:0 0 18px}}
.econ{{display:grid; grid-template-columns:repeat(auto-fit,minmax(146px,1fr)); gap:1px; background:var(--line);
  border:1px solid var(--line); border-radius:8px; overflow:hidden; margin-bottom:16px}}
.econ>div{{background:var(--surface); padding:11px 14px}}
.econ span{{display:block; font-size:10.5px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin-bottom:3px}}
.econ b{{font-family:"IBM Plex Mono",monospace; font-size:16px; font-weight:600; color:var(--ink); font-variant-numeric:tabular-nums}}
.econ b.neg{{color:var(--bad); font-weight:500}}
.econ .hl{{background:var(--accent-soft)}} .econ .hl b{{color:var(--accent)}}
.risk{{margin:0; font-size:15px; color:var(--body); background:var(--warn-soft); border-radius:8px; padding:12px 16px; max-width:none}}
.risk span{{display:block; font-size:10.5px; letter-spacing:.07em; text-transform:uppercase; color:var(--warn); font-weight:600; margin-bottom:3px}}

/* ---------- acantilado ---------- */
tr.peak td{{background:var(--accent-soft)}} tr.peak td b{{color:var(--accent)}}
tr.drop td{{background:var(--warn-soft)}} tr.drop td b{{color:var(--warn)}}
.callout{{border-left:3px solid var(--warn); background:var(--warn-soft); border-radius:0 10px 10px 0;
  padding:20px 24px; margin:24px 0 0}}
.callout p{{margin:0; max-width:72ch}}
.callout strong{{color:var(--ink)}}

/* ---------- método / validar ---------- */
.notes{{background:var(--sunk); border:1px solid var(--line); border-radius:12px; padding:26px 30px}}
.notes ul{{margin:0; padding-left:20px; display:grid; gap:9px}}
.notes li{{max-width:76ch}}
.notes strong{{color:var(--ink); font-weight:600}}
ol.steps{{list-style:none; counter-reset:s; padding:0; margin:0; display:grid; gap:14px}}
ol.steps li{{counter-increment:s; padding-left:44px; position:relative; max-width:74ch}}
ol.steps li::before{{content:counter(s); position:absolute; left:0; top:1px; width:26px; height:26px; border-radius:50%;
  background:var(--accent); color:var(--paper); display:grid; place-items:center;
  font-family:"IBM Plex Mono",monospace; font-size:12px; font-weight:600}}
footer{{border-top:1px solid var(--line); padding-top:26px; color:var(--muted); font-size:13.5px}}
</style>

<div class="wrap">
<header class="top">
  <div class="eyebrow">Estudio de mercado · MercadoLibre Chile · Agosto 2026</div>
  <h1>Veinte apuestas chicas</h1>
  <p class="lede">Productos pequeños y de demanda constante en hogar, baño, cocina y fitness — rankeados por demanda comprobada, competencia real y el margen que sobrevive después de que MercadoLibre cobra lo suyo.</p>
  <div class="scope">
    <div><b>1.117</b><span>publicaciones</span></div>
    <div><b>17</b><span>categorías hoja</span></div>
    <div><b>60</b><span>nichos</span></div>
    <div><b>20</b><span>apuestas ≤1,5 kg</span></div>
    <div><b>CLP</b><span>moneda</span></div>
  </div>
</header>

<section>
  <h2>Lo que dicen los datos</h2>
  <p class="sub">Seis hallazgos con cifras de la muestra, no generalidades.</p>
  <ol class="finds">
    <li>El <strong>cargo fijo de $600</strong> bajo el umbral de envío gratis es lo que decide si un producto barato sirve o no. En traperos húmedos ($1.690, la demanda más alta de todo el estudio con 15.250 uds/publicación) se lleva el 35% del precio y deja solo un 47% disponible. En los 20 seleccionados deja entre 61% y 80%.</li>
    <li>Cruzar los <strong>$19.990</strong> te hace ganar menos vendiendo más caro. A $19.890 quedan $15.909; a $19.990 quedan $13.182 — <strong>$2.727 menos por unidad</strong>. Hay que llegar a $23.280 solo para volver al mismo punto.</li>
    <li>El nicho menos disputado es <strong>cuerdas de saltar</strong>: 2 vendedores en toda la muestra, 1.275 uds/publicación y 0,3 kg. El más disputado de la lista es bandas elásticas, con 14.</li>
    <li>Los <strong>consumibles ganan por recompra</strong>: bolsas de sellado al vacío lideran con 3.333 uds/publicación, seguidas de guantes desechables, esponjas y paños de microfibra. Son los únicos productos de la lista donde el mismo cliente vuelve.</li>
    <li><strong>El peso manda sobre el precio.</strong> Mancuernas venden bien (636 uds/publicación) pero 12 kg de despacho dejan solo el 41% disponible; los 20 seleccionados pesan entre 0,2 y 1,2 kg y ninguno paga despacho.</li>
    <li>El <strong>uso de Full es desparejo</strong> y ahí hay una grieta: paños de microfibra y guantes desechables tienen 0% de publicaciones con Full pese a demanda alta. Es visibilidad que se gana solo despachando mejor.</li>
  </ol>
</section>

<section>
  <h2>Los 20 productos</h2>
  <p class="sub">Filtro aplicado: peso estimado ≤ 1,5 kg, mínimo 4 publicaciones en la muestra y al menos 200 unidades vendidas por publicación. Ordenados por score de oportunidad.</p>
  <div class="scroll"><table>
    <thead><tr><th></th><th class="l">Nicho y referencia de la muestra</th><th>Kg</th><th>Precio med.</th>
    <th>Compet.</th><th>Uds/pub.</th><th>Disponible</th><th>%</th><th>Costo máx.</th><th>Score</th></tr></thead>
    <tbody>{filas20}</tbody>
  </table></div>
  <p class="sub" style="margin-top:14px"><strong>Costo máx.</strong> = lo máximo que puedes pagar por el producto puesto en bodega y aún dejar 25% de margen neto sobre el precio de venta.</p>
</section>

<section>
  <h2>Las seis primeras, en detalle</h2>
  <p class="sub">Por qué cada una, qué queda de cada venta y qué puede salir mal.</p>
  <div class="bets">{apuestas}</div>
</section>

<section>
  <h2>El acantilado de los $19.990</h2>
  <p class="sub">Bajo el umbral pagas un cargo fijo de $600. Sobre el umbral el envío corre por tu cuenta: $3.410 para un producto de 0,7 kg con reputación verde. El salto es discontinuo.</p>
  <div class="scroll"><table>
    <thead><tr><th class="l">Precio de venta</th><th>Comisión 17%</th><th>Cargo fijo</th><th>Despacho</th><th>Contribución</th><th>%</th></tr></thead>
    <tbody>{cliff_rows}</tbody>
  </table></div>
  <div class="callout"><p><strong>Dónde no poner el precio:</strong> la franja entre $19.990 y $23.280 es tierra quemada — cobras más que a $19.890 y te llevas menos a casa. Si el producto no puede sostener $24.000 o más, déjalo en $19.890.</p></div>
</section>

<section>
  <h2>Qué evitar</h2>
  <p class="sub">Nichos que se ven bien en demanda y no sobreviven la economía unitaria.</p>
  <div class="scroll"><table>
    <thead><tr><th class="l">Nicho</th><th>Kg</th><th>Precio med.</th><th>Compet.</th><th>Disponible</th><th class="l">Por qué</th></tr></thead>
    <tbody>{evitar}</tbody>
  </table></div>
</section>

<section>
  <h2>Antes de comprar inventario</h2>
  <p class="sub">Los números de arriba sirven para elegir entre nichos. No sirven para comprometer plata sin verificar.</p>
  <ol class="steps">
    <li><strong>Confirma la comisión real de tu subcategoría</strong> en el simulador de costos de MercadoLibre. El 17% que usé es el techo referencial de Hogar y Muebles; tu categoría puede estar en 14%.</li>
    <li><strong>Mide el peso volumétrico</strong>, no solo el peso real. Un cesto de ropa plegable pesa 1,2 kg pero ocupa como 4 — y MercadoLibre cobra por el que salga más caro.</li>
    <li><strong>Verifica la demanda en el buscador</strong>, no solo en ofertas. Esta muestra solo ve productos con descuento activo; busca el término y mira cuántas publicaciones reales hay.</li>
    <li><strong>Pide muestra física</strong> antes de comprar volumen, sobre todo en bidet, barras de seguridad y balanzas — los tres tienen modos de falla que generan reclamo.</li>
    <li><strong>Arranca con 30 a 50 unidades</strong> de dos o tres productos, no con uno solo a fondo. El objetivo de la primera compra es medir conversión real, no ganar plata.</li>
  </ol>
</section>

<section>
  <h2>Cómo se obtuvieron estos datos</h2>
  <p class="sub">Y, más importante, qué no cubren.</p>
  <div class="notes"><ul>
    <li><strong>La fuente es la superficie de ofertas por categoría</strong> de mercadolibre.cl, 35 páginas de 17 categorías hoja. Muestra productos con oferta o descuento activo — no el catálogo completo. Subestima la oferta total de cada nicho.</li>
    <li><strong>"Vendidos" es acumulado histórico en cubos</strong> (+100, +1.000, +5.000, +10.000), no venta mensual. Sirve para comparar nichos entre sí y ordenar por popularidad; no para proyectar facturación.</li>
    <li><strong>El conteo de competidores es una cota superior.</strong> Solo el 48% de las tarjetas muestra vendedor; cada publicación sin vendedor visible se contó como un competidor propio.</li>
    <li><strong>El 97% de la muestra vive en fichas de catálogo compartidas</strong> (<code>/p/MLC…</code>). Eso es un sesgo de esta superficie —las ofertas se enganchan al catálogo—, no una medición del porcentaje real de cada nicho. Por eso ese factor casi no diferencia entre nichos en el score.</li>
    <li><strong>Los costos de envío son estimaciones</strong> interpoladas de ejemplos públicos, con 55% de descuento por reputación verde. Ninguna fuente publica la tabla oficial completa por peso. Confírmalos en el simulador antes de fijar precios.</li>
    <li><strong>Los pesos son estimaciones por criterio</strong> sobre el tipo de objeto, no medidas reales del producto que vayas a comprar.</li>
    <li><strong>El score</strong> combina log₁₀(uds/publicación) × 1/√competidores × (1 − 0,35 × %catálogo) × %disponible. Rankea, no predice: un score alto con 4 publicaciones de muestra es una pista, no una certeza.</li>
  </ul></div>
</section>

<section>
  <h2>Mapa de las categorías</h2>
  <p class="sub">Ofertas activas por subcategoría al momento de la descarga. Define de dónde salió la muestra.</p>
  <div class="two">
    <div class="scroll"><table>
      <thead><tr><th class="l">Hogar, Muebles y Jardín</th><th>ID</th><th>Ofertas</th></tr></thead>
      <tbody>{catrows(CATS)}</tbody></table></div>
    <div class="scroll"><table>
      <thead><tr><th class="l">Deportes y Fitness</th><th>ID</th><th>Ofertas</th></tr></thead>
      <tbody>{catrows(FIT)}</tbody></table></div>
  </div>
</section>

<section>
  <h2>Ranking completo de nichos</h2>
  <p class="sub">Los 60 nichos con al menos 3 publicaciones en la muestra, incluidos los pesados y los saturados.</p>
  <div class="scroll"><table>
    <thead><tr><th></th><th class="l">Nicho</th><th>Ofertas</th><th>Compet.</th><th>Uds/pub.</th>
    <th>% Full</th><th>Dto. med.</th><th>Precio med.</th><th>Kg</th><th>Disp.</th><th>Score</th></tr></thead>
    <tbody>{full_rows}</tbody>
  </table></div>
</section>

<section>
  <h2>Los 15 más vendidos de toda la muestra</h2>
  <p class="sub">Sin filtrar por peso ni por nicho — para dimensionar qué mueve realmente la categoría.</p>
  <div class="scroll"><table>
    <thead><tr><th class="l">Producto</th><th>Precio</th><th>Vendidos</th><th>Calif.</th><th>Vendedor</th><th>Dto.</th></tr></thead>
    <tbody>{anexo_rows}</tbody>
  </table></div>
</section>

<footer>
  <p>Datos descargados de la superficie pública de ofertas de mercadolibre.cl el 19 de agosto de 2026. Modelo de costos: comisión 17%, cargo fijo $600 bajo $19.990, descuento de envío 55% por reputación verde. Todas las cifras en pesos chilenos.</p>
</footer>
</div>
'''
open("/home/user/Prueba/informe/informe.html","w").write(HTML)
print("escrito:", len(HTML), "bytes")
