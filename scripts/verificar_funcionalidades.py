"""
Verificación de funcionalidades antes de subir la app.
Ejecutar con el servidor corriendo en http://127.0.0.1:8001
  cd backend_optimized && python scripts/verificar_funcionalidades.py
"""
import sys
import uuid

try:
    import requests
except ImportError:
    print("Instala requests: pip install requests")
    sys.exit(1)

BASE = "http://127.0.0.1:8001"
SESSION_ID = str(uuid.uuid4())
OK = 0
FAIL = 0
SKIP = 0


def req(method, path, expected_status=200, timeout_get=10, timeout_post=15, **kwargs):
    global OK, FAIL, SKIP
    url = BASE + path
    timeout = kwargs.pop("timeout", timeout_get if method == "GET" else timeout_post)
    try:
        if method == "GET":
            r = requests.get(url, timeout=timeout, **kwargs)
        else:
            r = requests.post(url, timeout=timeout, **kwargs)
        expected = (expected_status,) if isinstance(expected_status, int) else expected_status
        if r.status_code in expected:
            OK += 1
            return True, r
        FAIL += 1
        print(f"  [FALLO] {method} {path} -> {r.status_code} (esperado {expected_status})")
        return False, r
    except requests.exceptions.ConnectionError:
        SKIP += 1
        print(f"  [SKIP] {method} {path} - servidor no alcanzable")
        return False, None
    except Exception as e:
        FAIL += 1
        print(f"  [FALLO] {method} {path} -> {e}")
        return False, None


def main():
    print("=" * 60)
    print("VINO PRO IA - Verificación de funcionalidades")
    print("=" * 60)
    print(f"Base URL: {BASE}")
    print(f"Session-ID de prueba: {SESSION_ID[:8]}...")
    print()

    headers_json = {"Accept": "application/json", "X-Session-ID": SESSION_ID}
    headers_form = {"X-Session-ID": SESSION_ID}

    # --- Páginas HTML ---
    print("[1] Páginas principales (GET HTML)")
    for path, name in [
        ("/", "Inicio"),
        ("/escanear", "Escanear"),
        ("/registrar", "Registrar"),
        ("/preguntar", "Preguntar"),
        ("/bodega", "Mi Bodega"),
        ("/dashboard", "Dashboard"),
        ("/planes", "Planes"),
        ("/adaptador", "Adaptador"),
        ("/oferta/crear", "Oferta crear"),
        ("/mis-ofertas", "Mis ofertas"),
        ("/set-lang?lang=es", "Set lang (redirect)"),
    ]:
        exp = (200, 302) if path == "/set-lang?lang=es" else 200
        ok, r = req("GET", path, expected_status=exp)
        if ok and r and path != "/set-lang?lang=es" and "html" not in r.headers.get("Content-Type", "").lower():
            if r.headers.get("Content-Type", "").startswith("text/html"):
                pass
            else:
                print(f"  [AVISO] {path} Content-Type: {r.headers.get('Content-Type')}")
    print()

    # --- API status ---
    print("[2] API status y datos")
    req("GET", "/api/status")
    req("GET", "/paises")
    req("GET", "/vinos")
    print()

    # --- Búsqueda ---
    print("[3] Búsqueda (buscar-para-registrar puede tardar si llama a API externa)")
    req("GET", "/api/buscar-para-registrar?q=rioja", timeout=25, **{"headers": headers_json})
    req("GET", "/buscar?q=rioja")
    print()

    # --- Check limit / freemium ---
    print("[4] Planes y límite (check-limit)")
    req("GET", "/api/check-limit", **{"headers": headers_json})
    print()

    # --- Bodega (requiere X-Session-ID) ---
    print("[5] Bodega (lista, registros-hoy)")
    req("GET", "/api/bodega", **{"headers": headers_json})
    req("GET", "/api/bodega/registros-hoy", **{"headers": headers_json})
    print()

    # --- Escaneo por texto ---
    print("[6] Escaneo por texto (POST analyze/text)")
    req("POST", "/analyze/text", data={"texto": "Rioja reserva"}, **{"headers": headers_form})
    print()

    # --- Sumiller (Nube) ---
    print("[7] Preguntar sumiller (Nube)")
    req("GET", "/preguntar-sumiller?texto=Que+vino+con+carne&perfil=aficionado", **{"headers": headers_json})
    print()

    # --- IA Local solo Premium: sin session 401, con session no PRO 403 ---
    print("[8] IA Local solo Premium (401 sin header, 403 no PRO)")
    req("POST", "/api/preguntar-local", expected_status=401,
       json={"consulta_id": "fake-uuid", "pregunta": "test"}, headers={"Content-Type": "application/json"})
    req("POST", "/api/preguntar-local", expected_status=403,
       json={"consulta_id": "fake-uuid", "pregunta": "test"},
       headers={"Content-Type": "application/json", "X-Session-ID": SESSION_ID})
    print()

    # --- Comprar (página y API enlaces) ---
    print("[9] Comprar (página vino + enlaces)")
    req("GET", "/vino/espana_rioja_1/comprar")
    req("GET", "/api/vino/espana_rioja_1/enlaces", **{"headers": headers_json})
    print()

    # --- Ofertas ---
    print("[10] Ofertas (listar por vino, mis-ofertas)")
    req("GET", "/api/ofertas?vino_key=test")
    req("GET", "/api/ofertas/mis-ofertas", **{"headers": headers_json})
    print()

    # --- Historial escaneos ---
    print("[11] Historial escaneos")
    req("GET", "/historial-escaneos", **{"headers": headers_json})
    print()

    # --- Analytics ---
    print("[12] Analytics")
    req("GET", "/analytics/dashboard", **{"headers": headers_json})
    req("GET", "/analytics/tendencias?dias=7", **{"headers": headers_json})
    print()

    # --- Informes (bodega PDF requiere session) ---
    print("[13] Informes (bodega PDF)")
    req("GET", "/informes/bodega", expected_status=200, **{"headers": headers_json})
    print()

    # --- Adaptador (token) ---
    print("[14] Adaptador (token)")
    req("GET", "/api/adaptador/token", **{"headers": {"Accept": "application/json"}})
    print()

    # --- Resumen ---
    print("=" * 60)
    print(f"OK: {OK}  |  FALLOS: {FAIL}  |  Omitidos (sin servidor): {SKIP}")
    print("=" * 60)
    if FAIL > 0:
        print("Revisa los [FALLO] antes de subir.")
        sys.exit(1)
    if SKIP == OK + FAIL + SKIP and SKIP > 0:
        print("Servidor no estaba en marcha. Arranca: python -m uvicorn app:app --host 127.0.0.1 --port 8001")
        sys.exit(2)
    print("Verificación completada. Listo para subir.")
    sys.exit(0)


if __name__ == "__main__":
    main()
