"""
Descarga el catálogo base de películas populares de TMDB (100 páginas x 20 = 2000 películas)
y lo guarda en Base_Datos_TMDB.json. Después, enriquecer_dataset.py le agrega la duración y más campos.

La API key se lee de Back-End/.env (TMDB_API_KEY) o de la variable de entorno.
    python3 data/descargar_dataset.py
"""
import json
import os
import sys
import time

import requests

from enriquecer_dataset import CARPETA, ENV_FILE, cargar_env

URL_BASE = "https://api.themoviedb.org/3/movie/popular"
URL_GENEROS = "https://api.themoviedb.org/3/genre/movie/list"
SALIDA = os.path.join(CARPETA, "Base_Datos_TMDB.json")
PAGINAS = 100


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
    for pagina in range(1, PAGINAS + 1):
        time.sleep(0.2)
        respuesta = requests.get(URL_BASE, params={"api_key": api_key, "language": "es-ES", "page": pagina})
        print(f"Página {pagina} -> Código de respuesta: {respuesta.status_code}")

        if respuesta.status_code != 200:
            print(f"El servidor respondió con un error. Contenido: {respuesta.text[:200]}")
            break

        try:
            for peli in respuesta.json().get("results", []):
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
        except Exception as e:
            print(f"Error al procesar el JSON en la página {pagina}: {e}")
            break

    if not peliculas:
        sys.exit("No se pudo generar la base de datos porque no se obtuvieron registros.")

    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(peliculas, f, ensure_ascii=False, indent=4)
    print(f"\nSe guardaron {len(peliculas)} películas en: {SALIDA}")


if __name__ == "__main__":
    main()
