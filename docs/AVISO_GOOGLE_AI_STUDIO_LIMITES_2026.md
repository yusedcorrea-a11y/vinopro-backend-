# Aviso Google AI Studio – Límites y facturación (marzo/abril 2026)

**Resumen del email recibido:** Google anuncia cambios en los límites de uso y facturación de la API Gemini. Esto afecta a VINO PRO IA porque usamos Gemini para **visión (escáner de etiquetas)**, **sumiller en nube** y, opcionalmente, **traducción** cuando está configurada `GOOGLE_API_KEY`.

---

## Qué dice el email (resumen)

| Fecha | Cambio |
|-------|--------|
| **16 marzo 2026** | Límites de **gasto por proyecto** opcionales. Si configuras un tope y el proyecto lo supera, las peticiones se pausan en ~10 minutos. Los proyectos se reanudan el primer día del mes siguiente o al actualizar/eliminar el límite. |
| **1 abril 2026** | **Límites por nivel de cuenta (Tier).** Cada nivel tiene un tope máximo de gasto mensual. Si el gasto total de la cuenta llega al límite, las peticiones a la API Gemini se **suspenden hasta el mes siguiente**. Las subidas de nivel son automáticas según gasto y antigüedad. |

**Qué debes hacer (según Google):**

1. **Comprobar tu nivel:** Entra en [Google AI Studio](https://aistudio.google.com) y revisa tu nivel de uso actual y los límites (RPM/TPM y gasto).
2. **Revisar el gasto:** Evalúa el historial de gastos para ver si el límite de tu nivel te puede dejar sin servicio a mitad de mes.
3. **Límite opcional por proyecto (desde 16 marzo):** Si quieres, configura un límite de gasto por proyecto para que, si te pasas, solo se pause ese proyecto y no te lleves sorpresas en la factura.
4. **Excepción:** Si necesitas un límite mayor al de tu nivel, usa el [formulario de excepción](https://support.google.com/googleapi/answer/...) que indica el correo.

---

## Qué tenemos ya resuelto en el código (VINO PRO)

| Aspecto | Estado |
|---------|--------|
| **Errores 429 / quota / resource_exhausted** | ✅ En `vision_wine_service.py` y flujos que usan Gemini se capturan estos errores y se devuelve un mensaje claro al usuario (ej. "Límite de uso de la IA alcanzado. Espera un minuto o escribe el nombre del vino abajo."). La app no se cae. |
| **Traducción sin depender solo de Gemini** | ✅ La traducción del chat y de la comunidad usa **LibreTranslate** por defecto. La ruta con Gemini (`traducir_con_gemini_vino`) es opcional; si Gemini falla o no hay clave, sigue funcionando LibreTranslate. |
| **Escáner y sumiller** | ⚠️ Dependen de `GOOGLE_API_KEY`. Si se alcanza el límite o se suspende la cuenta, el usuario verá el mensaje de “límite alcanzado” o “IA no disponible”; puede seguir usando búsqueda por texto o por código de barras. |

Es decir: **el producto no se rompe** si Google corta por límite; ya manejamos el fallo y damos alternativas. Lo que **no** podemos hacer desde código es evitar que Google te corte: eso depende de tu **nivel, gasto y límites** en la cuenta de facturación.

---

## Qué no está resuelto (depende de ti en la consola)

- **Revisar tu Tier actual** en Google AI Studio y los límites de gasto que aplican desde abril.
- **Configurar un límite de gasto opcional por proyecto** (desde 16 marzo) si quieres que, al superarlo, se pause solo ese proyecto y no seguir gastando.
- **Solicitar una excepción** (límite más alto) si el nivel asignado te queda corto para el uso esperado de VINO PRO.

---

## Conclusión

- **En el código:** Estamos **cubiertos** ante cuotas y errores de Gemini: mensajes claros y, donde aplica, fallback (LibreTranslate, búsqueda por texto).
- **En la cuenta de Google:** **No está resuelto** hasta que revises nivel, gasto y, si quieres, configures límite por proyecto o pidas excepción. Eso hay que hacerlo en [Google AI Studio](https://aistudio.google.com) y en la cuenta de facturación asociada.

Cuando tengas el video para Google Play listo y enviado, conviene dedicar unos minutos a entrar en AI Studio y revisar nivel y límites para planificar abril sin sustos.
