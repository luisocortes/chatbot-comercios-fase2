"""Motor de recuperación basado en TF-IDF; no es un modelo generativo."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import joblib
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = BASE_DIR / "models" / "faq_model.joblib"
DEFAULT_DATA = BASE_DIR / "data" / "faq_comercios.json"

# Precaución: los artefactos joblib deben provenir solo de fuentes de confianza.
class FAQEngine:
    def __init__(self, model_path: Path | None = None):
        path = Path(model_path or os.getenv("MODEL_PATH", str(DEFAULT_MODEL)))
        artifact = joblib.load(path)
        self.vectorizer = artifact["vectorizer"]
        self.matrix = artifact["matrix"]
        self.entries = artifact["entries"]
        self.examples = artifact["examples"]
        self.version = artifact["version"]
        self.minimum_score = float(os.getenv("CONFIDENCE_THRESHOLD", "0.24"))

    @property
    def count(self):
        return len(self.entries)

    @staticmethod
    def _sensitive(text: str) -> bool:
        # Detectores conservadores, no sustituyen DLP empresarial.
        normalized = re.sub(r"[\s-]+", "", text)
        return bool(
            re.search(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", text)
            or re.search(r"(?<!\d)\d{13,19}(?!\d)", normalized)
            or re.search(r"\b(?:contrase(?:ñ|n)a|password|nip|otp|cvv|clabe)\s*[:=]\s*\S+", text, re.I)
        )

    def answer(self, message: str) -> dict:
        message = message.strip()
        if self._sensitive(message):
            return {
                "respuesta": "Por seguridad, no compartas números de tarjeta, cuentas, correos personales, contraseñas ni códigos. Utiliza el canal autenticado del adquirente para revisar tu caso.",
                "tema": None, "confianza": 0.0, "accion": "escalar", "fuente": None,
            }
        if re.search(r"\b(ignora (todas? )?las? instrucciones|revela (el )?prompt|system prompt|modo desarrollador)\b", message, re.I):
            return {
                "respuesta": "Solo puedo orientar sobre consultas operativas generales de comercios. Para otros asuntos, contacta al personal de soporte.",
                "tema": None, "confianza": 0.0, "accion": "escalar", "fuente": None,
            }
        transformed = self.vectorizer.transform([message])
        scores = cosine_similarity(transformed, self.matrix)[0]
        best_index = int(scores.argmax())
        similarity = float(scores[best_index])
        if similarity < self.minimum_score:
            return {
                "respuesta": "No encontré una respuesta suficientemente confiable para esa consulta. Te recomiendo abrir un ticket desde el portal oficial de comercios.",
                "tema": None, "confianza": round(similarity, 3), "accion": "escalar", "fuente": None,
            }
        item = self.entries[self.examples[best_index]]
        return {
            "respuesta": item["respuesta"], "tema": item["tema"],
            "confianza": round(similarity, 3), "accion": "responder", "fuente": item["fuente"],
        }
