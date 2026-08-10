"""Genera un informe HTML de una sola página con los productos encontrados.

Se usa desde `python -m productscout exportar --formato html`. El archivo que
produce es autocontenido: se abre haciendo doble clic, sin servidor ni internet.
"""

from __future__ import annotations

import html
from datetime import datetime
from typing import Any

VERDICT_LABEL = {
    "perseguir": "vale la pena",
    "investigar": "para investigar",
    "dudoso": "dudoso",
    "descartar": "descartar",
}

SCORE_LABEL = {
    "demanda": "se vende",
    "competencia": "poca competencia",
    "ganancia": "deja ganancia",
    "amazon": "confirmado en Amazon",
}

NO_DECIMALS = {"CLP", "COP", "ARS"}

CSS = """
:root {
  --ground:#f2f5f6; --surface:#ffffff; --sunken:#e8eef0;
  --ink:#111b1d; --ink-soft:#4a5c60; --ink-faint:#78898d;
  --line:#d8e2e4; --line-soft:#e7eef0;
  --accent:#0f6b6b; --accent-soft:#d3e6e4;
  --good:#1b6b45; --warn:#8a5a10; --bad:#9c3a2f;
  --good-bg:#dcefe4; --warn-bg:#f6ead2; --bad-bg:#f6dedb;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground:#0c1416; --surface:#131d20; --sunken:#0a1113;
    --ink:#e4edee; --ink-soft:#a3b4b7; --ink-faint:#77898d;
    --line:#223034; --line-soft:#1a2427;
    --accent:#4bb3ac; --accent-soft:#173634;
    --good:#5fc38c; --warn:#dda43f; --bad:#e18274;
    --good-bg:#12291f; --warn-bg:#2c2313; --bad-bg:#2e1a17;
  }
}
:root[data-theme="dark"] {
  --ground:#0c1416; --surface:#131d20; --sunken:#0a1113;
  --ink:#e4edee; --ink-soft:#a3b4b7; --ink-faint:#77898d;
  --line:#223034; --line-soft:#1a2427;
  --accent:#4bb3ac; --accent-soft:#173634;
  --good:#5fc38c; --warn:#dda43f; --bad:#e18274;
  --good-bg:#12291f; --warn-bg:#2c2313; --bad-bg:#2e1a17;
}

* { box-sizing:border-box; }
body {
  margin:0; background:var(--ground); color:var(--ink);
  font:16px/1.6 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing:antialiased;
}
.page { max-width:1080px; margin:0 auto; padding:40px 24px 80px; }
h1, h2, h3, .rank { font-family: ui-serif, Georgia, "Times New Roman", serif; font-weight:600; }
h1 { font-size:34px; line-height:1.2; margin:0 0 6px; letter-spacing:-0.015em; text-wrap:balance; }
.sub { color:var(--ink-soft); margin:0 0 28px; font-size:15px; }
h2 { font-size:13px; text-transform:uppercase; letter-spacing:.09em; color:var(--ink-faint);
     font-family: ui-sans-serif, system-ui, sans-serif; font-weight:700; margin:0 0 14px; }
.mono, .num { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
              font-variant-numeric: tabular-nums; }

.notice { border:1px solid var(--warn); background:var(--warn-bg); color:var(--warn);
          border-radius:4px; padding:14px 18px; margin:0 0 32px; font-size:14.5px; }
.notice strong { display:block; font-size:15.5px; margin-bottom:3px; color:var(--warn); }

.summary { display:flex; flex-wrap:wrap; gap:0; border-top:2px solid var(--ink);
           border-bottom:1px solid var(--line); margin-bottom:40px; }
.stat { flex:1 1 150px; padding:16px 20px 14px; border-right:1px solid var(--line-soft); }
.stat:last-child { border-right:none; }
.stat .k { display:block; font-size:12px; text-transform:uppercase; letter-spacing:.07em;
           color:var(--ink-faint); margin-bottom:4px; }
.stat .v { font-size:26px; font-family: ui-serif, Georgia, serif; }

.scan { overflow-x:auto; border:1px solid var(--line); border-radius:4px;
        background:var(--surface); margin-bottom:48px; }
table { border-collapse:collapse; width:100%; min-width:760px; font-size:14px; }
th, td { padding:9px 14px; text-align:left; border-bottom:1px solid var(--line-soft); white-space:nowrap; }
th { font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--ink-faint);
     background:var(--sunken); font-weight:700; }
tbody tr:last-child td { border-bottom:none; }
td.r, th.r { text-align:right; }
td.name { white-space:normal; min-width:210px; }
a { color:var(--accent); text-underline-offset:2px; }
a:focus-visible, .entry:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }

.pill { display:inline-block; padding:1px 9px; border-radius:99px; font-size:11.5px;
        font-weight:700; letter-spacing:.02em; white-space:nowrap; }
.p-perseguir { background:var(--good-bg); color:var(--good); }
.p-investigar { background:var(--accent-soft); color:var(--accent); }
.p-dudoso { background:var(--warn-bg); color:var(--warn); }
.p-descartar { background:var(--sunken); color:var(--ink-faint); }

.entry { border-top:1px solid var(--line); padding:28px 0 30px; display:grid;
         grid-template-columns:52px 1fr; gap:0 20px; }
.entry:first-of-type { border-top:2px solid var(--ink); }
.rank { font-size:30px; color:var(--ink-faint); line-height:1; padding-top:2px; }
.head { display:flex; flex-wrap:wrap; align-items:baseline; gap:10px; margin-bottom:4px; }
.head h3 { font-size:22px; margin:0; letter-spacing:-0.01em; }
.head .score { font-size:15px; color:var(--ink-soft); }

.meters { display:grid; grid-template-columns:repeat(auto-fit, minmax(170px, 1fr));
          gap:8px 22px; margin:16px 0 22px; }
.meter { font-size:12px; color:var(--ink-soft); }
.meter .track { height:5px; background:var(--sunken); border-radius:99px; margin-top:5px; overflow:hidden; }
.meter .fill { display:block; height:100%; background:var(--accent); border-radius:99px; }

.sources { display:grid; grid-template-columns:repeat(auto-fit, minmax(230px, 1fr)); gap:20px;
           margin-bottom:22px; }
.src { border-left:1px solid var(--line); padding-left:14px; }
.src .label { font-size:11px; text-transform:uppercase; letter-spacing:.07em;
              color:var(--ink-faint); font-weight:700; margin-bottom:6px; }
.src dl { display:grid; grid-template-columns:auto 1fr; gap:2px 12px; margin:0; font-size:14px; }
.src dt { color:var(--ink-soft); } .src dd { margin:0; }

.ledger { background:var(--surface); border:1px solid var(--line); border-radius:4px;
          padding:14px 18px; margin-bottom:20px; max-width:460px; }
.ledger .row { display:flex; justify-content:space-between; gap:16px; font-size:14px; padding:3px 0; }
.ledger .row.total { border-top:1px solid var(--line); margin-top:6px; padding-top:8px;
                     font-weight:700; font-size:15px; }
.ledger .row .lbl { color:var(--ink-soft); }
.ledger .neg { color:var(--bad); }
.ledger .pos { color:var(--good); }
.ledger .foot { font-size:12.5px; color:var(--ink-faint); margin-top:8px; }

.notes { display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:6px 24px;
         font-size:14px; margin-bottom:14px; }
.notes p { margin:0 0 4px; padding-left:16px; text-indent:-16px; }
.notes .pro::before { content:"+ "; color:var(--good); font-weight:700; }
.notes .con::before { content:"! "; color:var(--warn); font-weight:700; }

.next { border-top:2px solid var(--ink); margin-top:48px; padding-top:22px; }
.next ol { margin:0; padding-left:20px; font-size:15px; }
.next li { margin-bottom:8px; }
footer { margin-top:44px; padding-top:16px; border-top:1px solid var(--line);
         font-size:13px; color:var(--ink-faint); }
@media (max-width:640px) {
  .page { padding:28px 16px 56px; }
  .entry { grid-template-columns:1fr; gap:0; }
  .rank { font-size:20px; margin-bottom:2px; }
}
"""


def _money(value: Any, currency: str) -> str:
    if value is None:
        return "–"
    sign = "-" if value < 0 else ""
    amount = abs(float(value))
    if currency in NO_DECIMALS:
        return sign + "$" + f"{amount:,.0f}".replace(",", ".")
    return f"{sign}${amount:,.2f}"


def _usd(value: Any) -> str:
    return "–" if value is None else f"US${float(value):.2f}"


def _int(value: Any) -> str:
    return "–" if value is None else f"{round(float(value)):,}".replace(",", ".")


def _pct(value: Any) -> str:
    return "–" if value is None else f"{round(float(value) * 100)}%"


def _e(text: Any) -> str:
    return html.escape(str(text if text is not None else ""))


def _scan_table(ideas: list[dict]) -> str:
    rows = []
    for position, idea in enumerate(ideas, start=1):
        market = idea["ml_market"]
        econ = idea.get("economics")
        quote = (idea.get("quotes") or [None])[0]
        currency = market.get("currency") or ""
        rows.append(
            f'<tr><td class="num">{position}</td>'
            f'<td class="name">{_e(idea["term"])}</td>'
            f'<td><span class="pill p-{_e(idea["verdict"])}">'
            f'{_e(VERDICT_LABEL.get(idea["verdict"], idea["verdict"]))}</span></td>'
            f'<td class="r num">{idea["total_score"]:.0f}</td>'
            f'<td class="r num">{_int(market.get("total_listings"))}</td>'
            f'<td class="r num">{_int(market.get("monthly_units_est"))}</td>'
            f'<td class="r num">{_money(market.get("median_price"), currency)}</td>'
            f'<td class="r num">{_usd(quote["unit_price_usd"] if quote else None)}</td>'
            f'<td class="r num">{_money(econ["profit_local"] if econ else None, currency)}</td>'
            f'<td class="r num">{_pct(econ["margin"] if econ else None)}</td></tr>'
        )
    return (
        '<div class="scan"><table><thead><tr>'
        '<th class="r">#</th><th>Producto</th><th>Veredicto</th><th class="r">Puntaje</th>'
        '<th class="r">Publicaciones</th><th class="r">Ventas/mes</th><th class="r">Precio típico</th>'
        '<th class="r">Costo Alibaba</th><th class="r">Ganancia/u</th><th class="r">Margen</th>'
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def _ledger(econ: dict, currency: str) -> str:
    fees = econ["commission_local"] + econ["fixed_fee_local"]
    vat_line = econ["sale_price_local"] - econ["net_revenue_local"]
    rows = [
        ("Precio de venta en Mercado Libre", _money(econ["sale_price_local"], currency), ""),
    ]
    if vat_line > 0:
        rows.append(("IVA que declaras", "−" + _money(vat_line, currency), "neg"))
    rows.append(("Comisión de Mercado Libre", "−" + _money(fees, currency), "neg"))
    if econ["shipping_local"]:
        rows.append(("Envío que pagas tú", "−" + _money(econ["shipping_local"], currency), "neg"))
    rows.append(("Costo puesto en el país", "−" + _money(econ["landed_cost_local"], currency), "neg"))

    body = "".join(
        f'<div class="row"><span class="lbl">{_e(label)}</span>'
        f'<span class="num {cls}">{value}</span></div>'
        for label, value, cls in rows
    )
    profit_class = "pos" if econ["profit_local"] > 0 else "neg"
    body += (
        f'<div class="row total"><span>Te queda por unidad</span>'
        f'<span class="num {profit_class}">{_money(econ["profit_local"], currency)}</span></div>'
    )
    body += (
        f'<p class="foot">Margen {_pct(econ["margin"])} · '
        f'inversión inicial {_money(econ["upfront_investment_local"], currency)} '
        f'por {_int(econ["order_qty"])} unidades</p>'
    )
    return f'<div class="ledger">{body}</div>'


def _entry(position: int, idea: dict) -> str:
    market = idea["ml_market"]
    econ = idea.get("economics")
    quote = (idea.get("quotes") or [None])[0]
    amazon = (idea.get("amazon_products") or [None])[0]
    currency = market.get("currency") or ""

    meters = "".join(
        f'<div class="meter">{_e(SCORE_LABEL.get(key, key))} '
        f'<span class="num">{value:.0f}</span>'
        f'<span class="track"><i class="fill" style="width:{max(0, min(100, value)):.0f}%"></i></span></div>'
        for key, value in idea["scores"].items()
    )

    ml_block = (
        f'<div class="src"><div class="label">Mercado Libre</div><dl>'
        f'<dt>Compiten</dt><dd class="num">{_int(market.get("total_listings"))} publicaciones</dd>'
        f'<dt>Se vende</dt><dd class="num">~{_int(market.get("monthly_units_est"))} u/mes</dd>'
        f'<dt>Precio</dt><dd class="num">{_money(market.get("median_price"), currency)}</dd>'
        f'<dt>Oficiales</dt><dd class="num">{_pct(market.get("official_store_share"))}</dd>'
        f"</dl></div>"
    )

    if amazon:
        amazon_block = (
            f'<div class="src"><div class="label">Amazon EE.UU.</div><dl>'
            f'<dt>Se vende</dt><dd class="num">~{_int(idea.get("amazon_monthly_units"))} u/mes</dd>'
            f'<dt>Reseñas</dt><dd class="num">{_int(idea.get("amazon_reviews_median"))} (mediana)</dd>'
            f'<dt>Ejemplo</dt><dd>{_e(amazon["title"])}</dd>'
            f"</dl></div>"
        )
    else:
        amazon_block = (
            '<div class="src"><div class="label">Amazon EE.UU.</div>'
            "<p>Sin coincidencias: no se pudo confirmar la demanda.</p></div>"
        )

    if quote:
        supplier_block = (
            f'<div class="src"><div class="label">Alibaba</div><dl>'
            f'<dt>Costo</dt><dd class="num">{_usd(quote["unit_price_usd"])} por unidad</dd>'
            f'<dt>Mínimo</dt><dd class="num">{_int(quote["moq"])} unidades</dd>'
            f'<dt>Proveedor</dt><dd>{_e(quote["supplier_name"])}</dd>'
            f"</dl>"
            + (f'<p><a href="{_e(idea.get("alibaba_url"))}" target="_blank" rel="noopener">'
               f"Buscar proveedores →</a></p>" if idea.get("alibaba_url") else "")
            + "</div>"
        )
    else:
        supplier_block = '<div class="src"><div class="label">Alibaba</div><p>Sin cotizaciones.</p></div>'

    notes = "".join(f'<p class="pro">{_e(r)}</p>' for r in idea.get("reasons", [])[:5])
    notes += "".join(f'<p class="con">{_e(w)}</p>' for w in idea.get("warnings", [])[:4])

    return (
        f'<article class="entry"><div class="rank num">{position}</div><div>'
        f'<div class="head"><h3>{_e(idea["term"])}</h3>'
        f'<span class="pill p-{_e(idea["verdict"])}">'
        f'{_e(VERDICT_LABEL.get(idea["verdict"], idea["verdict"]))}</span>'
        f'<span class="score num">{idea["total_score"]:.0f}/100</span></div>'
        f'<div class="meters">{meters}</div>'
        f'<div class="sources">{ml_block}{amazon_block}{supplier_block}</div>'
        + (_ledger(econ, currency) if econ else "")
        + (f'<div class="notes">{notes}</div>' if notes else "")
        + "</div></article>"
    )


def render(
    ideas: list[dict],
    *,
    niche: str = "",
    site: str = "",
    site_name: str = "",
    sources: dict[str, str] | None = None,
    terms_scanned: int | None = None,
    standalone: bool = True,
) -> str:
    """Devuelve el informe en HTML. `standalone=False` omite doctype/head."""
    sources = sources or {}
    is_mock = sources.get("mercadolibre") == "mock"
    worth = sum(1 for i in ideas if i["verdict"] in ("perseguir", "investigar"))
    currency = (ideas[0]["ml_market"].get("currency") if ideas else "") or ""
    generated = datetime.now().strftime("%d-%m-%Y %H:%M")

    notice = ""
    if is_mock:
        notice = (
            '<div class="notice"><strong>Estos son datos de ejemplo, no productos reales.</strong>'
            "Sirven para mostrar cómo se ve el informe. Para que los números sean reales hay que "
            "conectar la API de Mercado Libre (gratis) — está explicado en el README, sección "
            "«Conectar Mercado Libre».</div>"
        )

    best_profit = max(
        (i["economics"]["profit_local"] for i in ideas if i.get("economics")), default=None
    )
    stats = (
        f'<div class="summary">'
        f'<div class="stat"><span class="k">Búsquedas revisadas</span>'
        f'<span class="v num">{terms_scanned if terms_scanned is not None else len(ideas)}</span></div>'
        f'<div class="stat"><span class="k">Productos en la lista</span>'
        f'<span class="v num">{len(ideas)}</span></div>'
        f'<div class="stat"><span class="k">Vale la pena mirar</span>'
        f'<span class="v num">{worth}</span></div>'
        f'<div class="stat"><span class="k">Mejor ganancia por unidad</span>'
        f'<span class="v num">{_money(best_profit, currency)}</span></div>'
        f"</div>"
    )

    where = f"Mercado Libre {site_name or site}".strip()
    body = (
        '<div class="page">'
        f"<h1>Productos de {_e(niche)} para vender en {_e(where)}</h1>"
        f'<p class="sub">Ordenados por oportunidad: cuánto se vende, cuánta competencia hay, '
        f"cuánto cuesta traerlo y cuánto queda. Generado el {generated}.</p>"
        f"{notice}{stats}"
        f'<h2>Comparación rápida</h2>{_scan_table(ideas)}'
        f"<h2>Ficha de cada producto</h2>"
        + "".join(_entry(position, idea) for position, idea in enumerate(ideas, start=1))
        + '<section class="next"><h2>Qué hacer ahora</h2><ol>'
        "<li>Abre el buscador de Alibaba de los dos o tres primeros y pídele cotización a tres "
        "proveedores: precio por unidad, pedido mínimo, peso y costo de envío.</li>"
        "<li>Anota esas respuestas en <code>data/supplier_quotes.json</code> y vuelve a buscar con "
        "<code>SUPPLIER_SOURCE=manual</code>: ahí la ganancia deja de ser una estimación.</li>"
        "<li>Mira en Mercado Libre las publicaciones que ya venden ese producto — fotos, precio y "
        "preguntas de los compradores — para ver qué puedes hacer mejor.</li>"
        "</ol></section>"
        f'<footer>Fuentes: Mercado Libre {_e(sources.get("mercadolibre", "?"))} · '
        f'Amazon {_e(sources.get("amazon", "?"))} · '
        f'proveedores {_e(sources.get("proveedores", "?"))}. '
        "Las comisiones, aranceles y costos de envío son aproximaciones configurables: "
        "verifícalas antes de comprar.</footer>"
        "</div>"
    )

    if not standalone:
        return f"<title>Productos de {_e(niche)}</title>\n<style>{CSS}</style>\n{body}"

    return (
        "<!doctype html>\n"
        '<html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>Productos de {_e(niche)} — ProductScout</title>"
        f"<style>{CSS}</style></head><body>{body}</body></html>"
    )
