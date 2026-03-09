"""
Endpoints de maridaje (Spoonacular): vino → platos, plato → vinos, descripción de vino.
"""
from fastapi import APIRouter, Query

from services import pairing_service as pairing_svc

router = APIRouter(prefix="/pairing", tags=["Maridaje"])


@router.get("/dishes")
def pairing_dishes_for_wine(wine: str = Query(..., description="Nombre del vino (ej. merlot, malbec, riesling)")):
    """
    Maridaje vino → platos. Devuelve alimentos que combinan bien con el vino indicado.
    """
    return pairing_svc.get_dish_pairing_for_wine(wine)


@router.get("/wines")
def pairing_wines_for_food(food: str = Query(..., description="Plato, ingrediente o cocina (ej. steak, salmon, italian)")):
    """
    Maridaje plato → vinos. Devuelve vinos recomendados para el plato/ingrediente indicado.
    """
    return pairing_svc.get_wine_pairing_for_food(food)


@router.get("/wine-description")
def wine_description(wine: str = Query(..., description="Nombre del vino (ej. merlot, chardonnay)")):
    """
    Descripción breve del tipo de vino. Útil para fichas o tooltips.
    """
    return pairing_svc.get_wine_description(wine)
