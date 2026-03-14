"""
API de comunidad (Fase 6B): perfiles, seguir, feed, notificaciones, traducción en tiempo real.
"""
from fastapi import APIRouter, Header, HTTPException, Request, Body

from services import usuario_service as usuario_svc
from services import seguidores_service as seg_svc
from services import feed_service as feed_svc
from services import notificacion_service as notif_svc
from services import valoraciones_service as val_svc
from services import wishlist_service as wish_svc
from services import translation_service as translation_svc
from services import chat_service as chat_svc
from services import news_service as news_svc

router = APIRouter(prefix="", tags=["Comunidad"])


def _vino_detalle_desde_db(vinos: dict, vino_key: str) -> dict:
    vino = vinos.get(vino_key, {}) if isinstance(vinos, dict) else {}
    if not isinstance(vino, dict):
        vino = {}
    return {
        "key": vino_key,
        "nombre": (vino.get("nombre") or vino.get("name") or vino_key or "Vino seleccionado"),
        "bodega": vino.get("bodega") or "No especificada",
        "region": vino.get("region") or "No especificada",
        "pais": vino.get("pais") or "No especificado",
        "tipo": vino.get("tipo") or "No especificado",
        "anada": vino.get("anada"),
        "puntuacion": vino.get("puntuacion"),
        "maridaje": vino.get("maridaje"),
        "precio_estimado": vino.get("precio_estimado"),
    }


def _post_desde_canal(item: dict) -> dict:
    """Convierte un item de canales_feed (noticias/eventos/enoturismo) al formato post del feed."""
    fuente = (item.get("fuente") or "VINO PRO").strip()
    avatar = (fuente[:1] or "V").upper()
    imagen = (item.get("imagen") or item.get("image_url") or "").strip()
    return {
        "id": f"canal-{item.get('id') or ''}",
        "created_at": int(item.get("created_at") or 0),
        "post_type": "canal",
        "username": fuente,
        "avatar_text": avatar,
        "title": (item.get("titulo") or "Sin título").strip(),
        "description": (item.get("descripcion") or "").strip(),
        "badge": (item.get("badge") or "").strip(),
        "vino_key": None,
        "vino_detalle": None,
        "image_url": imagen if imagen else None,
        "brindis_count": 0,
        "comentarios_count": 0,
        "link": (item.get("link") or "").strip(),
    }


def _post_desde_actividad(act: dict, vinos: dict) -> dict:
    tipo = (act.get("tipo") or "").strip().lower()
    vino_key = (act.get("vino_key") or "").strip()
    vino_nombre = (act.get("vino_nombre") or "").strip()
    if vino_key and not vino_nombre:
        det = _vino_detalle_desde_db(vinos, vino_key)
        vino_nombre = det.get("nombre") or vino_key
    badge = "Evento" if tipo == "evento" else ""
    if tipo == "valoracion":
        badge = "Cata"
    elif tipo == "deseado":
        badge = "Wishlist"
    elif tipo == "probado":
        badge = "Descorche"

    descripcion = (act.get("texto") or "").strip()
    if not descripcion:
        if tipo == "valoracion":
            score = act.get("score")
            descripcion = f"Ha valorado {vino_nombre or 'un vino'}" + (f" con {score}★." if score else ".")
        elif tipo == "deseado":
            descripcion = f"Quiere probar {vino_nombre or 'este vino'}."
        elif tipo == "probado":
            descripcion = f"Acaba de probar {vino_nombre or 'este vino'}."
        elif tipo == "evento":
            descripcion = (act.get("titulo") or "Evento en VINEROS").strip()
        else:
            descripcion = "Nueva actividad en VINEROS."

    return {
        "id": f"act-{act.get('id') or ''}",
        "created_at": int(act.get("created_at") or 0),
        "post_type": "sponsor" if tipo == "evento" else "user",
        "username": (act.get("username") or "vinero").strip().lower(),
        "avatar_text": ((act.get("username") or "V").strip()[:1] or "V").upper(),
        "title": vino_nombre or (act.get("titulo") or "Publicación"),
        "description": descripcion,
        "badge": badge,
        "vino_key": vino_key or None,
        "vino_detalle": _vino_detalle_desde_db(vinos, vino_key) if vino_key else None,
        "image_url": None,
        "brindis_count": 0,
        "comentarios_count": 0,
    }


def _spot_vino_pro() -> dict:
    """Spot de autopromoción VINO PRO IA: ejemplo para patrocinadores de cómo se verá su producto en la app."""
    return {
        "id": "spot-vino-pro-ia",
        "created_at": 9999999999,
        "post_type": "sponsor",
        "username": "vino_pro_ia",
        "avatar_text": "V",
        "title": "VINO PRO IA – Tu experto en vinos",
        "description": "Escanea etiquetas, pregunta por maridajes, guarda en tu bodega y comparte en VINEROS. Sin barreras de idioma. Así es como los patrocinadores promocionan su marca aquí.",
        "badge": "Spot ejemplo",
        "vino_key": None,
        "vino_detalle": None,
        "image_url": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&fit=crop",
        "brindis_count": 0,
        "comentarios_count": 0,
        "link": "/inicio",
    }


def _posts_demo_vineros(vinos: dict) -> list[dict]:
    keys = []
    if isinstance(vinos, dict):
        for k, v in vinos.items():
            if isinstance(v, dict):
                keys.append(k)
            if len(keys) >= 3:
                break
    while len(keys) < 3:
        keys.append("")
    base = 1760000000
    return [
        {
            "id": "demo-sponsor-casa-paca",
            "created_at": base + 30,
            "post_type": "sponsor",
            "username": "asador_casa_paca",
            "avatar_text": "C",
            "title": "Asador Casa Paca · Cena maridaje",
            "description": "Este viernes: menú degustación con vinos de autor y descorche comentado por el equipo de sala.",
            "badge": "Evento",
            "vino_key": None,
            "vino_detalle": None,
            "image_url": None,
            "brindis_count": 18,
            "comentarios_count": 4,
        },
        {
            "id": "demo-user-1",
            "created_at": base + 20,
            "post_type": "user",
            "username": "experta_vinos_ana",
            "avatar_text": "A",
            "title": "Cata nocturna en casa",
            "description": "Hoy abro un reserva con carnes a la brasa. Tanino fino y final largo.",
            "badge": "Descorche",
            "vino_key": keys[0] or None,
            "vino_detalle": _vino_detalle_desde_db(vinos, keys[0]) if keys[0] else None,
            "image_url": None,
            "brindis_count": 12,
            "comentarios_count": 3,
        },
        {
            "id": "demo-user-2",
            "created_at": base + 10,
            "post_type": "user",
            "username": "vinero_luca",
            "avatar_text": "L",
            "title": "¿Lo habéis probado?",
            "description": "Busco un tinto elegante para regalar. ¿Con qué plato lo maridaríais?",
            "badge": "Wishlist",
            "vino_key": keys[1] or None,
            "vino_detalle": _vino_detalle_desde_db(vinos, keys[1]) if keys[1] else None,
            "image_url": None,
            "brindis_count": 7,
            "comentarios_count": 5,
        },
        {
            "id": "demo-sponsor-2",
            "created_at": base,
            "post_type": "sponsor",
            "username": "catas_divertidas",
            "avatar_text": "D",
            "title": "Promo VINEROS: cata guiada",
            "description": "Promoción limitada para la comunidad VINEROS: cata guiada + tabla de quesos.",
            "badge": "Promoción",
            "vino_key": keys[2] or None,
            "vino_detalle": _vino_detalle_desde_db(vinos, keys[2]) if keys[2] else None,
            "image_url": None,
            "brindis_count": 22,
            "comentarios_count": 6,
        },
    ]


def _stories_desde_posts(posts: list[dict], limit: int = 10) -> list[dict]:
    stories = []
    seen_users = set()
    for p in posts:
        username = (p.get("username") or "").strip().lower()
        if not username or username in seen_users:
            continue
        seen_users.add(username)
        stories.append(
            {
                "id": f"story-{username}",
                "username": username,
                "avatar_text": (p.get("avatar_text") or username[:1] or "V").upper(),
                "badge": p.get("badge") or "",
                "post_id": p.get("id"),
                "title": p.get("title") or "Historia de VINEROS",
                "post_type": p.get("post_type") or "user",
            }
        )
        if len(stories) >= limit:
            break
    return stories


def _session_and_username(x_session_id: str | None):
    session_id = (x_session_id or "").strip()
    if not session_id:
        raise HTTPException(status_code=401, detail="X-Session-ID requerido")
    username = usuario_svc.get_username_por_session(session_id)
    return session_id, username


def _optional_username(x_session_id: str | None):
    """Sesión y username opcionales (no exige sesión)."""
    session_id = (x_session_id or "").strip()
    username = usuario_svc.get_username_por_session(session_id) if session_id else None
    return session_id, username


@router.post("/api/crear-perfil")
async def crear_perfil(
    username: str = Body(..., embed=True),
    bio: str = Body("", embed=True),
    ubicacion: str = Body("", embed=True),
    idioma: str = Body("", embed=True),
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Crea el perfil de comunidad para la sesión actual. Username único, 3-30 caracteres. idioma: código para leer contenido (es, en, ru, hi, etc.)."""
    session_id = (x_session_id or "").strip()
    if not session_id:
        raise HTTPException(status_code=401, detail="X-Session-ID requerido")
    ok, msg = usuario_svc.crear_perfil(session_id, username, bio, ubicacion, idioma=idioma)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"ok": True, "username": username.strip().lower()}


@router.get("/api/mi-perfil")
async def get_mi_perfil(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Devuelve el perfil del usuario actual (por sesión). 404 si no tiene perfil."""
    session_id, username = _session_and_username(x_session_id)
    perfil = usuario_svc.get_perfil_por_session(session_id)
    if not perfil:
        raise HTTPException(status_code=404, detail="Sin perfil. Crea uno con POST /api/crear-perfil")
    return perfil.to_dict()


@router.put("/api/mi-perfil")
async def actualizar_mi_perfil(
    bio: str | None = Body(None, embed=True),
    ubicacion: str | None = Body(None, embed=True),
    privado: bool | None = Body(None, embed=True),
    idioma: str | None = Body(None, embed=True),
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Actualiza bio, ubicación, privado o idioma del perfil actual. idioma: es, en, ru, hi, etc."""
    session_id, _ = _session_and_username(x_session_id)
    if not usuario_svc.actualizar_perfil(session_id, bio=bio, ubicacion=ubicacion, privado=privado, idioma=idioma):
        raise HTTPException(status_code=404, detail="Sin perfil")
    return {"ok": True}


@router.get("/api/perfil/{username}")
async def get_perfil_publico(
    username: str,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Perfil público por username. Incluye si el usuario actual sigue a este perfil (si hay sesión)."""
    perfil = usuario_svc.get_perfil_por_username(username)
    if not perfil:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    out = perfil.to_dict()
    _, mi_username = _optional_username(x_session_id)
    out["yo_sigo"] = seg_svc.sigue_a(mi_username or "", username) if mi_username else False
    out["seguidores_count"] = len(seg_svc.get_seguidores(username))
    out["seguidos_count"] = len(seg_svc.get_seguidos(username))
    return out


@router.post("/api/seguir/{username}")
async def seguir_usuario(
    username: str,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Seguir a un usuario. Crea notificación 'nuevo_seguidor' para el seguido."""
    session_id, mi_username = _session_and_username(x_session_id)
    if not mi_username:
        raise HTTPException(status_code=400, detail="Necesitas un perfil para seguir a otros")
    objetivo = username.strip().lower()
    if usuario_svc.get_perfil_por_username(objetivo) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not seg_svc.seguir(mi_username, objetivo):
        return {"ok": True, "already_following": True}
    notif_svc.add(objetivo, "nuevo_seguidor", from_username=mi_username)
    return {"ok": True}


@router.delete("/api/seguir/{username}")
async def dejar_seguir(
    username: str,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Dejar de seguir a un usuario."""
    _, mi_username = _session_and_username(x_session_id)
    if not mi_username:
        raise HTTPException(status_code=400, detail="Necesitas un perfil")
    seg_svc.dejar_de_seguir(mi_username, username.strip().lower())
    return {"ok": True}


@router.get("/api/seguidores")
async def listar_seguidores(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Lista de usernames que siguen al usuario actual."""
    _, mi_username = _session_and_username(x_session_id)
    if not mi_username:
        return {"seguidores": []}
    return {"seguidores": seg_svc.get_seguidores(mi_username)}


@router.get("/api/seguidos")
async def listar_seguidos(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Lista de usernames que el usuario actual sigue."""
    _, mi_username = _session_and_username(x_session_id)
    if not mi_username:
        return {"seguidos": []}
    return {"seguidos": seg_svc.get_seguidos(mi_username)}


@router.get("/api/feed")
async def get_feed(
    request: Request,
    canal: str = "para_ti",
    limit: int = 50,
    offset: int = 0,
    lang: str | None = None,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """
    Feed por canal. Si lang está definido y no es 'es', títulos y descripciones de posts
    de canal (noticias/eventos/enoturismo) se traducen al idioma del usuario. Sin barreras de idioma.
    """
    canal = (canal or "para_ti").strip().lower()
    if canal not in feed_svc.LISTA_CANALES:
        canal = "para_ti"
    vinos = getattr(request.app.state, "vinos_mundiales", None) or {}
    session_id = (x_session_id or "").strip()
    mi_username = usuario_svc.get_username_por_session(session_id) if session_id else None
    posts = []
    actividad = []
    eventos = []

    if canal == "para_ti":
        eventos = feed_svc.get_eventos_destacados(limit=10)
        if mi_username:
            seguidos = seg_svc.get_seguidos(mi_username)
            actividad = feed_svc.get_feed_para_usuario(seguidos, limit=limit)
            for a in actividad:
                if not a.get("vino_nombre") and a.get("vino_key"):
                    v = vinos.get(a.get("vino_key", ""), {})
                    if isinstance(v, dict):
                        a["vino_nombre"] = v.get("nombre") or v.get("name") or a.get("vino_key", "")
        for ev in eventos:
            posts.append(_post_desde_actividad(ev, vinos))
        for ac in actividad:
            posts.append(_post_desde_actividad(ac, vinos))
        posts.extend(_posts_demo_vineros(vinos))

    elif canal == "vineros":
        if mi_username:
            seguidos = seg_svc.get_seguidos(mi_username)
            actividad = feed_svc.get_feed_para_usuario(seguidos, limit=limit)
            for a in actividad:
                if not a.get("vino_nombre") and a.get("vino_key"):
                    v = vinos.get(a.get("vino_key", ""), {})
                    if isinstance(v, dict):
                        a["vino_nombre"] = v.get("nombre") or v.get("name") or a.get("vino_key", "")
        for ac in actividad:
            posts.append(_post_desde_actividad(ac, vinos))
        posts.extend(_posts_demo_vineros(vinos))

    elif canal == "noticias":
        for item in feed_svc.get_contenido_canal("noticias", limit=limit):
            posts.append(_post_desde_canal(item))

    elif canal == "eventos":
        eventos = feed_svc.get_eventos_destacados(limit=15)
        for ev in eventos:
            posts.append(_post_desde_actividad(ev, vinos))
        for item in feed_svc.get_contenido_canal("eventos", limit=10):
            posts.append(_post_desde_canal(item))

    elif canal == "enoturismo":
        for item in feed_svc.get_contenido_canal("enoturismo", limit=limit):
            posts.append(_post_desde_canal(item))

    elif canal == "equipamiento":
        for item in feed_svc.get_contenido_canal("equipamiento", limit=limit):
            posts.append(_post_desde_canal(item))

    posts.sort(key=lambda p: -(p.get("created_at") or 0))
    dedup = []
    seen = set()
    for p in posts:
        pid = p.get("id") or ""
        if pid in seen:
            continue
        seen.add(pid)
        dedup.append(p)
    safe_offset = max(0, int(offset))
    safe_limit = max(1, min(int(limit), 20))
    page = dedup[safe_offset:safe_offset + safe_limit]
    original_len = len(page)
    if canal == "para_ti" and safe_offset == 0:
        page = [_spot_vino_pro()] + page
    next_offset = safe_offset + original_len
    has_more = next_offset < len(dedup)
    stories = _stories_desde_posts(dedup, limit=10) if canal in ("para_ti", "vineros") else []

    target_lang = (lang or "").strip().lower()
    if target_lang and target_lang != "es":
        canal_indices = [
            i for i, p in enumerate(page)
            if p.get("post_type") == "canal" or p.get("id") == "spot-vino-pro-ia"
        ]
        if canal_indices:
            titles = [page[i].get("title") or "" for i in canal_indices]
            descs = [page[i].get("description") or "" for i in canal_indices]
            try:
                trans_titles = await translation_svc.traducir_lote(titles, target_lang, "es")
                trans_descs = await translation_svc.traducir_lote(descs, target_lang, "es")
                for k, i in enumerate(canal_indices):
                    if k < len(trans_titles):
                        page[i]["title"] = trans_titles[k]
                    if k < len(trans_descs):
                        page[i]["description"] = trans_descs[k]
            except Exception:
                pass

    return {
        "canal": canal,
        "actividad": actividad,
        "eventos": eventos,
        "stories": stories,
        "posts": page,
        "offset": safe_offset,
        "next_offset": next_offset,
        "has_more": has_more,
        "total": len(dedup),
    }


@router.get("/api/noticias")
async def get_noticias(limit: int = 20):
    """
    Canal de noticias de vino: siempre activo. GNews con caché 2h o fallback estático.
    Formato igual que posts del feed (post_type canal) para reutilizar tarjetas.
    """
    items = news_svc.get_wine_news(limit=max(1, min(int(limit), 30)))
    posts = [_post_desde_canal(item) for item in items]
    return {"canal": "noticias", "posts": posts, "has_more": False}


@router.post("/api/traducir")
async def traducir_texto(
    texto: str = Body(..., embed=True),
    idioma_destino: str = Body(..., embed=True),
    idioma_origen: str | None = Body(None, embed=True),
):
    """Traduce un texto al idioma del lector. Comunidad sin barreras de idioma (ruso → hindi, etc.)."""
    traducido = await translation_svc.traducir(texto, idioma_destino, idioma_origen)
    return {"traducido": traducido, "idioma_destino": idioma_destino}


@router.post("/api/traducir-lote")
async def traducir_lote(
    textos: list[str] = Body(..., embed=True),
    idioma_destino: str = Body(..., embed=True),
    idioma_origen: str | None = Body(None, embed=True),
):
    """Traduce varios textos de una vez (para feed/perfiles). Máximo ~20 textos por petición recomendado."""
    if len(textos) > 50:
        textos = textos[:50]
    traducidos = await translation_svc.traducir_lote(textos, idioma_destino, idioma_origen)
    return {"traducidos": traducidos, "idioma_destino": idioma_destino}


@router.post("/api/translate-comment")
async def translate_comment(
    texto_original: str = Body(..., embed=True),
    idioma_destino: str = Body(..., embed=True),
    idioma_origen: str | None = Body(None, embed=True),
):
    """
    Traduce un comentario del feed VINEROS con contexto vinícola.
    Prioriza Gemini para preservar términos técnicos del vino.
    """
    original = (texto_original or "").strip()
    if not original:
        raise HTTPException(status_code=400, detail="texto_original es obligatorio")
    traducido = await translation_svc.traducir_con_gemini_vino(
        original,
        idioma_destino=idioma_destino,
        idioma_origen=idioma_origen,
    )
    return {
        "ok": True,
        "texto_original": original,
        "texto_traducido": traducido,
        "idioma_destino": idioma_destino,
    }


# ----- Chat: cada usuario escribe en su idioma; la app traduce al idioma del lector -----

@router.get("/api/conversaciones")
async def listar_conversaciones(
    limit: int = 50,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Lista de conversaciones del usuario (other_username, last_message, last_at)."""
    _, mi_username = _session_and_username(x_session_id)
    if not mi_username:
        return {"conversaciones": []}
    lista = chat_svc.get_conversaciones(mi_username, limit=limit)
    return {"conversaciones": lista}


@router.get("/api/chat/{username}")
async def get_chat(
    username: str,
    limit: int = 100,
    lang: str | None = None,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """
    Mensajes con ese usuario. Si lang está definido, los mensajes del otro usuario
    se traducen al idioma del lector (texto_traducido). Sin barreras de idioma en VINEROS.
    """
    _, mi_username = _session_and_username(x_session_id)
    if not mi_username:
        raise HTTPException(status_code=401, detail="Necesitas perfil para chatear")
    other = (username or "").strip().lower()
    if not other or other == mi_username:
        raise HTTPException(status_code=400, detail="Usuario no válido")
    if usuario_svc.get_perfil_por_username(other) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    msgs = chat_svc.get_mensajes(mi_username, other, limit=limit)
    target_lang = (lang or "").strip().lower()
    if target_lang:
        to_translate = [m for m in msgs if (m.get("from_username") or "").strip().lower() != mi_username and (m.get("texto") or "").strip()]
        if to_translate:
            textos = [m.get("texto", "") for m in to_translate]
            try:
                traducidos = await translation_svc.traducir_lote(textos, target_lang, "auto")
                idx = 0
                for m in msgs:
                    if (m.get("from_username") or "").strip().lower() != mi_username and (m.get("texto") or "").strip():
                        if idx < len(traducidos):
                            m["texto_traducido"] = traducidos[idx]
                        idx += 1
            except Exception:
                pass
    return {"username": other, "mi_username": mi_username, "mensajes": msgs}


@router.post("/api/chat/{username}")
async def enviar_mensaje_chat(
    username: str,
    texto: str = Body(..., embed=True),
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Envía un mensaje al usuario. Guárdalo en tu idioma; el otro lo verá traducido al suyo."""
    _, mi_username = _session_and_username(x_session_id)
    if not mi_username:
        raise HTTPException(status_code=401, detail="Necesitas perfil para chatear")
    other = (username or "").strip().lower()
    if not other or other == mi_username:
        raise HTTPException(status_code=400, detail="Usuario no válido")
    if usuario_svc.get_perfil_por_username(other) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    msg = chat_svc.enviar_mensaje(mi_username, other, texto)
    if not msg:
        raise HTTPException(status_code=400, detail="Mensaje vacío o inválido")
    notif_svc.add(other, "nuevo_mensaje", from_username=mi_username, ref_id=msg.get("id", ""))
    return {"ok": True, "mensaje": msg}


@router.get("/api/perfil/{username}/valoraciones")
async def get_valoraciones_perfil(
    username: str,
    limit: int = 50,
):
    """Valoraciones públicas de un usuario (para su perfil)."""
    lista = val_svc.get_valoraciones_por_username(username, limit=limit)
    return {"username": username, "valoraciones": lista}


@router.get("/api/perfil/{username}/actividad")
async def get_actividad_perfil(
    username: str,
    limit: int = 30,
):
    """Actividad reciente de un usuario (para su perfil)."""
    actividades = feed_svc.get_actividad_de_usuario(username, limit=limit)
    return {"username": username, "actividad": actividades}


@router.get("/api/notificaciones")
async def get_notificaciones(
    limit: int = 50,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Notificaciones del usuario actual."""
    _, mi_username = _session_and_username(x_session_id)
    if not mi_username:
        return {"notificaciones": []}
    lista = notif_svc.get_todas(mi_username, limit=limit)
    return {"notificaciones": lista}


@router.post("/api/notificaciones/leer")
async def marcar_notificaciones_leidas(
    ids: list[str] | None = Body(None, embed=True),
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Marca notificaciones como leídas. Si ids es null, marca todas."""
    _, mi_username = _session_and_username(x_session_id)
    if not mi_username:
        return {"ok": True}
    notif_svc.marcar_leidas(mi_username, ids)
    return {"ok": True}
