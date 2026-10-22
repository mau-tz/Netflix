from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.algorithms.backtracking import PreferenceBacktracking
from app.algorithms.brute_force import BruteForceRecommender
from app.algorithms.divide_conquer import DivideAndConquer
from app.algorithms.dynamic_prog import DynamicProgrammingRecommender
from app.algorithms.graphs import GraphAlgorithms
from app.algorithms.greedy import GreedyRecommender
from app.algorithms.max_flow import MaxFlowAllocator
from app.algorithms.mst_clustering import MSTClustering
from app.algorithms.shortest_paths import ShortestPaths
from app.services.catalog import get_catalog
from app.services.movie_graph import build_distance_edges, build_knn_graph
from app.services.similarity import content_similarity
from app.utils.benchmark import BenchmarkRunner

router = APIRouter(prefix="/metrics", tags=["Benchmarking y Complejidad"])


# Cada runner recibe N, prepara su entrada FUERA del tiempo medido y devuelve
# (job, algoritmo, tamaño_real_usado). Los algoritmos cuadráticos/cúbicos limitan N
# para que la petición responda en tiempo razonable.
def _sample(n):
    return get_catalog()[:n]


def _brute_force(n):
    movies, algo = _sample(n), BruteForceRecommender()
    return (lambda: algo.rank_by_similarity(movies, movies[:3], content_similarity, 10)), algo, len(movies)


def _greedy(n):
    movies, algo = _sample(n), GreedyRecommender()
    candidates = [{"id": m["id"], "score": m["popularity"], "rating": m["rating"]} for m in movies]
    return (lambda: algo.get_top_k_recommendations(candidates, 10)), algo, len(movies)


def _merge_sort(n):
    movies, algo = _sample(n), DivideAndConquer()
    return (lambda: algo.merge_sort(movies, key=lambda m: m["rating"])), algo, len(movies)


def _knapsack(n):
    movies, algo = _sample(n), DynamicProgrammingRecommender()
    items = [{"rating": m["weighted_rating"], "runtime": m["runtime"]} for m in movies]
    return (lambda: algo.max_satisfaction_watchsequence(items, 600)), algo, len(movies)


def _backtracking(n):
    n = min(n, 25)
    movies, algo = _sample(n), PreferenceBacktracking()
    items = [{"rating": m["weighted_rating"], "runtime": m["runtime"]} for m in movies]
    return (lambda: algo.find_movie_combinations(items, 6.0, 3, None, 10 ** 9)), algo, n


def _bfs(n):
    n = min(n, 150)
    graph, algo = build_knn_graph(_sample(n), 4), GraphAlgorithms()
    return (lambda: algo.bfs_recommendations(graph, next(iter(graph)), 3)), algo, n


def _tarjan(n):
    n = min(n, 150)
    graph, algo = build_knn_graph(_sample(n), 4), GraphAlgorithms()
    return (lambda: algo.find_scc_tarjan(graph)), algo, n


def _topological(n):
    movies, algo = _sample(n), GraphAlgorithms()
    ordered = sorted(movies, key=lambda m: m["release_date"])
    graph = {str(a["id"]): [str(b["id"])] for a, b in zip(ordered, ordered[1:])}
    return (lambda: algo.topological_sort(graph)), algo, len(movies)


def _kruskal(n):
    n = min(n, 120)
    movies, algo = _sample(n), MSTClustering()
    nodes = [str(m["id"]) for m in movies]
    edges = [(1 - content_similarity(a, b), str(a["id"]), str(b["id"])) for i, a in enumerate(movies) for b in movies[i + 1:]]
    return (lambda: algo.kruskal_mst(nodes, edges)), algo, n


def _bellman_ford(n):
    n = min(n, 60)
    movies, algo = _sample(n), ShortestPaths()
    nodes = [str(m["id"]) for m in movies]
    edges = build_distance_edges(movies, 0.3, directed=True)
    return (lambda: algo.bellman_ford(nodes, edges, nodes[0])), algo, n


def _floyd_warshall(n):
    n = min(n, 60)
    movies, algo = _sample(n), ShortestPaths()
    nodes = [str(m["id"]) for m in movies]
    edges = build_distance_edges(movies, 0.3, directed=True)
    return (lambda: algo.floyd_warshall(nodes, edges)), algo, n


def _max_flow(n):
    n = min(n, 200)
    movies, algo = _sample(n), MaxFlowAllocator()
    users = 5
    capacity = {"S": {f"U{u}": 5 for u in range(users)}, "T": {}}
    for u in range(users):
        capacity[f"U{u}"] = {f"M{m['id']}": 1 for i, m in enumerate(movies) if i % users != u}
    for m in movies:
        capacity[f"M{m['id']}"] = {"T": 2}
    return (lambda: algo.edmonds_karp(capacity, "S", "T")), algo, n


ALGORITHMS = {
    "brute_force": ("Fuerza Bruta (similitud de contenido)", "O(N * L)", _brute_force),
    "greedy_topk": ("Voraz (Top-K con heap)", "O(N log K)", _greedy),
    "merge_sort": ("Divide y Vencerás (Merge Sort)", "O(N log N)", _merge_sort),
    "knapsack_dp": ("Programación Dinámica (Mochila 0/1)", "O(N * T)", _knapsack),
    "backtracking": ("Backtracking con poda", "O(C(N, k))", _backtracking),
    "bfs": ("BFS en grafo kNN", "O(V + E)", _bfs),
    "tarjan_scc": ("Tarjan SCC", "O(V + E)", _tarjan),
    "topological_sort": ("Ordenamiento Topológico (Kahn)", "O((V + E) log V)", _topological),
    "kruskal_mst": ("Kruskal MST + UFDS", "O(E log E)", _kruskal),
    "bellman_ford": ("Bellman-Ford", "O(V * E)", _bellman_ford),
    "floyd_warshall": ("Floyd-Warshall", "O(V^3)", _floyd_warshall),
    "max_flow": ("Flujo Máximo (Edmonds-Karp)", "O(V * E^2)", _max_flow),
}


def _run(key: str, n: int) -> dict:
    name, complexity, runner = ALGORITHMS[key]
    job, algo, used = runner(n)
    measured = BenchmarkRunner.measure_execution(job)
    return {
        "key": key,
        "algorithm": name,
        "theoretical_complexity": complexity,
        "input_size_used": used,
        "execution_time_ms": measured["metrics"]["execution_time_ms"],
        "peak_memory_kb": measured["metrics"]["peak_memory_kb"],
        "total_operations": algo.operation_count,
    }


@router.get("/compare", summary="Comparador experimental de algoritmos para N elementos")
def compare_algorithms(sample_size: int = Query(50, ge=10, le=1000)):
    """
    Ejecuta todos los algoritmos sobre los primeros N títulos del catálogo y reporta tiempo,
    memoria pico y operaciones. Los algoritmos de costo alto limitan N (ver input_size_used).
    """
    return {
        "sample_size_N": min(sample_size, len(get_catalog())),
        "results": [_run(key, sample_size) for key in ALGORITHMS],
    }


@router.get("/scaling", summary="Crecimiento empírico de un algoritmo al aumentar N")
def scaling(
    algorithm: str = Query(..., enum=list(ALGORITHMS)),
    sizes: List[int] = Query([25, 50, 100, 200, 400], description="Valores de N a medir"),
):
    """Mide un algoritmo con varios N para contrastar el crecimiento real con la complejidad teórica."""
    if not sizes or any(s < 5 or s > 1000 for s in sizes):
        raise HTTPException(status_code=400, detail="Cada tamaño debe estar entre 5 y 1000")
    runs = [_run(algorithm, n) for n in sorted(set(sizes))]
    return {
        "algorithm": ALGORITHMS[algorithm][0],
        "theoretical_complexity": ALGORITHMS[algorithm][1],
        "runs": runs,
    }
