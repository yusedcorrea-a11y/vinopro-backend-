"""
Servicio de QRs personalizados para networking.
Genera códigos únicos, guarda contactos, registra escaneos y genera imagen QR.
"""
import json
import random
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONTACTOS_PATH = DATA_DIR / "contactos_qr.json"

_lista: list[dict[str, Any]] = []
_CODIGO_LEN = 8
_ALFABETO = string.ascii_lowercase + string.digits


def _load() -> list[dict]:
    global _lista
    if _lista:
        return _lista
    if CONTACTOS_PATH.is_file():
        try:
            with open(CONTACTOS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            _lista = data if isinstance(data, list) else []
        except Exception:
            _lista = []
    else:
        _lista = []
    return _lista


def _save() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONTACTOS_PATH, "w", encoding="utf-8") as f:
        json.dump(_lista, f, ensure_ascii=False, indent=2)


def _generar_codigo_unico() -> str:
    _load()
    for _ in range(50):
        codigo = "".join(random.choices(_ALFABETO, k=_CODIGO_LEN))
        if not any(c.get("codigo") == codigo for c in _lista):
            return codigo
    return "".join(random.choices(_ALFABETO, k=_CODIGO_LEN + 2))


def crear_contacto(nombre: str, empresa: str = "", idioma: str = "it") -> dict[str, Any]:
    """
    Crea un contacto con código único. Devuelve el contacto creado (con codigo, created_at, etc.).
    """
    nombre = (nombre or "").strip()[:200]
    empresa = (empresa or "").strip()[:200]
    idioma = (idioma or "it").strip().lower()
    if idioma not in ("it", "es", "en"):
        idioma = "it"
    _load()
    codigo = _generar_codigo_unico()
    now = datetime.now(timezone.utc).isoformat()
    contacto = {
        "codigo": codigo,
        "nombre": nombre,
        "empresa": empresa,
        "idioma": idioma,
        "created_at": now,
        "escaneado": False,
        "fecha_escaneo": "",
        "pais_escaneo": "",
        "escaneos": [],
    }
    _lista.append(contacto)
    _save()
    return contacto


def get_por_codigo(codigo: str) -> dict[str, Any] | None:
    """Devuelve el contacto por código o None."""
    _load()
    codigo = (codigo or "").strip().lower()
    for c in _lista:
        if (c.get("codigo") or "").lower() == codigo:
            return c
    return None


def _notificar_escaneo(contacto: dict) -> None:
    """Hook: log y opcional webhook/email cuando alguien escanea (configurable por env)."""
    import os
    nombre = contacto.get("nombre", "?")
    codigo = contacto.get("codigo", "?")
    pais = contacto.get("pais_escaneo", "N/A")
    msg = f"[QR] {nombre} escaneó su QR (código={codigo}, país={pais})"
    try:
        print(msg)
        log_path = DATA_DIR / "qr_escaneos.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(datetime.now(timezone.utc).isoformat() + " " + msg + "\n")
    except Exception:
        pass
    webhook = os.environ.get("QR_WEBHOOK_URL", "").strip()
    if webhook:
        try:
            import urllib.request
            req = urllib.request.Request(
                webhook,
                data=json.dumps({"text": msg, "nombre": nombre, "codigo": codigo, "pais": pais}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass


def registrar_escaneo(codigo: str, pais: str = "") -> bool:
    """
    Marca el contacto como escaneado y guarda fecha y país.
    Devuelve True si existía y se actualizó. Dispara notificación.
    """
    _load()
    codigo = (codigo or "").strip().lower()
    now = datetime.now(timezone.utc).isoformat()
    for c in _lista:
        if (c.get("codigo") or "").lower() == codigo:
            c["escaneado"] = True
            c["fecha_escaneo"] = now
            c["pais_escaneo"] = (pais or "").strip()[:10]
            eventos = c.get("escaneos")
            if not isinstance(eventos, list):
                eventos = []
            eventos.append(
                {
                    "timestamp": now,
                    "pais": (pais or "").strip()[:10],
                    "estado": "ok",
                }
            )
            c["escaneos"] = eventos[-50:]
            _save()
            _notificar_escaneo(c)
            return True
    return False


def listar_contactos() -> list[dict[str, Any]]:
    """Todos los contactos, más recientes primero."""
    _load()
    return sorted(_lista, key=lambda x: -(x.get("created_at") or "").strip())


def generar_imagen_qr(url: str, size_px: int = 280) -> bytes:
    """
    Genera imagen PNG del QR que apunta a url.
    Requiere: pip install qrcode[pil]
    """
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size_px, size_px))
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        # Fallback: devolver PNG mínimo 1x1 o aviso
        from io import BytesIO
        try:
            from PIL import Image
            img = Image.new("RGB", (size_px, size_px), color=(255, 255, 255))
            buf = BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        except Exception:
            return b""
