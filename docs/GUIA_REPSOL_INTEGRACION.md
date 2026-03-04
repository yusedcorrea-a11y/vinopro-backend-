# Integración Guía Repsol – Dónde tomar el vino

## Investigación (2026-02-21)

### ¿Podemos enlazar a un sitio concreto donde tomar “este” vino?

- **API pública:** Guía Repsol **no ofrece API pública** para desarrolladores. No hay documentación de integración ni parámetros de búsqueda por vino o por establecimiento en la URL.
- **Buscador web:** La URL `https://www.guiarepsol.com/es/buscador/` no acepta parámetros de búsqueda visibles (probado `?q=rioja` sin efecto en resultados). La búsqueda se hace en la propia página/app.
- **Conclusión:** No es posible, con la información pública actual, generar un enlace que lleve a “restaurantes/vinotecas donde sirven este vino concreto”. Solo podemos enlazar a secciones genéricas de la guía.

### Lo que sí podemos hacer

Enlazar a secciones de Guía Repsol donde el usuario puede **buscar dónde tomar vino** en general (vinotecas, bodegas, restaurantes):

| Enlace | Uso recomendado |
|--------|------------------|
| [Vinotecas y Bodegas (Soletes)](https://www.guiarepsol.com/es/soletes/vinotecas-y-bodegas/) | Dónde ir a tomar vinos / vinotecas con Solete. |
| [Vinos y bodegas](https://www.guiarepsol.com/es/comer/vinos-y-bodegas/) | Reportajes y selección de vinos y bodegas. |
| [Buscador Guía Repsol](https://www.guiarepsol.com/es/buscador/) | Buscar restaurantes/establecimientos (el usuario escribe allí). |

En Vino Pro IA hemos añadido un enlace tipo **“¿Dónde tomarlo? Buscar en Guía Repsol”** que apunta a la sección de **Vinotecas y Bodegas**, para que el usuario pueda explorar sitios donde probar vinos (España/Portugal).

### Si en el futuro hubiera API o URLs con query

- Si Repsol publicara un parámetro de búsqueda (p. ej. `?q=nombre+vino` o `?establecimiento=id`), se podría:
  - Añadir en el backend una función que monte la URL con el nombre del vino (o región).
  - Mostrar ese enlace en la página de compra o en la respuesta del sumiller como “Dónde tomarlo en Guía Repsol”.
- Mientras tanto, el enlace genérico a Vinotecas y Bodegas ya da valor: el usuario ve dónde encontrar sitios para tomar vino.
