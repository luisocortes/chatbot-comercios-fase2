from pathlib import Path
from app.engine import FAQEngine

def test_model_exists():
    assert (Path(__file__).resolve().parent.parent/'models'/'faq_model.joblib').is_file()

def test_model_count_and_version():
    e=FAQEngine()
    assert e.count == 12
    assert e.version == '1.0.0'

def test_model_retrieval():
    e=FAQEngine()
    assert e.answer('¿Cómo respondo a una disputa de pago?')['tema'] == 'contracargos'

def test_model_no_payment_action():
    e=FAQEngine()
    assert 'no' in e.answer('Sospecho un fraude en mi comercio')['respuesta'].lower()
