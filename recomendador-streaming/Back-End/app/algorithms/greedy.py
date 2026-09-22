class GreedyRecommender:
    def __init__(self):
        self.operation_count = 0

    def get_top_k_recommendations(self, candidates: list, k: int) -> list:
        """
        Selecciona las K mejores películas basadas en la mayor puntuación ponderada.
        candidates: list of dicts [{'id': 1, 'score': 8.5}, ...]
        Complejidad: O(N log K) utilizando selección óptima local.
        """
        self.operation_count = 0
        
        # Ordenamiento voraz rápido por score
        sorted_candidates = sorted(
            candidates, 
            key=lambda x: (x.get('score', 0), x.get('rating', 0)), 
            reverse=True
        )
        
        self.operation_count += len(candidates)
        return sorted_candidates[:k]