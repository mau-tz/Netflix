class PreferenceBacktracking:
    def __init__(self):
        self.operation_count = 0
        self.truncated = False

    def find_movie_combinations(
        self,
        movies: list,
        min_rating: float,
        max_movies: int,
        max_total_minutes: int = None,
        max_results: int = 200,
    ) -> list:
        """
        Backtracking con poda + orden voraz.
        Encuentra combinaciones de exactamente 'max_movies' películas donde:
          - cada película tiene rating >= min_rating,
          - (opcional) la duración total <= max_total_minutes.
        Técnica adicional (Voraz): los candidatos se ordenan por rating descendente, de modo
        que las primeras combinaciones encontradas son las mejores y se puede cortar la
        búsqueda en 'max_results' sin explorar las C(n, k) combinaciones completas.
        Poda: (1) rating mínimo, (2) no quedan suficientes candidatos, (3) el tiempo ya no
        alcanza ni con las películas más cortas.
        """
        self.operation_count = 0
        self.truncated = False
        results = []

        candidates = []
        for movie in movies:
            self.operation_count += 1
            try:
                rating = float(movie.get("rating") or 0.0)
            except (ValueError, TypeError):
                continue
            if rating >= float(min_rating):
                candidates.append(movie)
        candidates.sort(key=lambda m: float(m.get("rating") or 0.0), reverse=True)

        n = len(candidates)
        runtimes = [int(m.get("runtime") or 0) for m in candidates]
        # shortest[i][r] sería costoso; usamos la duración mínima global del sufijo
        suffix_min = [0] * (n + 1)
        suffix_min[n] = float("inf")
        for i in range(n - 1, -1, -1):
            suffix_min[i] = min(runtimes[i], suffix_min[i + 1])

        def backtrack(start, combo, total_minutes):
            if self.truncated:
                return
            self.operation_count += 1

            if len(combo) == max_movies:
                results.append(list(combo))
                if len(results) >= max_results:
                    self.truncated = True
                return

            needed = max_movies - len(combo)
            for i in range(start, n):
                # Poda: ya no quedan suficientes películas para completar la combinación
                if n - i < needed:
                    break
                # Poda: ni con las películas más cortas restantes alcanza el tiempo
                if max_total_minutes is not None and total_minutes + needed * suffix_min[i] > max_total_minutes:
                    break
                if max_total_minutes is not None and total_minutes + runtimes[i] > max_total_minutes:
                    continue

                combo.append(candidates[i])
                backtrack(i + 1, combo, total_minutes + runtimes[i])
                combo.pop()  # Backtrack
                if self.truncated:
                    return

        backtrack(0, [], 0)
        return results
