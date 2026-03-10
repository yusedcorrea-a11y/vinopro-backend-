"""
i18n: idioma desde cookie, traducciones (14 idiomas: es, en, pt, fr, de, it, ar, ru, tr, zh, ja, ko, hi, he).
"""
import json
from pathlib import Path
from typing import Callable

from fastapi import Request

DATA_FOLDER = Path(__file__).resolve().parent.parent / "data"
TRANSLATIONS_DIR = DATA_FOLDER / "translations"
_CACHE: dict = {}

COOKIE_NAME = "vino_pro_lang"
COOKIE_MAX_AGE = 31536000  # 1 año

IDIOMAS_SOPORTADOS = ("es", "en", "pt", "fr", "de", "it", "ar", "ru", "tr", "zh", "ja", "ko", "hi", "he")
IDIOMA_POR_DEFECTO = "es"
# Fallback global cuando no hay cookie ni coincidencia en Accept-Language
IDIOMA_FALLBACK_GLOBAL = "en"

# Banderas por idioma para títulos (ej: 🇪🇸 Inicio)
BANDERAS = {
    "es": "🇪🇸", "en": "🇬🇧", "pt": "🇵🇹", "fr": "🇫🇷", "de": "🇩🇪", "it": "🇮🇹",
    "ar": "🇦🇪", "ru": "🇷🇺", "tr": "🇹🇷", "zh": "🇨🇳", "ja": "🇯🇵", "ko": "🇰🇷", "hi": "🇮🇳", "he": "🇮🇱",
}


def parse_accept_language(header: str) -> str:
    """Devuelve el primer código de idioma de Accept-Language que esté en IDIOMAS_SOPORTADOS, o ''."""
    if not header or not header.strip():
        return ""
    for part in header.split(","):
        part = part.strip().split(";")[0].strip().lower()
        if not part:
            continue
        if "-" in part:
            part = part.split("-")[0]
        if part in IDIOMAS_SOPORTADOS:
            return part
    return ""


def get_locale(request: Request) -> str:
    # Prioridad 1: cookie
    cookie_val = (request.cookies.get(COOKIE_NAME) or "").strip().lower()
    if cookie_val and cookie_val in IDIOMAS_SOPORTADOS:
        return cookie_val
    # Prioridad 2: Accept-Language del navegador
    lang = parse_accept_language(request.headers.get("Accept-Language", "") or "")
    if lang:
        return lang
    # Prioridad 3: inglés para mercado global
    return IDIOMA_FALLBACK_GLOBAL


def load_translations(lang: str) -> dict:
    if lang not in _CACHE:
        path = TRANSLATIONS_DIR / f"{lang}.json"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    _CACHE[lang] = json.load(f)
            except Exception:
                _CACHE[lang] = {}
        else:
            _CACHE[lang] = {}
    return _CACHE[lang]


def make_t(translations: dict, fallback_translations: dict | None = None) -> Callable[[str], str]:
    def t(key: str) -> str:
        def _resolve(src: dict | None) -> str | None:
            obj = src if isinstance(src, dict) else {}
            for part in key.split("."):
                obj = obj.get(part, {}) if isinstance(obj, dict) else None
            return obj if isinstance(obj, str) else None

        value = _resolve(translations)
        if value is not None:
            return value
        fallback = _resolve(fallback_translations)
        if fallback is not None:
            return fallback
        return key
    return t


def recognition_lang_for(lang: str) -> str:
    """Código de idioma para reconocimiento de voz (Web Speech API)."""
    m = {
        "es": "es-ES", "en": "en-US", "pt": "pt-PT", "fr": "fr-FR", "de": "de-DE", "it": "it-IT",
        "ar": "ar-SA", "ru": "ru-RU", "tr": "tr-TR", "zh": "zh-CN", "ja": "ja-JP", "ko": "ko-KR", "hi": "hi-IN", "he": "he-IL",
    }
    return m.get(lang, "es-ES")
