"""Búsqueda de artículos en PubMed y de preprints (medRxiv/bioRxiv) vía Europe PMC."""

import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, timedelta

import httpx

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
TIMEOUT = 20
MAX_ABSTRACT = 1200


@dataclass
class Article:
    title: str
    journal: str
    date: str
    abstract: str
    url: str
    pub_types: list[str]
    preprint: bool = False


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", text).strip()


def _text(el) -> str:
    return _clean("".join(el.itertext())) if el is not None else ""


def search_pubmed(query: str, days: int, limit: int = 6) -> list[Article]:
    params = {"tool": "bot-papers-salud", "email": os.getenv("NCBI_EMAIL", "")}
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.get(f"{EUTILS}/esearch.fcgi", params={
            **params, "db": "pubmed", "term": query, "retmax": limit,
            "retmode": "json", "sort": "relevance",
            "datetype": "pdat", "reldate": days,
        })
        r.raise_for_status()
        ids = r.json()["esearchresult"]["idlist"]
        if not ids:
            return []
        r = client.get(f"{EUTILS}/efetch.fcgi", params={
            **params, "db": "pubmed", "id": ",".join(ids), "retmode": "xml",
        })
        r.raise_for_status()
    return parse_pubmed_xml(r.text)


def parse_pubmed_xml(xml: str) -> list[Article]:
    articles = []
    for node in ET.fromstring(xml).iter("PubmedArticle"):
        pmid = node.findtext("MedlineCitation/PMID", "")
        art = node.find("MedlineCitation/Article")
        if art is None:
            continue
        pub = art.find("Journal/JournalIssue/PubDate")
        pub_date = ""
        if pub is not None:
            pub_date = pub.findtext("MedlineDate") or " ".join(
                p for p in (pub.findtext("Year"), pub.findtext("Month")) if p)
        abstract = " ".join(_text(a) for a in art.findall("Abstract/AbstractText"))
        articles.append(Article(
            title=_text(art.find("ArticleTitle")),
            journal=art.findtext("Journal/Title", ""),
            date=pub_date,
            abstract=abstract[:MAX_ABSTRACT],
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            pub_types=[_text(p) for p in art.findall("PublicationTypeList/PublicationType")],
        ))
    return articles


def search_preprints(keywords: str, days: int, limit: int = 3) -> list[Article]:
    start = (date.today() - timedelta(days=days)).isoformat()
    query = f"({keywords}) AND SRC:PPR AND FIRST_PDATE:[{start} TO {date.today().isoformat()}]"
    r = httpx.get(EUROPE_PMC, timeout=TIMEOUT, params={
        "query": query, "format": "json", "resultType": "core", "pageSize": limit,
    })
    r.raise_for_status()
    articles = []
    for item in r.json().get("resultList", {}).get("result", []):
        doi = item.get("doi")
        url = f"https://doi.org/{doi}" if doi else f"https://europepmc.org/article/PPR/{item.get('id')}"
        articles.append(Article(
            title=_clean(item.get("title", "")),
            journal=item.get("bookOrReportDetails", {}).get("publisher", "Preprint"),
            date=item.get("firstPublicationDate", ""),
            abstract=_clean(item.get("abstractText", ""))[:MAX_ABSTRACT],
            url=url,
            pub_types=["Preprint"],
            preprint=True,
        ))
    return articles
