"""Command line interface.

    python -m productscout scan --keyword "cable organizer" --small-only
    python -m productscout list --verdict perseguir
    python -m productscout show B0CQ7XK4M2
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

    scan = sub.add_parser("scan", help="ejecuta un análisis completo")
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
