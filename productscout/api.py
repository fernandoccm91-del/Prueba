"""HTTP API + dashboard (FastAPI). Optional: `pip install -e '.[web]'`."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .config import Settings
from .db import (
    connect,
    get_opportunity,
    latest_run_id,
    list_ideas,
    list_opportunities,
    list_runs,
    save_niche_run,
    save_run,
)
from .ideas import NicheScanner, NicheScanRequest
from .niches import load_niches
from .keywords import alibaba_query
from .models import to_dict
from .pipeline import Pipeline, ScanRequest

WEB_DIR = Path(__file__).parent / "web"


class BuscarBody(BaseModel):
    niche: str = "bano"
    terms: list[str] = []
    max_terms: int | None = None
    min_score: float = 0.0
    top: int = 20


class ScanBody(BaseModel):
    keywords: list[str] = []
    category: str | None = None
    limit_per_keyword: int = 25
    min_score: float = 0.0
    check_mercadolibre: bool = True
    check_suppliers: bool = True
    small_only: bool = False
    max_results: int = 50


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(title="ProductScout", version="0.1.0")

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        return (WEB_DIR / "index.html").read_text(encoding="utf-8")

    @app.get("/api/config")
    def config() -> dict:
        return {
            "sources": {
                "amazon": settings.amazon_source,
                "mercadolibre": settings.ml_source,
                "suppliers": settings.supplier_source,
            },
            "ml_site": settings.ml_site,
            "filters": {
                "max_weight_g": settings.max_weight_g,
                "min_price_usd": settings.min_price_usd,
                "max_price_usd": settings.max_price_usd,
            },
            "costs": to_dict(settings.costs),
        }

    # --- flujo principal: nichos en Mercado Libre -------------------------
    @app.get("/api/nichos")
    def nichos() -> dict:
        return {
            "default": settings.default_niche,
            "site": settings.ml_site,
            "items": [to_dict(niche) for niche in load_niches().values()],
        }

    @app.post("/api/buscar")
    def buscar(body: BuscarBody) -> dict:
        scanner = NicheScanner(settings)
        try:
            result = scanner.scan(NicheScanRequest(**body.model_dump()))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        conn = connect(settings.db_path)
        run_id = save_niche_run(conn, result)
        conn.close()
        return {
            "run_id": run_id,
            "nicho": result.niche_name,
            "site": result.site,
            "sources": result.sources,
            "errors": result.errors,
            "terms_scanned": result.terms_scanned,
            "count": len(result.ideas),
            "ideas": [to_dict(idea) for idea in result.ideas],
        }

    @app.get("/api/ideas")
    def ideas(
        limit: int = Query(50, ge=1, le=500),
        min_score: float = 0.0,
        run: int | None = None,
        last: bool = True,
    ) -> dict:
        conn = connect(settings.db_path)
        run_id = run or (latest_run_id(conn) if last else None)
        rows = list_ideas(conn, run_id=run_id, limit=limit, min_score=min_score)
        conn.close()
        return {
            "count": len(rows),
            "items": [{**row, "payload": json.loads(row["payload"])} for row in rows],
        }

    # --- flujo avanzado: Amazon FBA ---------------------------------------
    @app.post("/api/scan")
    def scan(body: ScanBody) -> dict:
        result = Pipeline(settings).scan(ScanRequest(**body.model_dump()))
        conn = connect(settings.db_path)
        run_id = save_run(conn, result)
        conn.close()
        return {
            "run_id": run_id,
            "sources": result.sources,
            "errors": result.errors,
            "count": len(result.opportunities),
            "opportunities": [to_dict(o) for o in result.opportunities],
        }

    @app.get("/api/opportunities")
    def opportunities(
        limit: int = Query(50, ge=1, le=500),
        min_score: float = 0.0,
        verdict: str | None = None,
        run: int | None = None,
        last: bool = False,
    ) -> dict:
        conn = connect(settings.db_path)
        run_id = run or (latest_run_id(conn) if last else None)
        rows = list_opportunities(conn, run_id=run_id, limit=limit,
                                  min_score=min_score, verdict=verdict)
        conn.close()
        return {
            "count": len(rows),
            "items": [{**row, "payload": json.loads(row["payload"])} for row in rows],
        }

    @app.get("/api/opportunities/{asin}")
    def opportunity(asin: str) -> dict:
        conn = connect(settings.db_path)
        row = get_opportunity(conn, asin)
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail=f"{asin} no encontrado")
        payload = json.loads(row["payload"])
        product = payload["product"]
        payload["alibaba_search_url"] = (
            "https://www.alibaba.com/trade/search?SearchText="
            + alibaba_query(product["title"], product.get("brand")).replace(" ", "+")
        )
        return payload

    @app.get("/api/runs")
    def runs(limit: int = 20) -> dict:
        conn = connect(settings.db_path)
        rows = list_runs(conn, limit=limit)
        conn.close()
        return {"items": rows}

    return app


app = create_app()
