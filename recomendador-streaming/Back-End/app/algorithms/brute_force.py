import math


class BruteForceRecommender:
    def __init__(self):
        self.operation_count = 0

    def _cosine(self, ratings_user1: dict, ratings_user2: dict) -> float:
        # Producto punto sobre películas en común (O(N))
        dot_product = 0.0
        for movie_id, score1 in ratings_user1.items():
            self.operation_count += 1
            if movie_id in ratings_user2:
                dot_product += score1 * ratings_user2[movie_id]

        if dot_product == 0:
            return 0.0

        # Las normas usan TODAS las calificaciones: si solo se usaran las comunes,
        # dos usuarios con una única película en común tendrían similitud 1.0.
        norm_a = math.sqrt(sum(s * s for s in ratings_user1.values()))
        norm_b = math.sqrt(sum(s * s for s in ratings_user2.values()))
        self.operation_count += len(ratings_user1) + len(ratings_user2)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def calculate_user_similarity(self, ratings_user1: dict, ratings_user2: dict) -> float:
        """
        Similitud del coseno entre dos usuarios. ratings: {movie_id: score}. O(N)
        """
        self.operation_count = 0
        return self._cosine(ratings_user1, ratings_user2)

    def compare_all_users(self, all_user_ratings: dict) -> dict:
        """
        Compara todos los pares de usuarios con Fuerza Bruta (O(U^2 * N)).
        operation_count acumula las operaciones de todos los pares.
        """
        self.operation_count = 0
        similarities = {}
        users = list(all_user_ratings.keys())
        n = len(users)

        for i in range(n):
            for j in range(i + 1, n):
                u1, u2 = users[i], users[j]
                similarities[(u1, u2)] = self._cosine(all_user_ratings[u1], all_user_ratings[u2])

        return similarities

    def rank_by_similarity(self, catalog: list, liked: list, similarity_func, k: int) -> list:
        """
        Recomendación basada en contenido por Fuerza Bruta: compara CADA película del
        catálogo contra CADA película que le gustó al usuario. O(N * L).
        Devuelve [(pelicula, score)] con las k mejores, excluyendo las ya vistas.
        """
        self.operation_count = 0
        liked_ids = {m["id"] for m in liked}
        scored = []
        for candidate in catalog:
            if candidate["id"] in liked_ids:
                continue
            total = 0.0
            for seen in liked:
                self.operation_count += 1
                total += similarity_func(candidate, seen)
            scored.append((candidate, total / len(liked) if liked else 0.0))

        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:k]
