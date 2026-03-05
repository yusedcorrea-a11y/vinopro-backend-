"""
Modelos para el sistema de compra multiplataforma (tiendas afiliadas y subastas).
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TiendaAfiliado:
    nombre: str
    url: str
    tipo: str  # ej: "tienda_online", "marketplace"
    precio: float | None = None
    moneda: str = "EUR"
    afiliado: bool = False
    envio_internacional: bool = False
    pais_origen: str = ""
    es_amazon: bool = False
    patrocinador: bool = False  # Fase 2+: tiendas que patrocinan para aparecer en "Dónde comprarlo"

    def to_dict(self) -> dict[str, Any]:
        out = {
            "nombre": self.nombre,
            "url": self.url,
            "tipo": self.tipo,
            "precio": self.precio,
            "moneda": self.moneda,
            "afiliado": self.afiliado,
            "envio_internacional": self.envio_internacional,
            "pais_origen": self.pais_origen,
        }
        if self.es_amazon:
            out["es_amazon"] = True
        if self.patrocinador:
            out["patrocinador"] = True
        return out

    @classmethod
    def from_dict(cls, d: dict) -> "TiendaAfiliado":
        return cls(
            nombre=d.get("nombre", ""),
            url=d.get("url", ""),
            tipo=d.get("tipo", "tienda_online"),
            precio=d.get("precio"),
            moneda=d.get("moneda", "EUR"),
            afiliado=d.get("afiliado", False),
            envio_internacional=d.get("envio_internacional", False),
            pais_origen=d.get("pais_origen", ""),
            es_amazon=d.get("es_amazon", False),
            patrocinador=d.get("patrocinador", False),
        )


@dataclass
class Subasta:
    casa: str
    url: str
    fecha_fin: str  # ISO o descripción
    puja_actual: float | None = None
    estimado: str | None = None  # ej: "300-500€"
    tipo: str = "coleccion"

    def to_dict(self) -> dict[str, Any]:
        return {
            "casa": self.casa,
            "url": self.url,
            "fecha_fin": self.fecha_fin,
            "puja_actual": self.puja_actual,
            "estimado": self.estimado,
            "tipo": self.tipo,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Subasta":
        return cls(
            casa=d.get("casa", ""),
            url=d.get("url", ""),
            fecha_fin=d.get("fecha_fin", ""),
            puja_actual=d.get("puja_actual"),
            estimado=d.get("estimado"),
            tipo=d.get("tipo", "coleccion"),
        )


@dataclass
class EnlacesVino:
    vino_id: str
    nacional: dict[str, list[dict]]  # pais -> lista de tiendas (dict)
    internacional: list[dict]  # lista de tiendas con envio_internacional
    subastas: list[dict]  # lista de subastas
    ultima_actualizacion: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "vino_id": self.vino_id,
            "nacional": self.nacional,
            "internacional": self.internacional,
            "subastas": self.subastas,
            "ultima_actualizacion": self.ultima_actualizacion,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EnlacesVino":
        return cls(
            vino_id=d.get("vino_id", ""),
            nacional=d.get("nacional", {}),
            internacional=d.get("internacional", []),
            subastas=d.get("subastas", []),
            ultima_actualizacion=d.get("ultima_actualizacion", ""),
        )
