"""API y frontend de demostración para soporte a comercios de adquirencia."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from app.engine import FAQEngine

app = FastAPI(
    title="API de soporte a comercios", version="1.0.0",
    description="Demostración académica: no consulta saldos ni ejecuta operaciones bancarias.",
)
engine = FAQEngine()
STATIC = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")

class ChatRequest(BaseModel):
    mensaje: str = Field(min_length=2, max_length=500)

    @field_validator("mensaje")
    @classmethod
    def non_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("La consulta debe contener al menos dos caracteres")
        return cleaned

class ChatResponse(BaseModel):
    respuesta: str
    tema: str | None
    confianza: float
    accion: str
    fuente: str | None
    aviso: str = "Demostración académica; no introduce ni comparte datos bancarios o personales."

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC / "index.html")

@app.get("/api/health")
def health():
    return {"estado": "ok", "modelo": "tfidf_faq", "version": engine.version, "temas": engine.count}

@app.get("/api/temas")
def topics():
    return [{"id": item["id"], "tema": item["tema"], "titulo": item["titulo"]} for item in engine.entries]

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    return ChatResponse(**engine.answer(payload.mensaje))
