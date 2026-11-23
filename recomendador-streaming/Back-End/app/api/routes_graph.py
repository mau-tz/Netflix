from fastapi import APIRouter, HTTPException, Query

from app.services.catalog import get_movie, public_view
from app.services.graph_overview import build_overview

router = APIRouter(prefix="/graph", tags=["Grafo completo"])


@router.get("/overview", summary="Grafo completo del catálogo (nodos, aristas y posiciones)")
def get_overview(
    k: int = Query(3, ge=1, le=6, description="Vecinas más parecidas con las que se conecta cada película"),
):
    """
    Devuelve las ~20.000 películas como nodos (con posición x/y y grupo) y el grafo kNN de
    similitud como aristas. Se calcula una vez por valor de k y queda en memoria.
    """
    return build_overview(k)


@router.get("/node/{movie_id}", summary="Detalle de una película (para el clic en el grafo)")
def get_node(movie_id: int):
    movie = get_movie(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"No existe la película con ID {movie_id}")
    return public_view(movie)
