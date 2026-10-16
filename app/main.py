"""Servidor web: recibe los mensajes de WhatsApp desde Twilio y responde."""

import logging
import os
from xml.sax.saxutils import escape

import httpx
from fastapi import BackgroundTasks, FastAPI, Form, Response

from .bot import GREETINGS, answer, split_message

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="Bot de papers para profesionales de la salud")


def twiml(text: str = "") -> Response:
    body = f"<Message>{escape(text)}</Message>" if text else ""
    return Response(f'<?xml version="1.0" encoding="UTF-8"?><Response>{body}</Response>',
                    media_type="application/xml")


def send_whatsapp(to: str, text: str) -> None:
    sid = os.environ["TWILIO_ACCOUNT_SID"]
    for chunk in split_message(text):
        r = httpx.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            auth=(sid, os.environ["TWILIO_AUTH_TOKEN"]),
            data={"From": os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"),
                  "To": to, "Body": chunk},
            timeout=20,
        )
        if r.status_code >= 400:
            log.error("Twilio respondió %s: %s", r.status_code, r.text)


def process(sender: str, message: str) -> None:
    try:
        reply = answer(message)
    except Exception:
        log.exception("Error procesando el mensaje")
        reply = "😕 Tuve un problema buscando. Intenta de nuevo en un minuto."
    send_whatsapp(sender, reply)


def is_allowed(sender: str) -> bool:
    allowed = {n.strip() for n in os.getenv("ALLOWED_NUMBERS", "").split(",") if n.strip()}
    return not allowed or sender in allowed


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/whatsapp")
def whatsapp(background: BackgroundTasks, From: str = Form(...), Body: str = Form("")):
    if not is_allowed(From):
        log.warning("Mensaje ignorado de número no autorizado: %s", From)
        return twiml()
    # Twilio espera respuesta en menos de 15 s: contesto ya y busco en segundo plano.
    background.add_task(process, From, Body)
    if Body.strip().lower() in GREETINGS:
        return twiml()
    return twiml("🔎 Buscando papers, dame unos segundos...")

