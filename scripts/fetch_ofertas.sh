#!/bin/bash
# Descarga una URL de MercadoLibre con headers de navegador real.
#
# Por qué existe este script: api.mercadolibre.com devuelve 403 sin token de
# aplicación, y las páginas de listado/búsqueda normales redirigen a un muro
# de verificación de cuenta (account-verification) cuando el cliente no
# parece un navegador. La superficie que sí responde de forma estable es la
# de "ofertas por categoría": https://www.mercadolibre.<tld>/ofertas?category=<ID>&page=<N>
#
# Un navegador headless (Playwright/Chromium) casi nunca es la solución más
# rápida acá: en muchos entornos con proxy de salida (agent proxy, sandboxes)
# la conexión del browser se corta (ERR_CONNECTION_RESET) aunque curl con los
# mismos headers funcione perfecto. Prueba primero con curl; solo si hace
# falta JavaScript real (raro en esta superficie) vale la pena pelear con
# Playwright y pasarle proxy:{server:...} al chromium.launch().
#
# Uso: fetch_ofertas.sh <url> <archivo_salida> [idioma_accept]
#   idioma_accept por defecto: es-CL,es;q=0.9,en;q=0.8 (Chile)
#   otros sitios: es-MX,es;q=0.9,en;q=0.8 (México), es-AR,es;q=0.9,en;q=0.8 (Argentina)

set -euo pipefail

URL="$1"
OUT="${2:-o.html}"
LANG="${3:-es-CL,es;q=0.9,en;q=0.8}"

curl -s -m 40 -o "$OUT" -w "%{http_code}\n" -L \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' \
  -H "accept-language: $LANG" --compressed \
  -H 'sec-ch-ua: "Chromium";v="127", "Not)A;Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: document' -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: none' -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' "$URL"

# Si el http_code es 200 pero el archivo tiene ~24KB y el título es de
# verificación de cuenta, el sitio igual te mandó al muro. Revisa con:
#   grep -o '<title>[^<]*' "$OUT"
# Si eso pasa, confirma que la URL sea la de /ofertas?category=... y no una
# de listado/búsqueda normal.
