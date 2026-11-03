"""Entrena y versiona un vectorizador TF-IDF con ejemplos ficticios aprobados."""
import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent.parent
entries = json.loads((ROOT / "data" / "faq_comercios.json").read_text(encoding="utf-8"))
examples = [(i, question) for i, entry in enumerate(entries) for question in entry["preguntas"]]
vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), strip_accents="unicode", lowercase=True)
matrix = vectorizer.fit_transform([q for _, q in examples])
artifact = {"version": "1.0.0", "vectorizer": vectorizer, "matrix": matrix, "entries": entries, "examples": [i for i, _ in examples]}
output = ROOT / "models" / "faq_model.joblib"
output.parent.mkdir(exist_ok=True)
joblib.dump(artifact, output, compress=3)
print(f"Modelo guardado: {output} | temas={len(entries)}, ejemplos={len(examples)}")
