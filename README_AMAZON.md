# Cumplimiento Amazon Afiliados (Associates)

**Última actualización:** Marzo 2025  
**Contexto:** Evitar suspensiones y mantener las cuentas en estado de cumplimiento.

---

## Contexto del problema

Se detectaron múltiples avisos de suspensión de cuenta en **Amazon Afiliados** (regiones: ES, FR, IT, DE, NL, UK, US, JP, IN) porque las URLs declaradas no eran accesibles o funcionales.

---

## Acciones realizadas

1. **URL oficial de auditoría**  
   Se ha establecido la URL de Render como destino oficial:  
   **https://vinopro-backend-1.onrender.com/inicio**

2. **Aviso legal multilingüe**  
   En la pantalla de `/inicio` (y en el modal de selección de idioma) el **aviso legal de afiliados** se muestra en el idioma detectado:
   - **Cookie** `vino_pro_lang` (si el usuario ya eligió idioma).
   - Si no hay cookie: **idioma del navegador** (`navigator.language`).
   - Textos disponibles: **Español**, **Japonés**, **Inglés** (por defecto).

3. **Autodetección de idioma (primera visita)**  
   La app detecta el idioma del navegador (`Accept-Language`) en la primera visita, establece la cookie y renderiza en ese idioma sin mostrar el modal. Así, un revisor de Amazon (p. ej. Holanda, UK, Japón) ve el aviso y la interfaz en un idioma coherente con su configuración, lo que refuerza el cumplimiento y la transparencia ante auditorías.

4. **Limpieza en Amazon Associates**  
   Se eliminaron todas las URLs obsoletas y enlaces de apps móviles no funcionales en los paneles internacionales de Amazon.

5. **Declaración de contenido**  
   Se confirmó en todas las regiones que el sitio **no está dirigido a menores de 13 años** (cumplimiento de políticas de protección de menores).

---

## Estado actual

- Las **9 cuentas regionales** están en estado de **cumplimiento (Compliance)**.
- El sistema automático de Amazon verificará la URL de Render antes del **2 de abril de 2026**.
- **Importante:** Mantener la ruta **`/inicio`** activa y con el **aviso legal visible** para evitar futuras incidencias.

---

## Qué no tocar (recomendación)

- No eliminar el footer del aviso de afiliados en `/inicio` ni en el modal de idioma.
- No cambiar la ruta `/inicio` sin actualizar las URLs declaradas en los paneles de Amazon.
- No quitar la clase `amazon-affiliate-legal` ni el script que rellena el texto según idioma (ver `templates/base.html` e `index.html`).

---

## Referencia técnica

- **Aviso:** elementos con clase `.amazon-affiliate-legal` (modal en `base.html`, footer en `templates/index.html`).
- **Script:** detección de idioma y textos ES/JA/EN en `base.html` (inline, justo después del modal de idioma).
- **Estilos:** `.modal-bienvenida-idioma-legal`, `.inicio-legal-amazon` en `static/style.css`.
