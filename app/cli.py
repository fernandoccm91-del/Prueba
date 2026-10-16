"""Prueba el bot desde la terminal, sin WhatsApp: python -m app.cli "tu pregunta"."""

import sys

from .bot import answer

if __name__ == "__main__":
    print(answer(" ".join(sys.argv[1:]) or "hola"))
