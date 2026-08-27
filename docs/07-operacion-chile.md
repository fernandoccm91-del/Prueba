# Operación en Chile

Lo aburrido que hace la diferencia entre una tienda y un problema con el SII.

## Constitución y tributación

| Paso | Dónde | Costo | Plazo |
|---|---|---|---|
| Constituir SpA | `empresaenundia.cl` | Gratis | 1 día |
| Iniciación de actividades | SII online | Gratis | Inmediato |
| Giro | Código 4791 — venta al por menor por internet | — | — |
| Verificación de domicilio | SII | Gratis | 1–3 semanas |
| Timbraje / habilitación DTE | SII online | Gratis | 1 día |
| Contador | Externo | $80–150.000/mes | — |

**¿SpA o persona natural?** Con importación, SpA sin dudarlo. Necesitas RUT de empresa
para el crédito fiscal del IVA de importación, y sin eso el 19% de la importación pasa
de ser un crédito recuperable a ser costo puro. Eso solo se come casi todo tu margen.

**Régimen tributario:** Pro Pyme Transparente (14 D N°8) si facturas bajo 75.000 UF.
Es el más simple y el que tu contador va a recomendar igual.

## Documentos tributarios electrónicos

Shopify **no emite boletas ni facturas chilenas**. Es el punto ciego más común de
quien monta Shopify en Chile.

Opciones:
- **Bsale** — la integración más usada con Shopify en Chile. ~$15.000/mes
- **Nubox** — más orientada a contabilidad completa
- **ERPSync / Facturación electrónica** — apps del Shopify App Store

Configura la emisión automática de boleta al confirmarse el pago, y factura cuando el
cliente ingresa RUT y giro en el checkout.

## Medios de pago

| Pasarela | Comisión | Notas |
|---|---|---|
| **Webpay Plus** (Transbank) | 1,49–2,5% MDR + cargo fijo en UF (0,001915 UF crédito / 0,001784 UF débito) | El estándar. **Imprescindible.** App oficial en Shopify |
| **Mercado Pago** | Desde 1,49% con liberación a 14 días | Cuotas sin interés. Clave para tickets sobre $50.000 |
| **Flow** | ~2,89–3,19% + IVA | Alternativa, agrega Khipu y transferencia |
| **Klap / Etpay** | Variable | Transferencia bancaria directa, comisión baja |

**Más la tarifa por transacción de Shopify:** 2,0% en Basic, 1,0% en Shopify, 0,5% en
Advanced. Aplica porque **Shopify Payments no opera en Chile** y estás usando una
pasarela externa. Súmalo siempre a tu cálculo: es el costo escondido más grande de
vender con Shopify acá.

**Recomendación:** Webpay + Mercado Pago desde el día 1. Agrega transferencia con
Khipu cuando el volumen justifique administrar las conciliaciones a mano.

## Importación desde China

### Umbrales que definen todo

| Valor FOB | Régimen | ¿Agente de aduanas? |
|---|---|---|
| Hasta USD 1.000 | Courier / despacho simplificado | No |
| Hasta USD 3.000 (courier) | Despacho simplificado | No |
| Sobre USD 3.000 | Importación general | **Sí, obligatorio** |

El pedido de lanzamiento del plan son **USD 1.540 FOB** — deliberadamente bajo el
umbral de USD 3.000 para no necesitar agente en la primera operación.

### Tributos

- **Arancel: 6% sobre valor CIF**, pero **0% con TLC Chile–China** (vigente desde
  2006). Para acceder, tu proveedor tiene que emitir el **Certificado de Origen
  Formulario F**. Pídelo por escrito antes de pagar; muchos proveedores lo emiten
  gratis pero solo si se lo pides.
- **IVA: 19% sobre (CIF + arancel)**. Recuperable como crédito fiscal si eres
  contribuyente de IVA. Es desembolso de caja, no costo.

### Vistos buenos

Los accesorios de baño en general **no requieren** visto bueno. Cuidado con:
- **SEC** — cualquier cosa con enchufe (espejos LED, toalleros eléctricos, secadores
  de manos). Certificación obligatoria y cara. **Motivo suficiente para no incluirlos
  en el catálogo inicial.**
- **ISP** — si algún día vendes cosmética o jabón.

Confirma la partida arancelaria de cada SKU antes de comprar. Tu freight forwarder
te la puede indicar.

### Flete

| Modalidad | Costo aprox. | Tiempo | Cuándo usarla |
|---|---|---|---|
| Marítimo LCL consolidado | USD 1,50–2,50/kg | 40–55 días | Pedidos de reposición |
| Aéreo consolidado | ~USD 7/kg | 12–18 días | Pedido de prueba y urgencias |
| DHL/FedEx puerta a puerta | USD 20–35/kg efectivo | 5–8 días | Solo muestras |

**Ojo con el peso volumétrico.** Una alfombra de diatomea de 2 kg puede facturar como
4 kg por volumen. Pide siempre las medidas de la caja máster al proveedor y calcula
`(largo × ancho × alto en cm) / 5000` para el aéreo.

### Proveedores

- **Alibaba** con filtro *Verified Supplier* + *Trade Assurance*. Nunca pagues por
  fuera de la plataforma en el primer pedido.
- **1688.com** — más barato que Alibaba (es el mercado interno chino) pero necesitas
  agente. Diferencia de precio del 20–40%.
- **Agente de compras en China** — cobra 3–5% y te ahorra errores caros: inspecciona,
  consolida y negocia. Para tu primer pedido vale cada peso.

**Regla que no se rompe: muestra física antes de cada pedido.** Sin excepciones. En
diatomea y cerámica la diferencia entre proveedores es abismal y las fotos de Alibaba
mienten sistemáticamente.

## Logística nacional

| Courier | Cobertura | Nota |
|---|---|---|
| **Starken** | Nacional, muy fuerte en regiones | El más barato para regiones |
| **Blue Express** | Nacional, fuerte en RM | Mejor experiencia de seguimiento |
| **Chilexpress** | Nacional | Caro pero confiable |
| **Correos de Chile** | Nacional, llega a todos lados | Lento |

Agrega **Shipit** o **Envíame** a Shopify: cotizan entre couriers, imprimen etiquetas
y consolidan el seguimiento. Se pagan solos apenas superas los 20 pedidos al mes.

**Sobre la bodega:** los primeros meses, tu casa. 320 unidades ocupan aproximadamente
3 m³. Cuando pases los 100 pedidos mensuales, evalúa un operador de fulfillment.

## Obligaciones legales de e-commerce

| Obligación | Detalle |
|---|---|
| **Derecho a retracto** | 10 días corridos desde la recepción para compras a distancia, sin expresión de causa. Ley 19.496, art. 3 bis. Tu política de 30 días lo supera y eso es un argumento de venta |
| **Botón de arrepentimiento** | Obligatorio y visible. Ley 21.398 ("Pro Consumidor"). Ponlo en el pie |
| **Precio final visible** | El precio mostrado debe incluir IVA. Nada de sorpresas en el checkout |
| **Datos de la empresa** | Razón social, RUT y dirección en el pie del sitio |
| **Stock real** | Vender lo que no tienes es publicidad engañosa ante el SERNAC |
| **Términos y condiciones** | Publicados y aceptados en el checkout |
| **Ley 21.719 (datos personales)** | Vigente desde diciembre de 2026. Necesitas política de privacidad, consentimiento explícito para marketing y un mecanismo para que el usuario ejerza sus derechos. Configúralo desde el inicio: adaptarlo después es más caro |

## Calendario comercial chileno

| Fecha | Relevancia para tu nicho |
|---|---|
| **CyberDay** (mayo) | Alta. Requiere inscripción en la CCS con anticipación |
| **CyberMonday** (octubre) | Alta. El evento más grande del e-commerce chileno |
| **Black Friday** (noviembre) | Media-alta, creciendo cada año |
| **Navidad** (diciembre) | Alta — los sets son regalo natural |
| **Marzo** | **Tu mejor mes.** Vuelta a clases, mudanzas y arriendos nuevos. La gente que se cambia de casa equipa el baño |
| **Septiembre** | Baja. Todo el país está en otra cosa |
| **Enero–febrero** | Baja. Vacaciones |

Planifica el pedido de reposición para que llegue **en febrero**, listo para marzo.
Con 45 días de tránsito marítimo, eso significa poner la orden en diciembre.
