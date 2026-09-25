from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json
import os

# Importación de algoritmos
from app.algorithms.graphs import GraphAlgorithms
from app.algorithms.greedy import GreedyRecommender
from app.algorithms.dynamic_prog import DynamicProgrammingRecommender
from app.algorithms.mst_clustering import MSTClustering
from app.algorithms.max_flow import MaxFlowAllocator
from app.algorithms.backtracking import PreferenceBacktracking

router = APIRouter(prefix="/recommend", tags=["Recomendaciones"])

# Cargar dataset local JSON
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/Base_Datos_TMDB.json")

def load_movies():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

movies_data = load_movies()

# Instancias de algoritmos
graph_algo = GraphAlgorithms()
greedy_algo = GreedyRecommender()
dp_algo = DynamicProgrammingRecommender()
mst_algo = MSTClustering()
max_flow_algo = MaxFlowAllocator()
backtrack_algo = PreferenceBacktracking()


@router.get("/top-k", summary="Recomendaciones rápidas Top-K (Algoritmo Voraz)")
def get_top_k(k: int = Query(10, ge=1, le=50)):
    """
    Retorna las K películas más populares/mejor calificadas usando el enfoque Greedy.
    """
    candidates = []
    for m in movies_data:
        candidates.append({
            "id": m.get("ID"),
            "title": m.get("Título en Español") or m.get("Título Original"),
            "score": m.get("Popularidad", 0),
            "rating": m.get("Calificación Promedio", 0)
        })
    
    top_k = greedy_algo.get_top_k_recommendations(candidates, k)
    return {"algorithm": "Greedy", "count": len(top_k), "data": top_k}


@router.get("/marathon", summary="Secuencia óptima de reproducción (Programación Dinámica)")
def get_marathon_playlist(available_minutes: int = Query(300, ge=60, le=1440)):
    """
    Resuelve el problema de la mochila (Knapsack DP) para maximizar la satisfacción
    de un usuario dado un tiempo límite en minutos.
    """
    # Asignamos una duración estimada de 120 min si no está en el JSON
    formatted_movies = []
    for m in movies_data:
        formatted_movies.append({
            "id": m.get("ID"),
            "title": m.get("Título en Español"),
            "rating": m.get("Calificación Promedio", 5.0),
            "runtime": m.get("Duracion_Minutos", 120) 
        })

    total_score, selected = dp_algo.max_satisfaction_watchsequence(formatted_movies, available_minutes)
    return {
        "algorithm": "Dynamic Programming (Knapsack 0/1)",
        "available_time_minutes": available_minutes,
        "total_satisfaction_score": total_score,
        "selected_movies_count": len(selected),
        "playlist": selected
    }


@router.get("/communities", summary="Detección de Comunidades (SCC - Tarjan / UFDS)")
def get_communities(method: str = Query("scc", enum=["scc", "ufds"])):
    """
    Identifica grupos de usuarios/películas fuertemente conectados o clusterizados.
    """
    # Construcción de un grafo de simulación a partir de similitud de calificaciones/géneros
    nodes = [str(m.get("ID")) for m in movies_data[:50]]
    
    if method == "scc":
        # Construir grafo adyacente sintético para prueba
        adj_graph = {node: [] for node in nodes}
        for i in range(len(nodes) - 1):
            adj_graph[nodes[i]].append(nodes[i+1])
            if i % 3 == 0:
                adj_graph[nodes[i+1]].append(nodes[i])  # Crear ciclos
        
        communities = graph_algo.find_scc_tarjan(adj_graph)
        return {"algorithm": "Tarjan SCC", "total_communities": len(communities), "communities": communities}
    else:
        edges = [(nodes[i], nodes[i+1]) for i in range(len(nodes)-1)]
        clusters = mst_algo.get_clusters_ufds(nodes, edges)
        return {"algorithm": "UFDS Clustering", "total_clusters": len(clusters), "clusters": clusters}


@router.get("/filter-backtracking", summary="Búsqueda de combinaciones bajo filtro (Backtracking)")
def filter_combinations(target_time: int = 240, min_rating: float = 7.0, max_movies: int = 2):
    """
    Explora combinaciones exactas mediante Backtracking aplicando poda por restricción.
    """
    formatted_movies = [
        {
            "id": m.get("ID"),
            "title": m.get("Título en Español"),
            "rating": m.get("Calificación Promedio", 0),
            "runtime": m.get("Duracion_Minutos", 120)
        }
        for m in movies_data[:20]  # Limitar entrada para evitar explosión combinatoria
    ]
    
    combinations = backtrack_algo.find_movie_combinations(
        formatted_movies, target_time, min_rating, max_movies
    )
    return {
        "algorithm": "Backtracking",
        "total_combinations_found": len(combinations),
        "results": combinations
    }