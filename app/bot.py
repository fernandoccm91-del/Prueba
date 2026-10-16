"""Lógica del bot: entiende la pregunta, busca papers y arma la respuesta."""

import json
import logging

from . import llm
from .search import Article, search_preprints, search_pubmed

log = logging.getLogger(__name__)

MAX_CHUNK = 1500  # Twilio corta los mensajes de WhatsApp en 1600 caracteres

GREETINGS = {"", "hola", "ayuda", "help", "menu", "menú", "inicio"}

HELP = (
    "👋 Soy tu buscador de *papers científicos*.\n\n"
    "Pregúntame en lenguaje normal, por ejemplo:\n"
    "• _Novedades del último mes en insuficiencia cardíaca_\n"
    "• _Ensayos clínicos recientes sobre semaglutida en obesidad_\n"
    "• _Soy pediatra, qué salió esta semana sobre bronquiolitis_\n\n"
    "Busco en PubMed y en preprints (medRxiv/bioRxiv) y te resumo lo más relevante."
)

QUERY_SYSTEM = """Eres un bibliotecario médico experto en PubMed.
Convierte la petición de un profesional de la salud en una búsqueda.
Responde SOLO un JSON con estas claves:
- "pubmed_query": búsqueda en inglés con sintaxis de PubMed (términos MeSH y [tiab], AND/OR).
  Si pide un tipo de estudio, agrégalo con [pt] (ej. randomized controlled trial[pt], meta-analysis[pt], guideline[pt]).
- "keywords": 2 a 5 palabras clave simples en inglés unidas por AND, para buscar preprints.
- "days": cuántos días hacia atrás buscar (entero). "esta semana"=7, "último mes" o sin indicación=30, "este año"=365.
- "topic_es": el tema en español, corto, para mostrarlo al usuario.
Si el mensaje no es una consulta médica o científica, usa "pubmed_query": "" ."""

SUMMARY_SYSTEM = """Eres un asistente que resume literatura científica para profesionales de la salud.
Reglas:
- Usa EXCLUSIVAMENTE los artículos que te entrego. Nunca inventes artículos, cifras ni links.
- Elige los 3 a 5 más relevantes para la pregunta; prioriza ensayos clínicos, metaanálisis y guías.
- Escribe en español, claro y técnico, con formato de WhatsApp (*negrita*, _cursiva_, sin markdown de títulos ni tablas).
- Para cada artículo: número y título traducido en *negrita*; revista y fecha; tipo de estudio;
  1 o 2 líneas con el hallazgo principal (incluye n y resultado clave si están en el abstract); el link tal cual.
- Si es preprint, márcalo con ⚠️ _Preprint, sin revisión por pares_.
- Si el abstract no tiene datos suficientes, dilo en vez de suponer.
- Máximo ~2500 caracteres en total. Sin introducción larga ni despedida."""

DISCLAIMER = "_Resumen automático de abstracts: revisa el artículo original antes de aplicarlo en la práctica clínica._"


def build_query(message: str) -> dict:
    try:
        q = llm.generate_json(QUERY_SYSTEM, message)
        q["days"] = max(1, min(int(q.get("days") or 30), 3650))
        return q
    except Exception:
        log.exception("No se pudo interpretar la consulta con Gemini; uso el texto tal cual")
        return {"pubmed_query": message, "keywords": message, "days": 30, "topic_es": message}


def find_articles(q: dict) -> tuple[list[Article], int]:
    days = q["days"]
    for attempt in range(2):
        articles: list[Article] = []
        try:
            articles += search_pubmed(q["pubmed_query"], days)
        except Exception:
            log.exception("Error buscando en PubMed")
        try:
            articles += search_preprints(q.get("keywords") or q["pubmed_query"], days)
        except Exception:
            log.exception("Error buscando preprints")
        if articles or attempt == 1:
            return articles, days
        days = min(days * 3, 3650)  # sin resultados: amplío la ventana una vez
    return [], days


def summarize(message: str, articles: list[Article]) -> str:
    payload = json.dumps([a.__dict__ for a in articles], ensure_ascii=False)
    try:
        return llm.generate(SUMMARY_SYSTEM, f"Pregunta: {message}\n\nArtículos:\n{payload}")
    except Exception:
        log.exception("No se pudo resumir con Gemini; envío lista simple")
        lines = []
        for i, a in enumerate(articles, 1):
            tag = " ⚠️ _Preprint_" if a.preprint else ""
            lines.append(f"*{i}. {a.title}*{tag}\n{a.journal} · {a.date}\n{a.url}")
        return "\n\n".join(lines)


def answer(message: str) -> str:
    text = message.strip()
    if text.lower() in GREETINGS:
        return HELP
    q = build_query(text)
    if not q.get("pubmed_query"):
        return HELP
    articles, days = find_articles(q)
    if not articles:
        return (f"No encontré artículos sobre _{q.get('topic_es', text)}_ en los últimos {days} días. "
                "Prueba con términos más generales o un período más largo.")
    header = f"📚 *{q.get('topic_es', text)}* · últimos {days} días\n\n"
    return f"{header}{summarize(text, articles)}\n\n{DISCLAIMER}"


def split_message(text: str, size: int = MAX_CHUNK) -> list[str]:
    chunks, current = [], ""
    for block in text.split("\n\n"):
        while len(block) > size:  # bloque más largo que el límite: lo corto a la fuerza
            if current:
                chunks.append(current)
                current = ""
            chunks.append(block[:size])
            block = block[size:]
        candidate = f"{current}\n\n{block}" if current else block
        if len(candidate) > size:
            chunks.append(current)
            current = block
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks
