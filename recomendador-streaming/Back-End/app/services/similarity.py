from app.algorithms.dynamic_prog import DynamicProgrammingRecommender

# Una sola instancia: la tabla memo (DP) se comparte entre peticiones, de modo que
# cada par de películas se compara una única vez durante la vida del servidor.
_dp = DynamicProgrammingRecommender()


def content_similarity(a: dict, b: dict) -> float:
    """Similitud 0..1: 70% Jaccard de géneros + 30% cercanía de calificación."""
    ga, gb = a["genre_set"], b["genre_set"]
    union = len(ga | gb)
    jaccard = len(ga & gb     ) / union if union else 0.0
    closeness = 1 - min(abs(a["rating"] - b["rating"]), 10) / 10
    return 0.7 * jaccard + 0.3 * closeness


def similarity(a: dict, b: dict) -> float:
    """content_similarity con memoización (Programación Dinámica)."""
    return _dp.memoized_similarity(str(a["id"]), str(b["id"]), content_similarity, a, b)


def cache_size() -> int:
    return len(_dp.memo)
