# Leer el archivo
with open('app.py', 'r', encoding='utf-8') as f:
    lineas = f.readlines()

# Buscar y corregir la línea de vino_mock
encontrado = False
for i in range(len(lineas)):
    if '"vino_mock"' in lineas[i]:
        # Añadir llave de cierre después de la línea de descripción
        if i+8 < len(lineas) and 'Sabor equilibrado' in lineas[i+8]:
            lineas[i+8] = lineas[i+8].rstrip() + '\n    }\n'
            encontrado = True
            print(f'✅ Llave de cierre añadida en línea {i+9}')
            break

if encontrado:
    # Guardar el archivo corregido
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(lineas)
    print('✅ app.py corregido')
    
    # Verificar las líneas alrededor
    print('\n📝 Líneas después de la corrección:')
    for j in range(i, i+10):
        if j < len(lineas):
            print(f'  {j+1}: {lineas[j].strip()}')
else:
    print('❌ No se encontró "vino_mock"')
