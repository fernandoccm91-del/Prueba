"""Cliente mínimo de la API de Gemini (plan gratuito de Google AI Studio)."""

import json
import os

import httpx

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def generate(system: str, prompt: str, json_output: bool = False) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Falta GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    config = {"temperature": 0.2}
    if json_output:
        config["responseMimeType"] = "application/json"
    r = httpx.post(
        API.format(model=model),
        headers={"x-goog-api-key": key},
        timeout=60,
        json={
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": config,
        },
    )
    r.raise_for_status()
    parts = r.json()["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts).strip()


def generate_json(system: str, prompt: str) -> dict:
    return json.loads(generate(system, prompt, json_output=True))
