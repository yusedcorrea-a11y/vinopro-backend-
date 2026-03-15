"""Tests del servicio de brindis del feed VINEROS."""
import pytest
from services import brindis_service as brindis_svc


@pytest.fixture(autouse=True)
def _brindis_aislado(monkeypatch, tmp_path):
    """Aísla brindis en un archivo temporal y resetea caché."""
    monkeypatch.setattr(brindis_svc, "DATA_DIR", tmp_path)
    monkeypatch.setattr(brindis_svc, "BRINDIS_PATH", tmp_path / "brindis.json")
    monkeypatch.setattr(brindis_svc, "_data", {})


def test_get_count_vacio():
    assert brindis_svc.get_count("post-1") == 0
    assert brindis_svc.get_count("") == 0


def test_add_brindis_incrementa():
    assert brindis_svc.add_brindis("post-1", "alice") == 1
    assert brindis_svc.get_count("post-1") == 1


def test_add_brindis_sin_duplicar():
    brindis_svc.add_brindis("post-1", "alice")
    assert brindis_svc.add_brindis("post-1", "alice") == 1
    assert brindis_svc.get_count("post-1") == 1


def test_yo_brindi():
    brindis_svc.add_brindis("post-1", "alice")
    assert brindis_svc.yo_brindi("post-1", "alice") is True
    assert brindis_svc.yo_brindi("post-1", "bob") is False


def test_varios_usuarios_mismo_post():
    brindis_svc.add_brindis("post-1", "alice")
    brindis_svc.add_brindis("post-1", "bob")
    assert brindis_svc.get_count("post-1") == 2
    assert brindis_svc.yo_brindi("post-1", "alice") is True
    assert brindis_svc.yo_brindi("post-1", "bob") is True


def test_post_id_y_username_normalizados():
    brindis_svc.add_brindis("  post-1  ", "  Alice  ")
    assert brindis_svc.get_count("post-1") == 1
    assert brindis_svc.yo_brindi("post-1", "alice") is True
