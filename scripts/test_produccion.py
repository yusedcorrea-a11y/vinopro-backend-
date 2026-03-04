#!/usr/bin/env python3
"""
Script de comprobaciones para producción.
Verifica: API responde, HTTPS (si aplica), CORS, sitemap, Stripe config (no pagos reales).
Uso: python scripts/test_produccion.py --base-url https://tudominio.com
"""
import argparse
import sys
import urllib.request
import urllib.error
import ssl


def get_url(url: str, timeout: int = 10, headers: dict | None = None) -> tuple[int, str, dict]:
    """GET y devuelve (status_code, body_preview, response_headers)."""
    req = urllib.request.Request(url, headers=headers or {})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read().decode("utf-8", errors="replace")[:500]
            return r.status, body, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:500], dict(e.headers)
    except Exception as e:
        return -1, str(e), {}


def main():
    p = argparse.ArgumentParser(description="Pruebas de producción Vino Pro IA")
    p.add_argument("--base-url", default="http://127.0.0.1:8001", help="URL base (ej. https://tudominio.com)")
    p.add_argument("--skip-https", action="store_true", help="No comprobar que la URL sea HTTPS en producción")
    args = p.parse_args()
    base = args.base_url.rstrip("/")

    errors = []
    print(f"Base URL: {base}\n")

    # 1) API responde
    print("1. API /api/status ...")
    status, body, _ = get_url(f"{base}/api/status")
    if status != 200:
        errors.append(f"/api/status devolvió {status}")
    else:
        print("   OK")

    # 2) HTTPS en producción (si la base es https)
    if base.startswith("https://") and not args.skip_https:
        print("2. HTTPS (conexión segura) ...")
        status, _, _ = get_url(base)
        if status == -1:
            errors.append("No se pudo conectar por HTTPS")
        else:
            print("   OK")
    else:
        print("2. HTTPS ... omitido (base no es https o --skip-https)")

    # 3) Sitemap
    print("3. Sitemap /sitemap.xml ...")
    status, body, h = get_url(f"{base}/sitemap.xml")
    if status != 200 or "<urlset" not in body:
        errors.append(f"/sitemap.xml falló (status={status})")
    else:
        print("   OK")

    # 4) CORS (solo comprobamos que la app responde; el header exacto depende de CORS_ORIGINS)
    print("4. CORS (OPTIONS/GET desde script) ...")
    status, _, headers = get_url(base, headers={"Origin": "https://ejemplo.com"})
    # No podemos simular CORS preflight completo con urllib fácilmente; comprobamos que no hay 5xx
    if status >= 500:
        errors.append(f"Respuesta {status} en GET /")
    else:
        print("   OK (respuesta no 5xx)")

    # 5) Stripe: solo comprobar que el endpoint existe (no hacer pago real)
    print("5. Endpoint webhook Stripe (POST sin body = 400 esperado) ...")
    req = urllib.request.Request(
        f"{base}/webhook-stripe",
        data=b"",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5, context=ssl.create_default_context()) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as e:
        status = -1
        errors.append(f"Webhook inaccesible: {e}")
    # 400 = firma inválida (normal si no enviamos evento real). 200 = no debería con body vacío
    if status not in (200, 400):
        if status == -1:
            pass  # ya añadido
        else:
            errors.append(f"Webhook devolvió {status} (esperado 400 sin payload válido)")
    else:
        print("   OK (endpoint accesible)")

    print()
    if errors:
        print("Errores:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("Todas las comprobaciones pasaron.")
    sys.exit(0)


if __name__ == "__main__":
    main()
