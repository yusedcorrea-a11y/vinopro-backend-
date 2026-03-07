"""
Big Data vinícola: dashboard de tendencias, búsquedas por país, preguntas frecuentes.
"""
from fastapi import APIRouter

from services import analytics_service as svc

router = APIRouter(prefix="", tags=["Analytics"])


@router.get("/analytics/dashboard")
def dashboard_api(dias: int = 30):
    """API: resumen para el dashboard (tendencias, por país, preguntas frecuentes)."""
    return svc.resumen_dashboard(dias=dias)


@router.get("/analytics/tendencias")
def tendencias(limite: int = 20, dias: int = 30):
    """Vinos/búsquedas más populares."""
    return {"tendencias": svc.tendencias_busquedas(limite=limite, dias=dias)}


@router.get("/analytics/por-pais")
def por_pais(dias: int = 30):
    """Estadísticas de búsquedas/escaneos por país."""
    return {"estadisticas": svc.estadisticas_por_pais(dias=dias)}


@router.get("/analytics/preguntas-frecuentes")
def preguntas_frecuentes(limite: int = 15, dias: int = 30):
    """Preguntas más repetidas al experto en vinos."""
    return {"preguntas": svc.preguntas_frecuentes(limite=limite, dias=dias)}
