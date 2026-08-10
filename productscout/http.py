"""Tiny stdlib HTTP helper so the core package has zero runtime dependencies."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class HttpError(RuntimeError):
    def __init__(self, status: int, body: str, url: str):
        super().__init__(f"HTTP {status} from {url}: {body[:300]}")
        self.status = status
        self.body = body
        self.url = url


def request_json(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    timeout: int = 25,
    retries: int = 3,
) -> Any:
    """GET/POST JSON with exponential backoff on 429/5xx and network errors."""
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{url}{'&' if '?' in url else '?'}{query}"

    all_headers = {"Accept": "application/json", "User-Agent": "ProductScout/1.0"}
    all_headers.update(headers or {})

    last_error: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=all_headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return json.loads(body) if body else None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                last_error = HttpError(exc.code, body, url)
                continue
            raise HttpError(exc.code, body, url) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    if last_error:
        raise last_error
    return None


def post_form(url: str, form: dict[str, str], timeout: int = 25) -> Any:
    body = urllib.parse.urlencode(form).encode()
    return request_json(
        url,
        method="POST",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=timeout,
    )
