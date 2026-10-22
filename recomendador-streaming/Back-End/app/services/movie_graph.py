from typing import Iterable, Optional

from app.services.catalog import get_catalog, get_movie, matches_genre
from app.services.similarity import similarity


def top_pool(size: int, genre: Optional[str] = None, include_ids: Iterable = ()) -> list:
    """
    Los 'size' mejores títulos por rating ponderado (opcionalmente de un género).
    Los 'include_ids' siempre se incluyen. El resultado queda ordenado por rating ponderado.
    """
    forced = {mid: get_movie(mid) for mid in include_ids if get_movie(mid)}
    candidates = [m for m in get_catalog() if matches_genre(m, genre) and m["id"] not in forced]
    candidates.sort(key=lambda m: m["weighted_rating"], reverse=True)
    pool = list(forced.values()) + candidates[:max(size - len(forced), 0)]
    pool.sort(key=lambda m: m["weighted_rating"], reverse=True)
    return pool


def build_knn_graph(pool: list, k: int) -> dict:
    """
    Grafo dirigido: cada película apunta a sus k vecinas más parecidas (al menos 1 género
    en común). Al ser dirigido (A puede estar en el top-k de B sin que B esté en el de A)
    tiene sentido buscar componentes fuertemente conectados.
    """
    graph = {}
    for a in pool:
        scored = [
            (similarity(a, b), b["id"]) for b in pool
            if b["id"] != a["id"] and a["genre_set"] & b["genre_set"]
        ]
        scored.sort(key=lambda t: t[0], reverse=True)
        graph[str(a["id"])] = [str(mid) for _, mid in scored[:k]]
    return graph


def build_distance_edges(pool: list, min_sim: float, directed: bool = False) -> list:
    """
    Aristas (u, v, peso) con peso = 1 - similitud, solo entre películas que comparten género.
    Si directed=True, subir a una película mejor calificada cuesta menos que bajar
    (se prefiere descubrir contenido igual o mejor); los pesos siguen siendo >= 0.
    """
    edges = []
    for i, a in enumerate(pool):
        for b in pool[i + 1:]:
            if not (a["genre_set"] & b["genre_set"]):
                continue
            sim = similarity(a, b)
            if sim < min_sim:
                continue
            base = 1 - sim
            if directed:
                gap = (b["rating"] - a["rating"]) / 10
                edges.append((str(a["id"]), str(b["id"]), round(base - 0.1 * max(gap, 0) + 0.1 * max(-gap, 0), 6)))
                edges.append((str(b["id"]), str(a["id"]), round(base - 0.1 * max(-gap, 0) + 0.1 * max(gap, 0), 6)))
            else:
                edges.append((str(a["id"]), str(b["id"]), round(base, 6)))
    return edges
