import requests
import pandas as pd
import time

# =====================================================================
# CONFIGURACIÓN: Reemplaza con tu API Key corta (32 caracteres)
# =====================================================================
API_KEY = "033294b0e1317e7be237ae20ce59e3d2" 

URL_BASE = "https://api.themoviedb.org/3/movie/popular"

# Lista vacía donde acumularemos los registros de las películas
base_datos_peliculas = []

print("Iniciando la descarga de datos desde TMDB...")

# Descarga 5 páginas (100 películas en total)
for pagina in range(1, 76):
    time.sleep(0.5) 
    parametros = {
        "api_key": API_KEY,  # Enviamos la clave como parámetro directo
        "language": "es-ES", 
        "page": pagina
    }
    
    # Realiza la petición HTTP
    respuesta = requests.get(URL_BASE, params=parametros)
    
    print(f"Probando página {pagina} -> Código de respuesta: {respuesta.status_code}")
    
    if respuesta.status_code == 200:
        try:
            datos_json = respuesta.json()
            peliculas_pagina = datos_json.get("results", [])
            
            for peli in peliculas_pagina:
                base_datos_peliculas.append({
                    "ID": peli.get("id"),
                    "Título Original": peli.get("original_title"),
                    "Título en Español": peli.get("title"),
                    "Fecha de Lanzamiento": peli.get("release_date"),
                    "Calificación Promedio": peli.get("vote_average"),
                    "Total de Votos": peli.get("vote_count"),
                    "Popularidad": peli.get("popularity"),
                    "Sinopsis": peli.get("overview")
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
    nombre_archivo = "Base_Datos_TMDB.xlsx"
    df.to_excel(nombre_archivo, index=False)
    
    print("\n==================================================")
    print(f"¡PROCESO COMPLETADO EXITOSAMENTE!")
    print(f"Se han guardado {len(base_datos_peliculas)} películas en el archivo: {nombre_archivo}")
    print("==================================================")
else:
    print("\n No se pudo generar la base de datos porque no se obtuvieron registros.")
