#!/usr/bin/env python3
"""Clasifica productos de MercadoLibre (nicho hogar CL) en nichos con sentido
de negocio y les asigna un peso estimado (kg) para el modelo de envio.

Las reglas se evaluan en orden: la primera que coincide gana. Por eso van de
lo mas especifico a lo mas general. Se opera sobre el titulo en minusculas.

Uso: python3 clasificar_nichos.py productos.json > productos_clasificados.json
"""
import json
import re
import sys

# (nombre_nicho, peso_kg, [patrones regex]). Orden importa.
REGLAS = [
    ("Camaras de seguridad WiFi", 0.5,
     [r"c[aá]mara.*(seguridad|vigilancia|wifi|exterior|ptz|ip )", r"\bezviz\b", r"\bptz\b", r"\bcctv\b", r"videoportero", r"c[aá]mara.*360"]),
    ("Alarmas y sirenas", 0.6,
     [r"\bsirena\b", r"alarma", r"sensor.*(movimiento|puerta|alarma)", r"estrobosc"]),
    ("Cerraduras, candados y herrajes", 0.8,
     [r"cerradura", r"candado", r"cerrojo", r"manilla", r"pestillo", r"herraje", r"bisagra", r"picaporte", r"chapa .*(puerta|seguridad)"]),
    ("Toallero electrico / secatoallas", 4.0,
     [r"toallero el[eé]ctric", r"secatoalla", r"secador de toalla", r"calienta toalla"]),
    ("WC / sanitarios / receptaculos / mamparas", 22.0,
     [r"\bwc\b", r"inodoro", r"one piece", r"sanitario", r"recept[aá]cul", r"mampara", r"\bbidet\b", r"alza ?ba[nñ]o", r"asiento.*(wc|inodoro)", r"tapa.*(wc|inodoro|ba[nñ]o)", r"estanque", r"urinario", r"barra.*(agarre|seguridad).*(ba[nñ]o|inodoro)", r"barra de agarre"]),
    ("Duchas / columnas / grifería de ducha", 2.0,
     [r"ducha", r"columna.*ducha", r"canilla el[eé]ctric", r"kit ducha", r"juego de ducha", r"barrera de agua"]),
    ("Dispensadores de papel (baño/industrial)", 1.0,
     [r"dispensador.*(papel|toalla|jumbo|interfoliad|higi[eé]nic|confort)"]),
    ("Toallas de baño", 1.0,
     [r"toall[oó]n", r"toalla", r"juego.*toalla", r"set.*toalla", r"bata.*ba[nñ]o"]),
    ("Accesorios de bano (sets/toalleros/dispensadores)", 1.2,
     [r"juego de ba[nñ]o", r"set.*ba[nñ]o", r"toallero", r"jabonera", r"dispensador.*(jab[oó]n|ba[nñ]o)", r"porta cepillo", r"organizador.*ba[nñ]o", r"repisa.*ba[nñ]o", r"accesorios.*ba[nñ]o", r"cepillo.*(inodoro|wc)"]),
    ("Grifería y lavamanos", 3.5,
     [r"lavamanos", r"lavacopa", r"lavabo", r"lavaplatos", r"grifer", r"llave.*(lavamanos|ba[nñ]o|cocina|lavaplatos|urinario)", r"monomando", r"llave temporizada", r"desag[uü]e", r"fregadero"]),
    ("Alfombras de bano/cocina antideslizantes", 0.6,
     [r"alfombra.*(ba[nñ]o|cocina|antideslizante|bajada de cama|absorbente)", r"pie de cama"]),
    ("Alfombras decorativas / living", 5.0,
     [r"alfombra", r"tapete", r"\byute\b", r"felpudo"]),
    ("Cortinas roller / blackout", 3.0,
     [r"cortina", r"visillo", r"roller", r"blackout", r"panel japon", r"cenefa"]),
    ("Almohadas cervicales / ortopedicas", 0.9,
     [r"almohada.*(cervical|ortop|viscoel|memory)", r"almohada.*cuello"]),
    ("Almohadas estandar", 1.2,
     [r"almohada", r"cojin.*cama"]),
    ("Mantas / frazadas electricas", 2.0,
     [r"manta.*(el[eé]ctric|t[eé]rmica)", r"frazada.*el[eé]ctric", r"calienta cama"]),
    ("Sabanas y juegos de cama", 1.6,
     [r"s[aá]bana", r"juego de cama", r"funda.*(almohada|plum[oó]n|n[oó]rdico)", r"quilt", r"cubrecama"]),
    ("Plumones / frazadas / mantas", 2.2,
     [r"plum[oó]n", r"frazada", r"\bmanta\b", r"cobertor", r"n[oó]rdico", r"edred[oó]n"]),
    ("Cubrecolchon / protectores", 1.4,
     [r"cubre ?colch[oó]n", r"protector.*colch[oó]n", r"cubrecolch"]),
    ("Selladoras al vacio / conservacion", 1.5,
     [r"selladora", r"sellad[oa].*vac[ií]o", r"envasadora", r"bolsa.*vac[ií]o.*(sellad|m[aá]quina)"]),
    ("Basculas / gramera de cocina", 0.5,
     [r"b[aá]scula", r"bascula", r"gramera", r"balanza.*(cocina|digital)", r"pesa.*(digital|aliment|cocina|comida)"]),
    ("Molinillos de cafe", 0.8,
     [r"molinillo", r"moledor", r"molino.*caf[eé]", r"french press", r"prensa francesa"]),
    ("Carritos y repisas organizadoras de cocina", 3.5,
     [r"carrito organizador", r"carro mopero", r"repisa.*(cocina|extra[ií]ble|microondas|extensible)", r"organizador.*(gabinete|extra[ií]ble|extensible|desplegable)", r"cesta.*(extra[ií]ble|cromada)", r"revestimiento caj[oó]n"]),
    ("Bandejas / laminas de horno / airfryer", 0.5,
     [r"bandeja.*(horno|aluminio)", r"l[aá]mina.*(tefl[oó]n|silicona|horno)", r"papel.*(airfryer|air.?fryer|freidora)", r"forro.*(airfryer|freidora)", r"rejilla.*(enfriar|horno|galleta)", r"tefl[oó]n.*sublimaci", r"papel.*(aluminio|film|pvc)", r"\bfilm\b"]),
    ("Guantes / protectores termicos de cocina", 0.4,
     [r"guante.*(horno|cocina|t[eé]rmic|temperatura|silicona)", r"protector t[eé]rmico", r"agarrador"]),
    ("Cortadores / picadoras manuales", 0.7,
     [r"cortador", r"cortadora", r"picador", r"picadora", r"mandolina", r"espiralizador"]),
    ("Baterias de cocina / ollas / sartenes", 4.5,
     [r"bater[ií]a\s+(de\s+)?cocina", r"set.*(olla|sart[eé]n)", r"\bollas?\b", r"sart[eé]n", r"wok", r"caldero", r"budinera", r"budare", r"paila", r"cacerola", r"arrocera", r"plancha.*(churrasq|hierro)", r"fondue", r"chocolatera"]),
    ("Cuchillos de cocina", 0.7,
     [r"cuchillo", r"cuchiller", r"set.*cuchill", r"afilador", r"piedra.*afilar", r"eversharp", r"tabla.*(picar|corte|cocina|cortar)", r"tabla.*(bamb[uú]|madera|acero|mdf)"]),
    ("Cubiertos", 0.8,
     [r"cubierto", r"tenedor", r"cuchara", r"tramontina.*(pzas|piezas|cubierto)"]),
    ("Cristaleria / vasos / copas", 2.5,
     [r"\bvasos?\b", r"\bcopas?\b", r"jarr[oó]n? de vidrio", r"set de vaso", r"piscola", r"cervecero", r"\bshot\b", r"posavaso"]),
    ("Jarras y jarros", 1.0,
     [r"\bjarras?\b", r"\bjarros?\b", r"jarra.*(vidrio|t[eé]rmica|medidora|jugo|agua)", r"purificador.*agua"]),
    ("Tazas / tazones / mugs (incl. sublimacion)", 0.5,
     [r"\btaza\b", r"\btazas\b", r"taz[oó]n", r"tazones", r"\bmug\b", r"sublimaci", r"pocillo", r"espresso", r"capuchino", r"cappuch"]),
    ("Vajilla / platos / loza / servir", 2.5,
     [r"\bplatos?\b", r"vajilla", r"loza", r"\bbowl\b", r"ensaladera", r"fuente.*(servir|horno)", r"bandeja.*(servir|melamina)", r"chafer", r"buffet", r"quesillera", r"porta ?(torta|cupcake|cake)"]),
    ("Termos y mates", 0.6,
     [r"\btermo\b", r"\bmate\b", r"bombilla", r"botella.*(t[eé]rmica|acero)", r"cooler"]),
    ("Reposteria / horneado (moldes, silicona)", 0.6,
     [r"molde", r"silicona.*horno", r"repost", r"bizcoch", r"uslero", r"manga paster", r"l[aá]mina.*horno", r"papel.*horno", r"base.*torta"]),
    ("Gadgets de cocina (termometro, temporizador, balanza aux)", 0.4,
     [r"term[oó]metro", r"temporizador", r"pulverizador.*aceite", r"rociador.*aceite", r"dispensador.*aceite", r"prensa.*(ajo|papa|tortilla|patacon)", r"prensapapas", r"regulador de gas", r"embudo", r"destapador", r"abridor"]),
    ("Utensilios de cocina (varios)", 0.5,
     [r"utensilio", r"esp[aá]tula", r"cuchar[oó]n", r"cuchara.*(hielo|servir)", r"colador", r"rallador", r"\bpela", r"exprimidor", r"batidor manual", r"pinza.*(cocina|acero)", r"set.*utensilio", r"set.*silicona.*cocina", r"brocheta", r"pincho", r"pala pizza"]),
    ("Contenedores hermeticos / almacenamiento cocina", 0.8,
     [r"contenedor", r"herm[eé]tic", r"tarro", r"frasco", r"dispensador.*(cereal|az[uú]car|alimento)", r"guarda.*(pan|aliment)", r"fiambre", r"tupper", r"organizador.*(refri|nevera|despensa)"]),
    ("Secaplatos / escurridores", 1.2,
     [r"secaplato", r"escurr", r"platera"]),
    ("Organizadores de ropa / closet", 1.5,
     [r"organizador.*(ropa|closet|clóset|cajon|caj[oó]n)", r"colgador.*ropa", r"\bpercha\b", r"perchero", r"separador.*caj[oó]n", r"organizador.*(zapato|calzado)", r"funda.*ropa", r"bolsa.*vac[ií]o"]),
    ("Zapateros / muebles organizadores", 6.0,
     [r"zapatero", r"mueble.*organizador", r"organizador.*mueble", r"repisa.*(pared|flotante)", r"estante"]),
    ("Cajas y canastos organizadores", 1.0,
     [r"\bcaja\b", r"cajas", r"canasto", r"caj[oó]n organizador", r"cesto"]),
    ("Basureros / papeleras", 2.5,
     [r"basurero", r"papelera", r"\bbote.*basura", r"tacho"]),
    ("Bolsas de basura / plasticas", 1.0,
     [r"bolsa.*basura", r"bolsa.*(compostable|biodegradable|camiseta)", r"bolsas pl[aá]sticas"]),
    ("Lamparas de sal / decorativas de mesa", 1.5,
     [r"l[aá]mpara de sal", r"lampara de sal", r"l[aá]mpara.*himalaya"]),
    ("Lamparas de techo / colgantes", 2.0,
     [r"l[aá]mpara.*(techo|colgante|ara[nñ]a|plaf[oó]n)", r"l[aá]mpara colgante", r"chandelier"]),
    ("Lamparas de pie / mesa / veladores", 3.0,
     [r"l[aá]mpara.*(pie|mesa|velador|escritorio|noche)", r"velador"]),
    ("Ampolletas / focos / plafones LED", 0.4,
     [r"ampolleta", r"cinta led", r"tira led", r"\bfoco", r"focos", r"plaf[oó]n", r"foco?plaf", r"reflector", r"panel led", r"panel plaf", r"tubo led", r"dicroic", r"luz de emergencia", r"foco.*solar", r"estaca led"]),
    ("Lamparas (otras) / apliques", 1.5,
     [r"l[aá]mpara", r"aplique", r"lampara", r"luminaria"]),
    ("Limpieza: traperos / mopas / cepillos", 1.0,
     [r"trapero", r"\bmopa\b", r"cepillo.*(limpieza|piso|ba[nñ]o|multiuso)", r"escoba", r"pala.*basura", r"limpiavidrio", r"pa[nñ]o.*(microfibra|limpieza)", r"guante.*limpieza", r"esponja"]),
    ("Aromas / home spray / difusores", 0.5,
     [r"home spray", r"difusor", r"aromatizante", r"sahumerio", r"varilla.*arom", r"vela arom", r"refill.*(arom|home)"]),
    ("Decoracion / cuadros / espejos / relojes", 1.5,
     [r"cuadro", r"espejo", r"reloj.*pared", r"vinilo", r"marco.*foto", r"figura decor", r"florero", r"jarr[oó]n"]),
]

COMPILADAS = [(n, w, [re.compile(p, re.I) for p in pats]) for n, w, pats in REGLAS]


def clasificar(titulo):
    t = titulo.lower()
    for nombre, peso, pats in COMPILADAS:
        if any(p.search(t) for p in pats):
            return nombre, peso
    return "Otros / sin clasificar", 1.0


def main():
    d = json.load(open(sys.argv[1]))
    for x in d:
        n, w = clasificar(x.get("title", ""))
        x["nicho"] = n
        x["peso_kg"] = w
    json.dump(d, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
