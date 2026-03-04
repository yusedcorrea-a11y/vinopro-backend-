"""
QR personalizados para networking (Turín).
Página pública /c/{codigo} y panel generador /qr.
"""
import os
from fastapi import APIRouter, Request, HTTPException, Body
from fastapi.responses import HTMLResponse, Response

from services import qr_service as qr_svc
from services import i18n as i18n_svc

router = APIRouter(tags=["QR personalizados"])


def _base_url(request: Request) -> str:
    base = os.environ.get("BASE_URL", "").strip()
    if base:
        return base.rstrip("/")
    return str(request.base_url).rstrip("/")


def _pais_desde_request(request: Request) -> str:
    """Cloudflare pone CF-IPCountry; otros proxies pueden usar X-Country."""
    cf = request.headers.get("CF-IPCountry", "").strip()
    if cf and cf != "XX" and len(cf) == 2:
        return cf.upper()
    return ""


@router.get("/c/{codigo}", response_class=HTMLResponse)
async def pagina_personalizada(request: Request, codigo: str, lang: str = ""):
    """
    Página que ve el contacto al escanear el QR.
    Registra el escaneo (primera vez) y sirve HTML personalizado.
    ?lang=es|en|it cambia el idioma de la página (por defecto el elegido al crear el QR).
    """
    contacto = qr_svc.get_por_codigo(codigo)
    if not contacto:
        raise HTTPException(status_code=404, detail="Código no encontrado")
    pais = _pais_desde_request(request)
    qr_svc.registrar_escaneo(codigo, pais)
    # Idioma: query ?lang= tiene prioridad; si no, el del contacto
    lang = (lang or contacto.get("idioma") or "it").strip().lower()
    if lang not in ("it", "es", "en"):
        lang = "it"
    trans = i18n_svc.load_translations(lang)
    t = i18n_svc.make_t(trans)
    base_url_str = _base_url(request)
    qr_email = os.environ.get("QR_EMAIL", "hola@vinoproia.com")
    qr_linkedin = os.environ.get("QR_LINKEDIN", "").strip()
    qr_whatsapp = os.environ.get("QR_WHATSAPP", "").strip()
    qr_calendly = os.environ.get("QR_CALENDLY", "").strip()
    return request.app.state.templates.TemplateResponse(
        "qr_pagina_personalizada.html",
        {
            "request": request,
            "contacto": contacto,
            "t": t,
            "lang": lang,
            "base_url_str": base_url_str,
            "codigo": codigo,
            "qr_email": qr_email,
            "qr_linkedin": qr_linkedin,
            "qr_whatsapp": qr_whatsapp,
            "qr_calendly": qr_calendly,
        },
    )


@router.get("/qr", response_class=HTMLResponse)
async def panel_generador(request: Request):
    """Panel para crear QRs (responsive, uso en móvil)."""
    trans = i18n_svc.load_translations(i18n_svc.get_locale(request))
    t = i18n_svc.make_t(trans)
    base_url_str = _base_url(request)
    return request.app.state.templates.TemplateResponse(
        "qr_generador.html",
        {
            "request": request,
            "t": t,
            "base_url_str": base_url_str,
        },
    )


@router.get("/api/qr/contactos")
async def api_listar_contactos():
    """Lista de contactos para el panel de seguimiento."""
    lista = qr_svc.listar_contactos()
    return {"contactos": lista}


@router.post("/api/qr/generar")
async def api_generar_qr(request: Request, nombre: str = Body(..., embed=True), empresa: str = Body("", embed=True), idioma: str = Body("it", embed=True)):
    """Crea un contacto y devuelve código y URL para el QR."""
    nombre = (nombre or "").strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="Nombre requerido")
    contacto = qr_svc.crear_contacto(nombre, empresa=empresa, idioma=idioma)
    base = _base_url(request)
    codigo = contacto["codigo"]
    url = f"{base}/c/{codigo}"
    return {"ok": True, "codigo": codigo, "url": url, "contacto": contacto}


@router.get("/api/qr/descargar/{codigo}")
async def api_descargar_qr(request: Request, codigo: str):
    """Devuelve la imagen PNG del QR para ese código."""
    contacto = qr_svc.get_por_codigo(codigo)
    if not contacto:
        raise HTTPException(status_code=404, detail="Código no encontrado")
    base = _base_url(request)
    url = f"{base}/c/{codigo}"
    png = qr_svc.generar_imagen_qr(url, size_px=320)
    if not png:
        raise HTTPException(status_code=500, detail="Error generando QR")
    return Response(content=png, media_type="image/png")
