from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.algorithms.backtracking import PreferenceBacktracking
from app.algorithms.brute_force import BruteForceRecommender
from app.algorithms.divide_conquer import DivideAndConquer
from app.algorithms.dynamic_prog import DynamicProgrammingRecommender
from app.algorithms.graphs import GraphAlgorithms
from app.algorithms.greedy import GreedyRecommender
from app.algorithms.max_flow import MaxFlowAllocator
from app.algorithms.mst_clustering import MSTClustering
from app.algorithms.shortest_paths import ShortestPaths
from app.services.catalog import get_catalog, get_movie, matches_genre, public_view
from app.services.movie_graph import build_distance_edges, build_knn_graph, top_pool
from app.services.similarity import similarity

router = APIRouter(prefix="/recommend", tags=["Recomendaciones"])

# Los algoritmos guardan operation_count en la instancia, por eso se crea una por petición.


def _require_movie(movie_id: int) -> dict:
    movie = get_movie(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"No existe la película con ID {movie_id}")
    return movie


def _runtime_info(movies: list) -> dict:
    estimated = sum(1 for m in movies if m["runtime_estimated"])
    return {
        "runtime_estimated_count": estimated,
        "runtime_note": (
            f"{estimated} de {len(movies)} películas usan una duración estimada de 120 min "
            "porque el dataset aún no incluye la duración real." if estimated else
            "Todas las duraciones provienen del dataset."
        ),
    }


def _dominant_genres(movies: list, top: int = 3) -> list:
    counts = {}
    for m in movies:
        for g in m["genres"]:
            counts[g] = counts.get(g, 0) + 1
    return [g for g, _ in sorted(counts.items(), key=lambda t: (-t[1], t[0]))[:top]]


# ---------------------------------------------------------------- Voraz
@router.get("/top-k", summary="Recomendaciones rápidas Top-K")
def get_top_k(
    k: int = Query(10, ge=1, le=50, description="Cantidad de películas a retornar"),
    genre: Optional[str] = Query(None, description="Género opcional (ej. 'Acción', 'Comedia')"),
    criteria: str = Query("popularity", enum=["popularity", "weighted_rating", "rating"],
                          description="Criterio voraz de selección"),
    min_votes: int = Query(0, ge=0, description="Votos mínimos para ser candidata"),
    max_runtime: Optional[int] = Query(None, ge=30, description="Duración máxima en minutos"),
):
    """Top-K con selección voraz (heap de tamaño K): O(N log K)."""
    field = {"popularity": "popularity", "weighted_rating": "weighted_rating", "rating": "rating"}[criteria]
    candidates = [
        {"id": m["id"], "score": m[field], "rating": m["weighted_rating"]}
        for m in get_catalog()
        if matches_genre(m, genre) and m["votes"] >= min_votes
        and (max_runtime is None or m["runtime"] <= max_runtime)
    ]

    greedy = GreedyRecommender()
    top = greedy.get_top_k_recommendations(candidates, k)
    data = [public_view(get_movie(c["id"]), score=c["score"]) for c in top]

    return {
        "algorithm": "Greedy (Selección Voraz Top-K con heap)",
        "criteria": criteria,
        "genre_filter": genre if genre else "Todos los géneros",
        "requested_k": k,
        "total_candidates": len(candidates),
        "total_returned": len(data),
        "operations": greedy.operation_count,
        "data": data,
    }


# ---------------------------------------------------- Programación dinámica
@router.get("/marathon", summary="Secuencia óptima de reproducción")
def get_marathon_playlist(
    available_minutes: int = Query(300, ge=60, le=1440),
    genre: Optional[str] = Query(None, description="Género opcional"),
    pool: int = Query(150, ge=10, le=500, description="Cantidad de mejores títulos a considerar"),
):
    """
    Mochila 0/1 (DP): maximiza la satisfacción (rating ponderado) sin pasar del tiempo disponible.
    Luego el Ordenamiento Topológico acomoda la playlist respetando el orden de estreno de cada saga.
    """
    candidates = top_pool(pool, genre)
    items = [
        {"id": m["id"], "rating": m["weighted_rating"], "runtime": m["runtime"]}
        for m in candidates
    ]

    dp = DynamicProgrammingRecommender()
    total_score, selected = dp.max_satisfaction_watchsequence(items, available_minutes)
    chosen = [get_movie(s["id"]) for s in selected]
    playlist, has_cycle, topo_ops = _order_by_franchise(chosen)

    total_minutes = sum(m["runtime"] for m in playlist)
    return {
        "algorithm": "Dynamic Programming (Knapsack 0/1) + Ordenamiento Topológico",
        "available_time_minutes": available_minutes,
        "used_time_minutes": total_minutes,
        "total_satisfaction_score": total_score,
        "selected_movies_count": len(playlist),
        "dp_operations": dp.operation_count,
        "topological_operations": topo_ops,
        **_runtime_info(playlist),
        "playlist": [public_view(m, position=i) for i, m in enumerate(playlist, start=1)],
    }


def _order_by_franchise(movies: list) -> tuple:
    """
    Ordena con Kahn: dentro de cada saga, la película más antigua es prerrequisito de la siguiente.
    Entre películas disponibles, gana la de mejor rating. Devuelve (orden, hay_ciclo, operaciones).
    """
    graph = {str(m["id"]): [] for m in movies}
    by_franchise = {}
    for m in movies:
        if m["franchise"]:
            by_franchise.setdefault(m["franchise"], []).append(m)
    for group in by_franchise.values():
        group.sort(key=lambda m: (m["release_date"], m["id"]))
        for earlier, later in zip(group, group[1:]):
            graph[str(earlier["id"])].append(str(later["id"]))

    priority = {str(m["id"]): -m["weighted_rating"] for m in movies}
    topo = GraphAlgorithms()
    order, has_cycle = topo.topological_sort(graph, priority)
    by_id = {str(m["id"]): m for m in movies}
    return [by_id[n] for n in order], has_cycle, topo.operation_count


# --------------------------------------------------- Ordenamiento topológico
@router.get("/watch-order", summary="Orden de visionado de una saga")
def get_watch_order(
    franchise: Optional[str] = Query(None, description="Nombre de la saga (ej. 'Spider-Man'). Sin valor lista las sagas"),
):
    """
    Ordenamiento topológico (Kahn): cada película de una saga es prerrequisito de la siguiente
    por fecha de estreno. Sin parámetro devuelve las sagas detectadas.
    """
    groups = {}
    for m in get_catalog():
        if m["franchise"]:
            groups.setdefault(m["franchise"], []).append(m)

    if not franchise:
        return {
            "total_franchises": len(groups),
            "franchises": sorted(
                ({"name": name, "movies": len(ms)} for name, ms in groups.items()),
                key=lambda f: (-f["movies"], f["name"]),
            ),
        }

    match = next((n for n in groups if n.lower() == franchise.strip().lower()), None)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Saga '{franchise}' no encontrada. Consulta /recommend/watch-order sin parámetros.")

    order, has_cycle, ops = _order_by_franchise(groups[match])
    return {
        "algorithm": "Ordenamiento Topológico (Kahn)",
        "franchise": match,
        "has_cycle": has_cycle,
        "operations": ops,
        **_runtime_info(order),
        "total_runtime_minutes": sum(m["runtime"] for m in order),
        "watch_order": [public_view(m, position=i) for i, m in enumerate(order, start=1)],
    }


# --------------------------------------------------------------- Grafos
@router.get("/communities", summary="Detección de Comunidades")
def get_communities(
    method: str = Query("scc", enum=["scc", "ufds"]),
    pool: int = Query(100, ge=10, le=300, description="Cantidad de mejores títulos a analizar"),
    neighbors: int = Query(3, ge=1, le=10, description="[scc] vecinas más parecidas por película"),
    min_similarity: float = Query(0.7, ge=0.0, le=1.0, description="[ufds] similitud mínima para unir"),
    min_size: int = Query(2, ge=1, description="Tamaño mínimo de comunidad a reportar"),
):
    """
    SCC: grafo dirigido kNN (cada película apunta a sus K más parecidas); una comunidad es un
    conjunto donde todas se alcanzan entre sí. UFDS: une películas con similitud >= umbral.
    """
    movies = top_pool(pool)
    by_id = {str(m["id"]): m for m in movies}
    nodes = list(by_id)

    if method == "scc":
        algo = GraphAlgorithms()
        groups = algo.find_scc_tarjan(build_knn_graph(movies, neighbors))
        name, prefix = "Tarjan SCC (grafo kNN dirigido de similitud)", "COM"
    else:
        algo = MSTClustering()
        connections = [
            (str(a["id"]), str(b["id"]))
            for i, a in enumerate(movies) for b in movies[i + 1:]
            if a["genre_set"] & b["genre_set"] and similarity(a, b) >= min_similarity
        ]
        groups = list(algo.get_clusters_ufds(nodes, connections).values())
        name, prefix = "UFDS (unión por similitud mínima)", "CLUSTER"

    groups.sort(key=len, reverse=True)
    communities = []
    for group in groups:
        if len(group) < min_size:
            continue
        members = [by_id[n] for n in group]
        communities.append({
            "community_id": f"{prefix}-{len(communities) + 1:03d}",
            "total_movies": len(members),
            "dominant_genres": _dominant_genres(members),
            "avg_rating": round(sum(m["rating"] for m in members) / len(members), 2),
            "movies": [public_view(m) for m in members],
        })

    return {
        "algorithm": name,
        "pool_size": len(movies),
        "total_communities_found": len(communities),
        "ignored_small_groups": len(groups) - len(communities),
        "operations": algo.operation_count,
        "communities": communities,
    }


@router.get("/related/{movie_id}", summary="Películas relacionadas por saltos (BFS)")
def get_related(
    movie_id: int,
    depth: int = Query(2, ge=1, le=4),
    neighbors: int = Query(4, ge=1, le=10),
    pool: int = Query(200, ge=20, le=400),
):
    """BFS sobre el grafo kNN: nivel 1 = muy parecidas, nivel 2 = parecidas de las parecidas..."""
    seed = _require_movie(movie_id)
    movies = top_pool(pool, include_ids=[movie_id])
    graph = build_knn_graph(movies, neighbors)

    algo = GraphAlgorithms()
    found = algo.bfs_recommendations(graph, str(movie_id), max_depth=depth)
    return {
        "algorithm": "BFS (grafo kNN de similitud)",
        "seed": public_view(seed),
        "max_depth": depth,
        "total_found": len(found),
        "operations": algo.operation_count,
        "related": [public_view(get_movie(int(n)), hops=d, similarity_to_seed=round(similarity(seed, get_movie(int(n))), 4))
                    for n, d in found],
    }


# -------------------------------------------------- Caminos mínimos
@router.get("/discovery-path", summary="Ruta de descubrimiento entre dos películas")
def get_discovery_path(
    from_id: int,
    to_id: int,
    pool: int = Query(60, ge=10, le=150),
    min_similarity: float = Query(0.4, ge=0.0, le=1.0),
):
    """
    Bellman-Ford sobre un grafo dirigido de similitud (peso = 1 - similitud; subir a películas
    mejor calificadas es más barato). Devuelve la cadena de títulos más suave entre ambas.
    """
    _require_movie(from_id)
    _require_movie(to_id)
    movies = top_pool(pool, include_ids=[from_id, to_id])
    nodes = [str(m["id"]) for m in movies]
    edges = build_distance_edges(movies, min_similarity, directed=True)

    sp = ShortestPaths()
    dist, pred, negative_cycle = sp.bellman_ford(nodes, edges, str(from_id))
    path = [] if negative_cycle else sp.build_path(pred, str(from_id), str(to_id))
    return {
        "algorithm": "Bellman-Ford",
        "negative_cycle_detected": negative_cycle,
        "path_found": bool(path),
        "total_cost": round(dist[str(to_id)], 4) if path else None,
        "hops": len(path) - 1 if path else None,
        "graph": {"nodes": len(nodes), "edges": len(edges)},
        "operations": sp.operation_count,
        "path": [public_view(get_movie(int(n))) for n in path],
    }


@router.get("/hubs", summary="Películas más 'centrales' del catálogo")
def get_hubs(
    top: int = Query(5, ge=1, le=20),
    genre: Optional[str] = Query(None),
    pool: int = Query(50, ge=10, le=100),
    min_similarity: float = Query(0.4, ge=0.0, le=1.0),
):
    """
    Floyd-Warshall calcula todas las distancias entre películas; la centralidad armónica
    (suma de 1/distancia) identifica las que conectan mejor con el resto: buenos
    puntos de partida para recomendar.
    """
    movies = top_pool(pool, genre)
    nodes = [str(m["id"]) for m in movies]
    edges = build_distance_edges(movies, min_similarity)
    edges += [(v, u, w) for u, v, w in edges]  # no dirigido

    sp = ShortestPaths()
    dist, _ = sp.floyd_warshall(nodes, edges)
    scored = []
    for u in nodes:
        centrality = sum(1 / d for v, d in dist[u].items() if v != u and 0 < d < float("inf"))
        scored.append((centrality, u))
    scored.sort(reverse=True)

    return {
        "algorithm": "Floyd-Warshall (centralidad armónica)",
        "genre_filter": genre if genre else "Todos los géneros",
        "graph": {"nodes": len(nodes), "edges": len(edges) // 2},
        "operations": sp.operation_count,
        "hubs": [public_view(get_movie(int(u)), centrality=round(c, 4)) for c, u in scored[:top]],
    }


# ------------------------------------------------------------------ MST
@router.get("/clusters-mst", summary="Grupos de géneros por MST (Kruskal)")
def get_mst_clusters(
    k: int = Query(6, ge=2, le=30, description="Cantidad de grupos"),
    pool: int = Query(80, ge=10, le=200),
):
    """
    Kruskal sobre el grafo completo de distancias (1 - similitud) y corte en k grupos
    (equivale a quitar las k-1 aristas más pesadas del MST).
    """
    movies = top_pool(pool)
    by_id = {str(m["id"]): m for m in movies}
    nodes = list(by_id)
    edges = [
        (round(1 - similarity(a, b), 6), str(a["id"]), str(b["id"]))
        for i, a in enumerate(movies) for b in movies[i + 1:]
    ]

    algo = MSTClustering()
    clusters, mst_edges = algo.mst_clusters(nodes, edges, k)
    groups = sorted(clusters.values(), key=len, reverse=True)
    return {
        "algorithm": "Kruskal MST + UFDS (single-linkage)",
        "requested_clusters": k,
        "pool_size": len(movies),
        "mst_edges_used": len(mst_edges),
        "operations": algo.operation_count,
        "clusters": [
            {
                "cluster_id": f"MST-{i:02d}",
                "total_movies": len(g),
                "dominant_genres": _dominant_genres([by_id[n] for n in g]),
                "movies": [public_view(by_id[n]) for n in g],
            }
            for i, g in enumerate(groups, start=1)
        ],
    }


# ----------------------------------------------------------- Fuerza bruta
@router.get("/similar", summary="Recomendación por gustos del usuario (Fuerza Bruta)")
def get_similar(
    liked: List[int] = Query(..., description="IDs de películas que le gustaron al usuario"),
    k: int = Query(10, ge=1, le=50),
    genre: Optional[str] = Query(None),
):
    """Compara cada película del catálogo contra todas las que le gustaron al usuario. O(N * L)."""
    liked_movies = [_require_movie(mid) for mid in dict.fromkeys(liked)]
    catalog = [m for m in get_catalog() if matches_genre(m, genre)]

    algo = BruteForceRecommender()
    ranked = algo.rank_by_similarity(catalog, liked_movies, similarity, k)
    return {
        "algorithm": "Fuerza Bruta (similitud de contenido promedio)",
        "liked": [public_view(m) for m in liked_movies],
        "operations": algo.operation_count,
        "recommendations": [public_view(m, match_score=round(s, 4)) for m, s in ranked],
    }


# ------------------------------------------------------ Divide y Vencerás
@router.get("/catalog", summary="Catálogo ordenado y filtrado por rango")
def get_catalog_sorted(
    sort_by: str = Query("weighted_rating", enum=["weighted_rating", "rating", "popularity", "release_date", "runtime", "votes"]),
    order: str = Query("desc", enum=["asc", "desc"]),
    min_value: Optional[float] = Query(None, description="Valor mínimo de sort_by (solo campos numéricos)"),
    max_value: Optional[float] = Query(None, description="Valor máximo de sort_by (solo campos numéricos)"),
    genre: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """
    Merge Sort (Divide y Vencerás) para ordenar y búsqueda binaria recursiva (lower/upper bound)
    para recortar el rango [min_value, max_value] en O(log n).
    """
    if sort_by == "release_date" and (min_value is not None or max_value is not None):
        raise HTTPException(status_code=400, detail="min_value/max_value solo aplican a campos numéricos")

    dc = DivideAndConquer()
    movies = [m for m in get_catalog() if matches_genre(m, genre)]
    ordered = dc.merge_sort(movies, key=lambda m: m[sort_by])
    sort_ops = dc.operation_count

    if min_value is not None or max_value is not None:
        low = min_value if min_value is not None else float("-inf")
        high = max_value if max_value is not None else float("inf")
        ordered = dc.range_query(ordered, low, high, key=lambda m: m[sort_by])
    if order == "desc":
        ordered = ordered[::-1]

    start = (page - 1) * size
    return {
        "algorithm": "Divide y Vencerás (Merge Sort + búsqueda binaria)",
        "sort_by": sort_by,
        "order": order,
        "total_results": len(ordered),
        "page": page,
        "size": size,
        "sort_operations": sort_ops,
        "range_operations": dc.operation_count - sort_ops,
        "data": [public_view(m) for m in ordered[start:start + size]],
    }


# ---------------------------------------------------------- Backtracking
@router.get("/filter-backtracking", summary="Combinaciones por Género, Calificación y Tiempo")
def filter_combinations(
    genre: Optional[str] = Query(None, description="Ejemplo: 'Acción', 'Ciencia ficción', 'Aventura'"),
    min_rating: float = Query(7.5, ge=0.0, le=10.0, description="Calificación mínima de cada película"),
    max_movies: int = Query(2, ge=1, le=5, description="Cantidad exacta de películas de la combinación"),
    max_total_minutes: Optional[int] = Query(None, ge=30, le=1440, description="Duración total máxima (min)"),
    pool: int = Query(40, ge=5, le=100, description="Mejores títulos a considerar"),
    max_results: int = Query(50, ge=1, le=500),
):
    """
    Backtracking con poda + orden voraz: combinaciones de N películas, todas con rating >= mínimo
    y cuya duración total entre en el tiempo disponible.
    """
    movies = top_pool(pool, genre)
    items = [{"id": m["id"], "rating": m["weighted_rating"], "runtime": m["runtime"]} for m in movies]

    algo = PreferenceBacktracking()
    combos = algo.find_movie_combinations(items, min_rating, max_movies, max_total_minutes, max_results)

    results = []
    for combo in combos:
        chosen = [get_movie(c["id"]) for c in combo]
        results.append({
            "avg_rating": round(sum(m["weighted_rating"] for m in chosen) / len(chosen), 3),
            "total_minutes": sum(m["runtime"] for m in chosen),
            "movies": [public_view(m) for m in chosen],
        })
    results.sort(key=lambda r: r["avg_rating"], reverse=True)

    return {
        "algorithm": "Backtracking con poda + orden voraz",
        "note": "El rating usado es el ponderado por votos.",
        "genre_filter": genre if genre else "Todos los géneros",
        "constraints": {
            "min_rating": min_rating,
            "exact_movies_count": max_movies,
            "max_total_minutes": max_total_minutes,
        },
        "pool_size": len(movies),
        "total_combinations_found": len(results),
        "truncated": algo.truncated,
        "operations": algo.operation_count,
        **_runtime_info([m for m in movies]),
        "results": results,
    }


# ------------------------------------------------------------ Flujo máximo
class UserProfile(BaseModel):
    name: str
    genres: List[str] = Field(..., min_length=1, description="Géneros de interés")
    slots: int = Field(3, ge=1, le=20, description="Cuántas recomendaciones quiere recibir")


class AllocationRequest(BaseModel):
    users: List[UserProfile] = Field(..., min_length=1, max_length=50)
    max_exposure: int = Field(2, ge=1, le=50, description="Máximo de usuarios a los que se recomienda la misma película")
    pool: int = Field(150, ge=10, le=500)


@router.post("/allocate", summary="Asignación de recomendaciones con Flujo Máximo")
def allocate_recommendations(request: AllocationRequest):
    """
    Red: fuente -> usuario (cap = slots) -> película (cap 1, si coincide el género) -> destino
    (cap = max_exposure). El flujo máximo reparte recomendaciones sin repetir una misma película
    a más usuarios del límite, evitando que todos reciban el mismo top.
    """
    movies = top_pool(request.pool)
    capacity = {"S": {}, "T": {}}
    for index, user in enumerate(request.users):
        u_node = f"U{index}"
        capacity["S"][u_node] = user.slots
        wanted = {g.strip().lower() for g in user.genres}
        capacity[u_node] = {f"M{m['id']}": 1 for m in movies if wanted & m["genre_set"]}
    for m in movies:
        capacity[f"M{m['id']}"] = {"T": request.max_exposure}

    algo = MaxFlowAllocator()
    max_flow, residual = algo.edmonds_karp(capacity, "S", "T")
    flows = algo.get_flow_edges(capacity, residual)

    assignments = []
    for index, user in enumerate(request.users):
        picked = [get_movie(int(v[1:])) for (u, v) in flows if u == f"U{index}"]
        picked.sort(key=lambda m: m["weighted_rating"], reverse=True)
        assignments.append({
            "user": user.name,
            "requested": user.slots,
            "assigned": len(picked),
            "movies": [public_view(m) for m in picked],
        })

    requested = sum(u.slots for u in request.users)
    return {
        "algorithm": "Flujo Máximo (Ford-Fulkerson / Edmonds-Karp)",
        "total_requested": requested,
        "total_assigned": max_flow,
        "fully_satisfied": max_flow == requested,
        "operations": algo.operation_count,
        "assignments": assignments,
    }
