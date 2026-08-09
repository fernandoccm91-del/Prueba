"""Interfaz de línea de comandos.

El comando principal es `buscar`:

    python -m productscout buscar                 # nicho por defecto (baño)
    python -m productscout buscar cocina
    python -m productscout buscar -t "organizador de ducha"
    python -m productscout nichos

Comandos avanzados (flujo Amazon FBA):

    python -m productscout scan --keyword "shower caddy" --small-only
    python -m productscout show B0DN4X8QW2
    python -m productscout export --format csv --out oportunidades.csv
    python -m productscout serve
"""

from __future__ import annotations

import argparse
import csv
import json
import sys

from .config import Settings
from .db import connect, get_opportunity, latest_run_id, list_opportunities, list_runs, save_run
from .keywords import alibaba_query
from .models import to_dict
from .niches import load_niches, niche_names
from .pipeline import Pipeline, ScanRequest

VERDICT_ICON = {"perseguir": "★", "investigar": "•", "dudoso": "·", "descartar": " "}


def _fmt_money(value: float | None) -> str:
    return f"${value:,.2f}" if value is not None else "-"


def _truncate(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"


def print_table(rows: list[dict]) -> None:
    if not rows:
        print("Sin resultados.")
        return
    header = f"{'':2}{'SCORE':>6}  {'ASIN':<12} {'PRODUCTO':<44} {'U/DÍA':>7} {'U/MES':>8} {'$/MES':>11} {'UTIL/U':>8} {'ROI':>7}  ML"
    print(header)
    print("-" * len(header))
    for row in rows:
        icon = VERDICT_ICON.get(row.get("verdict", ""), " ")
        ml = f"{row['ml_listings'] or 0} pub / {row['ml_monthly_units'] or 0:.0f} u-mes" if row.get("ml_listings") is not None else "-"
        print(
            f"{icon:2}{row['total_score']:>6.1f}  {row['asin']:<12} "
            f"{_truncate(row['title'], 44):<44} "
            f"{(row['daily_units'] or 0):>7.1f} {(row['monthly_units'] or 0):>8.0f} "
            f"{_fmt_money(row['monthly_revenue']):>11} "
            f"{_fmt_money(row['profit_per_unit']):>8} "
            f"{(row['roi'] or 0) * 100:>6.0f}%  {ml}"
        )
    print("\n★ perseguir   • investigar   · dudoso")


def print_detail(payload: dict) -> None:
    product = payload["product"]
    econ = payload.get("economics")
    market = payload.get("ml_market")

    print(f"\n{product['title']}")
    print(f"{'=' * min(len(product['title']), 78)}")
    print(f"ASIN         {product['asin']}   marca: {product.get('brand') or '-'}")
    print(f"Categoría    {product['category']}")
    print(f"Precio       {_fmt_money(product['price'])}   BSR: {product.get('bsr') or '-'}   "
          f"reseñas: {product.get('reviews_count') or 0}   rating: {product.get('rating') or '-'}")
    print(f"Tamaño       {product.get('weight_g') or '?'} g  "
          f"{product.get('length_mm') or '?'}x{product.get('width_mm') or '?'}x{product.get('height_mm') or '?'} mm")
    print(f"Publicado    {product.get('first_available') or 'desconocido'}")
    print(f"URL          {product.get('url') or '-'}")

    print(f"\nSCORE {payload['total_score']} → {payload['verdict'].upper()}")
    for name, value in payload["scores"].items():
        bar = "█" * int(value / 5)
        print(f"  {name:<14} {value:>5.1f}  {bar}")

    print(f"\nDEMANDA AMAZON")
    print(f"  {payload['amazon_daily_units']} u/día · {payload['amazon_monthly_units']:.0f} u/mes · "
          f"{_fmt_money(payload['amazon_monthly_revenue_usd'])}/mes")

    if market:
        print(f"\nMERCADO LIBRE ({market['site']}) — consulta: \"{market['query']}\"")
        print(f"  {market['total_listings']} publicaciones · "
              f"~{market['monthly_units_est']:.0f} u/mes estimadas · "
              f"precio mediano {market['median_price']} {market['currency']} · "
              f"tiendas oficiales {market['official_store_share']:.0%}")

    quotes = payload.get("quotes") or []
    if quotes:
        print("\nPROVEEDORES (Alibaba)")
        for quote in quotes[:5]:
            flags = []
            if quote.get("trade_assurance"):
                flags.append("Trade Assurance")
            if quote.get("verified_supplier"):
                flags.append("Verified")
            print(f"  {_fmt_money(quote['unit_price_usd'])}/u · MOQ {quote['moq']} · "
                  f"{quote['supplier_name']} ({quote.get('years_active') or '?'} años, "
                  f"rating {quote.get('rating') or '?'}) {' '.join(flags)}")
            if quote.get("url"):
                print(f"      {quote['url']}")

    if econ:
        print("\nECONOMÍA UNITARIA")
        print(f"  costo unitario   {_fmt_money(econ['unit_cost_usd'])} (pedido de {econ['order_qty']} u)")
        print(f"  flete            {_fmt_money(econ['freight_usd'])}")
        print(f"  arancel          {_fmt_money(econ['duty_usd'])}")
        print(f"  prep             {_fmt_money(econ['prep_usd'])}")
        print(f"  = landed cost    {_fmt_money(econ['landed_cost_usd'])}")
        print(f"  comisión Amazon  {_fmt_money(econ['platform_fee_usd'])}")
        print(f"  {'FBA (' + econ['size_tier'] + ')':<16} {_fmt_money(econ['fulfilment_fee_usd'])}")
        print(f"  → utilidad/u     {_fmt_money(econ['profit_per_unit_usd'])}  "
              f"margen {econ['margin']:.0%}  ROI {econ['roi']:.0%}")
        print(f"  inversión inicial {_fmt_money(econ['upfront_investment_usd'])}")

    if payload.get("reasons"):
        print("\nA FAVOR")
        for reason in payload["reasons"]:
            print(f"  + {reason}")
    if payload.get("warnings"):
        print("\nOJO")
        for warning in payload["warnings"]:
            print(f"  ! {warning}")
    print()


SITE_NAMES = {
    "MLC": "Chile", "MLM": "México", "MLA": "Argentina",
    "MCO": "Colombia", "MLB": "Brasil", "MPE": "Perú", "MLU": "Uruguay",
}


def money_local(value: float | None, currency: str) -> str:
    if value is None:
        return "–"
    sign = "-" if value < 0 else ""
    amount = abs(value)
    if currency in ("CLP", "COP", "ARS"):
        return sign + "$" + f"{amount:,.0f}".replace(",", ".")
    return f"{sign}${amount:,.2f}"


def print_ideas_table(ideas: list, currency: str) -> None:
    header = (f"  {'#':>2} {'PUNTAJE':>8}  {'PRODUCTO':<38} {'PUBS':>6} {'U/MES':>7} "
              f"{'PRECIO ML':>11} {'ALIBABA':>9} {'GANANCIA/U':>12} {'MARGEN':>7}")
    print(header)
    print("  " + "-" * (len(header) - 2))
    for position, idea in enumerate(ideas, start=1):
        market = idea.ml_market
        econ = idea.economics
        quote = idea.quotes[0] if idea.quotes else None
        icon = VERDICT_ICON.get(idea.verdict, " ")
        print(
            f"  {position:>2} {icon} {idea.total_score:>6.1f}  {_truncate(idea.term, 38):<38} "
            f"{market.total_listings:>6} {market.monthly_units_est:>7.0f} "
            f"{money_local(market.median_price, currency):>11} "
            f"{('US$' + format(quote.unit_price_usd, '.2f')) if quote else '–':>9} "
            f"{money_local(econ.profit_local, currency) if econ else '–':>12} "
            f"{(format(econ.margin, '.0%') if econ else '–'):>7}"
        )


def print_idea_card(position: int, idea) -> None:
    market = idea.ml_market
    econ = idea.economics
    quote = idea.quotes[0] if idea.quotes else None
    currency = market.currency

    print(f"\n{position}. {VERDICT_ICON.get(idea.verdict, ' ')} {idea.total_score} — {idea.term.upper()}")
    print(f"   {'Mercado Libre':<15} {market.total_listings} publicaciones · "
          f"~{market.monthly_units_est:.0f} unidades/mes · "
          f"precio típico {money_local(market.median_price, currency)}")
    if idea.amazon_products:
        best = idea.amazon_products[0]
        print(f"   {'Amazon (EE.UU.)':<15} ~{idea.amazon_monthly_units:.0f} unidades/mes · "
              f"«{_truncate(best.title, 46)}» · {best.reviews_count or 0} reseñas")
    else:
        print(f"   {'Amazon (EE.UU.)':<15} sin coincidencias")
    if quote:
        print(f"   {'Alibaba':<15} US${quote.unit_price_usd:.2f}/unidad · pedido mínimo {quote.moq} · "
              f"{_truncate(quote.supplier_name, 40)}")
    if econ:
        print(f"   {'Cuentas':<15} cuesta {money_local(econ.landed_cost_local, currency)} puesto en el país · "
              f"comisión+envío {money_local(econ.commission_local + econ.fixed_fee_local + econ.shipping_local, currency)} · "
              f"ganas {money_local(econ.profit_local, currency)}/unidad ({econ.margin:.0%})")
        print(f"   {'Inversión':<15} {money_local(econ.upfront_investment_local, currency)} "
              f"para traer {econ.order_qty} unidades")
    if idea.alibaba_url:
        print(f"   {'Proveedores':<15} {idea.alibaba_url}")
    for reason in idea.reasons[:3]:
        print(f"     + {reason}")
    for warning in idea.warnings[:3]:
        print(f"     ! {warning}")


def cmd_buscar(args: argparse.Namespace, settings: Settings) -> int:
    from .db import save_niche_run
    from .ideas import NicheScanner, NicheScanRequest

    request = NicheScanRequest(
        niche=args.nicho or settings.default_niche,
        terms=args.termino or [],
        max_terms=args.max_terminos,
        min_score=args.min_score,
        top=args.top,
    )
    scanner = NicheScanner(settings)
    try:
        terms, niche_name = scanner.resolve_terms(request)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        print(f"Nichos disponibles: {', '.join(niche_names())}", file=sys.stderr)
        return 1

    site_name = SITE_NAMES.get(settings.ml_site, settings.ml_site)
    print(f"\nBuscando productos de {niche_name} en Mercado Libre {site_name} ({settings.ml_site})")
    print(f"Fuentes: Mercado Libre = {scanner.ml.name} · Amazon = {scanner.amazon.name} · "
          f"Proveedores = {scanner.suppliers.name}")
    print(f"Revisando {len(terms)} búsquedas...\n")

    result = scanner.scan(request)
    for error in result.errors:
        print(f"  ! {error}", file=sys.stderr)

    if not result.ideas:
        print("No encontré nada con esos filtros. Prueba bajando --min-score.")
        return 0

    conn = connect(settings.db_path)
    run_id = save_niche_run(conn, result)
    conn.close()

    currency = result.ideas[0].ml_market.currency
    print(f"Revisé {result.terms_scanned} búsquedas. Estas son las mejores {len(result.ideas)} "
          f"(corrida #{run_id}):\n")
    print_ideas_table(result.ideas, currency)
    print("\n  ★ vale la pena    • para investigar    · dudoso")

    detail_count = len(result.ideas) if args.detalle else min(5, len(result.ideas))
    if detail_count:
        print(f"\n{'=' * 78}\nDETALLE DE LAS {detail_count} MEJORES\n{'=' * 78}")
        for position, idea in enumerate(result.ideas[:detail_count], start=1):
            print_idea_card(position, idea)

    print(f"\n{'=' * 78}\nQUÉ HACER AHORA\n{'=' * 78}")
    print("  1. Abre el link de Alibaba de los 2-3 primeros y pide cotización a 3 proveedores.")
    print("     Pregunta: precio por unidad, pedido mínimo, peso por unidad y costo de envío a Chile.")
    print("  2. Anota esas respuestas en data/supplier_quotes.json y vuelve a correr el comando")
    print("     con SUPPLIER_SOURCE=manual: ahí la ganancia deja de ser estimada y es real.")
    print("  3. Antes de comprar, revisa en Mercado Libre las publicaciones que ya venden ese")
    print("     producto: mira sus fotos, su precio y sus preguntas para ver qué puedes hacer mejor.")

    if scanner.ml.name == "mock":
        print("\n  NOTA: estás usando datos de EJEMPLO, no datos reales de Mercado Libre.")
        print("  Para conectar los datos de verdad, mira la sección «Conectar datos reales» del README.")
    print()
    return 0


def cmd_scan(args: argparse.Namespace, settings: Settings) -> int:
    request = ScanRequest(
        keywords=args.keyword or [],
        category=args.category,
        limit_per_keyword=args.limit,
        min_score=args.min_score,
        check_mercadolibre=not args.no_ml,
        check_suppliers=not args.no_suppliers,
        small_only=args.small_only,
        max_results=args.top,
    )
    pipeline = Pipeline(settings)
    result = pipeline.scan(request)

    print(f"Fuentes: amazon={result.sources['amazon']} "
          f"mercadolibre={result.sources['mercadolibre']} "
          f"proveedores={result.sources['suppliers']}")
    for error in result.errors:
        print(f"  ! {error}", file=sys.stderr)

    conn = connect(settings.db_path)
    run_id = save_run(conn, result)
    rows = list_opportunities(conn, run_id=run_id, limit=args.top)
    conn.close()

    if args.json:
        print(json.dumps([to_dict(o) for o in result.opportunities], ensure_ascii=False, indent=2))
    else:
        print(f"\n{len(result.opportunities)} oportunidades (run #{run_id})\n")
        print_table(rows)
    return 0


def cmd_list(args: argparse.Namespace, settings: Settings) -> int:
    conn = connect(settings.db_path)
    run_id = args.run or (latest_run_id(conn) if args.last else None)
    rows = list_opportunities(conn, run_id=run_id, limit=args.limit,
                              min_score=args.min_score, verdict=args.verdict)
    conn.close()
    print_table(rows)
    return 0


def cmd_show(args: argparse.Namespace, settings: Settings) -> int:
    conn = connect(settings.db_path)
    row = get_opportunity(conn, args.asin)
    conn.close()
    if not row:
        print(f"No encontré {args.asin}. Corre un scan primero.", file=sys.stderr)
        return 1
    print_detail(json.loads(row["payload"]))
    return 0


def cmd_nichos(args: argparse.Namespace, settings: Settings) -> int:
    niches = load_niches()
    if not niches:
        print("No hay nichos definidos. Crea data/nichos.json.")
        return 0
    print("\nNichos disponibles (edita data/nichos.json para agregar los tuyos):\n")
    for niche in niches.values():
        marker = " (por defecto)" if niche.slug == settings.default_niche else ""
        print(f"  {niche.slug}{marker}")
        print(f"    {niche.descripcion}")
        print(f"    {len(niche.terminos)} búsquedas, por ejemplo: "
              f"{', '.join(niche.terminos[:3])}...\n")
    print("Uso:  python -m productscout buscar <nicho>\n")
    return 0


def cmd_runs(args: argparse.Namespace, settings: Settings) -> int:
    conn = connect(settings.db_path)
    rows = list_runs(conn, limit=args.limit)
    conn.close()
    for row in rows:
        print(f"#{row['id']:<4} {row['started_at'][:19]}  {row['found']:>3} resultados  "
              f"[{row['keywords'] or 'sin keywords'}]  {row['sources']}")
    return 0


def cmd_export(args: argparse.Namespace, settings: Settings) -> int:
    conn = connect(settings.db_path)
    run_id = args.run or latest_run_id(conn)
    rows = list_opportunities(conn, run_id=run_id, limit=args.limit, min_score=args.min_score)
    conn.close()

    if args.format == "json":
        payload = [json.loads(row["payload"]) for row in rows]
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        _write(args.out, text)
        return 0

    fields = ["asin", "title", "category", "price", "total_score", "verdict", "daily_units",
              "monthly_units", "monthly_revenue", "profit_per_unit", "roi",
              "ml_listings", "ml_monthly_units"]
    handle = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
    writer = csv.DictWriter(handle, fieldnames=fields + ["alibaba_url"], extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        payload = json.loads(row["payload"])
        product = payload["product"]
        row["alibaba_url"] = (
            "https://www.alibaba.com/trade/search?SearchText="
            + alibaba_query(product["title"], product.get("brand")).replace(" ", "+")
        )
        writer.writerow(row)
    if args.out:
        handle.close()
        print(f"Escrito {args.out}")
    return 0


def _write(path: str | None, text: str) -> None:
    if path:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        print(f"Escrito {path}")
    else:
        print(text)


def cmd_serve(args: argparse.Namespace, settings: Settings) -> int:
    try:
        import uvicorn
    except ImportError:
        print("Falta uvicorn. Instala con: pip install -e '.[web]'", file=sys.stderr)
        return 1
    from .api import create_app

    uvicorn.run(create_app(settings), host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="productscout",
        description="Busca productos con demanda y poca competencia en Amazon, "
                    "cruza con Mercado Libre y cotiza proveedores en Alibaba.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    buscar = sub.add_parser(
        "buscar",
        help="busca productos de un nicho (el comando principal)",
        description="Busca productos con demanda y poca competencia en Mercado Libre, "
                    "los valida en Amazon y los cotiza en Alibaba.",
    )
    buscar.add_argument("nicho", nargs="?", help=f"nicho a revisar ({', '.join(niche_names())})")
    buscar.add_argument("--termino", "-t", action="append",
                        help="buscar un producto puntual en vez de un nicho completo (repetible)")
    buscar.add_argument("--top", type=int, default=15, help="cuántos resultados mostrar")
    buscar.add_argument("--min-score", type=float, default=0.0, help="puntaje mínimo")
    buscar.add_argument("--max-terminos", type=int, help="revisar solo los primeros N términos")
    buscar.add_argument("--detalle", action="store_true", help="ficha completa de todos, no solo del top 5")
    buscar.set_defaults(func=cmd_buscar)

    nichos = sub.add_parser("nichos", help="lista los nichos disponibles")
    nichos.set_defaults(func=cmd_nichos)

    scan = sub.add_parser("scan", help="análisis centrado en Amazon FBA (flujo avanzado)")
    scan.add_argument("--keyword", "-k", action="append", help="palabra clave (repetible)")
    scan.add_argument("--category", "-c", help="categoría de Amazon")
    scan.add_argument("--limit", type=int, default=25, help="productos por keyword")
    scan.add_argument("--top", type=int, default=25, help="máximo de resultados a mostrar")
    scan.add_argument("--min-score", type=float, default=0.0)
    scan.add_argument("--small-only", action="store_true", help="solo productos pequeños/livianos")
    scan.add_argument("--no-ml", action="store_true", help="omite Mercado Libre")
    scan.add_argument("--no-suppliers", action="store_true", help="omite proveedores")
    scan.add_argument("--json", action="store_true", help="salida JSON completa")
    scan.set_defaults(func=cmd_scan)

    listing = sub.add_parser("list", help="lista oportunidades guardadas")
    listing.add_argument("--limit", type=int, default=25)
    listing.add_argument("--min-score", type=float, default=0.0)
    listing.add_argument("--verdict", choices=["perseguir", "investigar", "dudoso", "descartar"])
    listing.add_argument("--run", type=int, help="id de corrida")
    listing.add_argument("--last", action="store_true", help="solo la última corrida")
    listing.set_defaults(func=cmd_list)

    show = sub.add_parser("show", help="ficha completa de un ASIN")
    show.add_argument("asin")
    show.set_defaults(func=cmd_show)

    runs = sub.add_parser("runs", help="historial de corridas")
    runs.add_argument("--limit", type=int, default=20)
    runs.set_defaults(func=cmd_runs)

    export = sub.add_parser("export", help="exporta a CSV o JSON")
    export.add_argument("--format", choices=["csv", "json"], default="csv")
    export.add_argument("--out", help="archivo destino (por defecto stdout)")
    export.add_argument("--limit", type=int, default=200)
    export.add_argument("--min-score", type=float, default=0.0)
    export.add_argument("--run", type=int)
    export.set_defaults(func=cmd_export)

    serve = sub.add_parser("serve", help="levanta el dashboard web")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.set_defaults(func=cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.from_env()
    return args.func(args, settings)


if __name__ == "__main__":
    raise SystemExit(main())
