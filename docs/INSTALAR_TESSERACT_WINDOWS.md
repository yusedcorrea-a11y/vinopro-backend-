# Instalar Tesseract OCR en Windows (Vino Pro IA)

El escaneo de etiquetas de vino usa **Tesseract OCR**. Es una dependencia del sistema que debe instalarse una sola vez en el equipo, no viene con el proyecto Python.

Si al escanear una etiqueta aparece el mensaje *"El escaneo requiere un componente adicional. Por favor, contacta al administrador"*, o en el log del servidor ves `TesseractNotFoundError`, sigue estos pasos.

---

## Opción A: Instalación con winget (un solo comando)

Si tienes **Windows Package Manager** (winget), en PowerShell ejecuta:

```powershell
winget install --id=UB-Mannheim.TesseractOCR -e --silent --accept-package-agreements --accept-source-agreements
```

El backend de Vino Pro está preparado para usar Tesseract en `C:\Program Files\Tesseract-OCR\` aunque no esté en el PATH. Después de instalar, **reinicia el backend** (`python main.py` o `python app.py`).

Para comprobar: abre una **nueva** terminal y ejecuta `tesseract --version`, o arranca el backend y prueba escanear una etiqueta desde la app.

---

## Opción B: Instalador manual

### 1. Descargar el instalador

1. Abre en el navegador:  
   **https://github.com/UB-Mannheim/tesseract/wiki**
2. Descarga la versión de **64 bits** (por ejemplo: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` o la más reciente que indique la página).

---

### 2. Instalar Tesseract

1. Ejecuta el instalador (puede requerir permisos de administrador).
2. Mantén las opciones por defecto.
3. En la pantalla **"Choose Components"**:
   - En **"Additional language data"** marca al menos:
     - **English**
     - **Spanish**
     - **Italian** (recomendado para etiquetas de vinos italianos)
   (Así el OCR podrá leer etiquetas en español, inglés e italiano.)
4. Completa la instalación hasta el final.

La instalación suele dejar Tesseract en `C:\Program Files\Tesseract-OCR\` y añadirlo al PATH del sistema.

---

### 3. Comprobar la instalación

Abre una **nueva** ventana de PowerShell (para que cargue el PATH actualizado) y ejecuta:

```powershell
tesseract --version
```

Deberías ver la versión de Tesseract. Si el comando no se reconoce, Tesseract no está en el PATH (ver sección 4).

---

### 4. Si `tesseract` no se reconoce — Comandos exactos para Lenovo IdeaPad 3

El backend busca Tesseract en `C:\Program Files\Tesseract-OCR\` por defecto. Si no lo encuentra, añade esa ruta al PATH.

**Opción 4a: Solo para la sesión actual (PowerShell)**

```powershell
$env:Path += ";C:\Program Files\Tesseract-OCR"
tesseract --version
```

**Opción 4b: Añadir al PATH del usuario de forma permanente (PowerShell como usuario)**

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Tesseract-OCR", "User")
```

Cierra y vuelve a abrir PowerShell para que el cambio surta efecto.

**Opción 4c: Añadir al PATH del sistema (PowerShell como Administrador)**

```powershell
$rutaActual = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($rutaActual -notlike "*Tesseract-OCR*") {
    [Environment]::SetEnvironmentVariable("Path", $rutaActual + ";C:\Program Files\Tesseract-OCR", "Machine")
    Write-Host "PATH actualizado. Cierra y abre una nueva terminal."
} else {
    Write-Host "Tesseract ya está en el PATH."
}
```

**Opción 4d: Variable de entorno TESSERACT_CMD (alternativa al PATH)**

Si prefieres no modificar el PATH, define la variable antes de arrancar el backend:

```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
python main.py
```

O en un archivo `.env` en la carpeta del proyecto:

```
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

**Verificar que funciona**

```powershell
# Comprobar que el ejecutable existe
Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe"

# Debe devolver True. Luego:
tesseract --version
```

**Opción 4e: GUI (Configuración de Windows)**

Configuración de Windows → Sistema → Acerca de → Configuración avanzada del sistema → Variables de entorno → Editar Path → Añadir `C:\Program Files\Tesseract-OCR`.

---

### 5. Reiniciar el backend

Después de instalar Tesseract:

1. Detén el servidor de Vino Pro IA (Ctrl+C en la terminal donde ejecutas `python main.py`).
2. Vuelve a iniciarlo: `python main.py`.

A partir de ahí, el escaneo de etiquetas debería funcionar sin ese mensaje de "componente adicional".
