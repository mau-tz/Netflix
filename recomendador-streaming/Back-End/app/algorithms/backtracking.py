class PreferenceBacktracking:
    def __init__(self):
        self.operation_count = 0

    def find_movie_combinations(self, movies: list, min_rating: float, max_movies: int) -> list:
        """
        Encuentra todas las combinaciones válidas de 'max_movies' películas
        que superan el 'min_rating' utilizando Backtracking con Poda.
        """
        self.operation_count = 0
        results = []

        def backtrack(start_index, current_combo):
            self.operation_count += 1
            
            # Condición de éxito: alcanzamos el número exacto de películas deseado
            if len(current_combo) == max_movies:
                results.append(list(current_combo))
                return

            for i in range(start_index, len(movies)):
                movie = movies[i]
                
                # Conversión segura de rating
                try:
                    movie_rating = float(movie.get('rating') or 0.0)
                except (ValueError, TypeError):
                    continue

                # Poda (Pruning): Si la película no cumple el rating mínimo, no se explora esa rama
                if movie_rating >= float(min_rating):
                    current_combo.append(movie)
                    backtrack(i + 1, current_combo)
                    current_combo.pop()  # Backtrack

        backtrack(0, [])
        return results