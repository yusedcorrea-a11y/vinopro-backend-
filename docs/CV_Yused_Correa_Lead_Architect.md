# Yused Correa Mercado  
**Project Director & Backend Engineer · Lead Architect**

---

## Perfil

Director de proyecto y ingeniero backend especializado en cerrar la brecha entre necesidades de negocio y soluciones técnicas de alta escala. Enfoque en estabilidad, escalabilidad y seguridad, con mentalidad enterprise desde el MVP. Experiencia en ciclo de vida completo del software: infraestructura, seguridad, desarrollo y monitorización post-despliegue.

---

## Experiencia técnica y proyectos

### VINO PRO IA — Experto en Vinos (Backend & Arquitectura)

*Herramienta en producción (Render, camino a Google Play) que combina visión por ordenador, OCR e IA para análisis de etiquetas, bodega virtual, comunidad global y mapas.*

- **Observabilidad global:** Diseño e implementación de un sistema de telemetría internacional para monitorizar tráfico en tiempo real desde 9 países (Europa y Latam), utilizando middlewares asíncronos en FastAPI. Persistencia de visitas en JSON para analítica y toma de decisiones basada en datos.
- **Privacy by Design (GDPR):** Integración de protocolos de anonimización de IP (último octeto a 0) y persistencia de datos estructurados en formato JSON, garantizando el cumplimiento de normativas de privacidad europeas desde el diseño.
- **Arquitectura de alto rendimiento:** Optimización de la escritura de logs mediante procesamiento en hilos (`asyncio.to_thread`) con lock, evitando bloqueos en el flujo principal de la API y manteniendo latencia baja en producción.
- Pipeline de escaneo (OCR + Gemini 2.0 Flash), quality gates, rate limiting, caché TTL, registro con avatar, comunidad (feed, chat traducido, perfiles). Infraestructura como código (Terraform de referencia AWS). CI/CD con GitHub Actions.

---

## Herramientas y competencias (validadas en producción)

| Área | Tecnologías |
|------|-------------|
| **Backend / API** | Python 3.11, FastAPI, Pydantic |
| **CI/CD** | GitHub Actions (tests automáticos en push a `main` antes de despliegue) |
| **Infrastructure as Code** | Terraform (referencia AWS: S3, RDS, security groups) |
| **Observabilidad** | Logging estructurado, telemetría por geolocalización, persistencia JSON para analítica |
| **Seguridad** | Variables de entorno para secretos (nunca en repo), anonimización de IP, ofuscación R8/ProGuard (guías para Google Play) |
| **Datos** | SQLite, JSON, diseño de esquemas y persistencia para explotación posterior (Data Engineer / práctico) |
| **Frontend / Full-stack** | Jinja2, JavaScript; integración con Stripe, Open Food Facts, APIs de geolocalización |

---

## Objetivo profesional

No solo desarrollo funcionalidades: gestiono el ciclo de vida completo del software, desde la infraestructura y la seguridad hasta la monitorización post-despliegue, con enfoque en cumplimiento normativo (GDPR) y observabilidad en entornos globales.

---

*Documento generado para reflejar el perfil de Lead Architect con hitos de VINO PRO IA (observabilidad, Privacy by Design, arquitectura de alto rendimiento). Actualizar según experiencia adicional.*
