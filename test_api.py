#!/usr/bin/env python3
"""
Script de prueba rápida: verifica si GNEWS_API_KEY es válida haciendo una petición a gnews.io.
Uso: desde la raíz del backend, ejecutar: python test_api.py
"""
import os
import sys

# Cargar .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def main():
    api_key = os.getenv("GNEWS_API_KEY", "").strip()
    if not api_key:
        print("ERROR: GNEWS_API_KEY no está definida o está vacía.")
        print("Defínela en .env o en el entorno (ej. Render Variables).")
        sys.exit(1)

    print(f"GNEWS_API_KEY encontrada (longitud: {len(api_key)} caracteres).")
    print("Realizando petición de prueba a gnews.io...")

    try:
        import httpx
    except ImportError:
        print("ERROR: Instala httpx: pip install httpx")
        sys.exit(1)

    url = f"https://gnews.io/api/v4/search?q=wine&max=1&apikey={api_key}"
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url)
            print(f"HTTP Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                articles = data.get("articles", []) if isinstance(data, dict) else []
                print(f"OK: Token válido. Respuesta con {len(articles)} artículo(s) de prueba.")
                if articles:
                    print(f"Ejemplo: {articles[0].get('title', '')[:60]}...")
            elif r.status_code == 400:
                print(f"ERROR 400 Bad Request. Cuerpo: {r.text}")
                print("Posibles causas: API Key inválida, formato incorrecto o cuota agotada.")
                sys.exit(1)
            else:
                print(f"Respuesta: {r.text[:300]}")
                sys.exit(1)
    except Exception as e:
        print(f"ERROR de conexión: {e}")
        sys.exit(1)

    print("Prueba completada. El token GNews es válido.")


if __name__ == "__main__":
    main()
