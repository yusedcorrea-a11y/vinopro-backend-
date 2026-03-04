"""
Comprueba que espana.json se lee bien y que Viña Pedrosa está en la BD.
Ejecutar SOLO este comando en PowerShell (desde backend_optimized):

  python scripts/verificar_bd_espana.py

No pegues nada más en la terminal, solo esa línea.
"""
import json
import os
from pathlib import Path

# Ruta absoluta al data (igual que en app.py)
BASE = Path(__file__).resolve().parent.parent
ruta = BASE / "data" / "espana.json"

print("Ruta al archivo:", ruta)
print("Existe:", ruta.exists())

if not ruta.exists():
    print("ERROR: No se encuentra data/espana.json")
    exit(1)

try:
    with open(ruta, "r", encoding="utf-8") as f:
        d = json.load(f)
except Exception as e:
    print("ERROR al abrir JSON:", e)
    exit(1)

print("Vinos en espana.json:", len(d))

pedrosa = [k for k in d if "pedrosa" in k.lower()]
print("Keys con 'pedrosa':", pedrosa)

if pedrosa:
    ej = d[pedrosa[0]]
    print("Ejemplo (nombre):", ej.get("nombre"))
    print("BD y encoding OK.")
else:
    print("No se encontraron entradas 'pedrosa' en el archivo.")
