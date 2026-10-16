# Bot de papers científicos por WhatsApp

Bot para profesionales de la salud: le escribes por WhatsApp algo como
*"novedades del último mes en insuficiencia cardíaca"* y te responde con un resumen
en español de los artículos más relevantes de **PubMed** y de **preprints**
(medRxiv/bioRxiv), cada uno con su link verificable.

Todo funciona con planes gratuitos:

| Pieza | Servicio | Costo |
|---|---|---|
| WhatsApp | Twilio WhatsApp Sandbox | Gratis (crédito de prueba) |
| IA (entender la pregunta y resumir) | Google Gemini (AI Studio) | Gratis |
| Servidor | Render (plan free) | Gratis |
| Papers | PubMed + Europe PMC | Gratis |

## Cómo funciona

```
WhatsApp → Twilio → /whatsapp (este servidor)
                      1. Gemini convierte la pregunta en una búsqueda de PubMed
                      2. Busca en PubMed y en preprints (Europe PMC)
                      3. Gemini resume solo los artículos encontrados
                    → Twilio → WhatsApp
```

Si Gemini falla (por ejemplo, porque se agotó la cuota gratis), el bot igual responde con
la lista de artículos y sus links, sin resumen.

## Puesta en marcha (unos 30 minutos)

### 1. Clave de Gemini
1. Entra a <https://aistudio.google.com/apikey> con tu cuenta de Google.
2. Haz clic en **Create API key** y copia la clave.

### 2. Twilio WhatsApp Sandbox
1. Crea una cuenta gratis en <https://www.twilio.com/try-twilio>.
2. En la consola, copia el **Account SID** y el **Auth Token**, que están en la página de inicio.
3. Ve a **Messaging → Try it out → Send a WhatsApp message**.
4. Desde tu WhatsApp, envía el mensaje `join <código>` al número que aparece ahí (+1 415 523 8886).
   Esto conecta tu teléfono al sandbox.

### 3. Publicar el servidor en Render
1. Crea una cuenta en <https://render.com> entrando con GitHub.
2. Haz clic en **New → Blueprint** y elige este repositorio y la rama con el código.
   Render lee el archivo `render.yaml` y configura todo solo.
3. Completa las variables que te pide:
   - `GEMINI_API_KEY`: la clave del paso 1.
   - `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN`: los datos del paso 2.
   - `ALLOWED_NUMBERS`: tu número en formato `whatsapp:+56912345678`. Así nadie más puede usar tu bot.
4. Cuando termine de desplegar, copia la URL, que se ve como `https://bot-papers-salud.onrender.com`.

### 4. Conectar Twilio con tu servidor
1. En Twilio, ve a **Messaging → Try it out → Send a WhatsApp message → Sandbox settings**.
2. En **When a message comes in**, pega `https://TU-URL.onrender.com/whatsapp` y elige el método **POST**.
3. Guarda los cambios.

### 5. Probar
Escríbele al número del sandbox: *"Ensayos clínicos recientes sobre semaglutida en obesidad"*.
Si escribes `hola` o `ayuda`, te muestra ejemplos de uso.

## Limitaciones del plan gratis
- **Render se duerme** tras 15 minutos sin uso. El primer mensaje después de eso puede tardar
  alrededor de 1 minuto. Los siguientes llegan en 10 a 20 segundos.
- **El sandbox de Twilio** solo funciona con los números que enviaron `join`, y la conexión vence
  a los 3 días. Si deja de responder, vuelve a enviar `join <código>`.
- **Gemini gratis** tiene un límite de consultas por minuto y por día. Además, Google puede usar
  lo que envías en el plan gratis para mejorar sus modelos: **no envíes datos de pacientes**.
- El bot resume **abstracts**, no los artículos completos. Es una herramienta de actualización,
  no de decisión clínica.

## Probar en tu computador (opcional)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY=tu_clave
python -m app.cli "novedades en dengue grave"   # responde en la terminal, sin WhatsApp
pip install pytest && pytest                     # tests
```

## Estructura
- `app/main.py`: el webhook que recibe los mensajes de Twilio y envía las respuestas.
- `app/bot.py`: interpreta la pregunta, busca los artículos, arma el resumen y lo corta en mensajes.
- `app/search.py`: las búsquedas en PubMed (E-utilities) y Europe PMC (preprints).
- `app/llm.py`: el cliente mínimo de la API de Gemini. El modelo se cambia con `GEMINI_MODEL`.
