# Pantalla "Preguntar al sumiller" – Especificación (aspecto + función)

**Objetivo:** Primero cerrar el aspecto visual (limpieza, jerarquía, glassmorphism). Luego la funcionalidad (modo, perfil, botón Preguntar).

**Principio:** Misma disciplina que la Home: creative + centered. Sin duplicados, con contenedores claros y microcopy que guíe.

---

## 1. Lo que NO se toca

- Estructura general: modo + perfil + consultas + pregunta + botón.
- Aviso Premium (mensaje claro).
- Placeholder del campo ("Ej: ¿Qué vino con carne?").

---

## 2. Auditoría visual (qué corregir YA)

| Problema | Acción |
|----------|--------|
| **Duplicación de modo** | Aparece "Modo: Nube" y debajo otra vez "Modo: Nube 🎵". Dejar **una sola** línea o chip. |
| **Jerarquía pobre** | Todo con el mismo peso. Diferenciar cabecera, modo, perfil, pregunta y botón. |
| **Texto "IA Local es exclusiva para Premium"** | Flota sin contenedor. Poner en **bloque con contenedor suave** (gris claro o glassmorphism). Botón "Pasar a PRO" con estilo burdeos. |
| **Perfil "Aficionado"** | Parece campo de formulario. Mostrarlo como **tarjeta/chip seleccionable**; si hay más perfiles (Experto, Sumiller), que se vea como selector. |
| **"Últimas consultas (local)"** | Con "-- Seleccionar --" que no invita. **Eliminar** si no hay datos, o sustituir por mensaje amable: "Tus consultas aparecerán aquí". |
| **"Tu pregunta" + botón** | Botón "Preguntar" solo, sin contexto. **Integrar**: campo de texto con botón a la derecha (estilo buscador) o botón debajo con más presencia. |
| **Sin microcopy** | Añadir línea de apoyo bajo el campo: "Pregunta sobre maridajes, variedades, precios..." que desaparezca al escribir. |
| **Panel muy oscuro** (Gemini) | El panel bloquea toda la vista. **Glassmorphism**: efecto cristal esmerilado para que se vea el viñedo difuminado detrás mientras el usuario elige perfil y escribe. |

---

## 3. Propuesta de aspecto (primera pasada)

### 3.1 Cabecera
- **Una sola línea clara:** p. ej. "VINO PRO IA" + "Preguntar al sumiller" (o solo "Preguntar al sumiller" si el logo va en la Home).
- Sin duplicados de título ni de modo.

### 3.2 Modo
- "Modo: Nube" en **badge o chip** (color azul claro o neutro).
- El detalle 🎵 como complemento, no protagonista.

### 3.3 Bloque Premium
- Recuadro sutil (gris claro o glassmorphism muy suave).
- Texto: "IA Local es exclusiva para Premium".
- Botón "Pasar a PRO" con estilo burdeos.

### 3.4 Perfil
- "Aficionado" (y resto si existen) como **tarjeta o chip seleccionable**.
- Que se entienda que es un selector, no un campo de texto.

### 3.5 Últimas consultas
- Si no hay datos: no mostrar "-- Seleccionar --". O texto: "Tus consultas aparecerán aquí".

### 3.6 Pregunta + botón
- Campo "Tu pregunta" y botón "Preguntar" **integrados** (ej. botón a la derecha del campo o debajo con más presencia).
- Microcopy bajo el campo: "Pregunta sobre maridajes, variedades, precios..." (oculto al escribir).

### 3.7 Panel y fondo
- **Glassmorphism** en el panel: fondo traslúcido + blur para que se vea el viñedo (o fondo de la app) difuminado detrás.

---

## 4. Orden de implementación (aspecto primero)

1. Quitar duplicado "Modo: Nube".
2. Cabecera única y clara.
3. Modo como badge/chip.
4. Bloque Premium con contenedor + botón "Pasar a PRO".
5. Perfil como chips/tarjetas seleccionables.
6. Últimas consultas: eliminar "-- Seleccionar --" o mensaje amable.
7. Integrar campo pregunta + botón; microcopy de apoyo.
8. Aplicar glassmorphism al panel (fondo traslúcido).

---

## 5. Siguiente fase (funcionalidad)

Cuando el aspecto esté cerrado:

- Comportamiento del selector de perfil.
- Lógica Modo Nube vs Local.
- Integración con Consulta ID.
- Historial de escaneos (sesión).
- Acción del botón Preguntar.

---

## 6. Resumen

| Elemento | Acción |
|----------|--------|
| Cabecera | Una línea, sin duplicados |
| Modo | Badge/chip, sin repetir |
| Premium | Contenedor suave + botón burdeos |
| Perfil | Chips/tarjetas seleccionables |
| Últimas consultas | Sin "-- Seleccionar --" o mensaje amable |
| Pregunta + botón | Integrados; microcopy que desaparezca al escribir |
| Panel | Glassmorphism (viñedo/fondo difuminado detrás) |

---

## 7. Prompt Maestro (para pegar en Cursor)

Abrir **ChatScreen.tsx** o **PreguntarSumillerScreen.tsx** (o el archivo de la pantalla de chat/sumiller) y pegar lo siguiente. **Solo aspecto (UI); no tocar la lógica de la IA.**

```
Aplica la especificación de la pantalla "Preguntar al sumiller" (CHAT_ESPEC.md). Concentración total en el ASPECTO. No toques la lógica todavía.

ORDEN DE EJECUCIÓN

1. Contenedor principal: Envuelve todo el formulario en un panel con Glassmorphism (fondo translúcido + blur) para que el viñedo de fondo siga visible.

2. Cabecera limpia:
   - Título: "VINO PRO IA" (o el que use la app)
   - Subtítulo: "Preguntar al sumiller"
   - Eliminar cualquier duplicado de "Modo: Nube" en la cabecera.

3. Modo como badge: "Modo: Nube" dentro de un badge/chip (fondo suave azul o gris). Icono ☁️ o 🎵 como detalle, no protagonista. Aviso "IA Local Premium" en línea fina y distinguida.

4. Bloque Premium: Envolver "IA Local es exclusiva para Premium" + "Pasar a PRO" en un contenedor con glassmorphism suave, bordes redondeados, padding. El enlace "Pasar a PRO" con estilo botón burdeos.

5. Perfil como chips: Aficionado, Experto, etc. como chips seleccionables en fila. El activo en color burdeos.

6. Últimas consultas: Si no hay datos, mostrar "Tus consultas aparecerán aquí". Eliminar "-- Seleccionar --". Si hay consultas, lista limpia.

7. Campo "Tu pregunta" + botón integrados: Diseño tipo buscador (campo a la izquierda, botón "Preguntar" a la derecha) o botón debajo con más presencia. Placeholder: "Ej: ¿Qué vino con carne?"

8. Microcopy: Bajo el campo, texto pequeño "Pregunta sobre maridajes, variedades, precios..." (color suave; puede ocultarse al escribir). Al final del panel, frase discreta: "Tu sumiller personal con IA".

9. Limpieza: Eliminar textos duplicados. Jerarquía visual clara: que parezca una conversación de lujo, no un cuestionario.

ESTILOS: Glassmorphism en panel y bloques secundarios. Fondo de pantalla = viñedo (misma que Home). Tipografía limpia, espaciado generoso.

SIGUIENTE FASE (después del aspecto): comportamiento chips de perfil, lógica Nube/Local, Consulta ID, historial de escaneos, acción del botón Preguntar.
```

**Checklist:** Cabecera sin duplicados | Modo como badge | Bloque Premium con contenedor y botón | Perfil como chips | Últimas consultas con mensaje amable si vacío | Campo + botón integrados | Microcopy visible | Glassmorphism aplicado | Fondo viñedo visible.

---

*Spec + Prompt Maestro. Primero aspecto, luego función. Alineada con DeepSeek + Gemini.*
