# Escáner: códigos de barras y QR

VINO PRO ofrece **dos formas** de usar códigos en la app:

## 1. Escáner en vivo (app móvil)

En la pantalla **Escanear**, el usuario puede elegir **"Escáner en vivo"**. Se abre la cámara en tiempo real y se detectan:

- **QR**
- **EAN-13, EAN-8**
- **UPC-A, UPC-E**
- **Code 128, Code 39**

Cuando se lee un código:

- Si el contenido es un **EAN/GTIN** (8–14 dígitos), la app envía `POST /escanear` con `{ "codigo_barras": "..." }`.
- Si es otro contenido (por ejemplo una URL en un QR), se envía `{ "texto": "..." }`.

El backend responde con la ficha del vino (BD local u Open Food Facts). La app usa **expo-camera** con `barcodeScannerEnabled` y un throttle de 3 segundos para no repetir la misma lectura.

## 2. Foto de etiqueta (cámara o galería)

El usuario hace una **foto** o elige una imagen de la galería. El backend:

1. **Código de barras (EAN)** en la imagen (vía **pyzbar**) → búsqueda en Open Food Facts.
2. **QR** en la imagen que contenga un EAN → mismo uso.
3. **Texto (OCR)** → búsqueda en la BD local y en OFF.

Si no se detecta ningún código en la imagen, el flujo sigue con OCR y todo funciona igual.

## Dependencia opcional: libzbar (para pyzbar)

El backend usa la librería **pyzbar**, que necesita **libzbar** instalado en el sistema:

- **Windows:** Puedes instalar libzbar (DLL) o dejar que solo funcione el OCR. Si `pyzbar` no está o falla al importar, el servicio devuelve lista vacía y el escáner usa solo OCR.
- **Linux:** `sudo apt install libzbar0` (o equivalente).
- **macOS:** `brew install zbar`.

Para comprobar si funciona: tras escanear una etiqueta que tenga código de barras visible, en la terminal del backend debería aparecer algo como `[ESCANEAR] Código de barras/QR detectado en imagen: 8412345...`.

Si no ves ese log, la foto no tenía código legible o libzbar no está instalado; en ese caso la identificación sigue por OCR y texto.

## Encontrar vinos de nuestra BD por código de barras

Si un vino está en la base de datos local (p. ej. `data/espana.json`) y quieres que al escanear **solo el código de barras** salga ese vino, añade en su ficha el campo opcional **`ean`** (o **`codigo_barras`**) con el EAN/GTIN de 8 a 14 dígitos. Ejemplo:

```json
"vina_pedrosa_crianza": {
  "nombre": "Viña Pedrosa Crianza",
  "bodega": "Hnos Pérez Pascuas",
  "ean": "8412345678901",
  ...
}
```

Al escanear ese código, se buscará primero en la BD local y, si coincide, se devolverá la ficha sin llamar a Open Food Facts.
