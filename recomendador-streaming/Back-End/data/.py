import requests
import pandas as pd
import time

API_KEY = "033294b0e1317e7be237ae20ce59e3d2"
URL_BASE = "https://api.themoviedb.org/3/movie/popular"
URL_GENEROS = "https://api.themoviedb.org/3/genre/movie/list"

base_datos_peliculas = []

print("Obteniendo el catálogo de nombres de géneros desde TMDB...")
params_gen = {"api_key": API_KEY, "language": "es-ES"}
res_generos = requests.get(URL_GENEROS, params=params_gen)
diccionario_generos = {}

if res_generos.status_code == 200:
    lista_generos = res_generos.json().get("genres", [])
    for g in lista_generos:
        diccionario_generos[g["id"]] = g["name"]
    print("  Catálogo de géneros cargado con éxito.\n")
else:
    print(" No se pudieron obtener los nombres de los géneros. Se guardarán los números.")

print("Iniciando la descarga de datos desde TMDB...")

for pagina in range(1, 101):
    time.sleep(0.2)
    parametros = {
        "api_key": API_KEY,
        "language": "es-ES",
        "page": pagina,
    }

    # Realiza la petición HTTP
    respuesta = requests.get(URL_BASE, params=parametros)

    print(f"Probando página {pagina} -> Código de respuesta: {respuesta.status_code}")

    if respuesta.status_code == 200:
        try:
            datos_json = respuesta.json()
            peliculas_pagina = datos_json.get("results", [])

            for peli in peliculas_pagina:
                ids_generos = peli.get("genre_ids") or []
                generos_en_texto = ", ".join(
                    diccionario_generos.get(gid, str(gid)) for gid in ids_generos
                )
                if not generos_en_texto:
                    generos_en_texto = "Sin género especificado"
                base_datos_peliculas.append({
                    "ID": peli.get("id"),
                    "Título Original": peli.get("original_title"),
                    "Título en Español": peli.get("title"),
                    "Género": generos_en_texto,
                    "Fecha de Lanzamiento": peli.get("release_date"),
                    "Calificación Promedio": peli.get("vote_average"),
                    "Total de Votos": peli.get("vote_count"),
                    "Popularidad": peli.get("popularity"),
                    "Sinopsis": peli.get("overview"),
                })
            print(f" -> Página {pagina} procesada correctamente.")
        except Exception as e:
            print(f" [!] Error al procesar el JSON en la página {pagina}: {e}")
            break
    else:
        print(f" [!] El servidor respondió con un error. Código: {respuesta.status_code}")
        print(f" Contenido del error: {respuesta.text[:200]}")
        break

# Transformamos la lista a un DataFrame de Pandas si encontramos datos
if base_datos_peliculas:
    df = pd.DataFrame(base_datos_peliculas)

    # Exportamos la información estructurada a un archivo Excel local
    nombre_archivo = "Base_Datos_TMDB.json"
    df.to_json(nombre_archivo, orient="records", indent=4, force_ascii=False)

    print("\n==================================================")
    print(f"¡PROCESO COMPLETADO EXITOSAMENTE!")
    print(f"Se han guardado {len(base_datos_peliculas)} películas en el archivo: {nombre_archivo}")
    print("==================================================")
else:
    print("\n No se pudo generar la base de datos porque no se obtuvieron registros.")
