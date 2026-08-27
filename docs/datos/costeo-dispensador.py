USD=950; FLETE=2.20; SEG=0.01; FIJOS_U=1333   # mismos supuestos que docs/03

def landed(fob, peso):
    cif = fob + peso*FLETE + fob*SEG
    return cif*USD + FIJOS_U, cif

ESC = [
 # etiqueta, FOB USD, peso kg, devoluciones %
 ("Genérico 'look acero' (ABS cromado)", 5.00, 0.50, 0.08),
 ("Acero real, gama media (MOQ 300)",    7.50, 0.60, 0.06),
 ("Premium: IP67, 304, batería 3 meses",14.00, 0.75, 0.04),
]
PRECIOS = [19_990, 24_990, 29_990, 39_990, 49_990]

print(f"{'ESCENARIO':<40}{'FOB$':>7}{'CIF$':>8}{'Landed':>9}")
print("-"*64)
L={}
for n,fob,peso,dev in ESC:
    l,cif = landed(fob,peso); L[n]=(l,dev)
    print(f"{n:<40}{fob:>7.2f}{cif:>8.2f}{round(l):>9,}")

print()
print("MARGEN BRUTO POR PRECIO DE VENTA (antes de devoluciones)")
print(f"{'PVP':>9}" + "".join(f"{n[:22]:>24}" for n,_,_,_ in ESC))
print("-"*(9+24*3))
for pvp in PRECIOS:
    fila=f"{pvp:>9,}"
    for n,_,_,_ in ESC:
        l,_=L[n]; m=pvp-l
        fila += f"{m:>13,.0f} ({m/pvp*100:>4.0f}%)"
    print(fila)

print()
print("CONTRIBUCIÓN NETA POR UNIDAD (con pagos 5,3%, despacho neto 2.400, packaging 900,")
print("y el costo de las devoluciones repartido sobre las unidades vendidas)")
print(f"{'PVP':>9}" + "".join(f"{n[:22]:>24}" for n,_,_,_ in ESC))
print("-"*(9+24*3))
for pvp in PRECIOS:
    fila=f"{pvp:>9,}"
    for n,_,_,_ in ESC:
        l,dev=L[n]
        # una devolución pierde el flete de ida y vuelta + el producto queda como usado (50% de recupero)
        costo_dev = dev*(l*0.5 + 2400*2)
        neto = pvp - l - pvp*0.053 - 2400 - 900 - costo_dev
        fila += f"{neto:>13,.0f} ({neto/pvp*100:>4.0f}%)"
    print(fila)

print()
print("PEDIDO DE PRUEBA — 80 unidades del escenario 'acero real'")
l,_ = L["Acero real, gama media (MOQ 300)"]
for u in (80,150,300):
    print(f"  {u:>3} unidades → inventario CLP {l*u:,.0f}   (FOB USD {7.50*u:,.0f})")
print()
print("REFERENCIA: simplehuman 9 oz sensor pump = USD 70–120 → CLP", f"{70*USD:,.0f}–{120*USD:,.0f}")
