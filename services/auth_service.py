"""
Registro e inicio de sesión: email + contraseña, y enlace con sesión y perfil VINEROS.
"""
import re
import uuid
from pathlib import Path

from passlib.context import CryptContext

from db import database as db
from services import usuario_service as usuario_svc

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Carpeta para avatares (se sirve como estático)
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "static" / "uploads" / "avatars"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


def email_valido(email: str) -> bool:
    return bool(email and EMAIL_RE.match(email.strip()))


def register_with_email(email: str, password: str, username: str, avatar_path: str = "") -> tuple[bool, str, str | None]:
    """
    Registra usuario con email y contraseña. Crea user en DB, sesión y perfil VINEROS.
    Devuelve (ok, mensaje, session_id). Si ok, session_id para guardar en frontend.
    """
    email = (email or "").strip().lower()
    password = (password or "").strip()
    username = (username or "").strip()

    if not email_valido(email):
        return False, "Correo no válido", None
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres", None
    if not username or not usuario_svc.username_valido(username):
        return False, "Usuario inválido (3-30 caracteres, letras, números y _)", None

    if db.get_user_by_email(email):
        return False, "Este correo ya está registrado", None
    if usuario_svc.existe_username(username):
        return False, "Este nombre de usuario ya existe", None

    user_id = db.create_user(email=email, password_hash=hash_password(password), avatar_path=avatar_path, display_name=username)
    if not user_id:
        return False, "No se pudo crear la cuenta", None

    session_id = db.create_session(user_id)
    ok, msg = usuario_svc.crear_perfil(session_id, username, idioma="es", avatar_path=avatar_path)
    if not ok:
        return False, msg or "Error al crear perfil", None
    return True, "", session_id


def login_with_email(email: str, password: str) -> tuple[bool, str, str | None]:
    """
    Inicia sesión con email y contraseña. Devuelve (ok, mensaje, session_id).
    """
    email = (email or "").strip().lower()
    password = (password or "").strip()
    if not email or not password:
        return False, "Indica correo y contraseña", None

    user = db.get_user_by_email(email)
    if not user:
        return False, "Correo o contraseña incorrectos", None
    if not verify_password(password, user["password_hash"] or ""):
        return False, "Correo o contraseña incorrectos", None

    session_id = db.create_session(user["id"])
    username = usuario_svc.get_username_por_session(session_id)
    if not username:
        ok, _ = usuario_svc.crear_perfil(session_id, user.get("display_name") or email.split("@")[0][:30], avatar_path=user.get("avatar_path") or "")
        if not ok:
            pass
    return True, "", session_id


def save_avatar_file(file_content: bytes, user_id: int, filename: str) -> str | None:
    """Guarda archivo de avatar. Devuelve ruta relativa para guardar en perfil (ej. /static/uploads/avatars/xxx.jpg) o None."""
    ext = Path(filename).suffix.lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        return None
    safe_name = f"{user_id}_{uuid.uuid4().hex[:12]}{ext}"
    path = UPLOADS_DIR / safe_name
    try:
        path.write_bytes(file_content)
        return f"/static/uploads/avatars/{safe_name}"
    except Exception:
        return None
