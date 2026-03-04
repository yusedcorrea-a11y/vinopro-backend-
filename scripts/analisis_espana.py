"""Análisis rápido de vinos en data/espana.json"""
import json
import os

path = os.path.join(os.path.dirname(__file__), "..", "data", "espana.json")
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
regiones = {}
tipos = {}
for key, v in data.items():
    r = v.get("region") or "Sin región"
    regiones[r] = regiones.get(r, 0) + 1
    t = (v.get("tipo") or "sin tipo").strip().lower()
    tipos[t] = tipos.get(t, 0) + 1

print("=== ESPAÑA — Análisis de vinos ===\n")
print("Total vinos:", total)
print("\nPor región (ordenado por cantidad):")
for r, c in sorted(regiones.items(), key=lambda x: -x[1]):
    print(f"  {r}: {c}")
print("\nPor tipo:")
for t, c in sorted(tipos.items(), key=lambda x: -x[1]):
    print(f"  {t}: {c}")
print("\nNúmero de regiones distintas:", len(regiones))
