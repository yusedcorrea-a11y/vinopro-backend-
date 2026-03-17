"""
WebSocket de signaling para llamadas de voz y videollamadas en el chat VINEROS.
Protocolo: register (implícito), set_lang, invite, incoming, offer, answer, ice, hangup, stt_text (traductor IA), translated, offline.
"""
import json
import logging
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from services import usuario_service as usuario_svc
from services import translation_service as translation_svc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Llamadas"])

# Usuarios conectados: username (lowercase) -> WebSocket
_connections: dict[str, WebSocket] = {}
# Idioma preferido por usuario (para traductor en llamada): username -> código (es, en, ru, hi, etc.)
_user_lang: dict[str, str] = {}


def _norm(u: str) -> str:
    return (u or "").strip().lower()


async def _send_json(ws: WebSocket, obj: dict[str, Any]) -> None:
    try:
        await ws.send_text(json.dumps(obj, ensure_ascii=False))
    except Exception as e:
        logger.warning("[CALL_WS] send_json: %s", e)


@router.websocket("/ws/call")
async def websocket_call(
    websocket: WebSocket,
    session_id: str = Query(..., alias="session_id"),
):
    """
    Conexión WebSocket para signaling de llamadas.
    Query: session_id (obligatorio). El servidor resuelve el username desde la sesión.
    Mensajes JSON: { "type": "invite"|"offer"|"answer"|"ice"|"hangup", "to": "username", ... }
    """
    await websocket.accept()
    username = None
    try:
        username = usuario_svc.get_username_por_session((session_id or "").strip())
        if not username:
            await _send_json(websocket, {"type": "error", "message": "Sesión inválida o sin perfil"})
            await websocket.close(code=4001)
            return
        username = _norm(username)
        _connections[username] = websocket
        logger.info("[CALL_WS] Conectado: %s", username)
        await _send_json(websocket, {"type": "registered", "username": username})

        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await _send_json(websocket, {"type": "error", "message": "JSON inválido"})
                continue
            t = (msg.get("type") or "").strip().lower()
            to_user = _norm(msg.get("to") or "")

            if t == "invite":
                # A quiere llamar a B. video: true = videollamada, false = solo voz
                if not to_user or to_user == username:
                    await _send_json(websocket, {"type": "error", "message": "Usuario destino inválido"})
                    continue
                if usuario_svc.get_perfil_por_username(to_user) is None:
                    await _send_json(websocket, {"type": "offline", "to": to_user})
                    continue
                peer_ws = _connections.get(to_user)
                if not peer_ws:
                    await _send_json(websocket, {"type": "offline", "to": to_user})
                    continue
                try:
                    await _send_json(peer_ws, {
                        "type": "incoming",
                        "from": username,
                        "video": bool(msg.get("video", False)),
                    })
                    await _send_json(websocket, {"type": "invite_ok", "to": to_user})
                except Exception as e:
                    logger.warning("[CALL_WS] invite to %s: %s", to_user, e)
                    await _send_json(websocket, {"type": "offline", "to": to_user})

            elif t in ("offer", "answer", "ice"):
                if not to_user:
                    await _send_json(websocket, {"type": "error", "message": "Falta 'to'"})
                    continue
                peer_ws = _connections.get(to_user)
                if not peer_ws:
                    await _send_json(websocket, {"type": "offline", "to": to_user})
                    continue
                try:
                    forward = {"type": t, "from": username, **{k: v for k, v in msg.items() if k not in ("type", "to")}}
                    await _send_json(peer_ws, forward)
                except Exception as e:
                    logger.warning("[CALL_WS] forward %s to %s: %s", t, to_user, e)

            elif t == "hangup":
                if to_user:
                    peer_ws = _connections.get(to_user)
                    if peer_ws:
                        try:
                            await _send_json(peer_ws, {"type": "hangup", "from": username})
                        except Exception:
                            pass
                # Siempre respondemos ok al que cuelga
                await _send_json(websocket, {"type": "hangup_ok"})

            elif t == "set_lang":
                # Idioma del usuario para traductor en llamada (es, en, ru, hi, fr, de, etc.)
                lang = (msg.get("lang") or "").strip().lower()[:5]
                if lang:
                    _user_lang[username] = lang
                    await _send_json(websocket, {"type": "set_lang_ok", "lang": lang})

            elif t == "stt_text":
                # Traductor IA: A habla → texto en su idioma → traducir al idioma de B → enviar a B
                if not to_user or to_user == username:
                    await _send_json(websocket, {"type": "error", "message": "Falta 'to' válido"})
                    continue
                text = (msg.get("text") or "").strip()
                if not text:
                    continue
                source_lang = (msg.get("source_lang") or "auto").strip().lower()[:5] or "auto"
                target_lang = _user_lang.get(to_user) or "en"
                if source_lang == "auto":
                    source_lang = None
                try:
                    translated = await translation_svc.traducir(text, target_lang, source_lang)
                    if translated:
                        peer_ws = _connections.get(to_user)
                        if peer_ws:
                            await _send_json(peer_ws, {
                                "type": "translated",
                                "from": username,
                                "text": translated,
                                "target_lang": target_lang,
                            })
                except Exception as e:
                    logger.warning("[CALL_WS] traducir stt_text: %s", e)

            else:
                await _send_json(websocket, {"type": "error", "message": f"Tipo desconocido: {t}"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.exception("[CALL_WS] Error: %s", e)
        try:
            await _send_json(websocket, {"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        if username and _connections.get(username) == websocket:
            del _connections[username]
            _user_lang.pop(username, None)
            logger.info("[CALL_WS] Desconectado: %s", username)
