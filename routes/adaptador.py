"""
API del adaptador para restaurantes: token, configuración (programas, webhook), venta.
Cuando un camerero vende un vino, el programa del restaurante llama a /venta y la bodega
resta esa botella; el dueño ve su inventario en tiempo real en la app.
"""
from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from services import adaptador_service as svc
from services import bodega_service as bodega_svc

router = APIRouter(prefix="/adaptador", tags=["Adaptador Restaurantes"])


@router.get("/token")
def get_or_create_token(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """
    Obtiene o crea un token de API único para el restaurante.
    Solo visible para uso desde la página /adaptador.
    """
    sid = (x_session_id or "").strip() or None
    return svc.get_or_create_restaurante(sid)


@router.post("/token/regenerate")
def regenerate_token(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """
    Invalida el token anterior y genera uno nuevo.
    Si hay sesión, rota el token del restaurante asociado.
    """
    sid = (x_session_id or "").strip() or None
    rest = svc.regenerate_token(sid)
    if not rest:
        raise HTTPException(status_code=404, detail="No se pudo regenerar el token.")
    return {"success": True, "token_data": rest}


class ConfigBody(BaseModel):
    nombre: str | None = Field(None, max_length=200)
    programas: list[str] | None = None
    webhook_url: str | None = Field(None, max_length=500)


@router.post("/config")
def update_config(body: ConfigBody, token: str = Query(..., description="Token del restaurante")):
    """
    Actualiza la configuración del restaurante (nombre, programas, webhook).
    Query param: token (obligatorio).
    """
    rest = svc.update_config(
        token.strip(),
        nombre=body.nombre,
        programas=body.programas,
        webhook_url=body.webhook_url,
    )
    if not rest:
        raise HTTPException(status_code=404, detail="Token no válido.")
    return {"success": True, "config": rest}


class VentaBody(BaseModel):
    """Cuando el TPV/programa del restaurante registra una venta de vino."""
    vino_nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del vino vendido")
    cantidad: int = Field(1, ge=1, description="Unidades vendidas (por defecto 1)")


@router.post("/venta")
def registrar_venta(
    body: VentaBody,
    x_api_token: str | None = Header(None, alias="X-API-Token"),
):
    """
    Registra una venta: resta botella(s) de la bodega del restaurante.
    El programa del restaurante (TPV, CoverManager, etc.) llama a este endpoint
    cuando un camerero vende un vino; el dueño ve el inventario actualizado en la app.
    Header obligatorio: X-API-Token (token obtenido en /api/adaptador/token).
    """
    if not x_api_token or not x_api_token.strip():
        raise HTTPException(status_code=400, detail="Header X-API-Token obligatorio.")
    session_id = svc.get_session_id_for_token(x_api_token.strip())
    if not session_id:
        raise HTTPException(status_code=401, detail="Token no válido.")
    resultado, encontrado = bodega_svc.restar_cantidad(
        session_id,
        body.vino_nombre.strip(),
        cantidad=body.cantidad,
    )
    stock = svc.get_stock_export(session_id)
    try:
        svc.notify_webhook(session_id)
    except Exception:
        pass
    if not encontrado:
        return {
            "success": False,
            "message": "Vino no encontrado en la bodega. Añádelo antes en la app Mi Bodega.",
            "stock_actualizado": stock,
        }
    if resultado is None:
        return {
            "success": True,
            "message": f"Vendido: {body.vino_nombre}. Esa entrada se ha agotado.",
            "stock_actualizado": stock,
        }
    return {
        "success": True,
        "message": f"Vendido: {body.vino_nombre}. Quedan {resultado.get('cantidad', 0)} en esa entrada.",
        "stock_actualizado": stock,
    }
