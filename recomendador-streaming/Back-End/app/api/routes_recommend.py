from fastapi import APIRouter, Query
from typing import Optional
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


@router.get("/top-k", summary="Recomendaciones rápidas Top-K")
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


@router.get("/marathon", summary="Secuencia óptima de reproducción")
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


def parse_genres(genre_str: str) -> set:
    """Convierte la cadena 'Ciencia ficción, Acción' en un conjunto {'ciencia ficción', 'acción'}."""
    if not genre_str:
        return set()
    return {g.strip().lower() for g in genre_str.split(",")}


@router.get("/communities", summary="Detección de Comunidades")
def get_communities(method: str = Query("scc", enum=["scc", "ufds"])):
    """
    Identifica nichos de películas agrupándolas por coincidencia de géneros y rango de calidad similar.
    """
    sub_movies = movies_data[:50]  # Tomamos una muestra de 50 películas
    nodes = [str(m.get("ID")) for m in sub_movies]
    
    # Mapa auxiliar para acceder rápido a los datos por ID
    movie_map = {str(m.get("ID")): m for m in sub_movies}
    
    formatted_communities = []

    if method == "scc":
        # Construcción del Grafo de Adyacencia Basado en Semántica Real
        adj_graph = {node: [] for node in nodes}
        
        for i, m1 in enumerate(sub_movies):
            id1 = str(m1.get("ID"))
            genres1 = parse_genres(m1.get("Género", ""))
            rating1 = m1.get("Calificación Promedio", 0)

            for j, m2 in enumerate(sub_movies):
                if i == j:
                    continue
                id2 = str(m2.get("ID"))
                genres2 = parse_genres(m2.get("Género", ""))
                rating2 = m2.get("Calificación Promedio", 0)

                # REGLA DE ADYACENCIA:
                # Comparten al menos 1 género Y tienen calificaciones similares (diferencia <= 0.8)
                shared_genres = genres1.intersection(genres2)
                if len(shared_genres) >= 1 and abs(rating1 - rating2) <= 0.8:
                    adj_graph[id1].append(id2)

        raw_sccs = graph_algo.find_scc_tarjan(adj_graph)

        for index, component in enumerate(raw_sccs, start=1):
            # Extraer títulos y géneros dominantes del grupo para dar contexto al usuario
            group_movies = [movie_map[mid] for mid in component if mid in movie_map]
            
            # Recolectar todos los géneros del grupo
            all_group_genres = set()
            for m in group_movies:
                all_group_genres.update(parse_genres(m.get("Género", "")))

            formatted_communities.append({
                "community_id": f"COM-{index:03d}",
                "total_movies": len(component),
                "shared_genres": list(all_group_genres),
                "movies": [
                    {
                        "id": m.get("ID"),
                        "title": m.get("Título en Español") or m.get("Título Original"),
                        "rating": m.get("Calificación Promedio"),
                        "genres": m.get("Género")
                    }
                    for m in group_movies
                ]
            })

        return {
            "algorithm": "Tarjan SCC (Componentes Fuertemente Conectados por Género/Rating)",
            "total_communities_found": len(formatted_communities),
            "communities": formatted_communities
        }

    else:  # Método UFDS
        edges = []
        for i in range(len(sub_movies)):
            for j in range(i + 1, len(sub_movies)):
                m1, m2 = sub_movies[i], sub_movies[j]
                g1, g2 = parse_genres(m1.get("Género", "")), parse_genres(m2.get("Género", ""))
                
                # Conectar si comparten géneros
                if len(g1.intersection(g2)) >= 1:
                    edges.append((str(m1.get("ID")), str(m2.get("ID"))))

        raw_clusters = mst_algo.get_clusters_ufds(nodes, edges)

        for index, (root_node, members) in enumerate(raw_clusters.items(), start=1):
            group_movies = [movie_map[mid] for mid in members if mid in movie_map]
            
            formatted_communities.append({
                "community_id": f"CLUSTER-{index:03d}",
                "leader_movie_id": root_node,
                "total_movies": len(members),
                "movies": [
                    {
                        "id": m.get("ID"),
                        "title": m.get("Título en Español") or m.get("Título Original"),
                        "genres": m.get("Género")
                    }
                    for m in group_movies
                ]
            })

        return {
            "algorithm": "UFDS Clustering (Agrupación por Géneros Compartidos)",
            "total_communities_found": len(formatted_communities),
            "communities": formatted_communities
        }

@router.get("/filter-backtracking", summary="Combinaciones por Género y Calificación ")
def filter_combinations(
    genre: Optional[str] = Query(None, description="Ejemplo: 'Acción', 'Ciencia ficción', 'Aventura'"),
    min_rating: float = Query(7.5, ge=0.0, le=10.0, description="Calificación mínima requerida"),
    max_movies: int = Query(2, ge=1, le=5, description="Cantidad exacta de películas para la combinación")
):
    """
    Busca combinaciones exactas de N películas pertenecientes a un género específico
    que satisfagan una calificación mínima promedio dada.
    """
    formatted_movies = []
    
    for m in movies_data:
        m_genres = parse_genres(m.get("Género", ""))
        
        # Filtro de género opcional
        if genre and genre.strip().lower() not in m_genres:
            continue

        # Parsing seguro del rating
        try:
            rating_val = float(m.get("Calificación Promedio") or 0.0)
        except (ValueError, TypeError):
            rating_val = 0.0

        formatted_movies.append({
            "id": m.get("ID"),
            "title": m.get("Título en Español") or m.get("Título Original"),
            "rating": rating_val,
            "genres": m.get("Género")
        })

    # Ejecución de Backtracking sobre la muestra
    combinations = backtrack_algo.find_movie_combinations(
        formatted_movies[:40],  # Muestra para mantener tiempos de respuesta óptimos
        min_rating=min_rating,
        max_movies=max_movies
    )

    return {
        "algorithm": "Backtracking (Filtro por Género y Rating)",
        "genre_filter": genre if genre else "Todos los géneros",
        "constraints": {
            "min_rating": min_rating,
            "exact_movies_count": max_movies
        },
        "total_combinations_found": len(combinations),
        "results": combinations
    }