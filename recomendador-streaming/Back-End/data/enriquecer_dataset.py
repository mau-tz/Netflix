"""
Agrega al dataset los campos que faltan consultando el detalle de cada película en TMDB:
  - "Duración (min)"  -> runtime (lo usan /marathon, /filter-backtracking, /top-k y /catalog)
  - "Colección"       -> belongs_to_collection.name (mejora /watch-order y el orden de /marathon)
  - "Póster"          -> poster_path (para el front-end)
  - "Idioma Original" -> original_language

Uso (la API key se lee de Back-End/.env o de la variable de entorno TMDB_API_KEY):
    cp .env.example .env     # y escribe tu key en .env (el archivo está en .gitignore)
    python3 data/enriquecer_dataset.py

Lee Base_Datos_TMDB.json y escribe Base_Datos_TMDB_enriquecido.json (no pisa el original).
Es reanudable: guarda el progreso en .cache_tmdb.json, así que si se corta puedes volver a correrlo.
"""
import json
import os
import sys
import time

import requests

CARPETA = os.path.dirname(os.path.abspath(__file__))
ENTRADA = os.path.join(CARPETA, "Base_Datos_TMDB.json")
SALIDA = os.path.join(CARPETA, "Base_Datos_TMDB_enriquecido.json")
CACHE = os.path.join(CARPETA, ".cache_tmdb.json")
ENV_FILE = os.path.join(CARPETA, "..", ".env")
URL = "https://api.themoviedb.org/3/movie/{}"


def cargar_env(ruta):
    """Lee líneas CLAVE=valor de un .env y las agrega al entorno (sin pisar las ya definidas)."""
    if not os.path.exists(ruta):
        return
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                os.environ.setdefault(clave.strip(), valor.strip().strip("\"'"))


def main():
    cargar_env(ENV_FILE)
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        sys.exit("Falta TMDB_API_KEY: créala en Back-End/.env (ver .env.example) o exporta la variable.")

    with open(ENTRADA, "r", encoding="utf-8") as f:
        peliculas = json.load(f)

    cache = {}
    if os.path.exists(CACHE):
        with open(CACHE, "r", encoding="utf-8") as f:
            cache = json.load(f)

    sesion = requests.Session()
    for i, peli in enumerate(peliculas, start=1):
        clave = str(peli["ID"])
        if clave not in cache:
            respuesta = sesion.get(URL.format(peli["ID"]), params={"api_key": api_key, "language": "es-ES"})
            if respuesta.status_code == 429:  # límite de peticiones: esperar y reintentar una vez
                time.sleep(int(respuesta.headers.get("Retry-After", 5)))
                respuesta = sesion.get(URL.format(peli["ID"]), params={"api_key": api_key, "language": "es-ES"})
            if respuesta.status_code == 200:
                d = respuesta.json()
                cache[clave] = {
                    "Duración (min)": d.get("runtime") or None,
                    "Colección": (d.get("belongs_to_collection") or {}).get("name"),
                    "Póster": d.get("poster_path"),
                    "Idioma Original": d.get("original_language"),
                }
            else:
                print(f"  ID {peli['ID']}: HTTP {respuesta.status_code}, se deja sin datos nuevos")
                cache[clave] = {}
            time.sleep(0.05)
            if i % 50 == 0:
                with open(CACHE, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False)
                print(f"{i}/{len(peliculas)} procesadas")
        peli.update(cache[clave])

    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(peliculas, f, ensure_ascii=False, indent=4)

    con_duracion = sum(1 for p in peliculas if p.get("Duración (min)"))
    print(f"Listo: {SALIDA}\nCon duración: {con_duracion}/{len(peliculas)}")


if __name__ == "__main__":
    main()
