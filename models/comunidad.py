"""
Modelos para la comunidad social (Fase 6B): perfiles, valoraciones públicas, actividad, seguimiento, notificaciones.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PerfilUsuario:
    """Perfil público de usuario de la comunidad."""
    username: str
    session_id: str  # sesión que posee este perfil
    bio: str = ""
    ubicacion: str = ""
    avatar_path: str = ""
    privado: bool = False
    created_at: int = 0
    idioma: str = ""  # idioma preferido para leer contenido (es, en, ru, hi, etc.)

    def to_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "session_id": self.session_id,
            "bio": self.bio,
            "ubicacion": self.ubicacion,
            "avatar_path": self.avatar_path,
            "privado": self.privado,
            "created_at": self.created_at,
            "idioma": self.idioma,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PerfilUsuario":
        return cls(
            username=d.get("username", ""),
            session_id=d.get("session_id", ""),
            bio=d.get("bio", ""),
            ubicacion=d.get("ubicacion", ""),
            avatar_path=d.get("avatar_path", ""),
            privado=d.get("privado", False),
            created_at=int(d.get("created_at") or 0),
            idioma=(d.get("idioma") or "").strip()[:10] or "",
        )


@dataclass
class ValoracionPublica:
    """Valoración de un vino con opcional username (perfil público)."""
    wine_key: str
    session_id: str
    score: int
    note: str = ""
    created_at: int = 0
    username: str = ""  # si tiene perfil, para mostrar en comunidad
    foto_path: str = ""
    id: str = ""  # id único para editar/borrar

    def to_dict(self) -> dict[str, Any]:
        out = {
            "wine_key": self.wine_key,
            "session_id": self.session_id,
            "score": self.score,
            "note": self.note,
            "created_at": self.created_at,
        }
        if self.username:
            out["username"] = self.username
        if self.foto_path:
            out["foto_path"] = self.foto_path
        if self.id:
            out["id"] = self.id
        return out

    @classmethod
    def from_dict(cls, d: dict) -> "ValoracionPublica":
        return cls(
            wine_key=d.get("wine_key", ""),
            session_id=d.get("session_id", ""),
            score=int(d.get("score", 0)),
            note=d.get("note", ""),
            created_at=int(d.get("created_at") or 0),
            username=d.get("username", ""),
            foto_path=d.get("foto_path", ""),
            id=d.get("id", ""),
        )


@dataclass
class Actividad:
    """Evento para el feed: valoración, añadido a probados, añadido a deseados."""
    username: str
    tipo: str  # "valoracion" | "probado" | "deseado"
    vino_key: str
    vino_nombre: str = ""
    score: int | None = None
    created_at: int = 0
    id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "tipo": self.tipo,
            "vino_key": self.vino_key,
            "vino_nombre": self.vino_nombre,
            "score": self.score,
            "created_at": self.created_at,
            "id": self.id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Actividad":
        return cls(
            username=d.get("username", ""),
            tipo=d.get("tipo", ""),
            vino_key=d.get("vino_key", ""),
            vino_nombre=d.get("vino_nombre", ""),
            score=d.get("score"),
            created_at=int(d.get("created_at") or 0),
            id=d.get("id", ""),
        )


@dataclass
class Notificacion:
    """Notificación para un usuario (nuevo seguidor, etc.)."""
    id: str
    username: str  # destinatario
    tipo: str  # "nuevo_seguidor" | "valoracion_bodega" | ...
    from_username: str = ""
    ref_id: str = ""
    leida: bool = False
    created_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "tipo": self.tipo,
            "from_username": self.from_username,
            "ref_id": self.ref_id,
            "leida": self.leida,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Notificacion":
        return cls(
            id=d.get("id", ""),
            username=d.get("username", ""),
            tipo=d.get("tipo", ""),
            from_username=d.get("from_username", ""),
            ref_id=d.get("ref_id", ""),
            leida=d.get("leida", False),
            created_at=int(d.get("created_at") or 0),
        )
