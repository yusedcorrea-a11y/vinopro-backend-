"""
API del adaptador para restaurantes: token, configuración (programas, webhook).
La página HTML /adaptador se sirve desde app.py.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import adaptador_service as svc

router = APIRouter(prefix="/adaptador", tags=["Adaptador Restaurantes"])


@router.get("/token")
def get_or_create_token():
    """
    Obtiene o crea un token de API único para el restaurante.
    Solo visible para uso desde la página /adaptador.
    """
    return svc.get_or_create_restaurante()


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
