# Primera página de la app – Especificación final (idioma)

**Objetivo:** Dejar la pantalla de selección de idioma como la primera impresión definitiva: clara, acogedora y con identidad, sin añadir complejidad innecesaria.

**Principio:** Creatividad en el detalle (copy, feedback, un toque de marca). Centrado en no tocar el flujo que ya funciona (idioma primero, luego el resto).

---

## 1. Lo que NO se toca

- El usuario abre la app y lo primero que ve es **elegir idioma**. Eso se mantiene.
- No cambiar a otro tipo de onboarding ni añadir pasos extra antes del idioma.

---

## 2. Estructura y textos

| Elemento | Qué hacer |
|----------|-----------|
| **Título** | Mantener **"VINO PRO"** como marca principal. |
| **Subtítulo** | Añadir una sola línea debajo: **"Selecciona tu idioma"** (o el equivalente traducido si esta pantalla se mostrara en otro idioma; si siempre es español hasta que elijan, este texto en español está bien). Da contexto sin saturar. |
| **Mensaje** | Mantener: *"Elige tu idioma. Podrás cambiarlo después en el menú."* Transmite que no es una decisión irreversible. |

---

## 3. Lista de idiomas

- **Bug a corregir:** En la lista hay una entrada **"वार्षिक"** (significa "Anual" en hindi). Eliminarla. El idioma Hindi debe aparecer solo como **"हिन्दी"**. Revisar que no haya más etiquetas erróneas en otros idiomas.
- **Agrupación (opcional):** Si la lista es muy larga (>10 idiomas), se puede agrupar en dos bloques con títulos suaves:
  - *"Europeos y latinos"* (o similar): Español, Inglés, Portugués, Francés, Alemán, Italiano…
  - *"Otros idiomas"*: Árabe, Ruso, Turco, Chino, Japonés, Coreano, हिन्दी…
  Si la lista es corta o ya se lee bien, no hace falta agrupar.
- **Banderas:** No añadir banderas por defecto. Si más adelante se quieren, hacerlo con cuidado (un idioma, varios países). Mejor no arriesgar en la primera versión final.

---

## 4. Interacción (centrado + un toque de calidad)

| Comportamiento | Especificación |
|----------------|----------------|
| **Al tocar un idioma** | Resaltar la fila con fondo suave **burdeos traslúcido** `#80002033` para que quede claro qué ha elegido. |
| **Botón "Continuar"** | **Deshabilitado** al inicio (gris, sin respuesta al toque). Al seleccionar un idioma se **activa** con el color de marca. No pulsable hasta que haya selección. |

---

## 5. Toque creativo (sin pasarse)

- **Paleta:** Usar el burdeos / tono de marca de VINO PRO para el estado "seleccionado" y para el botón Continuar activo. Que se note que es la misma app que el resto de pantallas.
- **Transición:** Si la app ya usa animaciones suaves, un pequeño feedback al seleccionar (p. ej. 150–200 ms) da sensación de pulido. No hace falta nada espectacular.

---

## 6. Resumen de implementación (Prompt Maestro para Cursor)

Aplicar **solo** en la pantalla de idioma, sin tocar el resto de la app:

1. **Limpieza de datos:** En la lista de idiomas, eliminar la entrada **वार्षिक**. El idioma Hindi debe aparecer solo como **हिन्दी**.
2. **Subtítulo:** Debajo del título "VINO PRO", añadir el texto: **"Selecciona tu idioma"**.
3. **Feedback visual:** Al tocar un idioma, resaltar la fila con fondo **#80002033** (burdeos traslúcido).
4. **Lógica del botón:** "Continuar" deshabilitado (gris, no pulsable) hasta que haya un idioma seleccionado; entonces activar con color de marca.
5. **Sin banderas:** No añadir iconos de banderas; diseño limpio solo con texto.

---

*Documento para alinear equipo y Cursor: primera página final, creativa en detalle y centrada en lo que ya funciona.*
