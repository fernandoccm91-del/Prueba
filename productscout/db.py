"""SQLite persistence so you can compare scans over time."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import Opportunity, to_dict

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    keywords TEXT,
    category TEXT,
    sources TEXT,
    errors TEXT,
    found INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    asin TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT,
    price REAL,
    total_score REAL NOT NULL,
    verdict TEXT,
    monthly_units REAL,
    daily_units REAL,
    monthly_revenue REAL,
    profit_per_unit REAL,
    roi REAL,
    ml_listings INTEGER,
    ml_monthly_units REAL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_opp_score ON opportunities(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_opp_asin ON opportunities(asin);

CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    term TEXT NOT NULL,
    site TEXT,
    total_score REAL NOT NULL,
    verdict TEXT,
    ml_listings INTEGER,
    ml_monthly_units REAL,
    ml_median_price REAL,
    currency TEXT,
    amazon_monthly_units REAL,
    supplier_price_usd REAL,
    moq INTEGER,
    profit_local REAL,
    margin REAL,
    roi REAL,
    alibaba_url TEXT,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ideas_score ON ideas(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_ideas_term ON ideas(term);
"""


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def save_run(conn: sqlite3.Connection, result) -> int:
    cur = conn.execute(
        "INSERT INTO runs (started_at, finished_at, keywords, category, sources, errors, found)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            result.started_at.isoformat(),
            result.finished_at.isoformat(),
            ", ".join(result.request.keywords),
            result.request.category or "",
            json.dumps(result.sources),
            json.dumps(result.errors),
            len(result.opportunities),
        ),
    )
    run_id = int(cur.lastrowid)
    for opp in result.opportunities:
        save_opportunity(conn, run_id, opp)
    conn.commit()
    return run_id


def save_opportunity(conn: sqlite3.Connection, run_id: int, opp: Opportunity) -> None:
    econ = opp.economics
    market = opp.ml_market
    conn.execute(
        "INSERT INTO opportunities (run_id, asin, title, category, price, total_score, verdict,"
        " monthly_units, daily_units, monthly_revenue, profit_per_unit, roi, ml_listings,"
        " ml_monthly_units, payload, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            run_id,
            opp.product.asin,
            opp.product.title,
            opp.product.category,
            opp.product.price,
            opp.total_score,
            opp.verdict,
            opp.amazon_monthly_units,
            opp.amazon_daily_units,
            opp.amazon_monthly_revenue_usd,
            econ.profit_per_unit_usd if econ else None,
            econ.roi if econ else None,
            market.total_listings if market else None,
            market.monthly_units_est if market else None,
            json.dumps(to_dict(opp), ensure_ascii=False),
            datetime.utcnow().isoformat(),
        ),
    )


def save_niche_run(conn: sqlite3.Connection, result) -> int:
    """Guarda una búsqueda por nicho (flujo Mercado Libre)."""
    cur = conn.execute(
        "INSERT INTO runs (started_at, finished_at, keywords, category, sources, errors, found)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            result.started_at.isoformat(),
            result.finished_at.isoformat(),
            f"nicho: {result.niche_name}",
            result.site,
            json.dumps(result.sources),
            json.dumps(result.errors),
            len(result.ideas),
        ),
    )
    run_id = int(cur.lastrowid)
    for idea in result.ideas:
        econ = idea.economics
        quote = idea.quotes[0] if idea.quotes else None
        conn.execute(
            "INSERT INTO ideas (run_id, term, site, total_score, verdict, ml_listings,"
            " ml_monthly_units, ml_median_price, currency, amazon_monthly_units,"
            " supplier_price_usd, moq, profit_local, margin, roi, alibaba_url, payload, created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                run_id,
                idea.term,
                result.site,
                idea.total_score,
                idea.verdict,
                idea.ml_market.total_listings,
                idea.ml_market.monthly_units_est,
                idea.ml_market.median_price,
                idea.ml_market.currency,
                idea.amazon_monthly_units,
                quote.unit_price_usd if quote else None,
                quote.moq if quote else None,
                econ.profit_local if econ else None,
                econ.margin if econ else None,
                econ.roi if econ else None,
                idea.alibaba_url,
                json.dumps(to_dict(idea), ensure_ascii=False),
                datetime.utcnow().isoformat(),
            ),
        )
    conn.commit()
    return run_id


def list_ideas(
    conn: sqlite3.Connection,
    run_id: int | None = None,
    limit: int = 50,
    min_score: float = 0.0,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM ideas WHERE total_score >= ?"
    params: list[Any] = [min_score]
    if run_id is not None:
        sql += " AND run_id = ?"
        params.append(run_id)
    sql += " ORDER BY total_score DESC LIMIT ?"
    params.append(limit)
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def get_idea(conn: sqlite3.Connection, term: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM ideas WHERE term = ? ORDER BY id DESC LIMIT 1", (term,)
    ).fetchone()
    return dict(row) if row else None


def latest_run_id(conn: sqlite3.Connection) -> int | None:
    row = conn.execute("SELECT id FROM runs ORDER BY id DESC LIMIT 1").fetchone()
    return int(row["id"]) if row else None


def list_opportunities(
    conn: sqlite3.Connection,
    run_id: int | None = None,
    limit: int = 50,
    min_score: float = 0.0,
    verdict: str | None = None,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM opportunities WHERE total_score >= ?"
    params: list[Any] = [min_score]
    if run_id is not None:
        sql += " AND run_id = ?"
        params.append(run_id)
    if verdict:
        sql += " AND verdict = ?"
        params.append(verdict)
    sql += " ORDER BY total_score DESC LIMIT ?"
    params.append(limit)
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def get_opportunity(conn: sqlite3.Connection, asin: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM opportunities WHERE asin = ? ORDER BY id DESC LIMIT 1", (asin,)
    ).fetchone()
    return dict(row) if row else None


def list_runs(conn: sqlite3.Connection, limit: int = 20) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    ]
