"""Prueba de humo contra el servidor real (no requiere pytest)."""
import json
import os
import urllib.request

BASE = os.getenv('BASE_URL', 'http://127.0.0.1:8000')

def call(path, payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=data, headers={'Content-Type': 'application/json'} if data else {})
    with urllib.request.urlopen(req, timeout=6) as response:
        return response.status, response.read().decode('utf-8')

for name, path, payload in [
    ('salud', '/api/health', None),
    ('frontend', '/', None),
    ('temas', '/api/temas', None),
    ('chat_liquidacion', '/api/chat', {'mensaje': '¿Cuándo se deposita el dinero de mis ventas con terminal?'}),
    ('chat_escalamiento', '/api/chat', {'mensaje': 'Cuál es la temperatura de Marte mañana'}),
]:
    status, body = call(path, payload)
    record = {'prueba': name, 'status_http': status, 'resultado': 'OK' if status == 200 else 'ERROR'}
    if path.startswith('/api'):
        record['datos'] = json.loads(body)
    print(json.dumps(record, ensure_ascii=False))
    assert status == 200
