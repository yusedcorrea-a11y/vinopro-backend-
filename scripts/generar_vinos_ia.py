#!/usr/bin/env python3
"""
Genera vinos con IA (OpenAI o OpenRouter) y guarda en data/vinos_generados_ia.json.
Países: España (--pais espana), Italia (--pais italia). Se puede combinar: generar 500 españoles
y luego 500 italianos; el script fusiona con el archivo existente.
Uso: python scripts/generar_vinos_ia.py [--cantidad 500] [--batch 50] [--pais espana|italia]
Requiere: OPENAI_API_KEY o OPENROUTER_API_KEY en .env
"""
import json
import os
import re
import sys
import argparse
from pathlib import Path

# Añadir raíz del proyecto al path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    import httpx
except ImportError:
    print("ERROR: Necesitas instalar httpx: pip install httpx")
    sys.exit(1)

# Cargar .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

DATA_DIR = ROOT / "data"
OUTPUT_FILE = DATA_DIR / "vinos_generados_ia.json"

# 20 países prioritarios: slug -> (nombre completo, regiones clave, uvas emblemáticas)
PAISES_IA = {
    "espana": ("España", "Rioja, Ribera del Duero, Rueda, Priorat, Rías Baixas, Penedès, Cava, Jerez, Toro, Bierzo", "Tempranillo, Albariño, Garnacha"),
    "francia": ("Francia", "Bordeaux, Borgoña, Champaña, Loira, Ródano, Alsacia", "Cabernet, Chardonnay, Pinot Noir, Syrah, Riesling"),
    "italia": ("Italia", "Toscana, Piamonte, Véneto, Sicilia, Lombardía, Emilia-Romaña", "Sangiovese, Nebbiolo, Barbera, Prosecco"),
    "portugal": ("Portugal", "Douro, Alentejo, Dão, Vinho Verde", "Touriga Nacional, Tinta Roriz, Alvarinho"),
    "alemania": ("Alemania", "Mosela, Rheingau, Pfalz, Baden", "Riesling, Spätburgunder"),
    "argentina": ("Argentina", "Mendoza, Salta, Patagonia", "Malbec, Torrontés, Cabernet Sauvignon"),
    "chile": ("Chile", "Maipo, Colchagua, Casablanca, Valle Central", "Carmenère, Cabernet Sauvignon, Sauvignon Blanc"),
    "usa": ("Estados Unidos", "California (Napa, Sonoma), Oregón, Washington", "Cabernet Sauvignon, Zinfandel, Pinot Noir, Chardonnay"),
    "australia": ("Australia", "Barossa, Hunter Valley, Yarra Valley, Margaret River", "Shiraz, Cabernet Sauvignon, Chardonnay"),
    "nueva_zelanda": ("Nueva Zelanda", "Marlborough, Central Otago, Hawke's Bay", "Sauvignon Blanc, Pinot Noir, Chardonnay"),
    "sudafrica": ("Sudáfrica", "Stellenbosch, Paarl, Constantia", "Pinotage, Chenin Blanc, Cabernet Sauvignon"),
    "uruguay": ("Uruguay", "Canelones, Maldonado, Colonia", "Tannat, Albariño"),
    "suiza": ("Suiza", "Valais, Vaud, Ticino", "Chasselas, Pinot Noir, Gamay"),
    "austria": ("Austria", "Wachau, Kamptal, Burgenland", "Grüner Veltliner, Riesling"),
    "hungria": ("Hungría", "Tokaj, Villány, Eger", "Furmint, Kékfrankos"),
    "grecia": ("Grecia", "Santorini, Nemea, Naoussa", "Assyrtiko, Agiorgitiko, Xinomavro"),
    "japon": ("Japón", "Yamanashi, Nagano, Hokkaido", "Koshu, Muscat Bailey A"),
    "china": ("China", "Ningxia, Yantai, Hebei", "Cabernet Gernischt, Marselan"),
    "brasil": ("Brasil", "Serra Gaúcha, Campanha", "Merlot, Cabernet Sauvignon, Chardonnay"),
    "colombia": ("Colombia", "Villa de Leyva, Valle del Cauca", "Criolla, Syrah, Cabernet Sauvignon"),
}

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_URL = os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

CAMPOS_REQUERIDOS = {"nombre", "bodega", "region", "pais", "tipo", "precio_estimado", "puntuacion", "descripcion", "notas_cata", "maridaje"}
TIPOS_VALIDOS = {"tinto", "blanco", "rosado", "espumoso", "dulce"}


def slugify(text: str) -> str:
    """Normaliza nombre a clave sin espacios ni caracteres especiales (ES/IT)."""
    if not text or not isinstance(text, str):
        return ""
    t = text.lower().strip()
    for old, new in [("áàäâ", "a"), ("éèëê", "e"), ("íìïî", "i"), ("óòöô", "o"), ("úùüû", "u"), ("ñ", "n"), ("ç", "c")]:
        for c in old:
            t = t.replace(c, new)
    t = re.sub(r"[^a-z0-9]+", "_", t)
    return t.strip("_") or "vino"


def normalizar_vino(raw: dict, pais_default: str = "España") -> dict | None:
    """Limpia y valida un vino; devuelve None si falta algo crítico."""
    if not isinstance(raw, dict):
        return None
    nombre = (raw.get("nombre") or "").strip()
    if not nombre or len(nombre) < 2:
        return None
    key = (raw.get("key") or "").strip() or slugify(nombre)
    tipo = (raw.get("tipo") or "tinto").strip().lower()
    if tipo not in TIPOS_VALIDOS:
        tipo = "tinto"
    pais = (raw.get("pais") or pais_default).strip()
    puntuacion = raw.get("puntuacion")
    if puntuacion is not None:
        try:
            puntuacion = int(puntuacion)
            puntuacion = max(0, min(100, puntuacion))
        except (TypeError, ValueError):
            puntuacion = 85
    else:
        puntuacion = 85
    precio = raw.get("precio_estimado")
    if precio is not None and isinstance(precio, (int, float)):
        precio = f"{int(precio)}€" if precio == int(precio) else f"{precio}€"
    elif not isinstance(precio, str) or not precio:
        precio = "Consultar"
    pais_lower = pais.lower()
    if "italia" in pais_lower or pais == "IT":
        fallback_bodega, fallback_region, fallback_desc, fallback_maridaje = "Cantina italiana", "Italia", "Vino italiano de calidad.", "Pasta, carnes, quesos."
    elif "francia" in pais_lower or pais == "FR":
        fallback_bodega, fallback_region, fallback_desc, fallback_maridaje = "Domaine français", "Francia", "Vino francés de calidad.", "Carnes, quesos, mariscos."
    elif "portugal" in pais_lower or pais == "PT":
        fallback_bodega, fallback_region, fallback_desc, fallback_maridaje = "Quinta portuguesa", "Portugal", "Vino portugués de calidad.", "Pescado, arroces, bacalao."
    else:
        fallback_bodega, fallback_region, fallback_desc, fallback_maridaje = f"Bodega {pais}", pais, f"Vino de {pais}, calidad.", "Carnes, quesos, gastronomía local."
    return {
        "nombre": nombre,
        "bodega": (raw.get("bodega") or "").strip() or fallback_bodega,
        "region": (raw.get("region") or "").strip() or fallback_region,
        "pais": pais,
        "tipo": tipo,
        "uva": (raw.get("uva") or "").strip() or "",
        "alcohol": (raw.get("alcohol") or "").strip() or "",
        "anyo": raw.get("anyo") if isinstance(raw.get("anyo"), int) else None,
        "precio_estimado": precio,
        "puntuacion": puntuacion,
        "descripcion": (raw.get("descripcion") or "").strip() or fallback_desc,
        "notas_cata": (raw.get("notas_cata") or "").strip() or "Notas de cata no especificadas.",
        "maridaje": (raw.get("maridaje") or "").strip() or fallback_maridaje,
        "key": key,
    }


def llamar_openai(messages: list[dict], max_tokens: int = 4000) -> str | None:
    """Llama a OpenAI (API compatible)."""
    if not OPENAI_API_KEY:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    try:
        with httpx.Client(timeout=90.0) as client:
            r = client.post(
                url,
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            if r.status_code != 200:
                print(f"  OpenAI HTTP {r.status_code}: {r.text[:200]}")
                return None
            data = r.json()
            return (data.get("choices") or [{}])[0].get("message", {}).get("content")
    except Exception as e:
        print(f"  Error OpenAI: {e}")
        return None


def llamar_openrouter(messages: list[dict], max_tokens: int = 4000) -> str | None:
    """Llama a OpenRouter."""
    if not OPENROUTER_API_KEY:
        return None
    try:
        with httpx.Client(timeout=90.0) as client:
            r = client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://vinopro.local",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            if r.status_code != 200:
                print(f"  OpenRouter HTTP {r.status_code}: {r.text[:200]}")
                return None
            data = r.json()
            return (data.get("choices") or [{}])[0].get("message", {}).get("content")
    except Exception as e:
        print(f"  Error OpenRouter: {e}")
        return None


def extraer_json(texto: str) -> list | dict | None:
    """Extrae JSON del texto (puede venir dentro de ```json ... ```)."""
    if not texto or not isinstance(texto, str):
        return None
    texto = texto.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", texto)
    if match:
        texto = match.group(1).strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass
    # Intentar encontrar array o objeto
    for start, end in [("[", "]"), ("{", "}")]:
        i = texto.find(start)
        if i == -1:
            continue
        depth = 0
        for j in range(i, len(texto)):
            if texto[j] == start:
                depth += 1
            elif texto[j] == end:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(texto[i : j + 1])
                    except json.JSONDecodeError:
                        break
    return None


PROMPT_ESPANA = """Genera exactamente {num} vinos españoles en formato JSON array.
Regiones: Rioja, Ribera del Duero, Rueda, Rías Baixas, Priorat, Penedès, Cava, Jerez, Valdepeñas, Toro, Bierzo, Ribera del Guadiana, Navarra, Somontano, etc.
Variedad de precios: desde 5€ hasta 300€. Incluye bodegas reales o verosímiles.
Cada elemento del array debe tener:
- nombre (string)
- bodega (string)
- region (string)
- pais: "España"
- tipo: uno de tinto, blanco, rosado, espumoso
- uva (string, ej. Tempranillo, Garnacha, Albariño)
- alcohol (string, ej. "13.5%")
- anyo (número, ej. 2020)
- precio_estimado (número o string como "15-20€")
- puntuacion (número 0-100)
- descripcion (1-2 frases)
- notas_cata (fruta, madera, etc.)
- maridaje (carnes, pescado, etc.)
- key (string: nombre en minúsculas, sin espacios, guiones bajos, sin tildes)
Devuelve SOLO el array JSON, sin explicaciones ni markdown."""

PROMPT_ITALIA = """Genera exactamente {num} vinos italianos en formato JSON array.
Regiones: Toscana (Brunello di Montalcino, Chianti Classico, Vino Nobile di Montepulciano, Sassicaia, Ornellaia), Piamonte (Barolo, Barbaresco, Barbera d'Asti, Moscato d'Asti), Véneto (Amarone della Valpolicella, Prosecco, Soave), Sicilia (Nero d'Avola, Etna Rosso, Marsala), Lombardía (Franciacorta), Emilia-Romaña (Lambrusco: varias versiones y bodegas), Campania, Friuli, etc.
Variedad de tipos: tintos (Sangiovese, Nebbiolo, Barbera), blancos (Pinot Grigio, Vermentino, Fiano), espumosos (Prosecco, Franciacorta), dulces (Vin Santo, Moscato d'Asti). Incluye varias versiones de Lambrusco.
Variedad de precios: desde 5€ hasta 500€. Bodegas reales o verosímiles.
Cada elemento del array debe tener:
- nombre (string)
- bodega (string)
- region (string)
- pais: "Italia"
- tipo: uno de tinto, blanco, rosado, espumoso, dulce
- uva (string, ej. Sangiovese, Nebbiolo, Lambrusco, Prosecco)
- alcohol (string, ej. "12.5%")
- anyo (número, ej. 2021)
- precio_estimado (número o string como "15-25€")
- puntuacion (número 0-100)
- descripcion (1-2 frases)
- notas_cata (fruta, madera, etc.)
- maridaje (pasta, carnes, embutidos, etc.)
- key (string: nombre en minúsculas, sin espacios, guiones bajos, sin tildes)
Devuelve SOLO el array JSON, sin explicaciones ni markdown."""

PROMPT_GENERICO = """Genera exactamente {num} vinos de {pais} en formato JSON array.
Regiones importantes: {regiones}.
Uvas emblemáticas: {uvas}.
Variedad de precios: desde 5€ hasta 500€ (o equivalente en moneda local). Variedad de tipos: tintos, blancos, rosados, espumosos.
Cada elemento del array debe tener:
- nombre (string)
- bodega (string)
- region (string)
- pais: "{pais}"
- tipo: uno de tinto, blanco, rosado, espumoso, dulce
- uva (string)
- alcohol (string, ej. "13%")
- anyo (número, ej. 2020)
- precio_estimado (string como "15-20€" o número)
- puntuacion (número 0-100)
- descripcion (1-2 frases)
- notas_cata (fruta, madera, etc.)
- maridaje (carnes, pescado, etc.)
- key (string: nombre normalizado en minúsculas, sin espacios, guiones bajos)
Devuelve SOLO el array JSON, sin explicaciones ni markdown."""

PROMPTS = {"espana": PROMPT_ESPANA, "italia": PROMPT_ITALIA}
PAIS_DEFAULT = {"espana": "España", "italia": "Italia"}
PREFIJO_KEY = {"espana": "ia_", "italia": "ia_it_"}
for slug in PAISES_IA:
    if slug not in PREFIJO_KEY:
        PREFIJO_KEY[slug] = f"ia_{slug[:3]}_"
    if slug not in PAIS_DEFAULT:
        PAIS_DEFAULT[slug] = PAISES_IA[slug][0]


def generar_batch(num: int, pais: str) -> list[dict]:
    """Genera un lote de vinos con IA según el país."""
    if pais in PROMPTS:
        prompt = PROMPTS[pais].format(num=num)
    elif pais in PAISES_IA:
        nombre, regiones, uvas = PAISES_IA[pais]
        prompt = PROMPT_GENERICO.format(num=num, pais=nombre, regiones=regiones, uvas=uvas)
    else:
        prompt = PROMPT_GENERICO.format(num=num, pais=pais.title(), regiones="Principales regiones", uvas="Variedades locales")
    messages = [{"role": "user", "content": prompt}]
    content = llamar_openrouter(messages, max_tokens=8000) or llamar_openai(messages, max_tokens=8000)
    if not content:
        return []

    parsed = extraer_json(content)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return list(parsed.values()) if parsed else []
    return []


def main():
    choices_pais = list(PAISES_IA.keys())
    parser = argparse.ArgumentParser(description="Genera vinos con IA por país (20 países soportados)")
    parser.add_argument("--cantidad", type=int, default=500, help="Total de vinos a generar")
    parser.add_argument("--batch", type=int, default=50, help="Vinos por petición a la IA")
    parser.add_argument("--pais", type=str, default="espana", choices=choices_pais, help="País: " + ", ".join(choices_pais[:5]) + ", ...")
    parser.add_argument("--output", type=str, default="", help="Archivo de salida (ej. data/vinos_fr_masivos.json). Si no se indica, se usa data/vinos_generados_ia.json")
    parser.add_argument("--dry-run", action="store_true", help="Solo probar una petición pequeña (10 vinos)")
    args = parser.parse_args()

    if not OPENROUTER_API_KEY and not OPENAI_API_KEY:
        print("ERROR: Configura OPENROUTER_API_KEY o OPENAI_API_KEY en .env")
        sys.exit(1)

    pais = args.pais.lower()
    prefijo = PREFIJO_KEY.get(pais, f"ia_{pais[:3]}_")
    pais_default = PAIS_DEFAULT.get(pais, PAISES_IA.get(pais, ("España", "", ""))[0])
    pais_nombre = pais_default  # para mensajes
    out_path = Path(args.output) if args.output.strip() else OUTPUT_FILE
    if not out_path.is_absolute():
        out_path = ROOT / out_path

    cantidad = 10 if args.dry_run else args.cantidad
    batch_size = min(args.batch, 80)
    todos: dict[str, dict] = {}

    # Cargar archivo existente (mismo out_path para reanudar o fusionar)
    if out_path.exists():
        try:
            with open(out_path, "r", encoding="utf-8") as f:
                todos = json.load(f)
            if not isinstance(todos, dict):
                todos = {}
            else:
                print(f"[*] Cargados {len(todos)} vinos existentes en {out_path.name}; se anadiran los nuevos.")
        except Exception as e:
            print(f"[!] No se pudo cargar el archivo existente: {e}")

    batch_num = 0
    total_batches = (cantidad + batch_size - 1) // batch_size
    objetivo = len(todos) + cantidad

    print(f"[>>] Generando hasta {cantidad} vinos de {pais_nombre} (lotes de {batch_size}) -> {out_path.name}")
    while len(todos) < objetivo:
        batch_num += 1
        restantes = objetivo - len(todos)
        pedir = min(batch_size, restantes)
        print(f"  Lote {batch_num}/{total_batches} (pidiendo {pedir})...")
        raw_list = generar_batch(pedir, pais)
        if not raw_list:
            print("  [!] Sin respuesta de la IA; parando.")
            break
        for raw in raw_list:
            vino = normalizar_vino(raw, pais_default=pais_default)
            if not vino:
                continue
            key = vino.pop("key")
            if not key:
                key = slugify(vino.get("nombre", ""))
            key = key[:80]
            key = f"{prefijo}{key}"
            if key in todos:
                key = f"{prefijo}{slugify(vino.get('nombre',''))}_{len(todos)}"
            todos[key] = vino
        print(f"  Acumulados: {len(todos)} vinos.")
        if args.dry_run:
            break

    if not todos:
        print("ERROR: No se genero ningun vino.")
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)
    print(f"OK: Guardados {len(todos)} vinos en {out_path}")
    print("   Reinicia el backend (o recarga) para que cargue el nuevo archivo.")


if __name__ == "__main__":
    main()
