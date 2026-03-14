from fastapi import APIRouter, File, Form, Header, HTTPException, Request, UploadFile

from services import account_service
from services import auth_service as auth_svc

router = APIRouter(tags=["Cuenta"])


@router.post("/api/auth/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    username: str = Form(...),
    avatar: UploadFile | None = File(None),
):
    """
    Registro con correo y contraseña. Opcional: foto de perfil.
    Crea cuenta, sesión y perfil VINEROs. Devuelve session_id para guardar en frontend.
    """
    # Bcrypt solo acepta 72 bytes; truncar aquí por si el servicio no lo hace
    if password and len(password.encode("utf-8")) > 72:
        password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    try:
        ok, msg, session_id = auth_svc.register_with_email(email, password, username, avatar_path="")
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        avatar_path = ""
        if avatar and avatar.filename and avatar.content_type and avatar.content_type.startswith("image/"):
            content = await avatar.read()
            if len(content) <= 5 * 1024 * 1024:
                from db import database as db
                from services import usuario_service as usuario_svc
                user_id = db.get_user_id_by_session(session_id)
                if user_id:
                    path = auth_svc.save_avatar_file(content, user_id, avatar.filename)
                    if path:
                        avatar_path = path
                        db.update_user_avatar(user_id, avatar_path)
                        usuario_svc.actualizar_perfil(session_id, avatar_path=avatar_path)
        return {"ok": True, "session_id": session_id, "message": "Cuenta creada. Ya puedes entrar a VINEROs."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la cuenta: {str(e)}")


@router.post("/api/auth/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
):
    """Inicio de sesión con correo y contraseña. Devuelve session_id."""
    if password and len(password.encode("utf-8")) > 72:
        password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    ok, msg, session_id = auth_svc.login_with_email(email, password)
    if not ok:
        raise HTTPException(status_code=401, detail=msg)
    return {"ok": True, "session_id": session_id, "message": "Sesión iniciada."}


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
