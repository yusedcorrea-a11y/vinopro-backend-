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

# Banderas por idioma para títulos (ej: 🇪🇸 Inicio)
BANDERAS = {
    "es": "🇪🇸", "en": "🇬🇧", "pt": "🇵🇹", "fr": "🇫🇷", "de": "🇩🇪", "it": "🇮🇹",
    "ar": "🇦🇪", "ru": "🇷🇺", "tr": "🇹🇷", "zh": "🇨🇳", "ja": "🇯🇵", "ko": "🇰🇷", "hi": "🇮🇳", "he": "🇮🇱",
}


def get_locale(request: Request) -> str:
    lang = (request.cookies.get(COOKIE_NAME) or IDIOMA_POR_DEFECTO).strip().lower()
    return lang if lang in IDIOMAS_SOPORTADOS else IDIOMA_POR_DEFECTO


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


def make_t(translations: dict) -> Callable[[str], str]:
    def t(key: str) -> str:
        obj = translations
        for part in key.split("."):
            obj = obj.get(part, {}) if isinstance(obj, dict) else key
        return obj if isinstance(obj, str) else key
    return t


def recognition_lang_for(lang: str) -> str:
    """Código de idioma para reconocimiento de voz (Web Speech API)."""
    m = {
        "es": "es-ES", "en": "en-US", "pt": "pt-PT", "fr": "fr-FR", "de": "de-DE", "it": "it-IT",
        "ar": "ar-SA", "ru": "ru-RU", "tr": "tr-TR", "zh": "zh-CN", "ja": "ja-JP", "ko": "ko-KR", "hi": "hi-IN", "he": "he-IL",
    }
    return m.get(lang, "es-ES")
