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

### 4. Si `tesseract` no se reconoce

- Cierra **todas** las terminales donde esté corriendo el backend y ábrelas de nuevo.
- Si sigue sin funcionar, comprueba que la carpeta de instalación esté en el PATH:
  - **Configuración de Windows** → **Sistema** → **Acerca de** → **Configuración avanzada del sistema** → **Variables de entorno**.
  - En **Variables del sistema**, edita **Path** y añade (si no está):  
    `C:\Program Files\Tesseract-OCR`
  - Acepta y vuelve a abrir PowerShell.

---

### 5. Reiniciar el backend

Después de instalar Tesseract:

1. Detén el servidor de Vino Pro IA (Ctrl+C en la terminal donde ejecutas `python main.py`).
2. Vuelve a iniciarlo: `python main.py`.

A partir de ahí, el escaneo de etiquetas debería funcionar sin ese mensaje de "componente adicional".
