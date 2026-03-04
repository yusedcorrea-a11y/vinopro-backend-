# Checklist antes de subir VINO PRO IA

## Verificación automática (ya ejecutada)

El script `scripts/verificar_funcionalidades.py` comprueba con el servidor en marcha:

- **Páginas HTML**: Inicio, Escanear, Registrar, Preguntar, Bodega, Dashboard, Planes, Adaptador, Oferta crear, Mis ofertas, Set lang
- **API**: status, paises, vinos, check-limit
- **Búsqueda**: buscar-para-registrar, buscar
- **Bodega**: lista, registros-hoy
- **Escaneo**: POST analyze/text
- **Sumiller**: preguntar-sumiller (Nube)
- **IA Local solo Premium**: 401 sin header, 403 con session no PRO
- **Comprar**: página vino, API enlaces
- **Ofertas**: listar por vino, mis-ofertas
- **Historial escaneos**, **Analytics**, **Informes bodega PDF**, **Adaptador token**

Para repetir la verificación:

```bash
cd backend_optimized
python -m uvicorn app:app --host 127.0.0.1 --port 8001
# En otra terminal:
python scripts/verificar_funcionalidades.py
```

---

## Pruebas manuales recomendadas antes de producción

1. **Navegación**
   - [ ] Inicio: se ve el fondo, nav y mascota flotante (doble toque abre guía).
   - [ ] Todas las páginas del menú cargan (Escanear, Registrar, Preguntar, Mi Bodega, Dashboard, Planes, Adaptador).
   - [ ] Selector de idioma y modo oscuro funcionan.

2. **Escanear**
   - [ ] Búsqueda por texto (ej. "Rioja") devuelve resultados.
   - [ ] Subir una imagen de etiqueta (si tienes) y comprobar que responde.
   - [ ] Enlace "Comprar este vino" y "Registrar este vino" cuando aplica.

3. **Registrar**
   - [ ] Buscador rellena el formulario al elegir un resultado.
   - [ ] Usuario no PRO: si no hay resultados, formulario bloqueado y mensaje de pasar a PRO.
   - [ ] Envío del formulario registra el vino y muestra éxito (y enlace a oferta si eres PRO).

4. **Preguntar**
   - [ ] Modo Nube: preguntas genéricas (ej. "Qué vino con carne") responden.
   - [ ] Usuario no PRO: opción "IA Local" deshabilitada y mensaje "Pasar a PRO".
   - [ ] Usuario PRO: puede elegir IA Local (con agente en 8080 si lo usas).

5. **Mi Bodega**
   - [ ] Añadir botella, editar, eliminar.
   - [ ] Contador "registros hoy" y límite (50 gratis).
   - [ ] Exportar PDF bodega.

6. **Planes y pagos**
   - [ ] Página Planes muestra Gratis, PRO (4,99 €/mes) y Restaurante.
   - [ ] Si Stripe no está configurado: mensaje amigable (sin mostrar claves).
   - [ ] Si Stripe está configurado: botón "Actualizar a PRO" redirige a Stripe; tras pago, vuelta a /pago-exitoso y usuario pasa a PRO.

7. **Ofertas (Premium)**
   - [ ] Crear oferta (foto + email) desde éxito de registrar o desde Mis ofertas.
   - [ ] En Comprar de un vino, bloque "Un usuario ofrece este vino" con foto y Contactar.
   - [ ] Mis ofertas: listado y marcar como respondido.

8. **Comprar**
   - [ ] Página /vino/{id}/comprar con pestañas y enlaces según país.
   - [ ] Bloque ofertas de usuarios cuando existan.

9. **Chatbot / mascota**
   - [ ] Mascota flotante visible; se puede arrastrar; doble toque/clic abre el panel de guía.
   - [ ] Temas y búsqueda en el panel responden correctamente.

10. **Tests unitarios**
    - [ ] `python -m pytest tests/ -v` → todos pasan.

---

## Entorno de producción

- [ ] Variables de entorno en el servidor: `.env` con `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` (si usas pagos), y opcionalmente `CORS_ORIGINS` (ej. `https://tudominio.com`).
- [ ] Carpeta `data/` accesible y con permisos de escritura (bodegas, ofertas, usuarios_pro, uploads).
- [ ] Si usas HTTPS: proxy inverso (nginx, etc.) configurado y redirigiendo al puerto de uvicorn.
- [ ] Webhook de Stripe apuntando a `https://tudominio.com/webhook-stripe` en modo live.

---

## Resumen

- **Verificación automática**: 32 comprobaciones OK (script `verificar_funcionalidades.py`).
- **Manual**: repasar este checklist en un entorno lo más parecido a producción posible.
- Después de esto, la app está lista para subir.
