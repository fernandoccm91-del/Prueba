#!/usr/bin/env python3
"""Clasifica los productos de productos_raw.json en nichos de negocio y les
asigna un peso estimado (necesario para el modelo de envío)."""
import json, re, sys

# (nicho, peso_kg estimado, patrón). Orden importa: gana la primera que matchea.
REGLAS = [
 # --- FITNESS ---
 ("Suplementos deportivos",      0.6, r"creatin|whey|prote[íi]na|proteic|omega|magnesio|colágeno|colageno|berberina|probi[óo]tic|vitamin|centrum|glucerna|citracal|stevia|endulzante|bcaa|glutamin|pre.?entren|multivitam|zinc|melatonin|ashwagandha|maca|espirulina|l-?carnitina|caseina|masa muscular|ganador|hipercal|suplemento"),
 ("Shakers y botellas fitness",  0.3, r"shaker|vaso mezclador|botella.*(gym|deportiv|fitness)"),
 ("Bandas elásticas resistencia",0.5, r"banda[s]? el[áa]stic|power ?band|banda[s]? de resistencia|liga[s]? de resistencia|mini ?band|tubo.*resistencia"),
 ("Cuerdas de saltar",           0.3, r"cuerda.*salt|salt(ar|o).*cuerda|speed rope|saltar.*velocidad"),
 ("Hand grip / agarre",          0.3, r"hand ?grip|ejercitador de mano|fortalecedor.*(mano|mu[ñn]ec|antebrazo)|pinza.*fuerza"),
 ("Accesorios crossfit textiles",0.3, r"mu[ñn]equer|coder[ao]s?|rodiller|straps|calleras|guantes.*(gym|gimnasio|pesas)|cintur[óo]n.*(lumbar|pesas)|k.?tape|kinesiol[óo]gic|venda"),
 ("Mat yoga y colchonetas",      1.8, r"mat de? ?yoga|mat yoga|colchoneta|tapete.*(yoga|pilates|ejercicio)|esterilla"),
 ("Accesorios pilates/yoga",     0.6, r"rueda.*yoga|bloque.*yoga|anillo.*pilates|c[íi]rculo m[áa]gico|pelota.*(pilates|yoga)|banda.*pilates"),
 ("Rodillos masaje / recuperación",0.6,r"foam ?roller|rodillo.*(masaj|muscular)|pistola.*masaj|masajeador.*muscular|bola.*masaj"),
 ("Agilidad y coordinación",     0.6, r"escalera.*(velocidad|agilidad)|cono[s]? .*(entrenamiento|agilidad)|paracaídas.*entren"),
 ("Pesas y mancuernas",         12.0, r"mancuerna|pesa[s]? ajustab|kettlebell|disco[s]? .*(peso|olímpic)|barra.*(olímpic|preolímpic|z |dominad)|tobiller.*peso|chaleco.*peso"),
 ("Máquinas de gimnasio",       35.0, r"trotadora|caminadora|bicicleta.*(est[áa]tica|spinning)|el[íi]ptic|press banca|banco.*(abdominal|pesas)|estaci[óo]n.*entren|multif?uncional.*gym|remo.*m[áa]quina|pedalera|abdominal.*(m[áa]quina|rueda)"),
 # --- BAÑO ---
 ("Bidet ducha para WC",         0.6, r"bidet|ducha ?[áa]rabe|ducha turca"),
 ("Asientos y tapas de WC",      2.5, r"tapa.*w\.?c|asiento.*w\.?c|tapa.*inodoro|asiento.*inodoro|alzaba[ñn]o"),
 ("Barras seguridad y movilidad",1.2, r"barra.*(seguridad|agarre|discapacit)|manilla.*(seguridad|ducha)|pasamano|silla.*ducha|banqueta.*ducha"),
 ("Grifería y monomandos",       1.4, r"monomando|grifo|griferia|grifer[íi]a|llave.*(lavatorio|fregadero|ducha|tina)|mezclador"),
 ("Cabezales y kits de ducha",   0.7, r"cabezal.*ducha|tel[ée]fono.*ducha|rociador|regadera|columna.*ducha|kit.*ducha|juego de ducha|ducha el[ée]ctrica|flexible.*ducha"),
 ("Organizadores de ducha",      0.9, r"(organizador|repisa|estante|esquiner).*(ducha|ba[ñn]o)|(ducha|ba[ñn]o).*(organizador|repisa|estante)|jabonera|porta.*shampoo"),
 ("Dispensadores baño",          1.2, r"dispensador"),
 ("Cortinas de baño",            0.8, r"cortina.*(ba[ñn]o|ducha)|barra.*cortina"),
 ("Antideslizantes y alfombras baño",0.9,r"antideslizante.*(ducha|ba[ñn]o|tina|ba[ñn]er)|(ducha|ba[ñn]o|tina|ba[ñn]er).*antideslizante|tapete.*(ducha|ba[ñn]o)|alfombra.*ba[ñn]o|barrera de agua|pisadera"),
 ("Escobillas y limpieza WC",    0.8, r"escobilla|cepillo.*(w\.?c|inodoro|ba[ñn]o)|limpiador.*inodoro|piedra.*p[óo]mez"),
 ("Rejillas y desagües",         0.7, r"(rejilla|tap[óo]n|atrapa ?cabello).*(desag|ducha|drenaje|pluvial|anti.?olor|obstrucc)|canaleta.*(drenaje|pluvial)|desag[üu]e de |draga.*tuber"),
 ("Cestos de ropa sucia",        1.2, r"cesto.*ropa|canasto.*ropa|ropa sucia"),
 ("Toalleros y ganchos baño",    0.6, r"toaller[ao]|gancho.*(adhesiv|ba[ñn]o)|colgador.*toalla|secador.*toalla"),
 # --- COCINA ---
 ("Bolsas para sellado al vacío",0.6, r"bolsa[s]?.*(vac[íi]o|sellad)|rollo.*vac[íi]o"),
 ("Selladoras al vacío",         2.0, r"selladora|sellador.*vac[íi]o|m[áa]quina.*vac[íi]o|foodsaver"),
 ("Balanzas y grameras",         0.5, r"gramera|balanza|b[áa]scula|bascula|pesa.*(aliment|cocina|digital)"),
 ("Termos y botellas térmicas",  0.6, r"termo|t[ée]rmic[ao].*(botella|vaso)|botella.*(agua|t[ée]rmic)|thermos|sif[óo]n.*litro"),
 ("Mate y accesorios",           0.7, r"\bmate\b|matero|bombilla|yerba"),
 ("Café: molinillos y prensas",  1.6, r"molinillo|moledor|prensa francesa|french press|cafetera|portac[áa]psul|porta.*c[áa]psul|c[áa]psula"),
 ("Tazas, mugs y vasos",         1.2, r"\bmug\b|taz[óa]n|taza|vaso[s]?|copa[s]?|shopero|jarr[oa]"),
 ("Escurridores y secaplatos",   1.8, r"escurridor|secaplatos|secador.*plato|escurre"),
 ("Estantes y racks de cocina",  2.2, r"(estante|repisa|rack|organizador).*(cocina|microondas|horno|especi|refriger|despens)|extensible|retr[áa]ctil.*cocina|condimenter|especier|porta.*rollo"),
 ("Carritos organizadores",      4.5, r"carrito|carro organizador"),
 ("Dispensador lavalozas/esponja",0.5,r"dispensador.*(lavaloz|jab[óo]n)|porta.*esponja|lavaloza"),
 ("Cortadores y mandolinas",     0.8, r"mandolina|picador|rallador|cortador|rebanador|chopper|pela.*(papa|verdura)|quickchop|smasher"),
 ("Termómetros de cocina",       0.2, r"term[óo]metro"),
 ("Bolsas de basura y plásticas",1.6, r"bolsa[s]? (de )?basura|bolsa[s]? pl[áa]stic|bolsa.*camiseta|film pvc|papel film|alusa"),
 ("Repostería: moldes y papel",  0.5, r"molde|repost|capacill|tulipa|manga paster|uslero|fondant|silicona.*(horno|macarr)|papel.*(mantequilla|horno|airfryer|freidora)|base giratoria|porta.*(torta|cupcake)|candy bar"),
 ("Cuchillos y tablas",          1.4, r"cuchill|santoku|tabla.*(picar|cortar|amasar)|taco.*(cuchill|pcs)|tijera.*cocina|afilador"),
 ("Sartenes, ollas y baterías", 6.0, r"sart[ée]n|olla|bater[íi]a de cocina|cacerola|wok|plancha.*(churrasquer|parrill)|budiner|paila|fondue"),
 ("Contenedores herméticos",     0.9, r"herm[ée]tic|contenedor|t[áa]pers?|tupper|frasco|almacenamiento.*aliment"),
 ("Utensilios y bowls",          1.0, r"utensilio|bowl|pocillo|esp[áa]tula|colador|set.*(pala|cubierto)|cubierto|vajilla|bandeja|fuente"),
 ("Dispensadores de bebidas",    2.0, r"dispensador.*(bebida|jugo|agua)|botell[óo]n|bid[óo]n"),
 # --- HOGAR ---
 ("Colgadores y perchas de ropa",1.2, r"colgador.*ropa|percha|gancho.*ropa|colgadores"),
 ("Organizadores de zapatos",    1.5, r"zapater|organizador.*zapato|caja.*zapato"),
 ("Cajas y bolsas organizadoras",1.0, r"caja[s]? organiz|bolsa[s]? organiz|organizador.*(caj[óo]n|closet|ropa interior)|separador.*caj[óo]n|bolsa.*al vac[íi]o|cubre traje|divisor"),
 ("Organizadores de maquillaje", 0.7, r"maquillaje|cosmetiquer|cosm[ée]tic|neceser"),
 ("Paños y traperos húmedos",    0.6, r"trapero|pa[ñn]o h[úu]medo|trapeador h[úu]medo|t[íi]a clarita"),
 ("Paños de microfibra",         0.5, r"pa[ñn]o.*microfibra|microfibra.*pa[ñn]o|pa[ñn]o.*limpieza|pa[ñn]o.*reutilizab|toalla.*limpieza"),
 ("Mopas y trapeadores",         2.0, r"mopa|trapeador|escoba|mop\b"),
 ("Quita pelusas y pelo mascota",0.4, r"pelusa|quita ?pelo|rodillo.*(pelo|adhesiv)|roller.*pelo"),
 ("Guantes desechables",         0.8, r"guante"),
 ("Esponjas y estropajos",       0.4, r"esponja|estropajo|fibra.*limpieza|virutex"),
 ("Tendederos y planchado",      4.0, r"tendeder|secador.*ropa|tabla.*planchar|planchado|colgador.*secar"),
 ("Bolsas de lavado",            0.3, r"bolsa.*(lavar|lavadora|delicad|brasier|sost[ée]n)|funda.*lavadora"),
 ("Basureros",                   3.0, r"basurero|papelero|tacho"),
 ("Muebles",                    30.0, r"ropero|c[óo]moda|buffet|aparador|mueble|cajonera|estante.*living|perchero de pie|banco "),
 ("Productos de limpieza líquidos",1.2,r"limpiador|desinfectante|detergente|quitamancha|cloro|pink stuff|neutralizador|desengrasante"),
 # --- reglas complementarias (2da pasada) ---
 ("Balones y balance",           1.2, r"bal[óo]n.*(yoga|pilates|ejercicio|rehabilit)|pelota.*(yoga|pilates)|bosu|balance board|tabla.*equilibrio|coj[íi]n.*(sensorial|balance)|disco.*balance"),
 ("Pesas de tobillo y muñeca",   3.0, r"tobiller|pesa[s]?.*(tobillo|mu[ñn]eca)"),
 ("Trampolines fitness",         8.0, r"trampol[íi]n|cama el[áa]stica"),
 ("Ruedas abdominales",          1.0, r"rueda[s]?.*(abdominal|ejercicio)|ab wheel"),
 ("Poleas y agarres gym",        1.0, r"polea|agarre.*(gym|espalda|tr[íi]cep)|cuerda.*tr[íi]cep"),
 ("Calistenia y barras",         6.0, r"calistenia|barra.*(paralela|dominada)|squat rack|jump box|pliom[ée]tric"),
 ("Suspensión y bandas TRX",     0.8, r"suspend|trx|cinta.*entrenamiento"),
 ("Percheros y ganchos pared",   1.5, r"perchero|gancho.*(pared|puerta|ventosa|techo)|colgador.*pared"),
 ("Cestas y cajas plegables",    1.0, r"cesta|caja plegable|canasto|bandeja organiz"),
 ("Gadgets eléctricos de cocina",1.5, r"espumador|batidora|abrelatas|exprimidor|licuadora|hervidor|freidora|tostador|procesador.*aliment"),
 ("Aceiteros y dosificadores",   0.5, r"aceiter|atomizador|pulverizador|dosificador|salero|pimenter"),
 ("Tablas de picoteo y madera",  1.2, r"tabla.*(aperitivo|picoteo|madera|puzzle|queso)|bamb[úu].*tabla"),
 ("Accesorios varios de baño",   0.8, r"shower door|soporte.*(ducha|secador)|ventosa|set.*accesorios.*ba[ñn]o|alza ?ba[ñn]o"),
 ("Afiladores y cortadores",     0.6, r"afilar|piedra.*afil|cortad?[oa].*pizza|abridor"),
]

def clasificar(titulo):
    t = titulo.lower()
    for nicho, peso, pat in REGLAS:
        if re.search(pat, t):
            return nicho, peso
    return None, None

if __name__ == "__main__":
    d = json.load(open("/home/user/Prueba/datos/productos_raw.json"))
    sin = []
    for x in d:
        n, p = clasificar(x["title"])
        x["nicho"], x["peso_kg"] = n, p
        if n is None:
            sin.append(x["title"])
    json.dump(d, open("/home/user/Prueba/datos/productos.json","w"), ensure_ascii=False, indent=1)
    print(f"Clasificados: {len(d)-len(sin)}/{len(d)}  |  sin clasificar: {len(sin)}")
    for t in sin[:60]: print("  ?", t[:95])
