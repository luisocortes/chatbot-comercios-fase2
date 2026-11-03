# Comercio Asiste — Proyecto Fase II

**Prototipo académico para atención a comercios de un adquirente bancario.** Incluye frontend HTML/CSS/JS, API FastAPI, motor de recuperación TF-IDF, Dockerfile, pruebas y manual de despliegue. Es la implementación mínima viable del caso financiero definido en Fase I.

> **Alcance real:** el motor recupera respuestas de una base de conocimiento **ficticia**; no es un LLM ni usa generación de texto. La arquitectura RAG generativa, las conexiones al CRM, autenticación y tickets reales se proponen para una fase posterior. No se deben introducir datos reales de clientes o tarjetas. No usar como servicio bancario de producción.

## Arquitectura

```text
[Navegador: HTML / JS]
        |
        | POST /api/chat (JSON)
        v
[FastAPI + validación Pydantic]
        |
        v
[Protección básica datos sensibles]
        |
        v
[TF-IDF / similitud coseno]
        |
   +----+-----------------------+
   |                            |
[Coincidencia >= umbral]   [Baja confianza / datos sensibles]
   |                            |
[FAQ aprobada + fuente]      [Mensaje de escalamiento]
   +-------------+--------------+
                 |
           [Respuesta JSON]
```

## Inicio rápido sin Docker

Requiere Python 3.12+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/train_model.py
python -m pytest -q
uvicorn app.main:app --reload --port 8000
```

Abre http://localhost:8000. API interactiva en http://localhost:8000/docs y salud en http://localhost:8000/api/health.

## Ejecución con Docker

Requiere Docker Desktop o Docker Engine en ejecución.

```bash
docker build -t chatbot-comercios-fase2:1.0 .
docker run --rm --name chatbot-comercios -p 8000:8000 chatbot-comercios-fase2:1.0
```

Alternativa:

```bash
docker compose up --build
```

Comprobación de salud (en otra terminal):

```bash
curl http://localhost:8000/api/health
python scripts/smokecheck.py
```

**Nota de evidencia:** las pruebas Python y la comunicación HTTP se validaron al generar la entrega. La construcción/ejecución real del contenedor Docker debe verificarse en un equipo con Docker (no disponible en el entorno de preparación).

## Endpoints

| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Interfaz web |
| GET | `/api/health` | Estado del modelo, versión y temas |
| GET | `/api/temas` | Catálogo de temas de soporte |
| POST | `/api/chat` | Respuesta o escalamiento |

Ejemplo de petición:

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"mensaje":"Mi terminal punto de venta no tiene internet"}'
```

Respuesta ilustrativa: `{"respuesta":"...","tema":"terminal","confianza":1.0,"accion":"responder","fuente":"...","aviso":"..."}`.

## Estructura del repositorio

```text
app/               API y frontend
  main.py           Endpoints / Pydantic
  engine.py         TF-IDF + controles + escalamiento
  static/           Interfaz HTML/CSS/JavaScript
data/              FAQs ficticias
models/            Modelo entrenado y versionado
scripts/           Entrenamiento y smoke test
tests/             Pruebas automatizadas
docs/              Manual, arquitectura, validación
evidencias/        Logs y respuestas HTTP observadas
.github/workflows/ CI para pruebas con GitHub Actions
Dockerfile         Contenedor Docker
compose.yaml       Ejecución sencilla de la aplicación
```

## Resguardo y limitaciones

- No existe conexión con infraestructura, cuentas o datos bancarios reales.
- Nunca enviar números de tarjetas, CLABE, contraseñas, OTP ni correos personales a esta demo.
- Se implementaron detectores básicos de información sensible, pero **no** un sistema DLP empresarial.
- El umbral de confianza es configurable con `CONFIDENCE_THRESHOLD` (predeterminado 0.24). Los puntajes TF-IDF **no** representan probabilidades calibradas.
- No almacena conversaciones en una base de datos; el servidor web puede mantener registros mínimos de solicitudes. Deben revisarse los logs del proveedor antes de exponer un servicio.
- El sitio no incluye autenticación, rate limiting ni controles perimetrales; desplegar únicamente con datos ficticios y para revisión académica.
- Para convertirse en un chatbot generativo RAG productivo se requerirían LLM, recuperación documental, monitoreo, pruebas de seguridad y gobierno con revisión legal.

Manual ampliado: [docs/Manual_despliegue.md](docs/Manual_despliegue.md). Resultados observados: [docs/Validacion_y_pruebas.md](docs/Validacion_y_pruebas.md).
