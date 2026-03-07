from fastapi import APIRouter, Header, HTTPException, Request

from services import account_service

router = APIRouter(tags=["Cuenta"])


@router.post("/api/auth/eliminar-cuenta")
async def eliminar_cuenta(
    request: Request,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    sid = (x_session_id or "").strip()
    if not sid:
        raise HTTPException(status_code=401, detail="X-Session-ID requerido")
    result = account_service.delete_account(sid, app_state=request.app.state)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error") or "No se pudo eliminar la cuenta")
    return {
        "ok": True,
        "message": "Tu cuenta y tus datos asociados se han eliminado de forma definitiva.",
        "result": result,
    }
