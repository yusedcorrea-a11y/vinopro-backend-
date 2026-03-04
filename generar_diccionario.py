import sqlite3
import json

print('🍷 GENERANDO DICCIONARIO DE VINOS DESDE SQLITE')
print('=' * 50)

conn = sqlite3.connect('vino.db')
cursor = conn.cursor()
cursor.execute('SELECT nombre, bodega, region, pais, tipo, puntuacion, precio_estimado, descripcion FROM vinos ORDER BY puntuacion DESC')
vinos = cursor.fetchall()

print(f'📊 Total vinos encontrados: {len(vinos)}')

# Generar entrada para cada vino
diccionario = {}
for v in vinos:
    nombre_key = v[0].lower().replace(' ', '_').replace("'", '').replace('-', '_')
    diccionario[nombre_key] = {
        "nombre": v[0],
        "bodega": v[1],
        "region": v[2],
        "pais": v[3],
        "tipo": v[4],
        "puntuacion": v[5],
        "precio_estimado": v[6],
        "descripcion": v[7]
    }

# Guardar como archivo JSON para referencia
with open('vinos_diccionario.json', 'w', encoding='utf-8') as f:
    json.dump(diccionario, f, ensure_ascii=False, indent=2)

print(f'✅ Diccionario guardado en vinos_diccionario.json con {len(diccionario)} vinos')

# Mostrar las primeras entradas como ejemplo
print('\n📝 PRIMERAS 3 ENTRADAS (para verificar):')
primeros = list(diccionario.items())[:3]
for key, value in primeros:
    print(f'  "{key}": {value["nombre"]} - {value["puntuacion"]} pts')

conn.close()
print('\n✅ Listo. Ahora necesitas reemplazar VINOS_MUNDIALES en app.py con este diccionario.')
