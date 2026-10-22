class DynamicProgrammingRecommender:
    def __init__(self):
        self.operation_count = 0
        self.memo = {}

    def memoized_similarity(self, u1_id: str, u2_id: str, compute_func, *args) -> float:
        """
        Optimización DP mediante Memoización: cada par de elementos se compara una sola vez.
        operation_count cuenta únicamente los cálculos reales (fallos de caché).
        """
        key = (u1_id, u2_id) if u1_id <= u2_id else (u2_id, u1_id)
        if key in self.memo:
            return self.memo[key]

        self.operation_count += 1
        result = compute_func(*args)
        self.memo[key] = result
        return result

    def max_satisfaction_watchsequence(self, movies: list, available_time: int) -> tuple:
        """
        Mochila 0/1 con Programación Dinámica: playlist de duración <= available_time
        con máxima satisfacción. movies: [{'runtime': min, 'rating': r, ...}]
        Complejidad: O(N * T) en tiempo; O(T) para la tabla de valores + N*T bits de decisión.
        Devuelve (satisfacción_total, películas_seleccionadas_en_orden_original).
        """
        self.operation_count = 0
        n = len(movies)
        T = max(int(available_time), 0)
        dp = [0] * (T + 1)  # dp[w] = mejor satisfacción con w minutos disponibles
        taken = [bytearray(T + 1) for _ in range(n)]  # taken[i][w] = 1 si la película i mejora dp[w]

        for i, movie in enumerate(movies):
            duration = int(movie["runtime"])
            score = int(round(float(movie.get("rating") or 0.0) * 10))  # escalar a entero
            if duration <= 0 or duration > T:
                continue
            row = taken[i]
            # w descendente: cada película se usa como máximo una vez (0/1)
            for w in range(T, duration - 1, -1):
                self.operation_count += 1
                candidate = dp[w - duration] + score
                if candidate > dp[w]:
                    dp[w] = candidate
                    row[w] = 1

        # Reconstrucción de la solución
        selected, w = [], T
        for i in range(n - 1, -1, -1):
            if taken[i][w]:
                selected.append(movies[i])
                w -= int(movies[i]["runtime"])
        selected.reverse()

        return dp[T], selected
