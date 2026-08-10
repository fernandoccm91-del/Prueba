"""Paquetes de palabras clave por nicho (`data/nichos.json`).

Un nicho es simplemente una lista de búsquedas que se le hacen a Mercado Libre.
Puedes editar el archivo y agregar tus propios términos sin tocar código.
"""

from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass

from .config import DATA_DIR

NICHES_FILE = DATA_DIR / "nichos.json"


@dataclass
class Niche:
    slug: str
    nombre: str
    descripcion: str
    terminos: list[str]


def _slug(text: str) -> str:
    normalised = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in normalised if not unicodedata.combining(c)).strip()


def load_niches() -> dict[str, Niche]:
    if not NICHES_FILE.exists():
        return {}
    raw = json.loads(NICHES_FILE.read_text(encoding="utf-8"))
    return {
        slug: Niche(
            slug=slug,
            nombre=data.get("nombre", slug),
            descripcion=data.get("descripcion", ""),
            terminos=list(data.get("terminos", [])),
        )
        for slug, data in raw.items()
    }


def get_niche(name: str) -> Niche | None:
    """Busca un nicho por slug o por nombre, ignorando tildes y mayúsculas."""
    niches = load_niches()
    wanted = _slug(name)
    if wanted in niches:
        return niches[wanted]
    for niche in niches.values():
        if _slug(niche.nombre) == wanted:
            return niche
    return None


def niche_names() -> list[str]:
    return sorted(load_niches().keys())
