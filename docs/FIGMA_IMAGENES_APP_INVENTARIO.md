# Inventario de imágenes de la app – Para subir a Figma

**Uso:** Tienes que subir tú los archivos a Figma (Figma no lee tu disco). Este doc lista **todas** las imágenes y dónde están para que copies la carpeta o arrastres los archivos.

---

## 1. Iconos y branding (app móvil y web)

**Carpeta en tu PC:**  
`backend_optimized/docs/app-imagenes-revision/`

| Archivo | Uso en la app |
|---------|----------------|
| `00-logo-master.png` | Logo principal (master para variantes) |
| `01-icon.png` | Icono de la app (Play Store, escritorio) |
| `02-splash-icon.png` | Pantalla de carga al abrir la app |
| `03-android-icon-foreground.png` | Icono adaptativo Android (primer plano) |
| `04-android-icon-background.png` | Fondo del icono adaptativo Android |
| `05-android-icon-monochrome.png` | Icono monocromo (Android 13+) |
| `06-favicon.png` | Favicon (web) |
| `07-react-logo.png` | Referencia (sustituir por branding si se usa) |

**En Figma:** Crear una página o sección "App – Iconos y branding" y subir estos 8 archivos (arrastrar la carpeta o los PNG).

---

## 2. Fondos de pantalla (web)

**Carpeta en tu PC:**  
`backend_optimized/static/images/`

**Modo claro (fondos de páginas):**

| Archivo | Página / uso |
|---------|----------------|
| `vino-pro-ia-fondo-claro-espectacular.jpg` | Inicio (viñedo espectacular) |
| `vino-pro-ia-fondo-escanear.jpg` | Escanear |
| `vino-pro-ia-fondo-registrar.jpg` | Registrar |
| `vino-pro-ia-fondo-preguntar.jpg` | Preguntar / Sumiller |
| `vino-pro-ia-fondo-mibodega.jpg` | Mi Bodega |
| `vino-pro-ia-fondo-dashboard.jpg` | Dashboard |
| `vino-pro-ia-fondo-adaptador-claro.jpg` | Adaptador (restaurantes) |
| `vino-pro-ia-fondo-planes-claro.jpg` | Planes |

**Modo oscuro:**

| Archivo | Página / uso |
|---------|----------------|
| `vino-pro-ia-fondo-oscuro-espectacular.jpg` | Inicio oscuro (bodega) |
| `vino-pro-ia-fondo-escanear-oscuro.jpg` | Escanear oscuro |
| `vino-pro-ia-fondo-registrar-oscuro.jpg` | Registrar oscuro |
| `vino-pro-ia-fondo-preguntar-oscuro.jpg` | Preguntar oscuro |
| `vino-pro-ia-fondo-mibodega-oscuro.jpg` | Mi Bodega oscuro |
| `vino-pro-ia-fondo-dashboard-oscuro.jpg` | Dashboard oscuro |
| `vino-pro-ia-fondo-adaptador-oscuro.jpg` | Adaptador oscuro |
| `vino-pro-ia-fondo-planes-oscuro.jpg` | Planes oscuro |

**Otras en esa carpeta:**  
`vino-pro-ia-fondo-claro.jpg`, `vino-pro-ia-fondo-inicio.jpg` (alternativas; el CSS usa sobre todo las de la tabla).

**En Figma:** Crear una página "Fondos – Web" y subir los JPG (por ejemplo solo los que uses en los diseños, o todos para tener biblioteca completa).

---

## 3. Cómo llevarlas a Figma

1. Abre Figma y tu proyecto (o crea uno "VINO PRO IA").
2. En el panel izquierdo: **Assets** o crea una página "Assets app".
3. Arrastra:
   - La carpeta **`docs/app-imagenes-revision`** (iconos y logo), o los PNG uno a uno.
   - Los **JPG de `static/images/`** que quieras (fondos). Puedes crear en Figma una carpeta "Fondos" y subir solo los que vayas a usar en los frames.
4. Opcional: en Figma puedes marcar algunos como "Component" o agrupar por tipo (Iconos, Fondos claro, Fondos oscuro).

**Rutas absolutas (por si las copias desde otra máquina):**

- Iconos/branding:  
  `[tu proyecto]/backend_optimized/docs/app-imagenes-revision/`
- Fondos web:  
  `[tu proyecto]/backend_optimized/static/images/`

---

## 4. Imágenes de vinos (placeholders)

La app usa imágenes por tipo de vino (tinto, blanco, rosado, espumoso, generico) en `static/images/vinos/`. Esa carpeta tiene solo un README; las imágenes se generan o se asignan por código. Para Figma no son obligatorias a menos que quieras diseñar tarjetas de vino con foto: en ese caso puedes usar placeholders genéricos (botella tinto, blanco, etc.) y luego sustituir por las reales en código.

---

**Resumen:** No hay un "archivo único" con todas las imágenes; están en dos sitios. Este doc es el inventario. Para Figma: sube la carpeta de iconos y, si quieres, los fondos de `static/images/`. Si me dices qué diseño vas a hacer primero (p. ej. solo Inicio), te digo el mínimo de imágenes que necesitas subir.
