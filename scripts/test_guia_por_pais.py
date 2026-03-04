"""
Pruebas de la sección "¿Dónde tomarlo?" por país.
Ejecutar con el servidor en marcha: uvicorn app:app --port 8001
Uso: python scripts/test_guia_por_pais.py
"""
import sys
try:
    import httpx
except ImportError:
    print("Instala httpx: pip install httpx")
    sys.exit(1)

BASE = "http://127.0.0.1:8001"
VINO_ID = "pingus"
# Español para comprobar textos esperados
HEADERS = {"Accept-Language": "es"}

# Español (Accept-Language: es): título, descripción contiene nombre del país, botón y URL
CASOS = [
    # Europa (originales + nuevos)
    {"pais": "ES", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "España", "boton_contiene": "Guía Repsol", "emoji": "🇪🇸", "url_contiene": "guiarepsol.com"},
    {"pais": "BE", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Bélgica", "boton_contiene": "Millau Belgique", "emoji": "🇧🇪", "url_contiene": "gaultmillau.be"},
    {"pais": "NL", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Países Bajos", "boton_contiene": "Millau Nederland", "emoji": "🇳🇱", "url_contiene": "gaultmillau.nl"},
    {"pais": "CH", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Suiza", "boton_contiene": "Millau Suisse", "emoji": "🇨🇭", "url_contiene": "gaultmillau.ch"},
    {"pais": "AT", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Austria", "boton_contiene": "Falstaff", "emoji": "🇦🇹", "url_contiene": "falstaff.at"},
    {"pais": "SE", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Suecia", "boton_contiene": "Vinjournalen", "emoji": "🇸🇪", "url_contiene": "vinjournalen.se"},
    {"pais": "NO", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Noruega", "boton_contiene": "Vinforum", "emoji": "🇳🇴", "url_contiene": "vinforum.no"},
    {"pais": "DK", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Dinamarca", "boton_contiene": "Vinbladet", "emoji": "🇩🇰", "url_contiene": "vinbladet.dk"},
    {"pais": "FI", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Finlandia", "boton_contiene": "Viinilehti", "emoji": "🇫🇮", "url_contiene": "viinilehti.fi"},
    {"pais": "PL", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Polonia", "boton_contiene": "Czas Wina", "emoji": "🇵🇱", "url_contiene": "czaswina.pl"},
    {"pais": "CZ", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "República Checa", "boton_contiene": "Moravy", "emoji": "🇨🇿", "url_contiene": "vinazmoravyvinazcech.cz"},
    {"pais": "HU", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Hungría", "boton_contiene": "Magyar Bor", "emoji": "🇭🇺", "url_contiene": "winesofhungary.hu"},
    {"pais": "GR", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Grecia", "boton_contiene": "Oinorama", "emoji": "🇬🇷", "url_contiene": "oinorama.gr"},
    # América (nuevos)
    {"pais": "BR", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Brasil", "boton_contiene": "Vinhos Brasil", "emoji": "🇧🇷", "url_contiene": "guiadevinhosbrasil.com"},
    {"pais": "UY", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Uruguay", "boton_contiene": "Guía de Vinos Uruguay", "emoji": "🇺🇾", "url_contiene": "guiadevinosuruguay.com"},
    {"pais": "PE", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Perú", "boton_contiene": "Guía de Vinos Perú", "emoji": "🇵🇪", "url_contiene": "guiadevinosperu.com"},
    {"pais": "CO", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Colombia", "boton_contiene": "Guía de Vinos Colombia", "emoji": "🇨🇴", "url_contiene": "guiadevinoscolombia.com"},
    # Otros continentes
    {"pais": "ZA", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Sudáfrica", "boton_contiene": "Platter", "emoji": "🇿🇦", "url_contiene": "wineonaplatter.com"},
    {"pais": "AU", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Australia", "boton_contiene": "Halliday", "emoji": "🇦🇺", "url_contiene": "winecompanion.com.au"},
    {"pais": "NZ", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Nueva Zelanda", "boton_contiene": "Bob Campbell", "emoji": "🇳🇿", "url_contiene": "bobcampbell.nz"},
    {"pais": "JP", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "Japón", "boton_contiene": "JWINE", "emoji": "🇯🇵", "url_contiene": "jwine.net"},
    # Fallback (Guía Repsol + tu país)
    {"pais": "CU", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "tu país", "boton_contiene": "Guía Repsol", "emoji": "🌍", "url_contiene": "guiarepsol.com"},
    {"pais": "DO", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "tu país", "boton_contiene": "Guía Repsol", "emoji": "🌍", "url_contiene": "guiarepsol.com"},
    {"pais": "CR", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "tu país", "boton_contiene": "Guía Repsol", "emoji": "🌍", "url_contiene": "guiarepsol.com"},
    {"pais": "TR", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "tu país", "boton_contiene": "Guía Repsol", "emoji": "🌍", "url_contiene": "guiarepsol.com"},
    {"pais": "CN", "titulo": "¿Dónde tomarlo?", "descripcion_contiene": "tu país", "boton_contiene": "Guía Repsol", "emoji": "🌍", "url_contiene": "guiarepsol.com"},
]


def run():
    resultados = []
    for c in CASOS:
        url = f"{BASE}/vino/{VINO_ID}/comprar?pais={c['pais']}"
        try:
            r = httpx.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            html = r.text
            ok_titulo = c["titulo"] in html
            ok_desc = c["descripcion_contiene"] in html
            ok_boton = c["boton_contiene"] in html
            ok_emoji = c["emoji"] in html
            ok_url = c["url_contiene"] in html
            ok_target = 'target="_blank"' in html or "target=_blank" in html
            todo_ok = ok_titulo and ok_desc and ok_boton and ok_emoji and ok_url and ok_target
            resultados.append({
                "pais": c["pais"],
                "ok": todo_ok,
                "obs": [] if todo_ok else [
                    x for x, v in [
                        ("falta titulo", not ok_titulo),
                        ("falta descripcion", not ok_desc),
                        ("falta nombre guia", not ok_boton),
                        ("falta emoji", not ok_emoji),
                        ("falta URL", not ok_url),
                        ("falta target=_blank", not ok_target),
                    ] if v
                ],
            })
        except Exception as e:
            resultados.append({"pais": c["pais"], "ok": False, "obs": [str(e)]})

    # Tabla (sin Unicode para consola Windows)
    print("\n--- REGISTRO DE RESULTADOS (E2E guias por pais) ---\n")
    print("Codigo  | Resultado | Observaciones")
    print("-" * 60)
    for r in resultados:
        marca = "OK" if r["ok"] else "FAIL"
        obs = "; ".join(r["obs"]) if r["obs"] else "-"
        print(f"{r['pais']:7} | {marca:9} | {obs}")
    print()
    total_ok = sum(1 for r in resultados if r["ok"])
    print(f"Total: {total_ok}/{len(resultados)} pruebas pasadas.")
    return 0 if total_ok == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(run())
