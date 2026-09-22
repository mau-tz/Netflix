import math

class BruteForceRecommender:
    def __init__(self):
        self.operation_count = 0

    def calculate_user_similarity(self, ratings_user1: dict, ratings_user2: dict) -> float:
        """
        Calcula la similitud del coseno entre dos usuarios comparando todas sus calificaciones (O(N)).
        ratings: {movie_id: score}
        """
        self.operation_count = 0
        common_movies = []
        
        # O(N) operaciones para encontrar películas comunes
        for movie_id in ratings_user1:
            self.operation_count += 1
            if movie_id in ratings_user2:
                common_movies.append(movie_id)

        if not common_movies:
            return 0.0

        dot_product = 0.0
        norm_a = 0.0
        norm_b = 0.0

        for movie_id in common_movies:
            self.operation_count += 1
            score1 = ratings_user1[movie_id]
            score2 = ratings_user2[movie_id]
            dot_product += score1 * score2
            norm_a += score1 ** 2
            norm_b += score2 ** 2

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (math.sqrt(norm_a) * math.sqrt(norm_b))

    def compare_all_users(self, all_user_ratings: dict) -> dict:
        """
        Compara todos los pares de usuarios con Fuerza Bruta (O(U^2 * N)).
        """
        similarities = {}
        users = list(all_user_ratings.keys())
        n = len(users)

        for i in range(n):
            for j in range(i + 1, n):
                u1, u2 = users[i], users[j]
                sim = self.calculate_user_similarity(all_user_ratings[u1], all_user_ratings[u2])
                similarities[(u1, u2)] = sim

        return similarities