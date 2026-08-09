"""Turning an Amazon listing title into search terms for other marketplaces.

Amazon titles are keyword-stuffed English; Mercado Libre needs a short Spanish
phrase and Alibaba needs a generic product noun. Extend `ES_TERMS` (or
`data/ml_terms.json`) with the vocabulary of your niche.
"""

from __future__ import annotations

import json
import re

from .config import DATA_DIR

STOPWORDS = {
    "the", "and", "for", "with", "your", "our", "pack", "set", "pcs", "pieces", "piece",
    "premium", "professional", "quality", "new", "best", "great", "perfect", "ideal",
    "of", "in", "on", "to", "a", "an", "by", "up", "no", "non", "free", "inch", "inches",
    "oz", "lb", "ml", "cm", "mm", "size", "sizes", "assorted", "black", "white", "blue",
    "compatible", "adjustable", "portable", "reusable", "rechargeable", "usb",
}

ES_TERMS = {
    "cup": "vaso", "travel": "viaje", "collapsible": "plegable", "silicone": "silicona",
    "cable": "cable", "organizer": "organizador", "clips": "clips", "magnetic": "magnetico",
    "herb": "hierbas", "stripper": "deshojador", "stainless": "acero", "steel": "inoxidable",
    "phone": "celular", "stand": "soporte", "holder": "soporte", "desk": "escritorio",
    "pet": "mascota", "hair": "pelo", "remover": "removedor", "roller": "rodillo",
    "baby": "bebe", "feeding": "alimentacion", "spoon": "cuchara",
    "resistance": "resistencia", "bands": "bandas", "door": "puerta", "anchor": "anclaje",
    "food": "comida", "storage": "almacenamiento", "bags": "bolsas", "leakproof": "hermetico",
    "milk": "leche", "frother": "espumador", "electric": "electrico", "mini": "mini",
    "car": "auto", "vent": "rejilla", "mount": "soporte",
    "beard": "barba", "growth": "crecimiento", "kit": "kit", "case": "estuche",
    "tray": "bandeja", "management": "organizacion", "under": "bajo",
    "sleep": "dormir", "mask": "antifaz", "cooling": "frio", "gel": "gel", "eye": "ojos",
    "stretch": "elasticas", "lids": "tapas", "covers": "cubiertas",
    "espresso": "espresso", "tamper": "tamper", "mat": "tapete", "coffee": "cafe",
    "book": "libro", "light": "luz", "reading": "lectura", "lamp": "lampara", "neck": "cuello",
    "pill": "pastillero", "waterproof": "impermeable",
    "skillet": "sarten", "handle": "mango", "cover": "cubierta", "heat": "calor",
    "resistant": "resistente", "cast": "hierro", "iron": "fundido",
    "bottle": "botella", "brush": "cepillo", "tool": "herramienta", "toy": "juguete",
    "kitchen": "cocina", "gadget": "gadget", "cleaner": "limpiador", "dispenser": "dispensador",
    "charger": "cargador", "wireless": "inalambrico", "backpack": "mochila", "wallet": "cartera",
}

_TERMS_FILE = DATA_DIR / "ml_terms.json"
_TRANSLATIONS_FILE = DATA_DIR / "traducciones.json"
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9\-]+")
_WORD_ES = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ\-]*")

# Palabras que no aportan a una búsqueda en Amazon/Alibaba.
ES_STOPWORDS = {"de", "del", "la", "el", "los", "las", "para", "con", "sin", "y", "en", "por", "a", "un", "una"}


def _extra_terms() -> dict[str, str]:
    if not _TERMS_FILE.exists():
        return {}
    try:
        return {k.lower(): str(v) for k, v in json.loads(_TERMS_FILE.read_text(encoding="utf-8")).items()}
    except ValueError:
        return {}


def core_words(title: str, brand: str | None = None, max_words: int = 4) -> list[str]:
    """The meaningful nouns of a listing title, in order."""
    brand_words = {w.lower() for w in _WORD.findall(brand or "")}
    words: list[str] = []
    for raw in _WORD.findall(title):
        word = raw.lower()
        if word in STOPWORDS or word in brand_words or len(word) < 3:
            continue
        if word not in words:
            words.append(word)
        if len(words) >= max_words:
            break
    return words


def alibaba_query(title: str, brand: str | None = None) -> str:
    """A generic sourcing phrase — no brand, no marketing adjectives."""
    return " ".join(core_words(title, brand, max_words=4))


def ml_query(title: str, brand: str | None = None) -> str:
    """Short Spanish phrase for a Mercado Libre search."""
    table = {**ES_TERMS, **_extra_terms()}
    words = core_words(title, brand, max_words=3)
    return " ".join(table.get(word, word) for word in words)


# --- español -> inglés ----------------------------------------------------
def _translations() -> dict[str, str]:
    if not _TRANSLATIONS_FILE.exists():
        return {}
    try:
        raw = json.loads(_TRANSLATIONS_FILE.read_text(encoding="utf-8"))
    except ValueError:
        return {}
    return {k.lower(): str(v) for k, v in raw.items() if not k.startswith("_")}


def _reverse_es_terms() -> dict[str, str]:
    """ES_TERMS va de inglés a español; aquí lo damos vuelta."""
    reverse: dict[str, str] = {}
    for english, spanish in ES_TERMS.items():
        reverse.setdefault(spanish, english)
    return reverse


def to_english(term: str) -> str:
    """Traduce un término de búsqueda al inglés para consultar Amazon y Alibaba.

    Primero busca la frase completa en `data/traducciones.json`; si no está,
    traduce palabra por palabra y deja tal cual lo que no reconoce.
    """
    clean = term.strip().lower()
    phrases = _translations()
    if clean in phrases:
        return phrases[clean]

    word_table = _reverse_es_terms()
    words = [w for w in _WORD_ES.findall(clean) if w not in ES_STOPWORDS]
    return " ".join(word_table.get(word, word) for word in words)
