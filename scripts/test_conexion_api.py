"""
Test rápido: ¿responde la API?
Uso: python scripts/test_conexion_api.py [URL]
Por defecto prueba https://vinoproia.com/api/status
Para local: python scripts/test_conexion_api.py http://127.0.0.1:8001/api/status
"""
import sys
import urllib.request

URL = (sys.argv[1] if len(sys.argv) > 1 else "https://vinoproia.com/api/status").strip()
if not URL.startswith("http"):
    URL = "https://vinoproia.com/api/status"

try:
    req = urllib.request.Request(URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        code = r.getcode()
        body = r.read().decode()[:200]
    print(f"OK {code} - La API responde: {URL}")
    if body:
        print(f"   Respuesta: {body[:150]}...")
except Exception as e:
    print(f"FALLO - No se pudo conectar a {URL}")
    print(f"   Error: {e}")
    sys.exit(1)
