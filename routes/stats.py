"""
Stats — VINO PRO IA
Endpoints de monitorización interna (costos de IA, tokens, etc.)
"""
from fastapi import APIRouter, HTTPException, Query
from services.cost_tracker_service import obtener_resumen, resetear

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/costos")
def get_costos():
    """
    Devuelve el resumen de consumo de tokens y coste estimado en USD de las
    llamadas a Gemini desde que se arrancó el tracker (o desde el último reset).

    Ejemplo de respuesta:
    {
      "resumen": {
        "tokens_entrada_total": 12400,
        "tokens_salida_total": 3100,
        "num_llamadas": 28,
        "coste_usd_total": 0.00184,
        "presupuesto_usd": 10.0,
        "restante_usd": 9.99816,
        "porcentaje_usado": 0.02
      },
      "por_funcion": { ... },
      "modelo": "gemini-2.0-flash",
      "iniciado_en": "2026-04-03T...",
      "ultima_llamada": "2026-04-03T..."
    }
    """
    try:
        return obtener_resumen()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/costos/reset")
def reset_costos(confirmar: bool = Query(False, description="Pasar confirmar=true para resetear")):
    """
    Resetea los contadores del Cost Tracker.
    Útil al inicio de cada ciclo de facturación.
    Requiere ?confirmar=true para evitar resets accidentales.
    """
    if not confirmar:
        raise HTTPException(
            status_code=400,
            detail="Pasa ?confirmar=true para confirmar el reset de contadores."
        )
    try:
        resetear()
        return {"ok": True, "mensaje": "Contadores reseteados correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
