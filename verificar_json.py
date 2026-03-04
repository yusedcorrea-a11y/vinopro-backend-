import json

# Cargar el diccionario de vinos
with open('vinos_diccionario.json', 'r', encoding='utf-8') as f:
    VINOS_MUNDIALES = json.load(f)

print(f'✅ Diccionario cargado con {len(VINOS_MUNDIALES)} vinos')
