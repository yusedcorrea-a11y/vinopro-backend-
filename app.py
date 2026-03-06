import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Producción: HOST=0.0.0.0 PORT=8000 (o el que uses). CORS_ORIGINS=https://tudominio.com
# 0.0.0.0 = aceptar conexiones desde la red local (móvil por WiFi). 127.0.0.1 = solo este PC.
_HOST = os.environ.get("HOST", "0.0.0.0").strip()
_PORT = int(os.environ.get("PORT", "8001").strip())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print(f"VINO PRO IA - Backend listo, aceptando conexiones en http://{_HOST}:{_PORT}")
    yield
    # shutdown (opcional: cerrar conexiones, etc.)


# Inicializar app
app = FastAPI(title="VINO PRO IA", description="API de análisis de vinos", lifespan=lifespan)


# CORS: por defecto solo mismo origen; en producción definir CORS_ORIGINS (ej. https://tudominio.com)
_cors_origins = os.environ.get("CORS_ORIGINS", "").strip()
if _cors_origins and _cors_origins != "*":
    _origins_list = [o.strip() for o in _cors_origins.split(",") if o.strip()]
else:
    _origins_list = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carpeta donde están los archivos JSON (ruta absoluta: no depende del directorio desde el que se ejecuta)
BASE_DIR = Path(__file__).resolve().parent
DATA_FOLDER = str(BASE_DIR / "data")


def cargar_todos_los_vinos():
    """Carga vinos de todos los archivos JSON en la carpeta data"""
    vinos = {}
    
    if not os.path.exists(DATA_FOLDER):
        print(f"[WARN] Carpeta {DATA_FOLDER} no encontrada")
        return vinos
    
    # Cargar solo archivos de catálogo de vinos (excluir config, analytics, usuarios, etc.).
    # Incluye data/vinos_generados_ia.json si existe (generado con scripts/generar_vinos_ia.py).
    excluir = {
        'analytics.json', 'bodegas.json', 'conocimiento_vinos.json',
        'enlaces_compra.json', 'restaurantes.json', 'registros_diarios.json',
        'usuarios_reputacion.json', 'usuarios_pro.json', 'ofertas.json',
        'valoraciones.json', 'wishlist.json', 'historial_usuario.json',
        'notificaciones_landing.json',
        'usuarios_perfiles.json', 'seguidores.json', 'actividad.json', 'notificaciones.json',
        'contactos_qr.json', 'lugares_destacados.json', 'chat_mensajes.json',
        'patrocinadores.json',  # no es catálogo de vinos
    }
    archivos = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.json') and f not in excluir]
    
    for archivo in archivos:
        ruta = os.path.join(DATA_FOLDER, archivo)
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
                vinos.update(data)
                print(f"[OK] Cargado {archivo}: {len(data)} vinos")
        except Exception as e:
            print(f"[ERROR] Cargando {archivo}: {e}")
    
    return vinos

# Cargar vinos al iniciar (encoding UTF-8 ya usado en open() para ñ y acentos)
VINOS_MUNDIALES = cargar_todos_los_vinos()
print(f"[INFO] Base de datos lista: {len(VINOS_MUNDIALES)} vinos cargados desde {DATA_FOLDER}")

# Estado para rutas de escaneo, sumiller, bodega y analytics
from routes import escaneo, sumiller, geolocalizacion, bodega, analytics, informes, adaptador, comprar, planes, pagos, ofertas, valoraciones_wishlist, comunidad, qr_personalizado
from services.busqueda_service import buscar_vinos_avanzado

app.state.vinos_mundiales = VINOS_MUNDIALES
app.state.consultas_escaneo = {}
app.state.historial_escaneos = {}  # session_id -> [ { consulta_id, vino_nombre, encontrado_en_bd }, ... ]

# Frontend: estáticos y plantillas (y rutas HTML ANTES de la API para evitar conflicto)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.state.templates = templates

# i18n: idioma desde cookie, traducciones ES/EN
from services import i18n as i18n_svc

def render_page(request: Request, template_name: str, **context):
    lang = i18n_svc.get_locale(request)
    trans = i18n_svc.load_translations(lang)
    t = i18n_svc.make_t(trans)
    recognition_lang = i18n_svc.recognition_lang_for(lang)
    # En producción definir BASE_URL (ej. https://vinoproia.com) para canonical y compartir
    base_url_str = os.environ.get("BASE_URL", "").strip() or str(request.base_url).rstrip("/")
    bandera = i18n_svc.BANDERAS.get(lang, "🇪🇸")
    return templates.TemplateResponse(
        template_name,
        {"request": request, "t": t, "lang": lang, "recognition_lang": recognition_lang, "base_url_str": base_url_str, "bandera": bandera, **context},
    )


@app.get("/set-lang", response_class=RedirectResponse)
def set_lang(request: Request, lang: str = "es"):
    """Establece cookie de idioma (1 año) y redirige a la página anterior (o a /inicio si venían de /)."""
    from urllib.parse import urlparse
    from services.i18n import IDIOMAS_SOPORTADOS, IDIOMA_POR_DEFECTO
    lang = lang.strip().lower() if lang else IDIOMA_POR_DEFECTO
    if lang not in IDIOMAS_SOPORTADOS:
        lang = IDIOMA_POR_DEFECTO
    referer = request.headers.get("referer") or ""
    path = (urlparse(referer).path or "").rstrip("/") or "/"
    # Si el usuario venía de la raíz (landing), llevar a la Home para que vea viñedo y botones
    if path == "/":
        url = "/inicio"
    else:
        url = referer if referer.startswith("http") else path or "/inicio"
    response = RedirectResponse(url=url)
    response.set_cookie("vino_pro_lang", lang, max_age=31536000, path="/")
    return response


@app.get("/health")
def health():
    """Health check para load balancers y monitoreo (siempre 200 si el proceso está vivo)."""
    return {"status": "ok"}


@app.get("/ready")
def ready():
    """Ready check: servicio listo para recibir tráfico (incluye comprobación mínima de datos)."""
    return {"ready": True, "vinos_cargados": len(VINOS_MUNDIALES)}


@app.get("/", response_class=HTMLResponse)
def pagina_landing(request: Request):
    """Landing (primera visita sin cookie) o redirige a Home si ya tiene idioma."""
    if request.cookies.get("vino_pro_lang"):
        return RedirectResponse(url="/inicio", status_code=302)
    return render_page(request, "landing.html", page_class="page-landing", active_page="")


@app.get("/inicio", response_class=HTMLResponse)
def pagina_inicio(request: Request):
    """Entrada a la app: Preguntar al sumiller y Escanear."""
    return render_page(request, "index.html", page_class="page-inicio", active_page="inicio")


@app.get("/escanear", response_class=HTMLResponse)
def pagina_escanear(request: Request):
    return render_page(request, "escanear.html", page_class="page-escanear", active_page="escanear")


@app.get("/registrar", response_class=HTMLResponse)
def pagina_registrar(request: Request):
    return render_page(request, "registrar.html", page_class="page-registrar", active_page="registrar")


@app.get("/preguntar", response_class=HTMLResponse)
def pagina_preguntar(request: Request):
    return render_page(request, "preguntar.html", page_class="page-preguntar", active_page="preguntar")


@app.get("/bodega", response_class=HTMLResponse)
def pagina_bodega(request: Request):
    return render_page(request, "bodega.html", page_class="page-bodega", active_page="bodega")


@app.get("/dashboard", response_class=HTMLResponse)
def pagina_dashboard(request: Request):
    return render_page(request, "dashboard.html", page_class="page-dashboard", active_page="dashboard")


@app.get("/adaptador", response_class=HTMLResponse)
def pagina_adaptador(request: Request):
    return render_page(request, "adaptador.html", page_class="page-adaptador", active_page="adaptador")


@app.get("/mapa", response_class=HTMLResponse)
def pagina_mapa(request: Request):
    return render_page(request, "mapa.html", page_class="page-mapa", active_page="mapa")


@app.get("/oferta/crear", response_class=HTMLResponse)
def pagina_oferta_crear(request: Request, key: str = ""):
    """Página para que un Premium cree una oferta (foto + email) para un vino recién registrado."""
    return render_page(request, "oferta_crear.html", page_class="page-oferta-crear", active_page="registrar", vino_key=(key or "").strip())


@app.get("/mis-ofertas", response_class=HTMLResponse)
def pagina_mis_ofertas(request: Request):
    """Página donde el usuario ve sus ofertas y las solicitudes de contacto (marcar como respondido)."""
    return render_page(request, "mis_ofertas.html", page_class="page-mis-ofertas", active_page="bodega")


@app.get("/privacidad", response_class=HTMLResponse)
def pagina_privacidad(request: Request):
    """Página de política de privacidad (requerida para Google Play y buenas prácticas)."""
    return render_page(request, "privacidad.html", page_class="page-privacidad", active_page="")


@app.get("/comunidad/feed", response_class=HTMLResponse)
def pagina_feed(request: Request):
    """Feed de actividad de la comunidad."""
    return render_page(request, "feed.html", page_class="page-feed", active_page="comunidad")


@app.get("/comunidad/perfil/{username:path}", response_class=HTMLResponse)
def pagina_perfil(request: Request, username: str):
    """Perfil público de un usuario."""
    return render_page(request, "perfil.html", page_class="page-perfil", active_page="comunidad", perfil_username=username)


@app.post("/api/landing-notify")
async def landing_notify(request: Request):
    """Registra email para avisar cuando la app esté en Google Play. Guarda en data/notificaciones_landing.json."""
    from fastapi.responses import JSONResponse
    try:
        body = await request.json()
        email = (body.get("email") or "").strip().lower()
        if not email or "@" not in email:
            return JSONResponse(status_code=400, content={"ok": False, "error": "Email no válido"})
        path = Path(DATA_FOLDER) / "notificaciones_landing.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"emails": [], "updated": ""}
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        if email not in data["emails"]:
            data["emails"].append(email)
        data["updated"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"ok": True, "message": "Te avisaremos cuando esté en Google Play"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


# API: routers (bodega bajo /api para no chocar con GET /bodega que sirve HTML)
app.include_router(escaneo.router)
app.include_router(sumiller.router)
app.include_router(geolocalizacion.router)
app.include_router(bodega.router, prefix="/api")
app.include_router(analytics.router)
app.include_router(informes.router)
app.include_router(adaptador.router, prefix="/api")
app.include_router(comprar.router)
app.include_router(planes.router)
app.include_router(pagos.router)
app.include_router(ofertas.router)
app.include_router(valoraciones_wishlist.router)
app.include_router(comunidad.router)
app.include_router(qr_personalizado.router)

@app.get("/api/status")
def api_status():
    """Estado del API (para clientes programáticos)"""
    return {
        "status": "ok",
        "service": "VINO PRO IA",
        "version": "5.0",
        "vinos_en_db": len(VINOS_MUNDIALES)
    }


@app.get("/api/vino-por-consulta")
def api_vino_por_consulta(request: Request, consulta_id: str):
    """Devuelve el vino asociado a un consulta_id (para el agente local)."""
    consultas = getattr(request.app.state, "consultas_escaneo", {})
    raw = consultas.get(consulta_id.strip()) if consulta_id else None
    if raw is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Consulta no encontrada. Escanee el vino antes.")
    # Compatible con formato nuevo { "vino", "key" } y antiguo (vino directo)
    vino = raw.get("vino") if isinstance(raw, dict) and "vino" in raw else raw
    return {"consulta_id": consulta_id, "vino": vino}


@app.post("/api/preguntar-local")
async def api_preguntar_local(request: Request):
    """
    Pregunta al sumiller vía agente local (puerto 8080). Solo usuarios Premium.
    Header X-Session-ID obligatorio. Body: { "consulta_id", "pregunta", "perfil" opcional }.
    Si el agente no responde, fallback a lógica rule-based.
    """
    import httpx
    from fastapi import HTTPException
    from routes.sumiller import _responder_pregunta
    from services import freemium_service as freemium_svc

    session_id = (request.headers.get("X-Session-ID") or "").strip()
    if not session_id:
        raise HTTPException(status_code=401, detail="X-Session-ID requerido para usar IA Local.")
    if not freemium_svc.is_pro(session_id):
        raise HTTPException(
            status_code=403,
            detail="IA Local es exclusiva para usuarios Premium. Pasa a PRO en Planes para usar el agente en tu PC."
        )

    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    consulta_id = (body.get("consulta_id") or "").strip()
    pregunta = (body.get("pregunta") or "").strip()
    perfil = (body.get("perfil") or "aficionado").strip() or "aficionado"

    if not consulta_id or not pregunta:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="consulta_id y pregunta son obligatorios.")

    consultas = getattr(request.app.state, "consultas_escaneo", {})
    raw = consultas.get(consulta_id)
    if raw is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Vino no encontrado para ese consulta_id. Escanee de nuevo.")
    if isinstance(raw, dict) and "vino" in raw:
        vino, key_para_comprar = raw["vino"], raw.get("key")
    else:
        vino, key_para_comprar = raw, raw.get("key") if isinstance(raw, dict) else None

    agent_url = "http://127.0.0.1:8080/skill/sumiller"
    payload = {"consulta_id": consulta_id, "pregunta": pregunta, "perfil": perfil}

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.post(agent_url, json=payload)
            if r.status_code == 200:
                try:
                    data = r.json()
                except Exception:
                    data = None
                if data and isinstance(data, dict):
                    respuesta = data.get("respuesta") or data.get("respuesta_sumiller")
                    vino_devuelto = data.get("vino") or vino
                    try:
                        from services import analytics_service
                        analytics_service.registrar_pregunta(pregunta, vino.get("nombre"))
                    except Exception:
                        pass
                    from services.imagen_service import get_imagen_vino
                    vino_para_imagen = vino_devuelto if isinstance(vino_devuelto, dict) else vino
                    tipo = (vino_para_imagen.get("tipo") or "tinto").strip().lower()
                    if tipo not in ("tinto", "blanco", "rosado", "espumoso"):
                        tipo = "tinto"
                    imagen_url = get_imagen_vino(key_para_comprar or "", tipo)
                    return {
                        "consulta_id": consulta_id,
                        "pregunta": pregunta,
                        "respuesta": respuesta,
                        "vino_nombre": vino_devuelto.get("nombre") if isinstance(vino_devuelto, dict) else vino.get("nombre"),
                        "vino": vino_devuelto,
                        "vino_key": key_para_comprar,
                        "imagen_url": imagen_url,
                        "mostrar_boton_comprar": bool(key_para_comprar),
                        "perfil": perfil,
                        "modo": "local",
                    }
    except (httpx.ConnectError, httpx.TimeoutException, Exception):
        pass

    # Fallback: rule-based como /preguntar-sumiller
    respuesta = _responder_pregunta(vino, pregunta, perfil=perfil)
    try:
        from services import analytics_service
        analytics_service.registrar_pregunta(pregunta, vino.get("nombre"))
    except Exception:
        pass
    from services.imagen_service import get_imagen_vino
    tipo = (vino.get("tipo") or "tinto").strip().lower()
    if tipo not in ("tinto", "blanco", "rosado", "espumoso"):
        tipo = "tinto"
    imagen_url = get_imagen_vino(key_para_comprar or "", tipo)
    return {
        "consulta_id": consulta_id,
        "pregunta": pregunta,
        "respuesta": respuesta,
        "vino_nombre": vino.get("nombre"),
        "vino": vino,
        "vino_key": key_para_comprar,
        "imagen_url": imagen_url,
        "mostrar_boton_comprar": bool(key_para_comprar),
        "perfil": perfil,
        "modo": "nube",
    }

@app.post("/analyze/text")
def analyze_wine(texto: str = Form(...)):
    """
    Analiza un vino por texto
    - Busca en el diccionario por nombre o palabras clave
    - Si no encuentra, devuelve análisis genérico
    """
    texto_lower = texto.lower().strip()

    # Búsqueda avanzada unificada (services.busqueda_service)
    coincidencias = buscar_vinos_avanzado(VINOS_MUNDIALES, texto_lower, limite=5)
    if coincidencias and coincidencias[0]["score"] >= 1.0:
        mejor = coincidencias[0]
        vino_encontrado = mejor["vino"]
        print(f"✓ Coincidencia avanzada: {vino_encontrado['nombre']} (score={mejor['score']:.2f})")
        return {
            "success": True,
            "analysis": vino_encontrado,
            "matches": [
                {
                    "key": c["key"],
                    "nombre": c["vino"]["nombre"],
                    "bodega": c["vino"]["bodega"],
                    "region": c["vino"]["region"],
                    "pais": c["vino"]["pais"],
                    "puntuacion": c["vino"]["puntuacion"],
                    "score": round(c["score"], 3),
                }
                for c in coincidencias
            ]
        }
    
    # Si no se encuentra, análisis genérico
    print(f"✗ Vino no encontrado: '{texto}'")
    
    # Detectar tipo por palabras clave
    tipo = "tinto"
    palabras_tinto = ["tinto", "rojo", "crianza", "reserva"]
    palabras_blanco = ["blanco", "blanco", "albariño", "verdejo", "blanc"]
    
    for p in palabras_blanco:
        if p in texto_lower:
            tipo = "blanco"
            break
    
    return {
        "success": True,
        "analysis": {
            "nombre": texto,
            "bodega": "No especificada",
            "region": "Por determinar",
            "pais": "Desconocido",
            "tipo": tipo,
            "puntuacion": 85,
            "precio_estimado": "15-30€",
            "descripcion": f"Análisis genérico de {texto}. Para un análisis más preciso, prueba con un vino de nuestra base de datos.",
            "notas_cata": "Notas no disponibles",
            "maridaje": "Información no disponible"
        }
    }

@app.get("/vinos")
def listar_vinos():
    """Lista todos los vinos disponibles (solo entradas que son dict de ficha de vino)."""
    vinos_validos = [(k, v) for k, v in VINOS_MUNDIALES.items() if isinstance(v, dict)]
    return {
        "total": len(vinos_validos),
        "vinos": [
            {
                "key": key,
                "nombre": vino.get("nombre", ""),
                "bodega": vino.get("bodega", ""),
                "region": vino.get("region", ""),
                "pais": vino.get("pais", ""),
                "puntuacion": vino.get("puntuacion", 0),
            }
            for key, vino in vinos_validos
        ]
    }

@app.get("/api/buscar-para-registrar")
def buscar_para_registrar(q: str):
    """
    Busca vinos para el flujo 'Registrar': primero en nuestra BD, luego en Open Food Facts.
    Devuelve en_bd (ya en nuestra base) y externos (para que el usuario elija y registre).
    """
    q = (q or "").strip()
    if len(q) < 2:
        return {"query": q, "en_bd": [], "externos": []}
    from services.api_externa_service import buscar_por_texto as off_buscar
    coincidencias = buscar_vinos_avanzado(VINOS_MUNDIALES, q, limite=10)
    en_bd = [
        {"key": c["key"], "vino": c["vino"]}
        for c in coincidencias
    ]
    externos = []
    try:
        lista_off = off_buscar(q, limite=5)
        for v in lista_off or []:
            if isinstance(v, dict) and v.get("nombre"):
                externos.append({"vino": v})
    except Exception:
        pass
    return {"query": q, "en_bd": en_bd, "externos": externos}


@app.get("/buscar")
def buscar_vino(q: str):
    """Busca vinos por nombre, bodega o región (búsqueda unificada en busqueda_service)."""
    coincidencias = buscar_vinos_avanzado(VINOS_MUNDIALES, q, limite=20)
    resultados = [
        {
            "key": c["key"],
            "nombre": c["vino"]["nombre"],
            "bodega": c["vino"]["bodega"],
            "region": c["vino"]["region"],
            "pais": c["vino"]["pais"],
            "puntuacion": c["vino"]["puntuacion"],
            "score": round(c["score"], 3),
        }
        for c in coincidencias
    ]
    try:
        from services import analytics_service
        pais = resultados[0]["pais"] if resultados else None
        analytics_service.registrar_busqueda(q, pais=pais, encontrados=len(resultados))
    except Exception:
        pass
    return {
        "query": q,
        "resultados": len(resultados),
        "vinos": resultados
    }

@app.get("/paises")
def listar_paises():
    """Lista los países disponibles en la base de datos"""
    paises = set(vino.get("pais") for vino in VINOS_MUNDIALES.values() if vino.get("pais"))
    return {
        "total_paises": len(paises),
        "paises": sorted(list(paises))
    }


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml(request: Request):
    """Sitemap para buscadores. BASE_URL en .env para producción (ej. https://tudominio.com)."""
    base = os.environ.get("BASE_URL", "").strip() or str(request.base_url).rstrip("/")
    pages = ["/", "/inicio", "/escanear", "/registrar", "/preguntar", "/bodega", "/dashboard", "/planes", "/adaptador", "/privacidad"]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path in pages:
        xml += f"  <url><loc>{base}{path}</loc><changefreq>weekly</changefreq></url>\n"
    xml += "</urlset>"
    return Response(content=xml, media_type="application/xml")


if __name__ == "__main__":
    import uvicorn
    debug = os.environ.get("DEBUG", "").strip().lower() in ("1", "true", "yes")
    print(f"Iniciando backend VinoPro en http://{_HOST}:{_PORT} (debug={debug}) ...")
    uvicorn.run(app, host=_HOST, port=_PORT, reload=debug)
