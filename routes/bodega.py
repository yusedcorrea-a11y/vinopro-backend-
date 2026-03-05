"""
Mi Bodega Virtual: API bajo prefijo /api (incluido en app con prefix="/api").
Rutas finales: GET /api/bodega, POST /api/bodega/botellas, DELETE /api/bodega/botellas/{id},
               GET /api/bodega/valoracion, GET /api/bodega/alertas.
GET /bodega (sin /api) sirve la página HTML en app.py.
Header X-Session-ID obligatorio en todas las peticiones API.
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from services import bodega_service as svc
from services import adaptador_service as adaptador_svc
from services import freemium_service as freemium_svc
from services import validacion_service as validacion_svc
from services import limite_diario_service as limite_diario_svc
from services import usuario_service as usuario_svc
from services import feed_service as feed_svc

router = APIRouter(prefix="", tags=["Bodega"])


def _session_id(x_session_id: str | None = Header(None, alias="X-Session-ID")) -> str:
    if not x_session_id or not x_session_id.strip():
        raise HTTPException(status_code=400, detail="Header X-Session-ID requerido. Genera uno en el frontend (UUID).")
    return x_session_id.strip()


def _session_id_or_token(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
    x_api_token: str | None = Header(None, alias="X-API-Token"),
) -> str:
    """Para /bodega/stock: acepta X-Session-ID (usuarios) o X-API-Token (restaurantes)."""
    if x_session_id and x_session_id.strip():
        return x_session_id.strip()
    if x_api_token and x_api_token.strip():
        sid = adaptador_svc.get_session_id_for_token(x_api_token.strip())
        if sid:
            return sid
        raise HTTPException(status_code=401, detail="Token de API no válido.")
    raise HTTPException(status_code=400, detail="Indica X-Session-ID o X-API-Token.")


class BotellaCreate(BaseModel):
    vino_nombre: str = Field(..., min_length=1, max_length=200)
    vino_key: str | None = None
    cantidad: int = Field(1, ge=1)
    anada: int | None = None
    ubicacion: str = ""
    temp_ideal: str = ""
    humedad_ideal: str = ""
    valor_unitario_estimado: float | None = None
    tipo: str = "tinto"


@router.get("/bodega/registros-hoy")
def get_registros_hoy(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Estado del límite diario: registros_hoy, limite, nivel (para contador en UI)."""
    sid = (x_session_id or "").strip()
    return limite_diario_svc.get_estado_hoy(sid) if sid else {"registros_hoy": 0, "limite": 10, "nivel": "nuevo"}


@router.get("/bodega")
def get_bodega(session_id: str = Depends(_session_id)):
    """
    Lista todas las botellas de la bodega del usuario.
    Incluye limite_max (30 para gratis, null para PRO) y es_pro para que la app muestre inventario y límite.
    """
    botellas = svc.get_bodega(session_id)
    for b in botellas:
        b["potencial_guarda"] = svc.get_potencial_guarda(b)
    es_pro = freemium_svc.is_pro(session_id)
    total_botellas = freemium_svc.count_botellas(session_id)
    limite_max = None if es_pro else freemium_svc.LIMITE_GRATIS
    return {
        "session_id": session_id,
        "botellas": botellas,
        "es_pro": es_pro,
        "limite_max": limite_max,
        "total_botellas": total_botellas,
    }


@router.post("/bodega/botellas")
def add_botella(body: BotellaCreate, session_id: str = Depends(_session_id)):
    """Añade una botella a la bodega. Validación anti-tonterías y límite freemium/diario."""
    nombre_limpio = (body.vino_nombre or "").strip()
    ok_val, msg_key = validacion_svc.validar_vino_completo(
        nombre_limpio,
        bodega=None,
        anio=body.anada,
        alcohol=None,
    )
    print(f"Resultado validación: {ok_val}, {msg_key}")
    if not ok_val:
        raise HTTPException(
            status_code=400,
            detail="Nombre de vino no válido",
        )
    puede, _ = limite_diario_svc.puede_registrar_hoy(session_id)
    if not puede:
        raise HTTPException(
            status_code=429,
            detail={"error": "limite_diario", "message_key": "limite_diario"},
        )
    puede, mensaje = freemium_svc.puede_anadir_botella(session_id, body.cantidad)
    if not puede:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "limit_reached",
                "message": mensaje,
                "redirect": "/planes",
            },
        )
    botella = svc.add_botella(
        session_id=session_id,
        vino_key=body.vino_key,
        vino_nombre=body.vino_nombre.strip(),
        cantidad=body.cantidad,
        anada=body.anada,
        ubicacion=body.ubicacion,
        temp_ideal=body.temp_ideal,
        humedad_ideal=body.humedad_ideal,
        valor_unitario_estimado=body.valor_unitario_estimado,
        tipo=body.tipo,
    )
    botella["potencial_guarda"] = svc.get_potencial_guarda(botella)
    limite_diario_svc.incrementar_registro(session_id)
    try:
        adaptador_svc.notify_webhook(session_id)
    except Exception:
        pass
    # Actividad en el feed: "X probó [vino]" para la comunidad
    username = usuario_svc.get_username_por_session(session_id)
    if username:
        vino_key = (body.vino_key or botella.get("vino_key") or "").strip() or nombre_limpio[:200]
        feed_svc.add_actividad(username, "probado", vino_key, vino_nombre=nombre_limpio[:200])
    return {"success": True, "botella": botella}


class BotellaUpdate(BaseModel):
    cantidad: int | None = None
    anada: int | None = None
    ubicacion: str | None = None
    temp_ideal: str | None = None
    humedad_ideal: str | None = None
    valor_unitario_estimado: float | None = None


@router.put("/bodega/botellas/{botella_id}")
def update_botella_endpoint(botella_id: str, body: BotellaUpdate, session_id: str = Depends(_session_id)):
    """Actualiza una botella (cantidad, ubicación, valor, etc.)."""
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    updated = svc.update_botella(session_id, botella_id, **kwargs)
    if not updated:
        raise HTTPException(status_code=404, detail="Botella no encontrada.")
    updated["potencial_guarda"] = svc.get_potencial_guarda(updated)
    try:
        adaptador_svc.notify_webhook(session_id)
    except Exception:
        pass
    return {"success": True, "botella": updated}


@router.delete("/bodega/botellas/{botella_id}")
def delete_botella_endpoint(botella_id: str, session_id: str = Depends(_session_id)):
    """Elimina una botella de la bodega."""
    if not svc.delete_botella(session_id, botella_id):
        raise HTTPException(status_code=404, detail="Botella no encontrada.")
    try:
        adaptador_svc.notify_webhook(session_id)
    except Exception:
        pass
    return {"success": True}


@router.get("/bodega/alertas")
def get_alertas(
    session_id: str = Depends(_session_id),
    temp: float | None = None,
    humedad: float | None = None,
):
    """Alertas de temperatura/humedad para las botellas del usuario."""
    return {"alertas": svc.get_alertas(session_id, temp, humedad)}


@router.get("/bodega/valoracion")
def get_valoracion(session_id: str = Depends(_session_id)):
    """Valoración estimada del inventario (suma de valor_unitario * cantidad)."""
    return svc.get_valoracion(session_id)


@router.get("/bodega/stock")
def get_stock(session_id: str = Depends(_session_id_or_token)):
    """
    Stock en tiempo real para integración externa (restaurantes, CoverManager, TheFork, etc.).
    Acepta X-Session-ID (usuarios) o X-API-Token (token de restaurante desde /adaptador).
    """
    stock = adaptador_svc.get_stock_export(session_id)
    return {"stock": stock, "total_entradas": len(stock)}
