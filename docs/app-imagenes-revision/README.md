# Imágenes de la app – Orden para revisión y Canva

Carpeta con todas las imágenes de VINO PRO numeradas para analizar **pantalla por pantalla** y, cuando toque, pasarlas a Canva para retoque. Canva te las puede devolver con el **mismo nombre** para sustituir en la app.

---

## Orden actual (assets que ya existen)

| Nº | Archivo | Dónde se usa | Qué tocar / notas |
|----|---------|--------------|-------------------|
| **01** | `01-icon.png` | Icono de la app (Play Store y escritorio) | Aspecto general, que se vea bien en pequeño. |
| **02** | `02-splash-icon.png` | Pantalla de carga al abrir la app | Logo/ilustración que ve el usuario al iniciar. |
| **03** | `03-android-icon-foreground.png` | Icono adaptativo Android (primero plano) | Debe verse bien sobre el color de fondo (04). |
| **04** | `04-android-icon-background.png` | Fondo del icono adaptativo Android | Color/fondo detrás del 03. |
| **05** | `05-android-icon-monochrome.png` | Icono monocromo (Android 13+) | Versión en un solo color para temas. |
| **06** | `06-favicon.png` | Favicon si hay web | Pequeño, reconocible. |
| **07** | `07-react-logo.png` | (Referencia / posible uso interno) | Sustituir por branding VINO PRO si se usa. |

---

## Capturas de pantalla (añadir tú cuando las tengas)

Estas son las **pantallas de la app** que conviene tener como imagen para analizar y luego retocar en Canva (textos, recortes, etc.). Cuando hagas las capturas, **guárdalas aquí con este número y nombre**:

| Nº | Nombre sugerido | Pantalla | Texto/idea para Canva |
|----|------------------|----------|------------------------|
| **10** | `10-pantalla-inicio.png` | Inicio / home | "Tu sumiller virtual, siempre contigo" |
| **11** | `11-pantalla-chat.png` | Chat / sumiller IA | "Recomendaciones personalizadas al instante" |
| **12** | `12-pantalla-escaneo.png` | Escáner de etiquetas | "Escanea y descubre el vino" |
| **13** | `13-pantalla-comunidad.png` | Comunidad / feed | "Comparte y descubre vinos con la comunidad" |
| **14** | `14-pantalla-noticias.png` | Noticias | "Noticias y tendencias del mundo del vino" |
| **15** | `15-pantalla-perfil-planes.png` | Perfil / planes PRO | "Desbloquea funciones PRO" |

Cómo obtenerlas: abre la app en el móvil o en el emulador, ve a cada pantalla y haz captura de pantalla. Pasa las fotos al PC y renómbralas como en la tabla (ej. `10-pantalla-inicio.png`) y guárdalas en esta misma carpeta.

---

## Flujo con Canva

1. **Revisar:** Abre esta carpeta y mira las imágenes en orden (01, 02, 03… luego 10, 11, 12…).
2. **Decidir:** Anota qué números quieres retocar (ej. "cambiar 01 y 02, y añadir texto a 11").
3. **Subir a Canva:** En Canva, sube solo esos archivos (o arrastra desde esta carpeta).
4. **Retocar:** Editas en Canva (textos, filtros, recortes, etc.).
5. **Descargar con el mismo nombre:** Al exportar desde Canva, guarda el archivo con **exactamente el mismo nombre** (ej. `01-icon.png`) y **sustituye** el archivo en esta carpeta.
6. **Llevar a la app:**  
   - Para **01–07:** copia los archivos ya retocados al proyecto:  
     `frontend/assets/images/`  
     (renombrando sin el número: `01-icon.png` → `icon.png`, etc., según la tabla de "Dónde se usa").  
   - Para **10–15:** son para Play Store / anuncios; no hace falta sustituir nada en el código, solo usarlas en la ficha y en creativos.

---

## Ruta de esta carpeta

```
.../backend_optimized/docs/app-imagenes-revision/
```

Aquí están las copias numeradas. Los originales de icono y splash siguen en `frontend/assets/images/`. Cuando Canva te devuelva un archivo con el mismo nombre, puedes reemplazar primero aquí y luego copiar al frontend cuando apruebes el diseño.
