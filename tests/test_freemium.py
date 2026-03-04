"""Tests del servicio freemium (is_pro, puede_anadir_botella, count_botellas)."""
import json
import os
import tempfile
import pytest


@pytest.fixture
def temp_data_dir():
    """Directorio temporal con usuarios_pro.json y bodegas.json para no tocar data real."""
    with tempfile.TemporaryDirectory() as d:
        pro_path = os.path.join(d, "usuarios_pro.json")
        bodegas_path = os.path.join(d, "bodegas.json")
        with open(pro_path, "w", encoding="utf-8") as f:
            json.dump({"pro_users": ["session-pro-123"]}, f, indent=2)
        with open(bodegas_path, "w", encoding="utf-8") as f:
            json.dump({
                "session-free-1": {"botellas": [{"cantidad": 10}, {"cantidad": 5}], "updated_at": "2025-01-01T00:00:00"},
            }, f, indent=2)
        old_data = os.environ.get("DATA_FOLDER")
        os.environ["DATA_FOLDER"] = d
        try:
            # Reimport para que el servicio use el nuevo DATA_FOLDER
            import importlib
            import services.freemium_service as freemium_svc
            importlib.reload(freemium_svc)
            yield freemium_svc
        finally:
            if old_data is not None:
                os.environ["DATA_FOLDER"] = old_data
            else:
                os.environ.pop("DATA_FOLDER", None)
            import importlib
            import services.freemium_service as _fs
            importlib.reload(_fs)


def test_is_pro_true(temp_data_dir):
    freemium_svc = temp_data_dir
    assert freemium_svc.is_pro("session-pro-123") is True


def test_is_pro_false(temp_data_dir):
    freemium_svc = temp_data_dir
    assert freemium_svc.is_pro("session-unknown") is False


def test_is_pro_empty(temp_data_dir):
    freemium_svc = temp_data_dir
    assert freemium_svc.is_pro("") is False
    assert freemium_svc.is_pro(None) is False


def test_count_botellas(temp_data_dir):
    freemium_svc = temp_data_dir
    # session-free-1 tiene 10 + 5 = 15
    assert freemium_svc.count_botellas("session-free-1") == 15
    assert freemium_svc.count_botellas("session-inexistente") == 0


def test_puede_anadir_botella_pro(temp_data_dir):
    freemium_svc = temp_data_dir
    puede, msg = freemium_svc.puede_anadir_botella("session-pro-123", 100)
    assert puede is True
    assert msg == ""


def test_puede_anadir_botella_sin_sesion(temp_data_dir):
    freemium_svc = temp_data_dir
    puede, msg = freemium_svc.puede_anadir_botella("", 1)
    assert puede is False
    assert "Sesión" in msg or "sesión" in msg
