"""
Módulo QR Premium (B2B): genera contactos, QR y landing /c/<codigo>.
Endpoints: /api/qr/generar, /api/qr/descargar, /c/<codigo>.
Métricas: cada escaneo se registra (fecha, código, éxito) en qr_service.registrar_escaneo.
"""
from routes.qr_personalizado import router

__all__ = ["router"]
