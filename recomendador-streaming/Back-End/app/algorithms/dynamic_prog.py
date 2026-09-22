class DynamicProgrammingRecommender:
    def __init__(self):
        self.operation_count = 0
        self.memo = {}

    def memoized_similarity(self, u1_id: str, u2_id: str, compute_func, *args) -> float:
        """
        Optimización DP mediante Memoización para evitar recalcular la similitud entre usuarios.
        """
        key = tuple(sorted([u1_id, u2_id]))
        if key in self.memo:
            return self.memo[key]

        self.operation_count += 1
        result = compute_func(*args)
        self.memo[key] = result
        return result

    def max_satisfaction_watchsequence(self, movies: list, available_time: int) -> tuple:
        """
        Problema de la Mochila (Knapsack 0/1) con Programación Dinámica para armar 
        la playlist perfecta de duración <= available_time con máxima satisfacción.
        Complejidad: O(N * T)
        """
        self.operation_count = 0
        n = len(movies)
        dp = [[0 for _ in range(available_time + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            duration = movies[i - 1]['runtime']
            score = int(movies[i - 1]['rating'] * 10)  # Escalar a entero

            for w in range(1, available_time + 1):
                self.operation_count += 1
                if duration <= w:
                    dp[i][w] = max(score + dp[i - 1][w - duration], dp[i - 1][w])
                else:
                    dp[i][w] = dp[i - 1][w]

        # Reconstruir la lista de películas seleccionadas
        selected_movies = []
        w = available_time
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                selected_movies.append(movies[i - 1])
                w -= movies[i - 1]['runtime']

        return dp[n][available_time], selected_movies