"""
Rutas de compra multiplataforma: página de compra por vino y API de enlaces.
Usa el mismo contexto i18n (t, lang) que el resto de páginas para coherencia con base.html.
"""
import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from services import enlaces_service as svc
from services import i18n as i18n_svc
from services import ofertas_service as ofertas_svc
from services import valoraciones_service as valoraciones_svc
from services import wishlist_service as wishlist_svc

router = APIRouter(tags=["Comprar"])
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _render_comprar(request: Request, **context):
    """Construye el contexto i18n (t, lang, recognition_lang) y devuelve TemplateResponse."""
    lang = i18n_svc.get_locale(request)
    trans = i18n_svc.load_translations(lang)
    t = i18n_svc.make_t(trans)
    recognition_lang = i18n_svc.recognition_lang_for(lang)
    return templates.TemplateResponse(
        "comprar_vino.html",
        {
            "request": request,
            "t": t,
            "lang": lang,
            "recognition_lang": recognition_lang,
            **context,
        },
    )


@router.get("/vino/{vino_id}/comprar", response_class=HTMLResponse)
def pagina_comprar_vino(request: Request, vino_id: str):
    """
    Detecta país por IP, busca tiendas (incluyendo Amazon como fallback universal) y renderiza comprar_vino.html.
    Incluye valoraciones de la comunidad y estado de wishlist.
    """
    session_id = (request.headers.get("X-Session-ID") or "").strip()
    qp = (request.query_params.get("pais") or "").strip().upper()
    if len(qp) == 2 and qp.isalpha():
        pais = qp
    else:
        client_ip = request.client.host if request.client else None
        pais = svc.detectar_pais_por_ip(client_ip)
    vinos = getattr(request.app.state, "vinos_mundiales", {})
    vino = vinos.get(vino_id) if vino_id else None
    vino_nombre = (vino.get("nombre") if isinstance(vino, dict) else None) or vino_id
    tiendas_pais = svc.buscar_tiendas_para_pais(vino_id, vino_nombre, pais)
    tiendas_internacional = svc.get_todas_tiendas_internacional(vino_id)
    nacional_por_pais = svc.get_todas_nacionales_por_pais(vino_id)
    subastas = svc.get_subastas(vino_id)
    enlaces = svc.get_enlaces_vino(vino_id)
    guia_vinos = svc.get_guia_vinos_por_pais(pais)
    ofertas = ofertas_svc.get_active_offers_for_vino(vino_id)
    valoraciones_summary = valoraciones_svc.get_summary(vino_id, session_id)
    wishlist_has = wishlist_svc.has(session_id, vino_id) if session_id else False
    ofertas_con_url = []
    for o in ofertas:
        pp = o.get("photo_path") or ""
        filename = os.path.basename(pp) if pp else ""
        ofertas_con_url.append({
            "id": o["id"],
            "photo_url": f"/api/uploads/ofertas/{filename}" if filename else None,
            "created_at": o.get("created_at"),
        })
    return _render_comprar(
        request,
        page_class="page-comprar",
        active_page="comprar",
        vino_id=vino_id,
        vino_nombre=vino_nombre,
        pais_detectado=pais,
        guia_vinos=guia_vinos,
        tiendas_pais=[t.to_dict() for t in tiendas_pais],
        tiendas_internacional=[t.to_dict() for t in tiendas_internacional],
        nacional_por_pais={
            p: [t.to_dict() for t in lst] for p, lst in nacional_por_pais.items()
        },
        subastas=subastas,
        tiene_enlaces=True,
        ofertas=ofertas_con_url,
        valoraciones_summary=valoraciones_summary,
        wishlist_has=wishlist_has,
    )


@router.get("/api/vino/{vino_id}/enlaces")
def api_enlaces_vino(vino_id: str):
    """Devuelve JSON con todos los enlaces de compra del vino."""
    enlaces = svc.get_enlaces_vino(vino_id)
    if not enlaces:
        return {"vino_id": vino_id, "nacional": {}, "internacional": [], "subastas": []}
    return enlaces.to_dict()
