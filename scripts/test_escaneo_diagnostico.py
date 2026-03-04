"""
Diagnóstico rápido: conexión API + búsqueda por texto (sin imagen).
Comprueba si el backend responde y si encuentra un vino conocido en la BD.

Uso:
  cd backend_optimized
  python scripts/test_escaneo_diagnostico.py
  python scripts/test_escaneo_diagnostico.py http://192.168.0.12:8001
  python scripts/test_escaneo_diagnostico.py http://192.168.0.12:8001 "Viña Pedrosa Crianza"
"""
import json
import sys
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001").rstrip("/")
TEXTO_PRUEBA = sys.argv[2] if len(sys.argv) > 2 else "Viña Pedrosa Crianza 2021 Bodegas Pérez Pascuas"

def main():
    print("=== Diagnóstico escaneo VINO PRO ===\n")
    print(f"Base URL: {BASE}")
    print(f"Texto de prueba: {TEXTO_PRUEBA}\n")

    # 1. ¿Responde la API?
    try:
        req = urllib.request.Request(f"{BASE}/api/status", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"[OK] API responde: GET /api/status -> {r.getcode()}")
    except Exception as e:
        print(f"[FALLO] No se pudo conectar a la API: {e}")
        print("        ¿Está el backend corriendo? (python main.py)")
        sys.exit(1)

    # 2. POST /escanear con solo texto (simula búsqueda sin OCR)
    try:
        body = json.dumps({"texto": TEXTO_PRUEBA}).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE}/escanear",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        print(f"[FALLO] Error al llamar POST /escanear: {e}")
        sys.exit(1)

    encontrado_bd = data.get("encontrado_en_bd", False)
    vino = data.get("vino") or {}
    nombre = (vino.get("nombre") or "").strip()
    mensaje = (data.get("mensaje") or "").strip()

    if encontrado_bd:
        print(f"[OK] Vino encontrado en BD: {nombre}")
        print(f"     Key: {data.get('vino_key', '—')}")
    elif nombre and not vino.get("_origen") == "generico":
        print(f"[OK] Vino encontrado en fuente externa (no en BD): {nombre}")
        print(f"     Mensaje: {mensaje[:80]}...")
    else:
        print("[INFO] No se encontró coincidencia fiable. Respuesta genérica.")
        print(f"       Mensaje: {mensaje[:100]}...")
        if data.get("recomendar_similar"):
            print("       Se ofrece recomendación similar.")

    print("\n--- Resumen ---")
    print(f"  encontrado_en_bd: {encontrado_bd}")
    print(f"  nombre devuelto: {nombre or '(genérico)'}")
    print("\nSi el texto de prueba SÍ encuentra el vino aquí pero en el móvil no:")
    print("  -> El OCR de la foto está devolviendo texto distinto/sucio. Mira en la terminal del backend los logs [ESCANEAR] al escanear desde la app.")
    print("Si el texto de prueba NO encuentra el vino:")
    print("  -> Revisa que el vino esté en data/*.json (ej. espana.json) o que la búsqueda sea la esperada.")

if __name__ == "__main__":
    main()
