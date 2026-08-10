#!/usr/bin/env python3
"""Modelo de costos de MercadoLibre por país, para calcular cuánto queda de un
precio de venta después de comisión, cargo fijo y despacho.

Los porcentajes y umbrales de abajo son los que se investigaron y verificaron
por última vez en agosto de 2026 (ver fuentes al final de cada perfil). Mercado
Libre cambia estas cifras con cierta frecuencia y no publica una tabla
scrapeable, así que:
  - Úsalos como estimación de orden de magnitud para rankear nichos entre sí.
  - Antes de comprometer inventario real, siempre dile al usuario que confirme
    la comisión exacta de su subcategoría y el costo de despacho con el peso y
    medidas reales en el simulador de costos de MercadoLibre.
  - Si el usuario menciona una cifra distinta (por ejemplo, su propia cuenta
    tiene una comisión negociada), usa la de él, no la de este archivo.

Uso como librería:
    from unit_economics import margen, PERFILES
    neto, desglose = margen(precio=24990, costo=0, peso_kg=2.0, pais="CL")

Uso como script (para pruebas rápidas desde la terminal):
    python3 unit_economics.py CL 24990 2.0
"""
import sys

PERFILES = {
    "CL": {
        "moneda": "CLP",
        "comision": {"clasica": 0.14, "premium": 0.17},  # rango referencial Hogar/Muebles 14%-17%
        "umbral_envio_gratis": 19990,
        "cargo_fijo": 600,          # por unidad, solo si precio < umbral_envio_gratis
        "descuento_reputacion": 0.55,  # % del costo de lista que paga el vendedor con reputación verde
        # (peso_max_kg, tarifa_lista_antes_de_descuento)
        "tarifas_envio": [(0.5, 5200), (1, 6200), (2, 7500), (5, 9500), (10, 13000), (25, 22000), (float("inf"), 38000)],
        "iva_sobre_comision": True,  # si el vendedor no es contribuyente, súmale 19% a la comisión
        "fuente": "Wivo Analytics, Rapiboy (comisiones 2026); Ayuda MercadoLibre Chile (envíos gratis)",
    },
    "MX": {
        "moneda": "MXN",
        "comision": {"clasica": 0.15, "premium": 0.195},  # Hogar, Muebles y Jardín
        "umbral_envio_gratis": 299,
        "cargo_fijo_tiers": [(99, 25), (149, 30), (299, 37)],  # (precio_bajo_que, cargo) solo Clásica
        "descuento_reputacion": 0.60,
        "tarifas_envio": [(0.5, 105), (1, 120), (2, 145), (5, 175), (10, 230), (25, 380), (float("inf"), 650)],
        "isr": 0.025,  # retención 2026, además de la comisión
        "fuente": "ProfitOS, Tiendanube (comisiones 2026)",
    },
}


def margen(precio, costo, peso_kg, pais="CL", tipo="premium"):
    """Devuelve (neto_disponible, desglose_dict) para un producto de `peso_kg`
    vendido a `precio`, con `costo` de compra puesto en bodega (0 si aún no lo
    sabes y solo quieres el margen bruto antes de costo de producto)."""
    p = PERFILES[pais]
    com = precio * p["comision"][tipo]
    bajo_umbral = precio < p["umbral_envio_gratis"]

    fijo = 0
    if bajo_umbral:
        if "cargo_fijo" in p:
            fijo = p["cargo_fijo"]
        elif "cargo_fijo_tiers" in p and tipo == "clasica":
            for tope, cargo in p["cargo_fijo_tiers"]:
                if precio < tope:
                    fijo = cargo
                    break

    envio = 0
    if not bajo_umbral:
        for tope, tarifa in p["tarifas_envio"]:
            if peso_kg <= tope:
                envio = round(tarifa * p["descuento_reputacion"])
                break

    otros = 0
    if pais == "MX":
        otros = precio * p.get("isr", 0)

    neto = precio - com - fijo - envio - otros - costo
    return neto, dict(comision=round(com), cargo_fijo=fijo, envio=envio, otros=round(otros))


def costo_maximo(precio, peso_kg, pais="CL", tipo="premium", margen_objetivo=0.25):
    """Costo máximo de compra para dejar `margen_objetivo` (25% por defecto) de
    margen neto sobre el precio de venta."""
    neto, _ = margen(precio, 0, peso_kg, pais, tipo)
    return neto - margen_objetivo * precio


if __name__ == "__main__":
    pais = sys.argv[1] if len(sys.argv) > 1 else "CL"
    precio = float(sys.argv[2]) if len(sys.argv) > 2 else 24990
    peso = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    neto, desglose = margen(precio, 0, peso, pais)
    cmax = costo_maximo(precio, peso, pais)
    moneda = PERFILES[pais]["moneda"]
    print(f"Precio: {precio:,.0f} {moneda} | peso: {peso} kg | país: {pais}")
    print(f"Desglose: {desglose}")
    print(f"Disponible tras costos: {neto:,.0f} {moneda}")
    print(f"Costo máximo de compra para 25% de margen neto: {cmax:,.0f} {moneda}")
