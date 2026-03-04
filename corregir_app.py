# Leer el archivo
with open('app.py', 'r', encoding='utf-8') as f:
    lineas = f.readlines()

# Corregir la línea 631 (índice 630) que tiene el error
if len(lineas) > 630:
    # La línea actual es: "} 2. Análisis normal para vinos no en DB"
    # La cambiamos a: "# 2. Análisis normal para vinos no en DB"
    lineas[630] = '# 2. Análisis normal para vinos no en DB\n'
    print('✅ Línea 631 corregida')

# Guardar el archivo corregido
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lineas)
print('✅ app.py corregido')

# Verificar la corrección
print('\n📝 Líneas 630-633 después de corregir:')
for i in range(630, 634):
    if i < len(lineas):
        print(f'  {i+1}: {lineas[i].strip()}')
