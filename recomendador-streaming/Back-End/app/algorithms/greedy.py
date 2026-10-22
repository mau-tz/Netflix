import heapq


class GreedyRecommender:
    def __init__(self):
        self.operation_count = 0

    def get_top_k_recommendations(self, candidates: list, k: int) -> list:
        """
        Selecciona las K mejores películas por score (desempate por rating).
        candidates: list of dicts [{'id': 1, 'score': 8.5, 'rating': 7.0}, ...]
        Complejidad: O(N log K) con un min-heap de tamaño K.
        """
        self.operation_count = 0
        if k <= 0:
            return []

        heap = []  # min-heap de (score, rating, -posición, candidato)
        for position, c in enumerate(candidates):
            self.operation_count += 1
            key = (c.get("score", 0), c.get("rating", 0), -position)
            if len(heap) < k:
                heapq.heappush(heap, (key, position, c))
            elif key > heap[0][0]:
                heapq.heapreplace(heap, (key, position, c))
            else:
                continue
            self.operation_count += 1  # costo log K de la operación sobre el heap

        heap.sort(key=lambda t: t[0], reverse=True)
        return [c for _, _, c in heap]
