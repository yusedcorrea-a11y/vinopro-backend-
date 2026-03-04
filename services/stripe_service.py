"""
Integración con Stripe: checkout session (4,99 €/mes) y webhook para marcar PRO.
Configuración vía variables de entorno: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET.
Usa claves live (sk_live_*, whsec_*) en producción; si solo hay sk_test_* funciona en modo test.
"""
import os

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "").strip()
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "").strip()
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
PRECIO_EUR_MES = 4.99  # €/mes


def _stripe_available() -> bool:
    return bool(STRIPE_SECRET_KEY)


def is_live_mode() -> bool:
    """True si está configurado con claves de producción (sk_live_)."""
    return STRIPE_SECRET_KEY.startswith("sk_live_") if STRIPE_SECRET_KEY else False


def crear_checkout_session(
    session_id: str,
    success_url: str,
    cancel_url: str,
) -> str | None:
    """
    Crea una Stripe Checkout Session (suscripción 4,99 €/mes).
    client_reference_id = session_id para identificar al usuario en el webhook.
    Devuelve la URL de checkout o None si Stripe no está configurado.
    """
    if not _stripe_available():
        return None
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            mode="subscription",
            client_reference_id=session_id or None,
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "unit_amount": 499,  # 4,99 € en céntimos
                        "product_data": {
                            "name": "Vino Pro IA - Plan PRO",
                            "description": "Bodega ilimitada y todas las ventajas PRO.",
                        },
                        "recurring": {"interval": "month"},
                    },
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.url if session else None
    except Exception as e:
        print(f"[Stripe] Error creando checkout: {e}")
        return None


def procesar_webhook(payload: bytes, signature: str | None) -> tuple[bool, str]:
    """
    Verifica la firma del webhook y procesa checkout.session.completed.
    Añade client_reference_id (session_id) a usuarios_pro.json.
    Devuelve (True, "") o (False, mensaje_error).
    """
    if not STRIPE_WEBHOOK_SECRET or not signature:
        return False, "Webhook secret or signature missing"
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(
            payload, signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return False, f"Invalid payload: {e}"
    except Exception as e:
        return False, f"Signature verification failed: {e}"

    if event.type != "checkout.session.completed":
        return True, ""  # Otros eventos los ignoramos pero no fallamos

    session = event.data.object
    client_ref = (session.get("client_reference_id") or "").strip()
    if not client_ref:
        print("[Stripe] checkout.session.completed sin client_reference_id")
        return True, ""

    try:
        from services import freemium_service as freemium_svc
        added = freemium_svc.add_pro_user(client_ref)
        print(f"[Stripe] Usuario {client_ref} marcado como PRO (añadido={added})")
    except Exception as e:
        print(f"[Stripe] Error añadiendo PRO: {e}")
        return False, str(e)
    return True, ""
