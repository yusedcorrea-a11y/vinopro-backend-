"""
API de valoraciones (estrellas + nota) y wishlist (quiero probar).
Requieren X-Session-ID para identificar al usuario. Sin sesión se devuelve 401.
"""
from fastapi import APIRouter, Header, Request, Body, HTTPException

from services import valoraciones_service as val_svc
from services import wishlist_service as wish_svc
from services import usuario_service as usuario_svc
from services import feed_service as feed_svc

router = APIRouter(tags=["Valoraciones y Wishlist"])


@router.post("/api/valorar-vino")
async def valorar_vino(
    request: Request,
    wine_key: str = Body(..., embed=True),
    score: int = Body(..., embed=True),
    note: str = Body("", embed=True),
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Registra o actualiza la valoración (1-5 estrellas y opcional nota) del usuario para un vino."""
    session_id = (x_session_id or "").strip()
    if not session_id:
        raise HTTPException(status_code=401, detail="X-Session-ID requerido")
    username = usuario_svc.get_username_por_session(session_id)
    id_val = val_svc.add_or_update(
        session_id, wine_key.strip(), score, (note or "").strip(),
        username=username,
    )
    if username and id_val:
        feed_svc.add_actividad(username, "valoracion", wine_key.strip(), vino_nombre="")
    return {"ok": True, "id": id_val}


@router.get("/api/vino/{vino_id}/valoraciones")
async def get_valoraciones_vino(
    vino_id: str,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Devuelve resumen (average, count), valoración del usuario si hay sesión, y últimas notas."""
    session_id = (x_session_id or "").strip()
    summary = val_svc.get_summary(vino_id, session_id)
    recent = val_svc.get_recent_notes(vino_id, limit=5)
    return {"vino_id": vino_id, "summary": summary, "recent_notes": recent}


@router.post("/api/wishlist/add")
async def wishlist_add(
    request: Request,
    wine_key: str = Body(..., embed=True),
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Añade un vino a la wishlist del usuario."""
    session_id = (x_session_id or "").strip()
    if not session_id:
        raise HTTPException(status_code=401, detail="X-Session-ID requerido")
    added = wish_svc.add(session_id, wine_key.strip())
    if added:
        username = usuario_svc.get_username_por_session(session_id)
        if username:
            feed_svc.add_actividad(username, "deseado", wine_key.strip(), vino_nombre="")
    return {"ok": True, "added": added}


@router.delete("/api/wishlist/remove")
async def wishlist_remove(
    request: Request,
    wine_key: str = Body(..., embed=True),
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Quita un vino de la wishlist."""
    session_id = (x_session_id or "").strip()
    if not session_id:
        raise HTTPException(status_code=401, detail="X-Session-ID requerido")
    removed = wish_svc.remove(session_id, wine_key.strip())
    return {"ok": True, "removed": removed}


@router.get("/api/wishlist/contains/{vino_id}")
async def wishlist_contains(
    vino_id: str,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Indica si el vino está en la wishlist del usuario."""
    session_id = (x_session_id or "").strip()
    in_list = wish_svc.has(session_id, vino_id) if session_id else False
    return {"vino_id": vino_id, "in_wishlist": in_list}


@router.get("/api/wishlist")
async def wishlist_list(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Devuelve la lista de wine_key de la wishlist del usuario."""
    session_id = (x_session_id or "").strip()
    keys = wish_svc.get_list(session_id) if session_id else []
    return {"wine_keys": keys}


@router.put("/api/valoracion/{id_val}")
async def actualizar_valoracion(
    id_val: str,
    request: Request,
    score: int = Body(..., embed=True),
    note: str = Body("", embed=True),
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Actualiza la valoración por id (solo del usuario actual)."""
    session_id = (x_session_id or "").strip()
    if not session_id:
        raise HTTPException(status_code=401, detail="X-Session-ID requerido")
    r = val_svc.get_valoracion_por_id(session_id, id_val)
    if not r:
        raise HTTPException(status_code=404, detail="Valoración no encontrada")
    username = usuario_svc.get_username_por_session(session_id)
    val_svc.add_or_update(
        session_id, r["wine_key"], score, (note or "").strip(),
        username=username,
    )
    return {"ok": True}


@router.delete("/api/valoracion/{id_val}")
async def borrar_valoracion(
    id_val: str,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Borra la valoración por id (solo del usuario actual)."""
    session_id = (x_session_id or "").strip()
    if not session_id:
        raise HTTPException(status_code=401, detail="X-Session-ID requerido")
    if not val_svc.delete_valoracion(session_id, id_val):
        raise HTTPException(status_code=404, detail="Valoración no encontrada")
    return {"ok": True}
