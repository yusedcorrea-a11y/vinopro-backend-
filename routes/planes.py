"""
Rutas de planes (Gratis / PRO / Restaurante) y API de verificación de límite freemium.
"""
from fastapi import APIRouter, Header, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from services import i18n as i18n_svc
from services import freemium_service as freemium_svc

router = APIRouter(prefix="", tags=["Planes"])
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _render_planes(request: Request, **context):
    """Contexto i18n (t, lang) y TemplateResponse para planes.html."""
    lang = i18n_svc.get_locale(request)
    trans = i18n_svc.load_translations(lang)
    t = i18n_svc.make_t(trans)
    recognition_lang = i18n_svc.recognition_lang_for(lang)
    return templates.TemplateResponse(
        "planes.html",
        {
            "request": request,
            "t": t,
            "lang": lang,
            "recognition_lang": recognition_lang,
            **context,
        },
    )


@router.get("/planes", response_class=HTMLResponse)
def pagina_planes(request: Request):
    """Página de planes: Gratis, PRO, Restaurante."""
    return _render_planes(
        request,
        page_class="page-planes",
        active_page="planes",
    )


@router.get("/api/check-limit")
def api_check_limit(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """
    Estado del límite freemium para la sesión.
    Devuelve puede_anadir, es_pro, usado, limite, mensaje.
    """
    session_id = (x_session_id or "").strip()
    es_pro = freemium_svc.is_pro(session_id) if session_id else False
    usado = freemium_svc.count_botellas(session_id) if session_id else 0
    limite = freemium_svc.LIMITE_GRATIS
    puede_anadir, mensaje = freemium_svc.puede_anadir_botella(session_id, 1) if session_id else (True, "")
    return {
        "puede_anadir": puede_anadir,
        "es_pro": es_pro,
        "usado": usado,
        "limite": limite,
        "mensaje": mensaje,
        "redirect": "/planes",
    }
