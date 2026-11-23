"""
Grafo completo del catálogo (las ~20.000 películas) listo para dibujarse en el Front-End.

NO modifica nada existente: solo LEE get_catalog() y reutiliza content_similarity().

Idea:
  - Nodos  = todas las películas con al menos un género.
  - Aristas = cada película se conecta con sus K más parecidas (misma fórmula de similitud
              que usa el resto del proyecto: 70% Jaccard de géneros + 30% cercanía de rating).
  - Posición = cada película cae dentro del "macro-grupo" de su género principal
              (Acción/Sci-Fi, Comedia, Drama/Romance, Terror/Suspenso), un poco atraída
              hacia los grupos de sus otros géneros.

Calcular el kNN con fuerza bruta serían 20.000² = 400 M comparaciones (inviable en Python).
Por eso se agrupan las películas por "firma de géneros" (≈1.400 firmas) y, dentro de cada
firma, se busca por rating con búsqueda binaria. El resultado es EXACTO, no aproximado.
"""
import bisect
import math
import random
from functools import lru_cache

from app.services.catalog import get_catalog
from app.services.similarity import content_similarity

# Macro-grupos (los mismos 4 de la imagen de referencia) y qué géneros caen en cada uno.
GROUPS = [
    {"id": 0, "name": "Acción/Sci-Fi",
     "genres": ["acción", "aventura", "ciencia ficción", "fantasía", "bélica", "western"]},
    {"id": 1, "name": "Comedia",
     "genres": ["comedia", "animación", "familia"]},
    {"id": 2, "name": "Drama/Romance",
     "genres": ["drama", "romance", "historia", "música", "documental", "película de tv"]},
    {"id": 3, "name": "Terror/Suspenso",
     "genres": ["terror", "suspense", "misterio", "crimen"]},
]
_GENRE_TO_GROUP = {g: grp["id"] for grp in GROUPS for g in grp["genres"]}

# Centro (x, y) y radios (rx, ry) de cada nube, en un lienzo de 1000 x 580.
_LAYOUT = {
    0: (790, 262, 150, 82),   # Acción/Sci-Fi   (derecha)
    1: (650, 480, 135, 88),   # Comedia         (abajo)
    2: (235, 395, 175, 72),   # Drama/Romance   (izquierda)
    3: (285, 170, 150, 76),   # Terror/Suspenso (arriba-izquierda)
}
WORLD_W, WORLD_H = 1000, 580


def _group_of(genres: list, genre_set: set) -> int:
    """Grupo del género principal (el primero listado); si no encaja, el primero que sí."""
    for g in genres:
        gid = _GENRE_TO_GROUP.get(g.lower())
        if gid is not None:
            return gid
    for g in genre_set:
        gid = _GENRE_TO_GROUP.get(g)
        if gid is not None:
            return gid
    return 2


def _position(movie: dict, group: int, rnd: random.Random) -> tuple:
    cx, cy, rx, ry = _LAYOUT[group]
    # Punto uniforme dentro de la elipse, con borde suave.
    angle = rnd.random() * math.tau
    radius = math.sqrt(rnd.random()) * (0.92 + 0.08 * rnd.random())
    x = cx + math.cos(angle) * radius * rx
    y = cy + math.sin(angle) * radius * ry

    # Atracción hacia los otros grupos según la mezcla de géneros de la película.
    shares = {}
    for g in movie["genre_set"]:
        gid = _GENRE_TO_GROUP.get(g)
        if gid is not None and gid != group:
            shares[gid] = shares.get(gid, 0) + 1
    if shares:
        total = len(movie["genre_set"])
        for gid, count in shares.items():
            weight = 0.22 * count / total
            x += (_LAYOUT[gid][0] - cx) * weight
            y += (_LAYOUT[gid][1] - cy) * weight
    return round(x, 1), round(y, 1)


def _bucket_neighbors(signatures: list) -> list:
    """Para cada firma de géneros: las demás firmas con géneros en común, de mayor a menor Jaccard."""
    result = []
    for a in signatures:
        row = []
        for index, b in enumerate(signatures):
            inter = len(a & b)
            if inter:
                row.append((inter / len(a | b), index))
        row.sort(reverse=True)
        result.append(row)
    return result


def _knn_edges(movies: list, k: int) -> list:
    """Aristas no dirigidas (i, j) con i < j entre cada película y sus K más parecidas."""
    # 1) Agrupar por firma de géneros y ordenar cada grupo por rating.
    sig_index, signatures, members = {}, [], []
    movie_sig = []
    for i, m in enumerate(movies):
        key = frozenset(m["genre_set"])
        if key not in sig_index:
            sig_index[key] = len(signatures)
            signatures.append(key)
            members.append([])
        movie_sig.append(sig_index[key])
        members[sig_index[key]].append(i)
    for lst in members:
        lst.sort(key=lambda i: movies[i]["rating"])
    ratings = [[movies[i]["rating"] for i in lst] for lst in members]
    neighbors = _bucket_neighbors(signatures)

    edges = set()
    for i, a in enumerate(movies):
        ra = a["rating"]
        best = []  # (score, j), se mantiene ordenada de mayor a menor y de tamaño <= k
        for jac, b in neighbors[movie_sig[i]]:
            # Cota superior de cualquier película de esta firma: si ya no puede ganar, se corta.
            if len(best) == k and 0.7 * jac + 0.3 <= best[-1][0]:
                break
            lst, rts = members[b], ratings[b]
            pos = bisect.bisect_left(rts, ra)
            lo, hi, taken = pos - 1, pos, 0
            while taken < k + 1 and (lo >= 0 or hi < len(lst)):
                # Elegir el candidato de rating más cercano a cada lado.
                if hi >= len(lst) or (lo >= 0 and ra - rts[lo] <= rts[hi] - ra):
                    j, lo = lst[lo], lo - 1
                else:
                    j, hi = lst[hi], hi + 1
                taken += 1
                if j == i:
                    continue
                score = 0.7 * jac + 0.3 * (1 - min(abs(ra - movies[j]["rating"]), 10) / 10)
                if len(best) < k or score > best[-1][0]:
                    best.append((score, j))
                    best.sort(reverse=True)
                    del best[k:]
        for _, j in best:
            edges.add((i, j) if i < j else (j, i))
    return sorted(edges)


@lru_cache(maxsize=4)
def build_overview(k: int = 3) -> dict:
    """Se calcula una sola vez por valor de k y queda en memoria."""
    movies = [m for m in get_catalog() if m["genre_set"]]
    rnd = random.Random(42)  # semilla fija: el dibujo es siempre el mismo

    groups_of, xs, ys = [], [], []
    for m in movies:
        gid = _group_of(m["genres"], m["genre_set"])
        x, y = _position(m, gid, rnd)
        groups_of.append(gid)
        xs.append(x)
        ys.append(y)

    edges = _knn_edges(movies, k)
    flat = []
    cross = 0
    for i, j in edges:
        flat.extend((i, j))
        if groups_of[i] != groups_of[j]:
            cross += 1

    counts = [0] * len(GROUPS)
    for gid in groups_of:
        counts[gid] += 1

    return {
        "world": {"width": WORLD_W, "height": WORLD_H},
        "k": k,
        "total_nodes": len(movies),
        "total_edges": len(edges),
        "cross_group_edges": cross,
        "groups": [{"id": g["id"], "name": g["name"], "count": counts[g["id"]]} for g in GROUPS],
        # Formato por columnas (más liviano que una lista de objetos).
        "ids": [m["id"] for m in movies],
        "titles": [m["title"] for m in movies],
        "ratings": [m["rating"] for m in movies],
        "x": xs,
        "y": ys,
        "group": groups_of,
        "edges": flat,  # [a0, b0, a1, b1, ...] con índices sobre las columnas de arriba
    }
