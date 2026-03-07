# Cómo dar buena impresión con Vino Pro ante cocineros y hosteleros (Valladolid)

Tu app ya está preparada para impresionar a profesionales del sector en Valladolid. Sigue esta guía rápida antes y durante la demo.

---

## Antes de la demo

1. **Tesseract instalado**  
   Si van a escanear etiquetas, ejecuta:  
   `.\scripts\verificar_tesseract.ps1`  
   Si falla, instala Tesseract (ver `docs/INSTALAR_TESSERACT_WINDOWS.md`).

2. **Backend arrancado**  
   En una terminal: `python main.py`  
   Deberías ver cargados, entre otros:  
   - `espana.json`  
   - `espana_ampliado.json`  
   - `espana_castilla_leon.json` (vinos de prestigio de Ribera, Rueda, Toro, Cigales).

3. **Probar en local**  
   Abre `http://127.0.0.1:8001` y prueba:
   - Buscar **"Vega Sicilia"**, **"Ribera del Duero"**, **"Verdejo Rueda"**, **"Pingus"**, **"Belondrade"**, **"Numanthia"**, **"Cigales"**.
   - Escanear una etiqueta (si Tesseract está instalado).
   - Preguntar al experto en vinos por un vino para cordero o para pescado.

4. **Si quieres enseñarla en el móvil**  
   Ejecuta `.\scripts\iniciar_ngrok.ps1` y comparte el enlace (ver `docs/USO_NGROK.md`).

---

## Durante la demo: qué enseñar

- **Catálogo de Castilla y León**  
  Buscar "Ribera", "Rueda", "Toro", "Cigales", "Vega Sicilia", "Belondrade", "Numanthia".  
  Verás referencias que conocen y descripciones/maridajes pensados para sala y cocina.

- **Escaneo de etiqueta**  
  Escanear una botella (p. ej. un Ribera o un Verdejo) y que vean el resultado al momento.

- **Experto en Vinos virtual**  
  Preguntas del tipo: "¿Qué vino me recomiendas para un lechazo asado?" o "¿Un blanco para mariscos?".

- **Detalle del vino**  
  Enseñar que cada vino lleva descripción, notas de cata, maridaje y precio orientativo; lenguaje pensado para profesionales.

---

## Mensaje clave

"Con Vino Pro tenéis en un solo sitio un catálogo serio de vinos, con Ribera, Rueda, Toro, Cigales y el resto de España, descripciones y maridajes útiles para carta y sala, escaneo de etiqueta y un experto en vinos virtual para recomendar. Pensado para hostelería y cocina."

---

## Si algo falla

- **Error al escanear:** "El escaneo requiere un componente que instalamos en el servidor; en local ya está listo." (Tesseract).
- **Lentitud:** La primera búsqueda puede tardar un poco; las siguientes son rápidas.
- **Sin internet en el local:** La app corre en tu PC; si usas ngrok, necesitan internet en el móvil para abrir el enlace.
