"""
Rutas de ofertas: crear oferta (Premium + foto), listar por vino, contactar, mis ofertas, marcar respondido.
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, Header, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from services import ofertas_service as ofertas_svc
from services import freemium_service as freemium_svc

router = APIRouter(prefix="/api", tags=["Ofertas"])
DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
UPLOADS_OFERTAS = os.path.join(DATA_FOLDER, "uploads", "ofertas")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIZE = 6 * 1024 * 1024  # 6 MB


def _is_pro(session_id: str) -> bool:
    return bool((session_id or "").strip() and freemium_svc.is_pro(session_id.strip()))


@router.get("/ofertas")
def listar_ofertas_vino(vino_key: str):
    """Ofertas activas para un vino (para la página Comprar)."""
    lista = ofertas_svc.get_active_offers_for_vino(vino_key)
    result = []
    for o in lista:
        pp = o.get("photo_path") or ""
        filename = os.path.basename(pp) if pp else ""
        result.append({
            "id": o["id"],
            "photo_path": pp,
            "photo_url": f"/api/uploads/ofertas/{filename}" if filename else None,
            "created_at": o.get("created_at"),
        })
    return {"vino_key": vino_key, "ofertas": result}


@router.post("/ofertas")
async def crear_oferta(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
    vino_key: str = Form(...),
    offerer_email: str = Form(""),
    photo: UploadFile = File(...),
):
    """Solo Premium. Crea oferta con foto. vino_key, offerer_email opcional, photo obligatoria."""
    sid = (x_session_id or "").strip()
    if not sid:
        return JSONResponse(status_code=401, content={"detail": "X-Session-ID requerido."})
    if not _is_pro(sid):
        return JSONResponse(status_code=403, content={"detail": "Solo usuarios Premium pueden crear ofertas."})
    vino_key = (vino_key or "").strip()
    if not vino_key:
        return JSONResponse(status_code=400, content={"detail": "vino_key obligatorio."})

    ext = Path(photo.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JSONResponse(status_code=400, content={"detail": "Formato de imagen no válido. Use JPG, PNG o WebP."})
    content = await photo.read()
    if len(content) > MAX_SIZE:
        return JSONResponse(status_code=400, content={"detail": "Imagen demasiado grande (máx. 6 MB)."})

    os.makedirs(UPLOADS_OFERTAS, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex[:12]}{ext}"
    path_full = os.path.join(UPLOADS_OFERTAS, safe_name)
    with open(path_full, "wb") as f:
        f.write(content)
    photo_path = f"uploads/ofertas/{safe_name}"

    oferta = ofertas_svc.crear_oferta(vino_key, sid, photo_path, offerer_email)
    return {"success": True, "oferta": oferta}


@router.post("/ofertas/{offer_id}/contactar")
def contactar_oferta(
    offer_id: str,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
    email: str = Form(...),
    message: str = Form(""),
):
    """El interesado envía email y mensaje. Se registra la solicitud; si 3 sin respuesta se quita la oferta."""
    ok, err = ofertas_svc.add_contact_request(offer_id, email, (x_session_id or "").strip(), message)
    if not ok:
        return JSONResponse(status_code=400, content={"detail": err})
    return {"success": True, "mensaje": "Tu solicitud se ha enviado. El oferente verá tu mensaje y decidirá si contestar."}


@router.get("/ofertas/mis-ofertas")
def mis_ofertas(x_session_id: str | None = Header(None, alias="X-Session-ID")):
    """Lista ofertas del usuario (para Mi Bodega / Mis ofertas)."""
    sid = (x_session_id or "").strip()
    lista = ofertas_svc.get_offers_by_offerer(sid)
    return {"ofertas": lista}


@router.post("/ofertas/{offer_id}/marcar-respondido")
def marcar_respondido(
    offer_id: str,
    request_id: str,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """El oferente marca una solicitud como respondida (para no ser retirado por 3 sin respuesta)."""
    sid = (x_session_id or "").strip()
    ok, err = ofertas_svc.mark_request_replied(offer_id, request_id, sid)
    if not ok:
        return JSONResponse(status_code=400, content={"detail": err})
    return {"success": True}


@router.delete("/ofertas/{offer_id}")
def retirar_oferta(offer_id: str, x_session_id: str | None = Header(None, alias="X-Session-ID")):
    """El oferente retira su oferta."""
    sid = (x_session_id or "").strip()
    ok, err = ofertas_svc.remove_offer(offer_id, sid)
    if not ok:
        return JSONResponse(status_code=400, content={"detail": err})
    return {"success": True}


@router.get("/uploads/ofertas/{filename}")
def servir_foto_oferta(filename: str):
    """Sirve la imagen de una oferta (solo nombre seguro)."""
    if ".." in filename or "/" in filename or "\\" in filename:
        return JSONResponse(status_code=404, content={})
    path = os.path.join(UPLOADS_OFERTAS, filename)
    if not os.path.isfile(path):
        return JSONResponse(status_code=404, content={})
    ext = os.path.splitext(filename)[1].lower()
    media = "image/png" if ext == ".png" else "image/webp" if ext == ".webp" else "image/jpeg"
    return FileResponse(path, media_type=media)
