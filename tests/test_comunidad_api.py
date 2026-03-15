"""Tests de las APIs de comunidad: eventos (calendario) y brindis."""
import pytest

from routes.comunidad import get_eventos_calendario


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
