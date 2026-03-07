"""
Reproduce el flujo completo de /preguntar-sumiller para "hoy toca comida japonesa"
y detectar en qué línea falla. Ejecutar: python scripts/test_sumiller_flow.py
"""
import sys
from pathlib import Path

# Raíz del proyecto
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Cargar vinos como en app (sin arrancar FastAPI)
import json
import os
DATA_FOLDER = str(ROOT / "data")
excluir = {
    'analytics.json', 'bodegas.json', 'conocimiento_vinos.json',
    'enlaces_compra.json', 'restaurantes.json', 'registros_diarios.json',
    'usuarios_reputacion.json', 'usuarios_pro.json', 'ofertas.json',
    'valoraciones.json', 'wishlist.json', 'historial_usuario.json',
    'notificaciones_landing.json',
    'usuarios_perfiles.json', 'seguidores.json', 'actividad.json', 'notificaciones.json',
    'contactos_qr.json', 'lugares_destacados.json', 'chat_mensajes.json',
    'patrocinadores.json',
}
vinos = {}
for f in Path(DATA_FOLDER).glob("*.json"):
    if f.name in excluir:
        continue
    try:
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            if isinstance(data, dict):
                vinos.update(data)
    except Exception as e:
        print(f"[WARN] {f.name}: {e}")

# Comprobar entradas no-dict (causa del error en producción si algún JSON no es catálogo)
non_dict = [(k, type(v).__name__) for k, v in vinos.items() if not isinstance(v, dict)]
if non_dict:
    print(f"[!] Entradas que NO son dict (pueden romper experto en vinos): {non_dict[:10]}")

print(f"[OK] Vinos cargados: {len(vinos)}")

# Simular request con app.state (necesita scope["app"] con .state)
from starlette.requests import Request

class FakeApp:
    class State:
        pass
    state = State()

app_fake = FakeApp()
app_fake.state.vinos_mundiales = vinos
app_fake.state.historial_sumiller = {}
app_fake.state.consultas_escaneo = {}

# Scope ASGI es un dict, no se instancia con Scope(...)
scope = {"type": "http", "method": "GET", "path": "/preguntar-sumiller", "headers": []}
scope["app"] = app_fake
request = Request(scope)

# Parámetros de la petición
texto = "hoy toca comida japonesa que vino pongo ?"
perfil = "aficionado"
x_session_id = "test-session-123"

# Llamar a la lógica del experto en vinos (igual que el endpoint)
from routes.sumiller import _get_vinos, _preguntar_sumiller_general

vinos_dict = _get_vinos(request)
if not isinstance(vinos_dict, dict):
    vinos_dict = {}
texto_clean = (texto or "").strip()

print("[1] Llamando _preguntar_sumiller_general (experto en vinos)...")
try:
    out = _preguntar_sumiller_general(request, vinos_dict, texto_clean, perfil, x_session_id)
    print("[OK] Respuesta:", out.get("respuesta", "")[:150] + "...")
    print("[OK] vinos_recomendados:", len(out.get("vinos_recomendados", [])))
except Exception as e:
    import traceback
    print("[ERROR]", type(e).__name__, str(e))
    traceback.print_exc()
    sys.exit(1)

print("Done.")
