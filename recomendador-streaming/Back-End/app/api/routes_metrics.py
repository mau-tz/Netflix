from fastapi import APIRouter, Query
from app.utils.benchmark import BenchmarkRunner
from app.algorithms.brute_force import BruteForceRecommender
from app.algorithms.greedy import GreedyRecommender
from app.algorithms.dynamic_prog import DynamicProgrammingRecommender
from app.algorithms.graphs import GraphAlgorithms
import json
import os

router = APIRouter(prefix="/metrics", tags=["Benchmarking y Complejidad"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/movies.json")

def load_movies():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

movies_data = load_movies()

brute_force_algo = BruteForceRecommender()
greedy_algo = GreedyRecommender()
dp_algo = DynamicProgrammingRecommender()
graph_algo = GraphAlgorithms()


@router.get("/compare", summary="Comparador experimental de algoritmos para N elementos")
def compare_algorithms(sample_size: int = Query(50, ge=10, le=1000)):
    """
    Ejecuta y compara empíricamente los algoritmos sobre un tamaño de entrada N:
    1. Fuerza Bruta O(N^2)
    2. Greedy O(N log N)
    3. Programación Dinámica O(N * T)
    """
    sub_data = movies_data[:sample_size]
    
    # 1. Prueba Fuerza Bruta (Simulación de matriz de similitud)
    user_ratings_sim = {
        f"user_{i}": {m.get("ID"): m.get("Calificación Promedio", 5) for m in sub_data[:10]}
        for i in range(min(sample_size, 30))
    }
    
    bf_benchmark = BenchmarkRunner.measure_execution(
        brute_force_algo.compare_all_users, user_ratings_sim
    )
    bf_ops = brute_force_algo.operation_count

    # 2. Prueba Voraz (Greedy Top-K)
    candidates = [{"id": m.get("ID"), "score": m.get("Popularidad", 0)} for m in sub_data]
    greedy_benchmark = BenchmarkRunner.measure_execution(
        greedy_algo.get_top_k_recommendations, candidates, 10
    )
    greedy_ops = greedy_algo.operation_count

    # 3. Prueba BFS en Grafos
    adj_graph = {str(m.get("ID")): [str(sub_data[(i+1)%len(sub_data)].get("ID"))] for i, m in enumerate(sub_data)}
    first_node = str(sub_data[0].get("ID")) if sub_data else "0"
    
    bfs_benchmark = BenchmarkRunner.measure_execution(
        graph_algo.bfs_recommendations, adj_graph, first_node, max_depth=2
    )
    bfs_ops = graph_algo.operation_count

    # Estructura del reporte comparativo
    return {
        "sample_size_N": len(sub_data),
        "results": [
            {
                "algorithm": "Fuerza Bruta (Matriz Usuarios)",
                "theoretical_complexity": "O(U^2 * N)",
                "execution_time_ms": bf_benchmark["metrics"]["execution_time_ms"],
                "peak_memory_kb": bf_benchmark["metrics"]["peak_memory_kb"],
                "total_operations": bf_ops
            },
            {
                "algorithm": "Algoritmo Voraz (Top-K Greedy)",
                "theoretical_complexity": "O(N log K)",
                "execution_time_ms": greedy_benchmark["metrics"]["execution_time_ms"],
                "peak_memory_kb": greedy_benchmark["metrics"]["peak_memory_kb"],
                "total_operations": greedy_ops
            },
            {
                "algorithm": "Búsqueda en Grafos (BFS)",
                "theoretical_complexity": "O(V + E)",
                "execution_time_ms": bfs_benchmark["metrics"]["execution_time_ms"],
                "peak_memory_kb": bfs_benchmark["metrics"]["peak_memory_kb"],
                "total_operations": bfs_ops
            }
        ]
    }