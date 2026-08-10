# Contexto del proyecto

## Sobre el usuario

- **Vive y vende en Chile.** Todo análisis de mercado, precios, comisiones y logística debe hacerse
  sobre **MercadoLibre Chile (sitio MLC, mercadolibre.cl)** y en **pesos chilenos (CLP)**, salvo que
  pida explícitamente otro país.
- No asumir México ni Argentina por defecto.

## Sobre los datos de MercadoLibre

- La API pública (`api.mercadolibre.com`) devuelve 403 sin token de aplicación, y las páginas de
  búsqueda (`listado.mercadolibre.cl`) redirigen a un muro de verificación de cuenta.
- La superficie que sí responde a `curl` con headers de navegador es
  **`https://www.mercadolibre.cl/ofertas?category=<ID>&page=<N>`**. Ver `scripts/fetch.sh`.
- Un navegador headless (Playwright/Chromium) no sirve en este entorno: el proxy de salida corta
  la conexión del browser.
