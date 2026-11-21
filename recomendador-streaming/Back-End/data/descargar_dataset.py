"""
Descarga el catálogo base de películas de TMDB y lo guarda en Base_Datos_TMDB.json.
Después, enriquecer_dataset.py le agrega la duración y más campos.

TMDB limita cada consulta a 500 páginas (10 000 películas), así que para llegar a ~20 000
se consulta /discover/movie año por año (de más reciente a más antiguo), tomando las más
populares de cada año que tengan un mínimo de votos. Las repetidas se descartan por ID.
Ajusta META, PAGINAS_POR_ANIO, ANIO_INICIO y ANIO_FIN para cambiar el tamaño.

La API key se lee de Back-End/.env (TMDB_API_KEY) o de la variable de entorno.
    python3 data/descargar_dataset.py
"""
import json
import os
import sys
import time
from datetime import date

import requests

from enriquecer_dataset import CARPETA, ENV_FILE, cargar_env

URL_BASE = "https://api.themoviedb.org/3/discover/movie"
URL_GENEROS = "https://api.themoviedb.org/3/genre/movie/list"
SALIDA = os.path.join(CARPETA, "Base_Datos_TMDB.json")
META = 20000            # se detiene al llegar a esta cantidad de películas
PAGINAS_POR_ANIO = 20   # 20 películas por página -> hasta 400 por año
ANIO_FIN = date.today().year + 1   # incluye el año actual y los estrenos anunciados del próximo
ANIO_INICIO = 1960
MIN_VOTOS = 50          # descarta películas casi sin votos (su calificación no es confiable)


def main():
    cargar_env(ENV_FILE)
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        sys.exit("Falta TMDB_API_KEY: créala en Back-End/.env (ver .env.example) o exporta la variable.")

    print("Obteniendo el catálogo de nombres de géneros desde TMDB...")
    res_generos = requests.get(URL_GENEROS, params={"api_key": api_key, "language": "es-ES"})
    generos = {}
    if res_generos.status_code == 200:
        generos = {g["id"]: g["name"] for g in res_generos.json().get("genres", [])}
        print("  Catálogo de géneros cargado con éxito.\n")
    else:
        print(" No se pudieron obtener los nombres de los géneros. Se guardarán los números.")

    peliculas = []
    vistos = set()
    sesion = requests.Session()
    for anio in range(ANIO_FIN, ANIO_INICIO - 1, -1):
        if len(peliculas) >= META:
            break
        nuevas = 0
        for pagina in range(1, PAGINAS_POR_ANIO + 1):
            params = {
                "api_key": api_key, "language": "es-ES", "page": pagina,
                "sort_by": "popularity.desc", "primary_release_year": anio,
                "vote_count.gte": MIN_VOTOS, "include_adult": "false",
            }
            respuesta = sesion.get(URL_BASE, params=params)
            if respuesta.status_code == 429:  # límite de peticiones: esperar y reintentar
                time.sleep(int(respuesta.headers.get("Retry-After", 5)))
                respuesta = sesion.get(URL_BASE, params=params)
            if respuesta.status_code != 200:
                print(f"  {anio} p.{pagina}: HTTP {respuesta.status_code} {respuesta.text[:120]}")
                break
            datos = respuesta.json()
            for peli in datos.get("results", []):
                if peli.get("id") in vistos:
                    continue
                vistos.add(peli.get("id"))
                nuevas += 1
                texto_generos = ", ".join(generos.get(g, str(g)) for g in (peli.get("genre_ids") or []))
                peliculas.append({
                    "ID": peli.get("id"),
                    "Título Original": peli.get("original_title"),
                    "Título en Español": peli.get("title"),
                    "Género": texto_generos or "Sin género especificado",
                    "Fecha de Lanzamiento": peli.get("release_date"),
                    "Calificación Promedio": peli.get("vote_average"),
                    "Total de Votos": peli.get("vote_count"),
                    "Popularidad": peli.get("popularity"),
                    "Sinopsis": peli.get("overview"),
                })
            if pagina >= datos.get("total_pages", 1) or len(peliculas) >= META:
                break
            time.sleep(0.05)
        print(f"Año {anio}: +{nuevas} (total {len(peliculas)})")

    peliculas = peliculas[:META]

    if not peliculas:
        sys.exit("No se pudo generar la base de datos porque no se obtuvieron registros.")

    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(peliculas, f, ensure_ascii=False, indent=4)
    print(f"\nSe guardaron {len(peliculas)} películas en: {SALIDA}")


if __name__ == "__main__":
    main()
