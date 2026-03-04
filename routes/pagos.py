"""
Rutas de pagos con Stripe: crear checkout, páginas éxito/cancelado, webhook.
En producción el webhook debe apuntar a https://tudominio.com/webhook-stripe.
"""
import logging
from fastapi import APIRouter, Header, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from services import i18n as i18n_svc
from services import stripe_service as stripe_svc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Pagos"])
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _render_page(request: Request, template_name: str, **context):
    """Contexto i18n y TemplateResponse."""
    lang = i18n_svc.get_locale(request)
    trans = i18n_svc.load_translations(lang)
    t = i18n_svc.make_t(trans)
    recognition_lang = i18n_svc.recognition_lang_for(lang)
    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "t": t,
            "lang": lang,
            "recognition_lang": recognition_lang,
            **context,
        },
    )


@router.post("/crear-checkout-session")
def crear_checkout_session(
    request: Request,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """
    Crea una sesión de Stripe Checkout (4,99 €/mes).
    Requiere X-Session-ID para asociar el pago al usuario (se guarda en client_reference_id).
    Devuelve { "url": "https://checkout.stripe.com/..." } o error 503 si Stripe no está configurado.
    """
    session_id = (x_session_id or "").strip()
    if not session_id:
        return JSONResponse(
            status_code=400,
            content={"detail": "X-Session-ID requerido. Inicia sesión o genera un ID en Mi Bodega."},
        )
    base = str(request.base_url).rstrip("/")
    success_url = f"{base}/pago-exitoso?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base}/pago-cancelado"
    logger.info("Checkout solicitado session_id=%s base=%s", session_id[:8] if session_id else "", base)
    url = stripe_svc.crear_checkout_session(session_id, success_url, cancel_url)
    if not url:
        logger.warning("Stripe no disponible (falta STRIPE_SECRET_KEY o error)")
        return JSONResponse(
            status_code=503,
            content={"detail": "pagos_no_disponibles"},
        )
    logger.info("Checkout URL generada (redirect)")
    return {"url": url}


@router.get("/pago-exitoso", response_class=HTMLResponse)
def pago_exitoso(request: Request):
    """Página mostrada tras un pago correcto en Stripe."""
    return _render_page(
        request,
        "pago-exitoso.html",
        page_class="page-pago-exitoso",
        active_page="planes",
    )


@router.get("/pago-cancelado", response_class=HTMLResponse)
def pago_cancelado(request: Request):
    """Página mostrada si el usuario cancela en Stripe."""
    return _render_page(
        request,
        "pago-cancelado.html",
        page_class="page-pago-cancelado",
        active_page="planes",
    )


@router.post("/webhook-stripe")
async def webhook_stripe(request: Request):
    """
    Endpoint para que Stripe envíe eventos (checkout.session.completed).
    En producción: configurar en Dashboard Stripe la URL https://tudominio.com/webhook-stripe.
    Verifica la firma con STRIPE_WEBHOOK_SECRET y marca al usuario como PRO.
    """
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "").strip()
    if not signature:
        logger.warning("Webhook Stripe recibido sin cabecera stripe-signature")
    ok, err = stripe_svc.procesar_webhook(payload, signature or None)
    if not ok:
        logger.warning("Webhook Stripe rechazado: %s", err)
        return JSONResponse(status_code=400, content={"detail": err})
    logger.info("Webhook Stripe procesado correctamente")
    return {"received": True}
