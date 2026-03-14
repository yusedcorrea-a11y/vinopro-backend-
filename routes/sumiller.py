"""
Endpoint del experto en vinos virtual: responde preguntas sobre el vino escaneado
o preguntas generales (maridajes, recomendaciones) usando la base de 539 vinos.
Mantiene contexto de las últimas 3 preguntas por sesión.
"""
import re

from fastapi import APIRouter, Header, HTTPException, Request, Body

from services import sumiller_service as svc_sumiller
from services import translation_service as translation_svc
from services.imagen_service import get_imagen_vino
from services.busqueda_service import buscar_vinos_avanzado, buscar_vinos_con_sugerencia
from services.api_externa_service import buscar_por_texto as off_buscar_por_texto
from services import recomendaciones_service as rec_svc
from services.ocr_normalizer import limpiar as normalizar_ocr
from services import enlaces_service as enlaces_svc
from routes.escaneo import _guardar_vino_consulta

router = APIRouter(prefix="", tags=["Experto en Vinos"])


async def _traducir_respuesta_si_lang(texto: str, lang: str | None) -> str:
    """Si lang está definido y no es 'es', traduce la respuesta al idioma del usuario."""
    if not (texto or "").strip():
        return texto or ""
    lang = (lang or "").strip().lower()
    if not lang or lang == "es":
        return texto
    try:
        return await translation_svc.traducir(texto, lang, "es")
    except Exception:
        return texto

MAX_CONTEXTO = 3


def _get_consultas(request: Request) -> dict:
    if not hasattr(request.app.state, "consultas_escaneo"):
        request.app.state.consultas_escaneo = {}
    return request.app.state.consultas_escaneo


def _unwrap_consulta(consultas: dict, consulta_id: str) -> tuple:
    """Devuelve (vino, key) compatible con formato antiguo (solo vino) o nuevo ({vino, key})."""
    raw = consultas.get(consulta_id)
    if raw is None:
        return None, None
    if isinstance(raw, dict) and "vino" in raw:
        return raw["vino"], raw.get("key")
    vino = raw
    key = raw.get("key") if isinstance(raw, dict) else None
    return vino, key


def _get_historial_sumiller(request: Request) -> dict:
    if not hasattr(request.app.state, "historial_sumiller"):
        request.app.state.historial_sumiller = {}
    return request.app.state.historial_sumiller


def _responder_pregunta(vino: dict, texto: str, perfil: str = "aficionado") -> str:
    """
    Responde una pregunta sobre el vino usando sus campos (rule-based).
    perfil: principiante (lenguaje simple), aficionado (normal), profesional (técnico).
    Tono: español elegante pero cercano; términos técnicos cuando toque; explicar si principiante.
    """
    texto_low = (texto or "").strip().lower()
    nombre = vino.get("nombre") or "este vino"
    maridaje = vino.get("maridaje") or "No tenemos información de maridaje."
    descripcion = vino.get("descripcion") or "No hay descripción."
    notas_cata = vino.get("notas_cata") or "No hay notas de cata."
    bodega = vino.get("bodega") or "No especificada"
    region = vino.get("region") or "Por determinar"
    pais = vino.get("pais") or "Desconocido"
    tipo = vino.get("tipo") or "tinto"
    precio = vino.get("precio_estimado") or "No indicado"
    puntuacion = vino.get("puntuacion")
    perfil = (perfil or "aficionado").strip().lower()
    if perfil not in ("principiante", "aficionado", "profesional"):
        perfil = "aficionado"

    if not texto_low:
        if perfil == "principiante":
            return f"Pregúntame sobre {nombre}: por ejemplo maridaje, descripción o tipo de vino."
        if perfil == "profesional":
            return f"Puedo contarle maridaje, descripción, notas de cata, bodega, región, tipo, precio o puntuación de «{nombre}»."
        return f"Puedo hablarle de maridaje, descripción, bodega, región o tipo del vino «{nombre}». ¿Qué le interesa?"

    raw = None
    if any(p in texto_low for p in ["maridaje", "comer", "comida", "acompañar", "ir bien", "recomienda"]):
        raw = f"Para {nombre}, recomendamos: {maridaje}"
    elif any(p in texto_low for p in ["descripcion", "descripción", "qué es", "cuéntame", "hablar"]):
        raw = f"{nombre}: {descripcion}"
    elif any(p in texto_low for p in ["notas", "cata", "sabor", "aroma", "gusto"]):
        raw = f"Notas de cata de {nombre}: {notas_cata}"
    elif any(p in texto_low for p in ["bodega", "productor", "quién hace"]):
        raw = f"La bodega de {nombre} es: {bodega}."
    elif any(p in texto_low for p in ["región", "region", "origen", "dónde", "donde"]):
        raw = f"Procede de {region}, {pais}."
    elif any(p in texto_low for p in ["tipo", "blanco", "tinto", "rosado"]):
        raw = f"Es un vino {tipo}."
    elif any(p in texto_low for p in ["precio", "cuesta", "valor"]):
        raw = f"Precio estimado: {precio}."
    elif any(p in texto_low for p in ["puntuacion", "puntuación", "puntos", "nota", "valoración"]):
        if puntuacion is not None:
            raw = f"Tiene una puntuación de {puntuacion} puntos."
        else:
            raw = "No tenemos puntuación registrada para este vino."
    else:
        raw = f"Resumen de {nombre}: {bodega}, {region} ({pais}). {descripcion[:200]}... Maridaje: {maridaje}"

    if perfil == "principiante":
        if len(raw) > 180:
            raw = raw[:180].rsplit(".", 1)[0].strip() + "." if "." in raw[:180] else raw[:177] + "..."
        if any(term in raw for term in ["crianza", "tanino", "roble"]) and "(" not in raw:
            raw += " (Crianza: tiempo en barrica; taninos: sensación en boca; roble: madera que aporta especias.)"
    if perfil == "profesional" and raw and not raw.endswith("."):
        raw = raw + " (Datos de ficha técnica.)"
    return raw


def _get_vinos(request: Request) -> dict:
    return getattr(request.app.state, "vinos_mundiales", {})


def _es_maridaje(texto: str) -> bool:
    t = (texto or "").lower()
    return (
        "maridaje" in t or "vino con" in t or "qué vino" in t or "que vino" in t
        or "vino para" in t or "acompañar" in t or "ir bien con" in t
        or any(c in t for c in ["carne", "pescado", "cordero", "caza", "queso", "pasta", "ensalada", "postre"])
    )


def _es_info_vino_concreto(texto: str) -> bool:
    t = (texto or "").lower()
    return (
        "háblame" in t or "hablame" in t or "cuéntame" in t or "cuentame" in t
        or "información del" in t or "informacion del" in t or "info del" in t
        or "qué es el" in t or "que es el" in t or "qué es la" in t or "quien es" in t
    )


def _es_recomendacion(texto: str) -> bool:
    t = (texto or "").lower()
    return (
        "me gustan" in t or "me gusta" in t or "recomiéndame" in t or "recomienda" in t
        or "recomendación" in t or "recomendaciones" in t or "recomendacion" in t
        or "qué recomendación" in t or "que recomendacion" in t or "qué me recomiendas" in t or "que me recomiendas" in t
        or ("ribera" in t and ("donde" in t or "tomar" in t or "tomarme" in t or "puedo" in t or "tomarme" in t))
        or "busco" in t or "quiero" in t or "tintos" in t or "blancos" in t or "robusto" in t or "elegante" in t
        or "qué tinto" in t or "que tinto" in t or "qué blanco" in t or "que blanco" in t
        or "qué vino" in t or "que vino" in t or "dame un" in t or "dame una" in t
        or "vino argentino" in t or "vino español" in t or "vino chileno" in t or "tinto rioja" in t
        or "menos de" in t or "barato" in t or "económico" in t or "economico" in t
        or "mejor" in t or "cuál es el mejor" in t or "cual es el mejor" in t or "cuál es la mejor" in t
    )


def _es_info_general(texto: str) -> bool:
    """Preguntas tipo 'qué es X', 'información sobre X' (sin vino concreto en BD)."""
    t = (texto or "").lower()
    return (
        "qué es" in t or "que es" in t or "qué es el" in t or "que es el" in t
        or "información sobre" in t or "informacion sobre" in t
        or "hablar del" in t or "hablame del" in t or "cuéntame del" in t or "cuentame del" in t
    )


def _es_pregunta_tipo_famoso(texto: str) -> bool:
    """Preguntas tipo 'qué lambrusco es la más famosa', 'cuál es el mejor malbec' -> usar conocimiento."""
    t = (texto or "").lower()
    return (
        "famoso" in t or "famosa" in t or "famosos" in t or "conocido" in t or "conocida" in t
        or ("mejor" in t and ("lambrusco" in t or "malbec" in t or "rioja" in t or "champagne" in t or "cava" in t or "riesling" in t))
    )


def _maridaje_por_tipo(tipo: str) -> str:
    """Sugerencia genérica de maridaje según tipo cuando no hay dato específico."""
    t = (tipo or "tinto").strip().lower()
    if "blanco" in t:
        return "Pescados, mariscos, ensaladas, arroces y quesos frescos. Ideal para aperitivo."
    if "rosado" in t or "rosé" in t:
        return "Ensaladas, pasta ligera, tapas y barbacoa. Muy versátil."
    if "espumoso" in t or "cava" in t or "champagne" in t:
        return "Aperitivos, mariscos, sushi y celebraciones. Perfecto para brindar."
    if "dulce" in t or "postre" in t:
        return "Postres, foie gras, quesos azules y frutas."
    return "Carnes rojas, guisos, quesos curados y embutidos. Clásico maridaje de tinto."


def _construir_ficha_respuesta(vino: dict, key_used: str | None) -> dict:
    """Construye la respuesta estándar de experto-en-vinos-ficha a partir de un dict vino."""
    nombre = (vino.get("nombre") or "").strip() or "Sin nombre"
    info_basica = {
        "nombre": nombre,
        "bodega": (vino.get("bodega") or "").strip() or "No especificada",
        "region": (vino.get("region") or "").strip() or "Por determinar",
        "pais": (vino.get("pais") or "").strip() or "Desconocido",
        "tipo": (vino.get("tipo") or "").strip() or "tinto",
        "puntuacion": vino.get("puntuacion"),
        "precio_estimado": (vino.get("precio_estimado") or "").strip() or None,
    }
    especificacion_tecnica = {
        "descripcion": (vino.get("descripcion") or "").strip() or None,
        "notas_cata": (vino.get("notas_cata") or "").strip() or None,
        "uva_principal": (vino.get("uva_principal") or "").strip() or None,
        "graduacion": (vino.get("graduacion") or "").strip() or None,
    }
    maridaje_raw = (vino.get("maridaje") or "").strip()
    if not maridaje_raw or maridaje_raw == "Información no disponible." or "no tenemos información" in maridaje_raw.lower():
        maridaje = "Recomendación por tipo: " + _maridaje_por_tipo(info_basica["tipo"])
    else:
        maridaje = maridaje_raw
    return {
        "vino_key": key_used,
        "info_basica": info_basica,
        "especificacion_tecnica": especificacion_tecnica,
        "maridaje": maridaje,
        "incorporado": vino.get("_incorporado", False),
    }


@router.get("/api/sumiller-ficha")
def api_sumiller_ficha(
    request: Request,
    vino_key: str | None = None,
    consulta_id: str | None = None,
    nombre: str | None = None,
    pais: str | None = None,
):
    """
    Ficha estructurada del vino para la app (Fase 1 + Fase 2).
    Devuelve: info_basica, especificacion_tecnica, maridaje, enlaces_compra.
    - vino_key o consulta_id: vino ya en nuestra base.
    - pais: código ISO (ES, FR, MX...) para enlaces de compra (Amazon primero si tiene, luego locales).
      Si no se envía, se usa X-Country o detección por IP (por defecto ES).
    - Si no está en base: indica nombre (o texto de búsqueda). Se busca en BD por nombre
      y si no hay resultado en Open Food Facts; si se encuentra, se GUARDA en nuestra base
      (registrados.json) y se devuelve la ficha. Así la base crece con cada consulta.
    """
    vinos_dict = _get_vinos(request)
    vino = None
    key_used = None

    if consulta_id:
        consultas = _get_consultas(request)
        vino, key_used = _unwrap_consulta(consultas, consulta_id)
    if vino is None and vino_key:
        key_used = (vino_key or "").strip()
        vino = vinos_dict.get(key_used) if key_used else None

    # Si no encontramos por key/consulta: buscar por nombre y, si viene de fuera, incorporar a la base
    if (not vino or not isinstance(vino, dict)) and nombre and (nombre := (nombre or "").strip()):
        # 1) Buscar en nuestra BD por nombre (por si la key no coincidía)
        coincidencias = buscar_vinos_avanzado(vinos_dict, nombre, limite=3)
        if coincidencias and coincidencias[0]["score"] >= 3.0:
            mejor = coincidencias[0]
            vino = mejor["vino"]
            key_used = mejor["key"]
        else:
            # 2) Buscar en Open Food Facts
            resultados_off = off_buscar_por_texto(nombre, limite=1)
            if resultados_off and len(resultados_off) > 0:
                vino_externo = resultados_off[0]
                key_used = _guardar_vino_consulta(request, vino_externo)
                if key_used:
                    vino = vinos_dict.get(key_used) or vino_externo
                    vino["_incorporado"] = True
                else:
                    vino = vino_externo
                    vino["_incorporado"] = False
                    key_used = None

    if not vino or not isinstance(vino, dict):
        raise HTTPException(
            status_code=404,
            detail="Vino no encontrado. Indica vino_key, consulta_id o nombre del vino para buscarlo e incorporarlo.",
        )

    # País para enlaces de compra: query param, cabecera X-Country o IP (Fase 2)
    pais_resuelto = (pais or "").strip().upper() or request.headers.get("X-Country", "").strip().upper()
    if not pais_resuelto and request.client:
        pais_resuelto = enlaces_svc.detectar_pais_por_ip(request.client.host)
    if not pais_resuelto:
        pais_resuelto = "ES"

    respuesta = _construir_ficha_respuesta(vino, key_used)
    vino_id = key_used or ""
    vino_nombre = (vino.get("nombre") or "").strip()
    enlaces = enlaces_svc.enlaces_ordenados_para_app(vino_id, vino_nombre, pais_resuelto)
    respuesta["enlaces_compra"] = [t.to_dict() for t in enlaces]
    respuesta["pais_enlaces"] = pais_resuelto
    return respuesta


@router.get("/preguntar-sumiller")
async def preguntar_sumiller(
    request: Request,
    texto: str,
    consulta_id: str | None = None,
    vino_key: str | None = None,
    perfil: str = "aficionado",
    lang: str | None = None,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """
    Pregunta al experto en vinos virtual.
    - lang: idioma de la respuesta (es, en, fr, de, it, pt, ru, etc.). Si no es 'es', la respuesta se traduce automáticamente.
    - Con consulta_id o vino_key: responde sobre ese vino (rule-based).
    - Sin ellos: responde con maridajes o recomendaciones de la base de 539 vinos,
      y usa el contexto de las últimas 3 preguntas (X-Session-ID) para "Y de esos, ¿cuál...?"
    """
    vinos_dict = _get_vinos(request)
    # Normalizar texto OCR sucio (Sados -> Viña Pedrosa, Bobgcas -> Bodegas, etc.) para búsqueda y respuestas
    texto_clean = normalizar_ocr((texto or "").strip()) or (texto or "").strip()
    perfil = (perfil or "aficionado").strip().lower()
    if perfil not in ("principiante", "aficionado", "profesional"):
        perfil = "aficionado"

    # --- Modo: vino concreto (consulta_id o vino_key) ---
    vino = None
    key_para_comprar = None
    origen = None
    if consulta_id:
        consultas = _get_consultas(request)
        vino, key_para_comprar = _unwrap_consulta(consultas, consulta_id)
        origen = "consulta_id"
    if not vino and vino_key:
        vino = vinos_dict.get(vino_key)
        key_para_comprar = vino_key
        origen = "vino_key"

    if vino:
        if key_para_comprar is None and origen == "vino_key":
            key_para_comprar = vino_key
        tipo = (vino.get("tipo") or "tinto").strip().lower()
        if tipo not in ("tinto", "blanco", "rosado", "espumoso"):
            tipo = "tinto"
        imagen_url = get_imagen_vino(key_para_comprar or "", tipo)
        try:
            from services import sumiller_gemini_service as gemini_svc
            respuesta_gemini = gemini_svc.responder_sobre_vino(texto_clean, vino, perfil=perfil)
            respuesta = respuesta_gemini if respuesta_gemini else _responder_pregunta(vino, texto_clean, perfil=perfil)
        except Exception:
            respuesta = _responder_pregunta(vino, texto_clean, perfil=perfil)
        respuesta = await _traducir_respuesta_si_lang(respuesta, lang)
        try:
            from services import analytics_service
            analytics_service.registrar_pregunta(texto_clean, vino.get("nombre"))
        except Exception:
            pass
        return {
            "consulta_id": consulta_id,
            "vino_key": key_para_comprar,
            "pregunta": texto_clean,
            "respuesta": respuesta,
            "vino_nombre": vino.get("nombre"),
            "imagen_url": imagen_url,
            "mostrar_boton_comprar": bool(key_para_comprar),
            "perfil": perfil,
        }

    # --- Sin vino concreto: 404/400 solo si pidieron uno y no lo tenemos ---
    if consulta_id or vino_key:
        raise HTTPException(
            status_code=404,
            detail="Vino no encontrado para el consulta_id o vino_key indicado. Escanee de nuevo o use una key válida.",
        )

    # --- Comandos de navegación (sin vino concreto) ---
    texto_low = texto_clean.lower()
    navegacion = None
    respuesta_nav = None
    if any(x in texto_low for x in [
        "dónde puedo tomar un vino", "donde puedo tomar un vino", "tomar un vino cerca",
        "restaurantes con vinos cerca", "vinotecas cercanas", "bares de vino cerca",
        "dónde sirven", "donde sirven", "lugares para tomar vino", "sitios para vino",
        "dónde hay vinoteca", "donde hay vinoteca", "cerca de mí", "cerca de mi"
    ]):
        navegacion = "/mapa"
        respuesta_nav = "Te llevo al mapa de lugares cercanos: restaurantes, vinotecas y bares. Ahí puedes usar tu ubicación o buscar por ciudad."
    if not navegacion and any(x in texto_low for x in ["abrir mi bodega", "ir a mi bodega", "quiero ver mi bodega", "mostrar mi bodega"]):
        navegacion = "/bodega"
        respuesta_nav = "Puedes abrir Mi Bodega aquí."
    if not navegacion and any(x in texto_low for x in ["mostrar planes", "ver planes", "ir a planes", "abrir planes", "quiero ver planes"]):
        navegacion = "/planes"
        respuesta_nav = "Te llevo a Planes."
    if not navegacion and any(x in texto_low for x in ["ir a adaptador", "abrir adaptador", "adaptador para restaurantes", "ver adaptador"]):
        navegacion = "/adaptador"
        respuesta_nav = "Aquí tienes el Adaptador para restaurantes."
    if not navegacion and any(x in texto_low for x in ["abrir menú", "abrir menu", "menú secreto", "menu secreto", "abrir el menú", "mostrar menú"]):
        navegacion = "menu"
        respuesta_nav = "Abre el menú con el botón ☰ o haciendo doble clic en el ayudante."
    if not navegacion and ("cambiar idioma" in texto_low or "cambiar el idioma" in texto_low or "idioma a " in texto_low):
        lang_map = {"ingles": "en", "english": "en", "español": "es", "espanol": "es", "francés": "fr", "frances": "fr",
                    "alemán": "de", "aleman": "de", "italiano": "it", "portugués": "pt", "portugues": "pt",
                    "ruso": "ru", "árabe": "ar", "arabe": "ar", "chino": "zh", "japonés": "ja", "japones": "ja", "coreano": "ko", "türkçe": "tr", "turco": "tr"}
        for nombre, code in lang_map.items():
            if nombre in texto_low:
                navegacion = f"/set-lang?lang={code}"
                respuesta_nav = f"Idioma cambiado a {nombre.capitalize()}. Redirigiendo..."
                break
    if navegacion and respuesta_nav:
        respuesta_nav = await _traducir_respuesta_si_lang(respuesta_nav, lang)
        return {
            "consulta_id": None,
            "vino_key": None,
            "pregunta": texto_clean,
            "respuesta": respuesta_nav,
            "vino_nombre": None,
            "imagen_url": None,
            "mostrar_boton_comprar": False,
            "perfil": perfil,
            "navegacion": navegacion,
        }

    # --- Modo: pregunta general (maridaje, recomendación, contexto) ---
    if not isinstance(vinos_dict, dict):
        vinos_dict = {}
    try:
        out = _preguntar_sumiller_general(request, vinos_dict, texto_clean, perfil, x_session_id)
        if out.get("respuesta"):
            out["respuesta"] = await _traducir_respuesta_si_lang(out["respuesta"], lang)
        return out
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("[EXPERTO_EN_VINOS] Error en preguntar_sumiller:", e)
        traceback.print_exc()
        # Incluir error real en respuesta para depurar (ver en pantalla qué falla)
        err_msg = str(e)
        err_tb = traceback.format_exc()
        detail = f"Error al procesar la pregunta. Inténtalo de nuevo. [Debug: {err_msg}]"
        raise HTTPException(status_code=500, detail=detail)


def _preguntar_sumiller_general(
    request: Request,
    vinos_dict: dict,
    texto_clean: str,
    perfil: str,
    x_session_id: str | None,
):
    if not isinstance(vinos_dict, dict):
        vinos_dict = {}
    session_id = (x_session_id or "").strip()
    historial_store = _get_historial_sumiller(request)
    contexto = list(historial_store.get(session_id, [])) if session_id else []
    # Keys ya recomendadas en esta sesión (últimas respuestas) para no repetir el mismo vino
    keys_ya_recomendados = []
    for ent in contexto:
        refs = ent.get("vinos_ref") or []
        keys_ya_recomendados.extend(r for r in refs if isinstance(r, str) and r.strip())
    exclude_keys_sesion = list(dict.fromkeys(keys_ya_recomendados))[-25:]
    quizas_quisiste_decir = None

    # Búsqueda previa en BD: si la pregunta menciona un vino (Protos, Viña Pedrosa, etc.), responder con datos de nuestra BD
    coincidencias_bd = buscar_vinos_avanzado(vinos_dict, texto_clean, limite=1)
    vino_bd = None
    key_bd = None
    if coincidencias_bd and coincidencias_bd[0].get("score", 0) >= 3.0:
        cand = coincidencias_bd[0].get("vino")
        if isinstance(cand, dict):
            vino_bd = cand
            key_bd = coincidencias_bd[0].get("key")

    # Intentar resolver "de esos, ¿cuál es el más económico?" con los vinos de la última respuesta
    vinos_ref = []
    if contexto:
        ultimo = contexto[-1]
        refs = ultimo.get("vinos_ref")
        if refs is not None and isinstance(refs, list):
            vinos_ref = [r for r in refs if r]  # keys (str) o dicts; filtrar vacíos
    print("[SUMILLER] session_id=%r, len(contexto)=%s, vinos_ref=%s" % (session_id, len(contexto), vinos_ref))
    respuesta_contexto = svc_sumiller.resolver_contexto_esos(vinos_ref, texto_clean, vinos_dict) if vinos_ref else None

    # Si el usuario preguntó "de esos..." pero no teníamos contexto, ofrecer disculpa
    parece_de_esos = any(p in texto_clean.lower() for p in ["de esos", "de esas", "y de esos", "y de esas"])
    if respuesta_contexto:
        respuesta = respuesta_contexto
        vinos_recomendados = None
        vinos_ref_para_guardar = [r for r in vinos_ref if isinstance(r, str) and (r or "").strip()]
    elif parece_de_esos and not vinos_ref:
        respuesta = "Disculpe, no recordaba los vinos que le recomendé antes. ¿Puede repetir su pregunta sobre maridaje o gustos para que le recomiende de nuevo y luego le diga el más barato o el más caro?"
        vinos_recomendados = None
        vinos_ref_para_guardar = []
    elif parece_de_esos and vinos_ref and not respuesta_contexto:
        respuesta = "Disculpe, no he podido resolver su pregunta sobre esos vinos. ¿Quiere que le recomiende de nuevo y luego le indique el más económico o el más caro?"
        vinos_recomendados = None
        vinos_ref_para_guardar = [r for r in vinos_ref if isinstance(r, str) and (r or "").strip()]
    elif vino_bd and key_bd:
        # Usuario preguntó por un vino que SÍ está en nuestra BD (Protos, Viña Pedrosa, etc.) -> responder con datos reales
        print("[SUMILLER] Búsqueda previa BD: encontrado %s (key=%s)" % (vino_bd.get("nombre", "")[:50], key_bd))
        respuesta = _responder_pregunta(vino_bd, texto_clean, perfil=perfil)
        if any(p in texto_clean.lower() for p in ["código", "codigo", "key", "clave", "identificador", " id "]):
            respuesta += f" En nuestra base de datos la clave de este vino es: «{key_bd}»."
        vinos_recomendados = [vino_bd]
        vinos_ref_para_guardar = [key_bd]
    elif _es_maridaje(texto_clean):
        # Extraer comida aproximada del texto
        comida = texto_clean
        cl = comida.lower()
        for palabra in ["qué vino con", "que vino con", "vino para", "maridaje para", "con qué", "con que"]:
            if palabra in cl:
                comida = cl.split(palabra, 1)[-1].strip().strip("?¿.")
                break
        else:
            if "tengo " in cl and (" que " in cl or " qué " in cl):
                # "tengo cocido hoy que vino me aconsejas" -> cocido hoy
                parte = cl.split("tengo ", 1)[-1].strip()
                for sep in [" que ", " qué ", " que vino", " qué vino"]:
                    if sep in parte:
                        comida = parte.split(sep)[0].strip().strip("?¿.,")
                        break
                else:
                    comida = parte[:50].strip()
            elif " para acompañar" in cl or " acompañar " in cl:
                # "qué vino para acompañar las empanadas" -> empanadas
                idx = cl.find(" para acompañar") if " para acompañar" in cl else cl.find(" acompañar ")
                if idx >= 0:
                    comida = (cl[idx:] + " ").split(" ", 2)[-1].strip().strip("?¿.,") or comida
            elif "hoy toca comida " in cl:
                # "hoy toca comida japonesa que vino pongo" -> comida japonesa / japonesa
                parte = cl.split("hoy toca comida ", 1)[-1].strip()
                for sep in [" que ", " qué ", " que vino", " qué vino", " ?", "?"]:
                    if sep in parte:
                        comida = parte.split(sep)[0].strip().strip("?¿.,")
                        break
                else:
                    comida = parte[:50].strip() if parte else comida
        if not comida or len(comida) < 2:
            comida = "plato"
        coincidencias = svc_sumiller.buscar_vinos_por_maridaje(
            vinos_dict, comida, limite=5, exclude_keys=exclude_keys_sesion
        )
        if coincidencias:
            respuesta = svc_sumiller.formatear_respuesta_maridaje(
                [{"key": r["key"], "vino": r["vino"]} for r in coincidencias if isinstance(r.get("vino"), dict)],
                comida,
                perfil=perfil,
            )
            vinos_recomendados = [r["vino"] for r in coincidencias if isinstance(r.get("vino"), dict)]
            vinos_ref_para_guardar = [str(r["key"]) for r in coincidencias if r.get("key")]
        else:
            respuesta, similares = svc_sumiller.fallback_sin_resultados(comida, vinos_dict, exclude_keys=exclude_keys_sesion)
            vinos_recomendados = [s["vino"] for s in (similares or []) if isinstance(s.get("vino"), dict)] if similares else None
            vinos_ref_para_guardar = [str(s["key"]) for s in similares if s.get("key")] if similares else []
    elif _es_info_vino_concreto(texto_clean):
        # Buscar vino por nombre (ej. "háblame del Marqués de Riscal") con sugerencia "Quizás quisiste decir..."
        nombre_busqueda = texto_clean
        for prefijo in ["háblame del", "hablame del", "cuéntame del", "cuentame del", "información del", "informacion del", "info del", "qué es el", "que es el", "qué es la", "que es la"]:
            if prefijo in nombre_busqueda.lower():
                nombre_busqueda = nombre_busqueda.lower().split(prefijo, 1)[-1].strip().strip("?¿.")
                break
        quizas_quisiste_decir = None
        if nombre_busqueda and len(nombre_busqueda) >= 3:
            busqueda_con_sug = buscar_vinos_con_sugerencia(vinos_dict, nombre_busqueda, limite=5)
            resultados_busqueda = busqueda_con_sug.get("resultados") or []
            quizas_quisiste_decir = busqueda_con_sug.get("quizas_quisiste_decir")
            if resultados_busqueda:
                key_primer = resultados_busqueda[0].get("key")
                vino_primer = vinos_dict.get(key_primer) or resultados_busqueda[0].get("vino")
                if not isinstance(vino_primer, dict):
                    vino_primer = None
                if vino_primer:
                    respuesta = _responder_pregunta(vino_primer, "descripción y maridaje", perfil=perfil)
                    if quizas_quisiste_decir:
                        respuesta = f"Quizás quisiste decir {quizas_quisiste_decir}. " + respuesta
                    vinos_recomendados = [vinos_dict.get(r.get("key")) or r.get("vino") for r in resultados_busqueda[:5] if r.get("key") or r.get("vino")]
                    vinos_recomendados = [v for v in vinos_recomendados if v and isinstance(v, dict)]
                    vinos_ref_para_guardar = [str(r.get("key")) for r in resultados_busqueda[:5] if r.get("key")]
                else:
                    respuesta, similares = svc_sumiller.fallback_sin_resultados(texto_clean, vinos_dict, exclude_keys=exclude_keys_sesion)
                    vinos_recomendados = [s["vino"] for s in (similares or []) if isinstance(s.get("vino"), dict)] if similares else None
                    vinos_ref_para_guardar = [str(s["key"]) for s in similares if s.get("key")] if similares else []
            else:
                respuesta, similares = svc_sumiller.fallback_sin_resultados(texto_clean, vinos_dict, exclude_keys=exclude_keys_sesion)
                vinos_recomendados = [s["vino"] for s in (similares or []) if isinstance(s.get("vino"), dict)] if similares else None
                vinos_ref_para_guardar = [str(s["key"]) for s in similares if s.get("key")] if similares else []
        else:
            respuesta, similares = svc_sumiller.fallback_sin_resultados(texto_clean, vinos_dict, exclude_keys=exclude_keys_sesion)
            vinos_recomendados = [s["vino"] for s in (similares or []) if isinstance(s.get("vino"), dict)] if similares else None
            vinos_ref_para_guardar = [str(s["key"]) for s in similares if s.get("key")] if similares else []
    elif _es_pregunta_tipo_famoso(texto_clean):
        respuesta, similares = svc_sumiller.fallback_sin_resultados(texto_clean, vinos_dict, exclude_keys=exclude_keys_sesion)
        vinos_recomendados = [s["vino"] for s in (similares or []) if isinstance(s.get("vino"), dict)] if similares else None
        vinos_ref_para_guardar = [str(s["key"]) for s in similares if s.get("key")] if similares else []
    elif _es_recomendacion(texto_clean):
        coincidencias = svc_sumiller.buscar_vinos_por_preferencia(
            vinos_dict, texto_clean, limite=5, exclude_keys=exclude_keys_sesion
        )
        if coincidencias:
            respuesta = svc_sumiller.formatear_respuesta_recomendacion(
                [{"key": r["key"], "vino": r["vino"]} for r in coincidencias if isinstance(r.get("vino"), dict)],
                perfil=perfil,
            )
            vinos_recomendados = [r["vino"] for r in coincidencias if isinstance(r.get("vino"), dict)]
            vinos_ref_para_guardar = [str(r["key"]) for r in coincidencias if r.get("key")]
        else:
            respuesta, similares = svc_sumiller.fallback_sin_resultados(texto_clean, vinos_dict, exclude_keys=exclude_keys_sesion)
            vinos_recomendados = [s["vino"] for s in (similares or []) if isinstance(s.get("vino"), dict)] if similares else None
            vinos_ref_para_guardar = [str(s["key"]) for s in similares if s.get("key")] if similares else []
    else:
        respuesta, similares = svc_sumiller.fallback_sin_resultados(texto_clean, vinos_dict, exclude_keys=exclude_keys_sesion)
        vinos_recomendados = [s["vino"] for s in (similares or []) if isinstance(s.get("vino"), dict)] if similares else None
        vinos_ref_para_guardar = [str(s["key"]) for s in similares if s.get("key")] if similares else []

    # Guardar en contexto (últimas 3): pregunta, respuesta y keys de vinos recomendados para "de esos..."
    if session_id:
        nuevo = {
            "pregunta": texto_clean,
            "respuesta": respuesta,
            "vinos_ref": list(vinos_ref_para_guardar),
        }
        contexto = (contexto + [nuevo])[-MAX_CONTEXTO:]
        historial_store[session_id] = contexto
        print("[SUMILLER] historial_store después de guardar: session_id=%r, entradas=%s, última vinos_ref=%s" % (
            session_id, len(contexto), len(nuevo.get("vinos_ref") or [])))

    vinos_ref_para_guardar = [k for k in (vinos_ref_para_guardar or []) if isinstance(k, str) and (k or "").strip()]
    # Dar vida a la respuesta con Gemini (mismo plan gratuito que el escáner). Si falla, se mantiene la respuesta rule-based.
    try:
        from services import sumiller_gemini_service as gemini_svc
        respuesta_rewrite = gemini_svc.reescribir_respuesta_sumiller(texto_clean, respuesta, perfil=perfil)
        if respuesta_rewrite:
            respuesta = respuesta_rewrite
    except Exception:
        pass
    vino_nombre = vinos_recomendados[0].get("nombre") if vinos_recomendados and isinstance(vinos_recomendados[0], dict) else None
    primer_key = (vinos_ref_para_guardar[0] if vinos_ref_para_guardar else None)
    if primer_key is not None and not isinstance(primer_key, str):
        primer_key = str(primer_key) if primer_key else None
    primer_vino = vinos_recomendados[0] if vinos_recomendados and isinstance(vinos_recomendados[0], dict) else None
    tipo_primer = (primer_vino.get("tipo") or "tinto").strip().lower() if primer_vino else "tinto"
    if tipo_primer not in ("tinto", "blanco", "rosado", "espumoso"):
        tipo_primer = "tinto"
    imagen_url = get_imagen_vino((primer_key or "").strip(), tipo_primer) if primer_key else None
    out = {
        "consulta_id": None,
        "vino_key": primer_key,
        "pregunta": texto_clean,
        "respuesta": respuesta,
        "vino_nombre": vino_nombre,
        "imagen_url": imagen_url,
        "mostrar_boton_comprar": bool(primer_key),
        "perfil": perfil,
    }
    if vinos_recomendados is not None:
        # Solo incluir entradas que son dict (evitar 500 si el catálogo tiene valores no-ficha)
        validos = [(i, v) for i, v in enumerate(vinos_recomendados[:5]) if isinstance(v, dict)]
        out["vinos_recomendados"] = [
            {
                "key": vinos_ref_para_guardar[i] if i < len(vinos_ref_para_guardar) else None,
                "nombre": v.get("nombre"),
                "bodega": v.get("bodega"),
                "region": v.get("region"),
                "precio_estimado": v.get("precio_estimado"),
            }
            for i, v in validos
        ]
    if quizas_quisiste_decir:
        out["quizas_quisiste_decir"] = quizas_quisiste_decir
    if session_id:
        try:
            rec_svc.registrar_busqueda(session_id, texto_clean, vinos_ref_para_guardar or [])
        except Exception:
            pass
    exclude_keys = list(vinos_ref_para_guardar) if vinos_ref_para_guardar else []
    try:
        sugerencias = rec_svc.get_recomendaciones_personalizadas(session_id or "", vinos_dict, exclude_keys=exclude_keys, limite=3) or []
    except Exception:
        sugerencias = []
    out["sugerencias_personalizadas"] = [
        {"key": s.get("key"), "nombre": (s.get("vino") or {}).get("nombre"), "bodega": (s.get("vino") or {}).get("bodega"), "region": (s.get("vino") or {}).get("region"), "precio_estimado": (s.get("vino") or {}).get("precio_estimado")}
        for s in sugerencias if isinstance(s, dict)
    ]
    return out


@router.post("/api/feedback-vino")
async def feedback_vino(
    request: Request,
    session_id: str = Body(..., embed=True),
    wine_key: str = Body(..., embed=True),
    like: bool = Body(..., embed=True),
):
    """Registra me gusta (like=True) o no me gusta (like=False) para un vino en la sesión."""
    rec_svc.registrar_voto((session_id or "").strip(), (wine_key or "").strip(), like)
    return {"ok": True}
