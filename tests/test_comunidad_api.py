"""Tests de las APIs de comunidad: eventos (calendario), brindis y canales."""
import pytest

from routes.comunidad import get_eventos_calendario
from services import feed_service as feed_svc


def test_canal_en_vivo_tiene_contenido():
    """El canal en_vivo (Wine News TV, Colectivo Decantado) devuelve entradas con link y badge."""
    items = feed_svc.get_contenido_canal("en_vivo", limit=10)
    assert isinstance(items, list)
    assert len(items) >= 2
    for item in items:
        assert "link" in item
        assert "titulo" in item
        assert item.get("badge") == "En vivo"
        assert "youtube.com" in (item.get("link") or "")


def test_add_actividad_foto_vino_requiere_image_path():
    """foto_vino sin image_path no crea actividad."""
    assert feed_svc.add_actividad("user", "foto_vino", image_path="", texto="caption") == ""
    assert feed_svc.add_actividad("user", "foto_vino", texto="cap") == ""


def test_api_eventos_sin_params():
    """GET /api/eventos sin year/month devuelve mes actual y lista eventos."""
    data = get_eventos_calendario()
    assert "year" in data
    assert "month" in data
    assert "eventos" in data
    assert isinstance(data["eventos"], list)
    assert 1 <= data["month"] <= 12


def test_api_eventos_con_mes():
    """GET /api/eventos?year=2025&month=3 devuelve marzo 2025."""
    data = get_eventos_calendario(year=2025, month=3)
    assert data["year"] == 2025
    assert data["month"] == 3
    assert "eventos" in data
    assert isinstance(data["eventos"], list)
