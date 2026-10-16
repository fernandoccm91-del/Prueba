import json

from fastapi.testclient import TestClient

from app import bot, llm, main
from app.search import Article


def test_split_message_respects_limit():
    text = "\n\n".join(["a" * 900, "b" * 900, "c" * 3500])
    chunks = bot.split_message(text)
    assert all(len(c) <= bot.MAX_CHUNK for c in chunks)
    assert "".join(chunks).replace("\n", "") == text.replace("\n", "")


def test_greeting_skips_llm(monkeypatch):
    monkeypatch.setattr(llm, "generate", lambda *a, **k: (_ for _ in ()).throw(AssertionError))
    assert "papers" in bot.answer("Hola")


def test_answer_pipeline_with_fake_llm(monkeypatch):
    query = {"pubmed_query": "q", "keywords": "k", "days": 30, "topic_es": "Insuficiencia cardíaca"}
    monkeypatch.setattr(llm, "generate_json", lambda *a: query)
    monkeypatch.setattr(llm, "generate", lambda system, prompt: "RESUMEN " + str(prompt.count("pubmed")))
    art = Article("T", "J", "2026", "A", "https://pubmed.ncbi.nlm.nih.gov/1/", ["RCT"])
    monkeypatch.setattr(bot, "search_pubmed", lambda q, d: [art])
    monkeypatch.setattr(bot, "search_preprints", lambda q, d: [])
    reply = bot.answer("novedades en insuficiencia cardíaca")
    assert "Insuficiencia cardíaca" in reply and "RESUMEN 1" in reply


def test_fallback_list_when_llm_fails(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("sin cuota")
    monkeypatch.setattr(llm, "generate", boom)
    art = Article("Title", "BMJ", "2026", "", "https://doi.org/x", ["Preprint"], preprint=True)
    out = bot.summarize("x", [art])
    assert "Title" in out and "https://doi.org/x" in out and "Preprint" in out


def test_webhook_blocks_unknown_numbers(monkeypatch):
    monkeypatch.setenv("ALLOWED_NUMBERS", "whatsapp:+56900000000")
    called = []
    monkeypatch.setattr(main, "process", lambda *a: called.append(a))
    client = TestClient(main.app)
    r = client.post("/whatsapp", data={"From": "whatsapp:+1555", "Body": "x"})
    assert r.status_code == 200 and not called
    r = client.post("/whatsapp", data={"From": "whatsapp:+56900000000", "Body": "dengue"})
    assert "Buscando" in r.text and called == [("whatsapp:+56900000000", "dengue")]
