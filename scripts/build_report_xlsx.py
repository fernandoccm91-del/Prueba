#!/usr/bin/env python3
"""Construye el Excel final de un estudio: dos hojas, "Resumen por nicho" y
"Productos", con formato de tabla, moneda, encabezados congelados y enlaces.

Por qué existe: entregar un CSV a un usuario que lo va a abrir en el celular
es ilegible (se ve como texto plano lleno de comas). Un .xlsx con columnas
en español, formato de moneda y una hoja de resumen arriba de los datos crudos
se abre bien en cualquier app de hojas de cálculo (Excel, Google Sheets, la
app nativa del teléfono) y comunica el hallazgo, no solo los datos.

Uso:
    python3 build_report_xlsx.py resumen_nichos.json productos.json salida.xlsx \
        --moneda CLP --titulo "Productos de baño en MercadoLibre Chile"

Formato esperado de resumen_nichos.json: lista de dicts con al menos las claves
    nicho, score, ofertas, vendedores (o "competidores"), uds_publ, uds_tot,
    p50, pmin, pmax, peso, catalogo, full, desc, disp
(las claves que falten simplemente no se muestran; no hace falta tenerlas todas)

Formato esperado de productos.json: la salida directa de parse_cards.py, más
el campo "nicho" que le hayas agregado a cada producto al clasificarlo.
"""
import argparse
import json
import re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

FONT = "Arial"
NAVY = "1F3B4D"
LIGHT = "F4F5F3"
WHITE = "FFFFFF"

header_font = Font(name=FONT, bold=True, color=WHITE, size=10)
header_fill = PatternFill("solid", fgColor=NAVY)
title_font = Font(name=FONT, bold=True, size=14, color=NAVY)
sub_font = Font(name=FONT, italic=True, size=9, color="65736F")
body_font = Font(name=FONT, size=10)
thin = Side(style="thin", color="D9DEDA")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

RESUMEN_COLS = [
    ("Nicho", "nicho", 34, None),
    ("Score", "score", 9, "0.0"),
    ("Ofertas", "ofertas", 9, "#,##0"),
    ("Competidores", "vendedores", 12, "#,##0"),
    ("Uds/publicación", "uds_publ", 13, "#,##0"),
    ("Uds. totales", "uds_tot", 12, "#,##0"),
    ("Precio mediano", "p50", 13, "MONEDA"),
    ("Precio mín.", "pmin", 12, "MONEDA"),
    ("Precio máx.", "pmax", 12, "MONEDA"),
    ("Peso (kg)", "peso", 9, "0.0"),
    ("% en catálogo", "catalogo", 11, '0"%"'),
    ("% Full", "full", 9, '0"%"'),
    ("Desc. mediano", "desc", 11, '0"%"'),
    ("% disponible tras costos", "disp", 14, '0"%"'),
]

PRODUCTO_COLS = [
    ("Nicho", "nicho", 30, None, False),
    ("Producto", "title", 55, None, False),
    ("Precio", "price", 13, "MONEDA", False),
    ("Precio de lista", "list_price", 15, "MONEDA", False),
    ("Descuento", "_desc_pct", 11, "0%", False),
    ("Unidades vendidas", "sold", 13, '"+"#,##0', False),
    ("Calificación", "rating", 11, '0.0"★"', False),
    ("Vendedor", "seller", 20, None, False),
    ("Full", "_full", 8, None, False),
    ("Más vendido", "_top", 11, None, False),
    ("Enlace", "link", 12, None, False),
]


def style_header(ws, row, cols):
    for j, col in enumerate(cols, start=1):
        c = ws.cell(row=row, column=j, value=col[0])
        c.font, c.fill, c.border = header_font, header_fill, border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def build(resumen_path, productos_path, out_path, moneda="CLP", titulo="Estudio de mercado"):
    money_fmt = "$#,##0" if moneda in ("CLP", "COP") else f'$#,##0"{" " + moneda if moneda != "USD" else ""}"'

    wb = Workbook()

    # ---- Hoja 1: Resumen por nicho ----
    ws1 = wb.active
    ws1.title = "Resumen por nicho"
    resumen = json.load(open(resumen_path, encoding="utf-8"))
    resumen = sorted(resumen, key=lambda r: -r.get("score", 0))

    ws1["A1"] = f"{titulo} — resumen por nicho"
    ws1["A1"].font = title_font
    ws1["A2"] = f"Score = demanda x (1/competencia) x disponibilidad de catálogo x margen · precios en {moneda}"
    ws1["A2"].font = sub_font
    ws1.merge_cells(f"A1:{get_column_letter(len(RESUMEN_COLS))}1")
    ws1.merge_cells(f"A2:{get_column_letter(len(RESUMEN_COLS))}2")

    header_row = 4
    style_header(ws1, header_row, RESUMEN_COLS)
    for i, r in enumerate(resumen, start=header_row + 1):
        for j, (label, key, width, fmt) in enumerate(RESUMEN_COLS, start=1):
            c = ws1.cell(row=i, column=j, value=r.get(key))
            c.font, c.border = body_font, border
            if fmt:
                c.number_format = money_fmt if fmt == "MONEDA" else fmt
            c.alignment = Alignment(
                vertical="center", wrap_text=(key == "nicho"), horizontal="left" if key == "nicho" else "center"
            )
        if i % 2 == 0:
            for j in range(1, len(RESUMEN_COLS) + 1):
                ws1.cell(row=i, column=j).fill = PatternFill("solid", fgColor=LIGHT)
    for j, (_l, _k, width, _f) in enumerate(RESUMEN_COLS, start=1):
        ws1.column_dimensions[get_column_letter(j)].width = width
    ws1.freeze_panes = f"A{header_row + 1}"
    if resumen:
        ws1.add_table(
            Table(
                displayName="ResumenNichos",
                ref=f"A{header_row}:{get_column_letter(len(RESUMEN_COLS))}{header_row + len(resumen)}",
                tableStyleInfo=TableStyleInfo(name="TableStyleMedium2", showRowStripes=False),
            )
        )
    ws1.row_dimensions[header_row].height = 28

    # ---- Hoja 2: Productos ----
    ws2 = wb.create_sheet("Productos")
    productos = json.load(open(productos_path, encoding="utf-8"))
    for r in productos:
        m = re.search(r"\d+", r.get("discount") or "")
        r["_desc_pct"] = int(m.group(0)) / 100 if m else None
        r["_full"] = "Sí" if r.get("full") else "No"
        r["_top"] = "Sí" if r.get("top_seller") else "No"
    productos.sort(key=lambda r: (r.get("nicho", ""), -(r.get("sold") or 0), r.get("price") or 0))

    ws2["A1"] = f"{titulo} — detalle de productos"
    ws2["A1"].font = title_font
    ws2["A2"] = f"{len(productos)} publicaciones únicas · superficie de ofertas por categoría"
    ws2["A2"].font = sub_font

    header_row2 = 4
    style_header(ws2, header_row2, PRODUCTO_COLS)
    for i, r in enumerate(productos, start=header_row2 + 1):
        for j, (label, key, width, fmt, wrap) in enumerate(PRODUCTO_COLS, start=1):
            if key == "link":
                c = ws2.cell(row=i, column=j, value="Ver ficha ↗")
                if r.get("link"):
                    c.hyperlink = r["link"]
                c.font = Font(name=FONT, size=10, color="0D6B5F", underline="single")
            else:
                c = ws2.cell(row=i, column=j, value=r.get(key))
                c.font = body_font
                if fmt:
                    c.number_format = money_fmt if fmt == "MONEDA" else fmt
            c.border = border
            c.alignment = Alignment(
                vertical="center",
                wrap_text=wrap,
                horizontal="left" if key in ("nicho", "title", "seller") else "center",
            )
        if i % 2 == 0:
            for j in range(1, len(PRODUCTO_COLS) + 1):
                ws2.cell(row=i, column=j).fill = PatternFill("solid", fgColor=LIGHT)
    for j, (_l, _k, width, _f, _w) in enumerate(PRODUCTO_COLS, start=1):
        ws2.column_dimensions[get_column_letter(j)].width = width
    ws2.freeze_panes = f"C{header_row2 + 1}"
    if productos:
        ws2.add_table(
            Table(
                displayName="Productos",
                ref=f"A{header_row2}:{get_column_letter(len(PRODUCTO_COLS))}{header_row2 + len(productos)}",
                tableStyleInfo=TableStyleInfo(name="TableStyleMedium2", showRowStripes=False),
            )
        )
    ws2.row_dimensions[header_row2].height = 30

    wb.save(out_path)
    print(f"guardado {out_path} · {len(resumen)} nichos · {len(productos)} productos")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("resumen_json")
    ap.add_argument("productos_json")
    ap.add_argument("salida_xlsx")
    ap.add_argument("--moneda", default="CLP")
    ap.add_argument("--titulo", default="Estudio de mercado en MercadoLibre")
    args = ap.parse_args()
    build(args.resumen_json, args.productos_json, args.salida_xlsx, args.moneda, args.titulo)
