import json
import re

print('🍷 ACTUALIZANDO app.py CON LOS 61 VINOS')
print('=' * 50)

# Cargar el diccionario generado
with open('vinos_diccionario.json', 'r', encoding='utf-8') as f:
    nuevos_vinos = json.load(f)

# Leer el archivo app.py actual
with open('app.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Buscar la sección VINOS_MUNDIALES
patron = r'(VINOS_MUNDIALES\s*=\s*\{).*?(\}\s*\n\s*#)'
import re
match = re.search(patron, contenido, re.DOTALL)

if match:
    inicio = match.start(1)
    fin = match.end(2)
    
    # Crear nuevo diccionario como string
    nuevo_contenido = 'VINOS_MUNDIALES = ' + json.dumps(nuevos_vinos, ensure_ascii=False, indent=4)
    
    # Reemplazar en el archivo
    nuevo_archivo = contenido[:inicio] + nuevo_contenido + contenido[fin:]
    
    # Guardar backup
    with open('app.py.bak', 'w', encoding='utf-8') as f:
        f.write(contenido)
    print('✅ Backup guardado como app.py.bak')
    
    # Guardar nuevo archivo
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(nuevo_archivo)
    print('✅ app.py actualizado con 61 vinos')
    
    # Verificar
    print(f'\n📊 Total vinos en nuevo diccionario: {len(nuevos_vinos)}')
    print('\n📝 Primeros 5 vinos actualizados:')
    items = list(nuevos_vinos.items())[:5]
    for key, value in items:
        print(f'  {key}: {value["nombre"]} - {value["puntuacion"]} pts')
else:
    print('❌ No se encontró VINOS_MUNDIALES en app.py')
