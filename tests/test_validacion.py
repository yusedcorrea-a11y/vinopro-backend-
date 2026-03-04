"""Tests del servicio de validación (nombre, añada, alcohol)."""
import pytest
from services.validacion_service import (
    validar_nombre,
    validar_anio,
    validar_alcohol,
    validar_vino_completo,
)


def test_validar_nombre_vacio():
    ok, msg = validar_nombre("")
    assert ok is False
    assert "vacío" in msg or msg == "Nombre vacío."


def test_validar_nombre_corto():
    ok, msg = validar_nombre("ab")
    assert ok is False
    assert msg == "nombre_corto"


def test_validar_nombre_solo_numeros():
    ok, msg = validar_nombre("12345")
    assert ok is False
    assert msg == "nombre_solo_numeros"


def test_validar_nombre_prohibido():
    ok, msg = validar_nombre("test vino")
    assert ok is False
    assert msg == "nombre_prohibido"


def test_validar_nombre_ok():
    ok, msg = validar_nombre("Château Margaux")
    assert ok is True
    assert msg == ""


def test_validar_anio_none():
    assert validar_anio(None) == (True, "")


def test_validar_anio_valido():
    assert validar_anio(2020) == (True, "")
    assert validar_anio(1900) == (True, "")
    assert validar_anio(2026) == (True, "")


def test_validar_anio_invalido():
    ok, msg = validar_anio(1899)
    assert ok is False
    assert msg == "anio_invalido"
    ok, msg = validar_anio(2027)
    assert ok is False


def test_validar_alcohol_ok():
    assert validar_alcohol(12.5) == (True, "")
    assert validar_alcohol(5) == (True, "")
    assert validar_alcohol(25) == (True, "")
    assert validar_alcohol(None) == (True, "")


def test_validar_alcohol_invalido():
    ok, msg = validar_alcohol(4)
    assert ok is False
    assert msg == "alcohol_invalido"
    ok, msg = validar_alcohol(30)
    assert ok is False


def test_validar_vino_completo_ok():
    ok, msg = validar_vino_completo("Rioja Reserva", bodega="Bodega X", anio=2019, alcohol=13.5)
    assert ok is True
    assert msg == ""
