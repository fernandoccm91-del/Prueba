#!/bin/bash
u="$1"; out="${2:-o.html}"
curl -s -m 40 -o "$out" -w "%{http_code}|%{url_effective}\n" -L \
 -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36' \
 -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' \
 -H 'accept-language: es-419,es;q=0.9,en;q=0.8' --compressed \
 -H 'sec-ch-ua: "Chromium";v="127", "Not)A;Brand";v="99"' -H 'sec-ch-ua-mobile: ?0' -H 'sec-ch-ua-platform: "macOS"' \
 -H 'sec-fetch-dest: document' -H 'sec-fetch-mode: navigate' -H 'sec-fetch-site: none' -H 'sec-fetch-user: ?1' -H 'upgrade-insecure-requests: 1' "$u"
