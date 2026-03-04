#!/usr/bin/env python3
"""
Revisión automática de las acciones de la app Vino Pro IA.
Hace peticiones HTTP a http://127.0.0.1:8001 y muestra OK/FAIL por cada ítem.
Ejecutar con el servidor arrancado: uvicorn app:app --host 127.0.0.1 --port 8001
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    import httpx
except ImportError:
    print("Instala httpx: pip install httpx")
    sys.exit(1)

BASE = "http://127.0.0.1:8001"
SESSION_ID = "revision-test-session"
HEADERS = {"X-Session-ID": SESSION_ID}


def ok(name: str, res: httpx.Response, allow_redirect=False) -> bool:
    if res.status_code == 200 or (allow_redirect and res.status_code in (302, 303)):
        print(f"  OK   {name}")
        return True
    print(f"  FAIL {name} (status={res.status_code})")
    return False


def main():
    print("Revision de la app Vino Pro IA")
    print("Base URL:", BASE)
    print("-" * 50)
    client = httpx.Client(follow_redirects=True, timeout=10.0)
    fallos = 0

    # 1. Paginas principales
    print("\n1. Paginas principales (GET)")
    rutas = [
        ("/", "Inicio"),
        ("/escanear", "Escanear"),
        ("/registrar", "Registrar vino"),
        ("/preguntar", "Preguntar (sumiller)"),
        ("/bodega", "Mi Bodega"),
        ("/planes", "Planes"),
        ("/vino/vega_sicilia_unico/comprar", "Comprar (ejemplo)"),
        ("/dashboard", "Dashboard"),
        ("/pago-exitoso", "Pago exitoso"),
        ("/pago-cancelado", "Pago cancelado"),
        ("/adaptador", "Adaptador"),
    ]
    for ruta, nombre in rutas:
        try:
            r = client.get(BASE + ruta, headers=HEADERS)
            if not ok(nombre + " " + ruta, r):
                fallos += 1
        except Exception as e:
            print(f"  FAIL {nombre} {ruta}: {e}")
            fallos += 1

    # 2. Escaneo - historial
    print("\n2. Escaneo")
    try:
        r = client.get(BASE + "/historial-escaneos", headers=HEADERS)
        if not ok("Historial escaneos", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL Historial escaneos: {e}")
        fallos += 1

    # 3. Sumiller (parametro es "texto", no "pregunta")
    print("\n3. Sumiller")
    try:
        r = client.get(
            BASE + "/preguntar-sumiller",
            params={"texto": "Que vino va bien con carne?"},
            headers=HEADERS,
        )
        if not ok("Preguntar sumiller (recomendacion)", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL Preguntar sumiller: {e}")
        fallos += 1

    # 4. Bodega API
    print("\n4. Bodega (API)")
    try:
        r = client.get(BASE + "/api/bodega", headers=HEADERS)
        if not ok("GET /api/bodega", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL GET /api/bodega: {e}")
        fallos += 1
    try:
        r = client.get(BASE + "/api/bodega/registros-hoy", headers=HEADERS)
        if not ok("GET registros-hoy", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL registros-hoy: {e}")
        fallos += 1
    try:
        r = client.get(BASE + "/api/bodega/valoracion", headers=HEADERS)
        if not ok("GET valoracion", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL valoracion: {e}")
        fallos += 1
    try:
        r = client.get(BASE + "/api/bodega/alertas", headers=HEADERS)
        if not ok("GET alertas", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL alertas: {e}")
        fallos += 1

    # 5. Comprar y guias
    print("\n5. Comprar y guias por pais")
    for pais, label in [("ES", "ES"), ("IT", "IT")]:
        try:
            r = client.get(BASE + f"/vino/vega_sicilia_unico/comprar?pais={pais}", headers=HEADERS)
            if not ok(f"Comprar ?pais={pais}", r):
                fallos += 1
        except Exception as e:
            print(f"  FAIL Comprar ?pais={pais}: {e}")
            fallos += 1
    try:
        r = client.get(BASE + "/api/vino/vega_sicilia_unico/enlaces", headers=HEADERS)
        if not ok("API enlaces vino", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL API enlaces: {e}")
        fallos += 1

    # 6. Planes
    print("\n6. Planes")
    try:
        r = client.get(BASE + "/api/check-limit", headers=HEADERS)
        if not ok("GET check-limit", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL check-limit: {e}")
        fallos += 1

    # 7. Pagos - crear sesion (200=OK, 402/500/503=Stripe no configurado o no disponible)
    print("\n7. Pagos")
    try:
        r = client.post(BASE + "/crear-checkout-session", headers=HEADERS)
        if r.status_code == 200:
            print("  OK   POST crear-checkout-session (Stripe configurado)")
        elif r.status_code in (402, 500, 503):
            print("  OK   POST crear-checkout-session (Stripe no configurado o no disponible)")
        else:
            print(f"  FAIL POST crear-checkout-session (status={r.status_code})")
            fallos += 1
    except Exception as e:
        print(f"  FAIL crear-checkout-session: {e}")
        fallos += 1

    # 8. Adaptador
    print("\n8. Adaptador")
    try:
        r = client.get(BASE + "/api/adaptador/token", headers=HEADERS)
        if not ok("GET adaptador token", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL adaptador token: {e}")
        fallos += 1

    # 9. Analytics
    print("\n9. Analytics")
    try:
        r = client.get(BASE + "/analytics/dashboard", params={"dias": 30}, headers=HEADERS)
        if not ok("GET analytics/dashboard", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL analytics/dashboard: {e}")
        fallos += 1

    # 10. API auxiliares
    print("\n10. API auxiliares")
    try:
        r = client.get(BASE + "/api/status", headers=HEADERS)
        if not ok("GET /api/status", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL /api/status: {e}")
        fallos += 1
    try:
        r = client.get(BASE + "/buscar", params={"q": "rioja"}, headers=HEADERS)
        if not ok("GET /buscar?q=rioja", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL /buscar: {e}")
        fallos += 1
    try:
        r = client.get(BASE + "/paises", headers=HEADERS)
        if not ok("GET /paises", r):
            fallos += 1
    except Exception as e:
        print(f"  FAIL /paises: {e}")
        fallos += 1

    print("-" * 50)
    if fallos == 0:
        print("Resultado: TODO OK. Revisa en el navegador los flujos que uses (escaneo con imagen, sumiller con contexto, etc.).")
    else:
        print(f"Resultado: {fallos} fallo(s). Comprueba que el servidor esta en marcha (uvicorn app:app --host 127.0.0.1 --port 8001).")
    return 0 if fallos == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
