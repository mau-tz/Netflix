import json
import os
import re
import statistics
from collections import Counter
from functools import lru_cache
from typing import Optional

DATA_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../../data/Base_Datos_TMDB.json")
)

# Nombres aceptados para la duración (minutos) cuando se agregue al JSON.
RUNTIME_KEYS = ("Duración (min)", "Duración", "Duracion_Minutos", "Duracion", "runtime")
DEFAULT_RUNTIME = 120  # Estimación mientras el dataset no incluya la duración
MAX_RUNTIME = 600
NO_GENRE = "sin género especificado"


def parse_genres(genre_str: str) -> set:
    """Convierte 'Ciencia ficción, Acción' en {'ciencia ficción', 'acción'}."""
    if not genre_str:
        return set()
    genres = {g.strip().lower() for g in genre_str.split(",") if g.strip()}
    genres.discard(NO_GENRE)
    return genres


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def _read_runtime(raw: dict) -> Optional[int]:
    """Devuelve la duración en minutos si el registro la trae, o None."""
    for key in RUNTIME_KEYS:
        value = raw.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            value = int(match.group()) if match else None
        try:
            minutes = int(value)
        except (ValueError, TypeError):
            continue
        if 0 < minutes <= MAX_RUNTIME:
            return minutes
    return None


def _franchise_prefix(title: str) -> Optional[str]:
    if title and ":" in title:
        prefix = title.split(":", 1)[0].strip()
        if len(prefix) >= 3:
            return prefix
    return None


@lru_cache(maxsize=1)
def get_catalog() -> list:
    """
    Carga el JSON una sola vez y lo normaliza: elimina IDs repetidos, convierte tipos,
    resuelve la duración y calcula el rating ponderado (estilo IMDb) y la saga.
    """
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_movies = json.load(f)

    movies, seen = [], set()
    for raw in raw_movies:
        movie_id = raw.get("ID")
        if movie_id is None or movie_id in seen:
            continue
        seen.add(movie_id)

        runtime = _read_runtime(raw)
        title = raw.get("Título en Español") or raw.get("Título Original") or str(movie_id)
        genres_text = raw.get("Género") or ""
        movies.append({
            "id": movie_id,
            "title": title,
            "original_title": raw.get("Título Original") or title,
            "genres": [g.strip() for g in genres_text.split(",") if g.strip()],
            "genre_set": parse_genres(genres_text),
            "rating": _to_float(raw.get("Calificación Promedio")),
            "votes": int(_to_float(raw.get("Total de Votos"))),
            "popularity": _to_float(raw.get("Popularidad")),
            "release_date": raw.get("Fecha de Lanzamiento") or "",
            "runtime": runtime if runtime else DEFAULT_RUNTIME,
            "runtime_estimated": runtime is None,
            "franchise": None,
        })

    # Rating ponderado: WR = v/(v+m)*R + m/(v+m)*C. Evita que una película con 6 votos
    # y nota 8 supere a otra con miles de votos.
    rated = [m for m in movies if m["votes"] > 0]
    if rated:
        mean_rating = statistics.mean(m["rating"] for m in rated)
        min_votes = statistics.median(m["votes"] for m in rated)
    else:
        mean_rating, min_votes = 0.0, 1
    for m in movies:
        v = m["votes"]
        m["weighted_rating"] = round((v * m["rating"] + min_votes * mean_rating) / (v + min_votes), 4)

    # Sagas: prefijo de título antes de ':' compartido por 2 o más películas.
    prefixes = {m["id"]: _franchise_prefix(m["title"]) for m in movies}
    counts = Counter(p.lower() for p in prefixes.values() if p)
    for m in movies:
        prefix = prefixes[m["id"]]
        if prefix and counts[prefix.lower()] >= 2:
            m["franchise"] = prefix
    return movies


@lru_cache(maxsize=1)
def _index() -> dict:
    return {m["id"]: m for m in get_catalog()}


def get_movie(movie_id) -> Optional[dict]:
    return _index().get(movie_id)


def matches_genre(movie: dict, genre: Optional[str]) -> bool:
    return not genre or genre.strip().lower() in movie["genre_set"]


def public_view(movie: dict, **extra) -> dict:
    """Representación JSON de una película (sin estructuras internas como sets)."""
    view = {
        "id": movie["id"],
        "title": movie["title"],
        "rating": movie["rating"],
        "weighted_rating": movie["weighted_rating"],
        "popularity": movie["popularity"],
        "votes": movie["votes"],
        "genres": movie["genres"],
        "release_date": movie["release_date"],
        "runtime": movie["runtime"],
        "runtime_estimated": movie["runtime_estimated"],
        "franchise": movie["franchise"],
    }
    view.update(extra)
    return view
