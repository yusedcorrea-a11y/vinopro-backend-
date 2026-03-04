"""
Modelo para contactos de QR personalizados (networking Turín).
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContactoQR:
    """Un contacto con QR único para la página personalizada."""
    codigo: str          # código único corto (ej. a1b2c3)
    nombre: str          # nombre de la persona
    empresa: str = ""    # empresa/vinoteca opcional
    idioma: str = "it"   # it | es | en (idioma del mensaje al crear)
    created_at: str = "" # ISO date
    escaneado: bool = False
    fecha_escaneo: str = ""
    pais_escaneo: str = ""  # país desde donde escaneó (CF-IPCountry o N/A)

    def to_dict(self) -> dict[str, Any]:
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "empresa": self.empresa,
            "idioma": self.idioma,
            "created_at": self.created_at,
            "escaneado": self.escaneado,
            "fecha_escaneo": self.fecha_escaneo,
            "pais_escaneo": self.pais_escaneo,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ContactoQR":
        return cls(
            codigo=d.get("codigo", ""),
            nombre=d.get("nombre", ""),
            empresa=d.get("empresa", ""),
            idioma=d.get("idioma", "it"),
            created_at=d.get("created_at", ""),
            escaneado=d.get("escaneado", False),
            fecha_escaneo=d.get("fecha_escaneo", ""),
            pais_escaneo=d.get("pais_escaneo", ""),
        )
