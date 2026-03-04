"""Tests del servicio de búsqueda de vinos."""
import pytest
from services.busqueda_service import buscar_vinos_avanzado, normalizar_texto, obtener_tokens_busqueda


@pytest.fixture
def vinos_mini():
    """Diccionario mínimo de vinos para pruebas."""
    return {
        "key-1": {
            "nombre": "Rioja Reserva 2018",
            "bodega": "Marqués de Riscal",
            "region": "Rioja",
            "pais": "España",
            "puntuacion": 92,
        },
        "key-2": {
            "nombre": "Ribera del Duero Crianza",
            "bodega": "Vega Sicilia",
            "region": "Ribera del Duero",
            "pais": "España",
            "puntuacion": 95,
        },
        "key-3": {
            "nombre": "Chardonnay",
            "bodega": "Bodega Sur",
            "region": "Mendoza",
            "pais": "Argentina",
            "puntuacion": 85,
        },
    }


def test_normalizar_texto():
    # La función mantiene acentos (áéíóú); minúsculas y espacios normalizados
    assert normalizar_texto("  Ríoja   Alta  ") == "ríoja alta"
    assert normalizar_texto("") == ""


def test_obtener_tokens_busqueda():
    tokens = obtener_tokens_busqueda("un vino de rioja")
    assert "rioja" in tokens
    assert "vino" in tokens


def test_buscar_vinos_avanzado_exacto(vinos_mini):
    r = buscar_vinos_avanzado(vinos_mini, "rioja reserva 2018", limite=5)
    assert len(r) >= 1
    assert r[0]["vino"]["nombre"] == "Rioja Reserva 2018"
    assert r[0]["score"] >= 1.0


def test_buscar_vinos_avanzado_parcial(vinos_mini):
    r = buscar_vinos_avanzado(vinos_mini, "ribera duero", limite=5)
    assert len(r) >= 1
    assert "Ribera" in r[0]["vino"].get("region", "") or "Ribera" in r[0]["vino"].get("nombre", "")


def test_buscar_vinos_avanzado_vacio(vinos_mini):
    r = buscar_vinos_avanzado(vinos_mini, "xyznonexistente", limite=5)
    assert r == []


def test_buscar_vinos_avanzado_limite(vinos_mini):
    r = buscar_vinos_avanzado(vinos_mini, "españa", limite=2)
    assert len(r) <= 2
