# Leer el archivo
with open('app.py', 'r', encoding='utf-8') as f:
    lineas = f.readlines()

# Corregir líneas problemáticas
if len(lineas) > 630:
    lineas[630] = '# 2. Análisis normal para vinos no en DB\n'
    print('✅ Línea 631 corregida')

if len(lineas) > 631:
    # Si la línea 632 también tiene el mismo error, la corregimos
    if '} 2. Análisis normal' in lineas[631]:
        lineas[631] = '# 2. Análisis normal (continuación)\n'
        print('✅ Línea 632 corregida')

# Guardar el archivo corregido
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lineas)
print('✅ app.py corregido completamente')

# Verificar la corrección
print('\n📝 Líneas 630-634 después de corregir:')
for i in range(630, 635):
    if i < len(lineas):
        print(f'  {i+1}: {lineas[i].strip()}')
