# Guía Repsol: ¿se puede abrir solo con la info de la ciudad? (solo explicación)

**Pregunta:** ¿Podemos hacer que al elegir Guía Repsol (España, Argentina, etc.) el usuario llegue directamente a la información **solo de esa ciudad** (como cuando en la web de Repsol pones "Valladolid" y te salen resultados de esa ciudad)?

---

## Respuesta corta

**Parcialmente, y depende de Repsol, no solo de nosotros.**

---

## Qué hace la app hoy

- El botón **"Buscar Soles Repsol cerca de mí"** abre una URL base de Repsol.
- Si el usuario **ha escrito algo en el campo de ciudad** arriba, el código añade `?q=...` a la URL (búsqueda en su web).
- Eso **no garantiza** que Repsol muestre una página “solo Valladolid”: su sitio decide cómo interpreta `q` (búsqueda interna, redirección, etc.).

---

## Qué haría falta para “solo ciudad” de verdad

1. **Que Repsol tenga URLs estables por ciudad o por país**  
   Ejemplo hipotético: `.../ciudad/valladolid` o parámetros oficiales documentados.  
   Sin documentación o API pública, solo podemos **adivinar** URLs y se rompen con el tiempo.

2. **API o embed oficial**  
   Si Repsol ofreciera widget o API con filtro por ciudad/país, entonces sí podríamos enlazar o incrustar “solo eso”. Hoy la app solo **abre su web** en una pestaña nueva.

3. **Scraping** (no recomendado)  
   Leer su HTML para extraer “solo ciudad” viola términos de uso y es frágil.

---

## Conclusión

- **Sí se puede intentar** mejorar el enlace si **encontramos** en su web URLs fijas por ciudad o parámetros que sí filtren bien (habría que probar país por país).
- **No se puede prometer** “solo información básica de esa ciudad” solo cambiando un parámetro, a menos que Repsol lo soporte explícitamente.
- **Alternativa:** mantener el flujo actual (abrir guía + opcional `?q=ciudad` si el usuario escribió ciudad) y, si en el futuro tienen API o URLs claras, actualizar `buildRepsolUrl()` en `static/js/geolocalizacion.js` y/o `services/enlaces_service.py`.

---

## Actualización: comodidad “ya sabemos dónde está”

**Implementado:** Si el usuario **ya buscó por ciudad** o **ya tiene coords en sesión** (tras usar el mapa con la API), al pulsar **“Abrir Guía Repsol con mi zona”**:

1. Si en el campo de ciudad hay **texto** (no solo coords) → abrimos Repsol con `?q=ese texto`.
2. Si el campo tiene **solo coords** pero tenemos **userCoords** → **geocodificación inversa** (Nominatim) para obtener **ciudad/localidad** y abrimos Repsol con `?q=Ciudad`.
3. Si no hay nada → abrimos la guía general.

Así se **ahorra** escribir otra vez en la lupa cuando ya localizamos su zona en la app. Repsol sigue siendo quien muestra resultados; nosotros solo les pasamos la búsqueda por URL.

*Doc de referencia + comportamiento actual.*
