import json
from pathlib import Path
from typing import Any

from services import adaptador_service as adaptador_svc
from services import qr_service as qr_svc

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

PERFILES_PATH = DATA_DIR / "usuarios_perfiles.json"
SEGUIDORES_PATH = DATA_DIR / "seguidores.json"
VALORACIONES_PATH = DATA_DIR / "valoraciones.json"
WISHLIST_PATH = DATA_DIR / "wishlist.json"
CHAT_PATH = DATA_DIR / "chat_mensajes.json"
NOTIF_PATH = DATA_DIR / "notificaciones.json"
ACTIVIDAD_PATH = DATA_DIR / "actividad.json"
BODEGAS_PATH = DATA_DIR / "bodegas.json"
HISTORIAL_PATH = DATA_DIR / "historial_usuario.json"
REGISTROS_DIARIOS_PATH = DATA_DIR / "registros_diarios.json"
REPUTACION_PATH = DATA_DIR / "usuarios_reputacion.json"
USUARIOS_PRO_PATH = DATA_DIR / "usuarios_pro.json"


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _remove_session_map_entry(path: Path, session_id: str) -> int:
    data = _read_json(path, {})
    if not isinstance(data, dict):
        return 0
    existed = 1 if session_id in data else 0
    data.pop(session_id, None)
    if existed:
        _write_json(path, data)
    return existed


def delete_account(session_id: str, app_state: Any | None = None) -> dict[str, Any]:
    sid = (session_id or "").strip()
    if not sid:
        return {"ok": False, "error": "session_id requerido"}

    report: dict[str, Any] = {"session_id": sid}
    username = ""

    perfiles = _read_json(PERFILES_PATH, {"profiles": [], "session_to_username": {}})
    profiles = perfiles.get("profiles", []) if isinstance(perfiles, dict) else []
    session_to_username = perfiles.get("session_to_username", {}) if isinstance(perfiles, dict) else {}
    username = (session_to_username.pop(sid, "") or "").strip().lower()
    kept_profiles = []
    deleted_profiles = 0
    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        if (profile.get("session_id") or "").strip() == sid:
            deleted_profiles += 1
            if not username:
                username = (profile.get("username") or "").strip().lower()
            continue
        kept_profiles.append(profile)
    perfiles["profiles"] = kept_profiles
    perfiles["session_to_username"] = session_to_username
    _write_json(PERFILES_PATH, perfiles)
    report["perfil_eliminado"] = deleted_profiles
    report["username"] = username

    if username:
        seguidores = _read_json(SEGUIDORES_PATH, {"seguidores": {}, "seguidos": {}})
        seguidores_map = seguidores.get("seguidores", {}) if isinstance(seguidores, dict) else {}
        seguidos_map = seguidores.get("seguidos", {}) if isinstance(seguidores, dict) else {}
        removed_rel = len(seguidores_map.pop(username, []) or []) + len(seguidos_map.pop(username, []) or [])
        for key, values in list(seguidores_map.items()):
            if isinstance(values, list) and username in values:
                seguidores_map[key] = [value for value in values if value != username]
                removed_rel += 1
        for key, values in list(seguidos_map.items()):
            if isinstance(values, list) and username in values:
                seguidos_map[key] = [value for value in values if value != username]
                removed_rel += 1
        seguidores["seguidores"] = seguidores_map
        seguidores["seguidos"] = seguidos_map
        _write_json(SEGUIDORES_PATH, seguidores)
        report["relaciones_sociales_limpiadas"] = removed_rel

        actividad = _read_json(ACTIVIDAD_PATH, [])
        if isinstance(actividad, list):
            original = len(actividad)
            actividad = [
                item for item in actividad
                if not isinstance(item, dict) or (item.get("username") or "").strip().lower() != username
            ]
            _write_json(ACTIVIDAD_PATH, actividad)
            report["actividad_eliminada"] = original - len(actividad)

        notificaciones = _read_json(NOTIF_PATH, {})
        removed_notifications = 0
        if isinstance(notificaciones, dict):
            removed_notifications += len(notificaciones.pop(username, []) or [])
            for key, items in list(notificaciones.items()):
                if not isinstance(items, list):
                    continue
                filtered = [
                    item for item in items
                    if not (isinstance(item, dict) and (item.get("from_username") or "").strip().lower() == username)
                ]
                removed_notifications += len(items) - len(filtered)
                notificaciones[key] = filtered
            _write_json(NOTIF_PATH, notificaciones)
        report["notificaciones_eliminadas"] = removed_notifications

        chats = _read_json(CHAT_PATH, {"conversations": {}})
        removed_conversations = 0
        if isinstance(chats, dict):
            conversations = chats.get("conversations", {})
            if isinstance(conversations, dict):
                kept_conversations = {}
                for conv_key, mensajes in conversations.items():
                    users = [(part or "").strip().lower() for part in str(conv_key).split("|")]
                    if username in users:
                        removed_conversations += 1
                        continue
                    kept_conversations[conv_key] = mensajes
                chats["conversations"] = kept_conversations
                _write_json(CHAT_PATH, chats)
        report["conversaciones_eliminadas"] = removed_conversations

    valoraciones = _read_json(VALORACIONES_PATH, [])
    removed_ratings = 0
    if isinstance(valoraciones, list):
        kept_ratings = []
        for item in valoraciones:
            if not isinstance(item, dict):
                kept_ratings.append(item)
                continue
            same_session = (item.get("session_id") or "").strip() == sid
            same_username = username and (item.get("username") or "").strip().lower() == username
            if same_session or same_username:
                removed_ratings += 1
                continue
            kept_ratings.append(item)
        _write_json(VALORACIONES_PATH, kept_ratings)
    report["valoraciones_eliminadas"] = removed_ratings

    report["wishlist_eliminada"] = _remove_session_map_entry(WISHLIST_PATH, sid)
    report["bodega_eliminada"] = _remove_session_map_entry(BODEGAS_PATH, sid)
    report["historial_recomendaciones_eliminado"] = _remove_session_map_entry(HISTORIAL_PATH, sid)

    registros_diarios = _read_json(REGISTROS_DIARIOS_PATH, {})
    removed_daily = 0
    if isinstance(registros_diarios, dict):
        for day_key in list(registros_diarios.keys()):
            day_data = registros_diarios.get(day_key)
            if not isinstance(day_data, dict):
                continue
            if sid in day_data:
                removed_daily += 1
                day_data.pop(sid, None)
            if not day_data:
                registros_diarios.pop(day_key, None)
        _write_json(REGISTROS_DIARIOS_PATH, registros_diarios)
    report["registros_diarios_eliminados"] = removed_daily

    report["reputacion_eliminada"] = _remove_session_map_entry(REPUTACION_PATH, sid)

    pro_data = _read_json(USUARIOS_PRO_PATH, {"pro_users": []})
    removed_pro = 0
    if isinstance(pro_data, dict):
        pro_users = pro_data.get("pro_users", [])
        if isinstance(pro_users, list):
            filtered = [value for value in pro_users if (value or "").strip() != sid]
            removed_pro = len(pro_users) - len(filtered)
            pro_data["pro_users"] = filtered
            _write_json(USUARIOS_PRO_PATH, pro_data)
    report["suscripcion_pro_eliminada"] = removed_pro

    report["adaptador_eliminado"] = 1 if adaptador_svc.delete_session(sid) else 0
    report["contactos_qr_eliminados"] = qr_svc.delete_by_session(sid)

    if app_state is not None:
        historial_escaneos = getattr(app_state, "historial_escaneos", None)
        if isinstance(historial_escaneos, dict):
            historial_escaneos.pop(sid, None)

    report["ok"] = True
    return report
