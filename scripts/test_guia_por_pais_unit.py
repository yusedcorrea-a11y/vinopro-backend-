"""
Pruebas unitarias de guías por país (sin servidor).
Comprueba que get_guia_vinos_por_pais devuelve nombre, url y emoji correctos.
Ejecutar desde la raíz del backend: python scripts/test_guia_por_pais_unit.py
"""
import sys
from pathlib import Path

# Raíz del proyecto
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.enlaces_service import get_guia_vinos_por_pais

CASOS = [
    ("ES", "Guía Repsol", "guiarepsol.com", "🇪🇸"),
    ("IT", "Gambero Rosso", "gamberorosso.it", "🇮🇹"),
    ("FR", "Guide Hachette", "leguidehachette.com", "🇫🇷"),
    ("DE", "Gault&Millau", "gaultmillau.de", "🇩🇪"),
    ("AR", "Guía de Vinos Argentina", "guiadevinos.com.ar", "🇦🇷"),
    ("BR", "Guia de Vinhos Brasil", "guiadevinhosbrasil.com", "🇧🇷"),
    ("UY", "Guía de Vinos Uruguay", "guiadevinosuruguay.com", "🇺🇾"),
    ("AT", "Falstaff", "falstaff.at", "🇦🇹"),
    ("CH", "Gault&Millau Suisse", "gaultmillau.ch", "🇨🇭"),
    ("ZA", "Platter's Wine Guide", "wineonaplatter.com", "🇿🇦"),
    ("AU", "Halliday Wine Companion", "winecompanion.com.au", "🇦🇺"),
    ("JP", "JWINE (日本ワイン)", "jwine.net", "🇯🇵"),
    ("CU", "Guía Repsol", "guiarepsol.com", "🌍"),  # fallback (no guía específica)
]


def run():
    fallos = []
    for pais, nombre_esperado, url_contiene, emoji_esperado in CASOS:
        g = get_guia_vinos_por_pais(pais)
        ok_n = g.get("nombre") == nombre_esperado
        ok_u = url_contiene in (g.get("url") or "")
        ok_e = g.get("emoji") == emoji_esperado
        if not (ok_n and ok_u and ok_e):
            fallos.append(pais)

    print("\n--- REGISTRO DE RESULTADOS (lógica backend) ---\n")
    print("Pais      | Resultado | Observaciones")
    print("-" * 60)
    for pais, nombre, url_c, emoji in CASOS:
        g = get_guia_vinos_por_pais(pais)
        ok = (
            g.get("nombre") == nombre
            and url_c in (g.get("url") or "")
            and g.get("emoji") == emoji
        )
        marca = "OK" if ok else "FAIL"
        obs = "-"
        if not ok:
            u = g.get("url") or ""
            obs = f"nombre={g.get('nombre')!r} url={u[:50]} emoji={g.get('emoji')!r}"
        # Evitar Unicode en consola Windows
        try:
            print(f"{pais:9} | {marca:6} | {obs}")
        except UnicodeEncodeError:
            print(f"{pais:9} | {marca:6} | (obs con caracteres no ASCII)")
    print()
    if fallos:
        print("Fallos (codigos):", fallos)
        return 1
    print(f"Total: {len(CASOS)}/{len(CASOS)} pruebas pasadas (backend).")
    return 0


if __name__ == "__main__":
    sys.exit(run())
