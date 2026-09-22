class PreferenceBacktracking:
    def __init__(self):
        self.operation_count = 0

    def find_movie_combinations(self, movies: list, target_duration: int, min_rating: float, max_movies: int) -> list:
        """
        Encuentra todas las combinaciones válidas de películas que suman aproximadamente 'target_duration'
        cumpliendo restricciones de rating mediante Backtracking.
        """
        self.operation_count = 0
        results = []

        def backtrack(start_index, current_combo, current_duration):
            self.operation_count += 1
            
            # Condición de parada / solución válida
            if len(current_combo) == max_movies:
                if current_duration <= target_duration:
                    results.append(list(current_combo))
                return

            if current_duration > target_duration:
                return  # Poda (Pruning)

            for i in range(start_index, len(movies)):
                movie = movies[i]
                if movie.get('rating', 0) >= min_rating:
                    current_combo.append(movie)
                    backtrack(i + 1, current_combo, current_duration + movie.get('runtime', 0))
                    current_combo.pop()  # Backtrack

        backtrack(0, [], 0)
        return results