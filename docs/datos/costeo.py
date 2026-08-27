USD = 950          # CLP por USD (ajustar al dolar observado del dia)
FLETE_KG = 2.20    # USD/kg maritimo LCL consolidado
SEGURO = 0.01      # 1% del FOB
ARANCEL = 0.00     # 0% con Certificado de Origen China-Chile (6% sin el)
FIJOS_CLP = 400_000  # despacho, agente, almacenaje, transporte interno por pedido

SKUS = [
 # nombre, FOB USD, peso kg, unidades pedido 1, PVP CLP
 ("Alfombra de diatomea 60x39",              5.20, 2.0,  60, 27_990),
 ("Set coordinado 4 piezas ceramica mate",   6.80, 1.4,  60, 37_990),
 ("Dispensador de pared doble 2x400 ml",     4.10, 0.7,  50, 22_990),
 ("Organizador de ducha adhesivo 2 niveles", 3.90, 0.8,  50, 21_990),
 ("Bandeja organizadora de lavamanos",       2.90, 0.6,  40, 16_990),
 ("Toallero-repisa de pared negro mate",    12.00, 1.8,  20, 69_990),
 ("Set 4 ganchos adhesivos acero negro",     1.60, 0.3,  40,  9_990),
]

tot_u = sum(s[3] for s in SKUS)
filas = []
inv_total = 0
for nombre, fob, peso, u, pvp in SKUS:
    flete = peso * FLETE_KG
    seg = fob * SEGURO
    cif = fob + flete + seg
    landed_usd = cif * (1 + ARANCEL)
    landed = landed_usd * USD + FIJOS_CLP / tot_u
    margen = pvp - landed
    filas.append((nombre, fob, peso, u, round(cif,2), round(landed), pvp, round(margen), margen/pvp*100, pvp/landed))
    inv_total += landed * u

print(f"{'SKU':<42}{'FOB$':>6}{'kg':>5}{'Uds':>5}{'CIF$':>7}{'Landed':>9}{'PVP':>9}{'Margen':>9}{'%':>7}{'x':>6}")
print("-"*105)
for f in filas:
    print(f"{f[0]:<42}{f[1]:>6.2f}{f[2]:>5.1f}{f[3]:>5}{f[4]:>7.2f}{f[5]:>9,}{f[6]:>9,}{f[7]:>9,}{f[8]:>7.1f}{f[9]:>6.1f}")
print("-"*105)
peso_tot = sum(s[2]*s[3] for s in SKUS)
fob_tot = sum(s[1]*s[3] for s in SKUS)
print(f"Unidades pedido 1: {tot_u}   Peso total: {peso_tot:.0f} kg   FOB total: USD {fob_tot:,.0f}")
print(f"Inversion en inventario (landed): CLP {inv_total:,.0f}")
print(f"Valor de venta del inventario:    CLP {sum(s[3]*s[4] for s in SKUS):,.0f}")
print()

# --- P&L por pedido en Shopify ---
AOV = 48_000
MB = 0.72
print("=== P&L POR PEDIDO (ticket promedio $48.000) ===")
ing = AOV
cogs = AOV*(1-MB)
pago = AOV*0.053     # 2% fee Shopify (sin Shopify Payments en CL) + ~2,5% Webpay + IVA
envio = 3_200        # costo real medio despacho nacional, neto de lo que cobras
pack = 900
lineas = [("Ingreso", ing), ("Costo de producto (landed)", -cogs),
          ("Medios de pago + fee Shopify (5,3%)", -pago),
          ("Despacho neto", -envio), ("Packaging", -pack)]
sub = sum(v for _,v in lineas)
lineas.append(("= Contribucion antes de ads", sub))
for cpa in (10_000, 15_000, 20_000):
    lineas.append((f"  -- con CPA ${cpa:,}", sub-cpa))
for n,v in lineas:
    print(f"{n:<40}{v:>12,.0f}")
print()
print(f"CPA maximo para no perder plata: ${sub:,.0f}")
print(f"ROAS minimo de equilibrio:        {AOV/sub:.2f}x")
print(f"ROAS objetivo (CPA $15.000):      {AOV/15_000:.2f}x")
