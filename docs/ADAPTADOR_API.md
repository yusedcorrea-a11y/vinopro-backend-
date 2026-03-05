# API del Adaptador – Integración Mi Bodega con tu programa de restaurante

Conecta tu TPV o programa de restaurante (CoverManager, TheFork, etc.) a **Mi Bodega** de VINO PRO. Cuando un camarer@ vende un vino, tu programa llama a nuestra API y el inventario se actualiza en tiempo real en la app.

---

## 1. Obtener el token

1. Entra en la **página del Adaptador** en la web de VINO PRO:  
   `https://tu-dominio.com/adaptador`  
   (En producción: sustituir por la URL real del backend.)
2. La página te muestra un **token de API** único para tu restaurante. Guárdalo en lugar seguro.
3. Opcional: configura un **webhook URL** para que, cada vez que se actualice la bodega (venta o cambio manual), te enviemos el stock actualizado en un POST.

El token se usa en todas las llamadas como cabecera **X-API-Token**.

---

## 2. Registrar una venta (restar botella)

Cuando en tu programa se registra la venta de un vino, llama a este endpoint para restar esa botella de Mi Bodega.

**URL (producción):**

```
POST https://vinopro-backend-production.up.railway.app/api/adaptador/venta
```

**Cabeceras:**

| Cabecera          | Valor                          |
|-------------------|--------------------------------|
| `Content-Type`    | `application/json`             |
| `X-API-Token`     | Tu token del paso 1 (obligatorio) |
| `Accept`          | `application/json` (opcional)  |

**Cuerpo (JSON):**

| Campo        | Tipo   | Obligatorio | Descripción                          |
|-------------|--------|-------------|--------------------------------------|
| `vino_nombre` | string | Sí          | Nombre del vino vendido (como está en Mi Bodega) |
| `cantidad`    | number | No (default 1) | Unidades vendidas                    |

**Ejemplo de cuerpo:**

```json
{
  "vino_nombre": "Viña Pedrosa Reserva",
  "cantidad": 1
}
```

**Respuesta 200 – Venta registrada:**

```json
{
  "success": true,
  "message": "Vendido: Viña Pedrosa Reserva. Quedan 2 en esa entrada.",
  "stock_actualizado": [
    {
      "id": "uuid-botella",
      "vino_nombre": "Viña Pedrosa Reserva",
      "cantidad": 2,
      "anada": 2018,
      "ubicacion": "",
      "tipo": "tinto"
    }
  ]
}
```

**Respuesta 200 – Vino no encontrado en la bodega:**

```json
{
  "success": false,
  "message": "Vino no encontrado en la bodega. Añádelo antes en la app Mi Bodega.",
  "stock_actualizado": [...]
}
```

**Errores:**

- **400** – Falta la cabecera `X-API-Token`.
- **401** – Token no válido.

---

## 3. Ejemplo con cURL

Sustituye `TU_TOKEN` por el token que te dio la página del Adaptador.

```bash
curl -X POST "https://vinopro-backend-production.up.railway.app/api/adaptador/venta" \
  -H "Content-Type: application/json" \
  -H "X-API-Token: TU_TOKEN" \
  -d '{"vino_nombre": "Viña Pedrosa Reserva", "cantidad": 1}'
```

---

## 4. Consultar stock actual (solo lectura)

Para obtener el inventario actual sin modificar nada:

```
GET https://vinopro-backend-production.up.railway.app/api/bodega/stock
```

**Cabecera:** `X-API-Token: TU_TOKEN`

**Respuesta:** `{ "stock": [...], "total_entradas": N }`  
(formato de cada entrada igual que en `stock_actualizado` del POST /venta).

---

## 5. Flujo resumido

1. Dueño del restaurante: en la **app VINO PRO** añade sus vinos a **Mi Bodega** (mismo usuario/sesión que el token del Adaptador).
2. En la **web**, obtiene el token en **/adaptador** y lo configura en su TPV o programa.
3. Cuando un camarer@ vende un vino, el programa hace **POST /api/adaptador/venta** con el nombre del vino.
4. La bodega resta esa botella; el dueño ve el **inventario en tiempo real** en la app (y opcionalmente recibe el stock por webhook).

---

*Documento para integradores. Si necesitas soporte: contacto en la web de VINO PRO.*
