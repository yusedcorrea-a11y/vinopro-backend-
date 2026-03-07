# Home – Especificación definitiva ("Biblia de la Home")

**Objetivo:** Visión inmersiva (viñedo a pantalla completa), control ergonómico (botones abajo con glassmorphism), identidad de marca (logo serif, zorrito transparente). Ejecutar sin desviarse.

**Principio:** Creatividad medida, límites claros. No tocar navegación ni API (Render).

---

## 1. Lo que NO se toca

- Estructura de navegación (escáner, bodega, perfil, etc.).
- Conexión con el backend en Render.
- No tercer botón. No animaciones pesadas.

---

## 2. Orden de implementación (ejecutar en este orden)

| # | Elemento | Acción |
|---|----------|--------|
| 1 | **Fondo** | Imagen del viñedo **a pantalla completa**. `resizeMode: 'cover'`, contenedor full screen (`flex: 1`). Que las copas y el atardecer envuelvan toda la pantalla. |
| 2 | **Logo** | **VINO PRO IA** unificado en 1 o 2 líneas. Tipografía **Serif** elegante. Más peso visual (bold). Sin cortes raros entre palabras. |
| 3 | **Zorrito** | Asset en **PNG transparente**. Sin círculo blanco. Que flote sobre el viñedo en zona equilibrada (esquina o centro según composición). |
| 4 | **Botones abajo** | En la **parte inferior**. Sobre una **barra con Glassmorphism** suave (traslúcida + blur). Ancho completo, padding vertical cómodo. Botones centrados o con separación equilibrada. |
| 4a | **Copy de botones** | · **"Habla con el experto en vinos"** (icono burbuja/conversación). · **"Descubre un vino"** (icono cámara o lupa). |
| 4b | **Microcopy** | Debajo de los botones: **"Tu experto en vinos personal con IA"**. Tamaño pequeño, color suave (gris claro o blanco con opacidad). Sin robar protagonismo. |
| 5 | **Menú lateral** | Sustituir **emojis por iconos de línea** (Lucide o Ionicons). **Modo oscuro:** color **burdeos** de marca (quitar amarillo). **Glassmorphism** en el panel del menú para que se vea el viñedo detrás. |
| 6 | **Limpieza** | Eliminar el texto **"Sin escaneos en esta sesión"** de la Home. Si no hay escaneos, no mostrar nada. |

---

## 3. Resumen para ejecución (checklist)

- [ ] Fondo: imagen viñedo full screen, `cover`
- [ ] Logo: VINO PRO IA unificado, serif, bold
- [ ] Zorrito: PNG transparente, sin círculo blanco
- [ ] Botones: abajo, barra glassmorphism; "Habla con el experto en vinos" (icono) + "Descubre un vino" (icono)
- [ ] Microcopy: "Tu experto en vinos personal con IA" (discreto)
- [ ] Menú: iconos línea, burdeos, glassmorphism
- [ ] Quitar: "Sin escaneos en esta sesión"

---

## 4. Prompt Maestro (para pegar a Cursor al abrir HomeScreen)

```
Ejecuta la fase de lujo de la HOME. Solo esta pantalla, sin tocar API ni otras pantallas.

1. Fondo: Imagen del viñedo a pantalla completa (resizeMode cover, contenedor flex:1).
2. Logo: Unificar "VINO PRO IA" en el header con tipografía Serif elegante y mayor peso (bold).
3. Zorrito: Asset PNG transparente, sin círculo blanco; que flote sobre el viñedo.
4. Botones: Mover a la parte inferior. Contenedor con Glassmorphism (traslúcido + blur), ancho completo.
   - "Habla con el experto en vinos" con icono burbuja.
   - "Descubre un vino" con icono cámara/lupa.
5. Microcopy debajo de los botones: "Tu experto en vinos personal con IA" (tamaño pequeño, color suave).
6. Menú lateral: Sustituir emojis por iconos Lucide/Ionicons. Modo oscuro en burdeos. Fondo del panel con glassmorphism.
7. Eliminar el texto "Sin escaneos en esta sesión".
```

---

## 5. Validación

Tras aplicar: `npx expo start --clear --port 8083` → recargar en móvil (r en terminal).

---

*Spec cerrada por equipo (DeepSeek + Gemini + Yused). No tocar más hasta que sea perfecta en el móvil.*
