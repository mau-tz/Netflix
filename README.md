# Recomendador de Contenido Streaming (Estilo Netflix)

> **Curso:** Complejidad Algorítmica  
> **Proyecto:** Sistema de Recomendación y Análisis de Grafos en Tiempo Real  
> **Universidad:** Universidad Peruana de Ciencias Aplicadas (UPC)

---

## Integrantes del Equipo

* **Joaquin Daniel Carneiro Zevallos** — `u202317018`
* **Tamara Mia Guzman Uriarte** — `u202411366`
* **Cristina Marcela Yarleque Ruiz** — `u20241f859`
* **Mauricio Alejandro Teran Zavala** — `u202417423`

---

## Descripción del Proyecto

Dado un conjunto de usuarios y sus calificaciones sobre películas o series, el sistema construye un grafo de interacción y ejecuta algoritmos avanzados para:
1. Recomendar contenido relevante según afinidad y proximidad.
2. Detectar comunidades de usuarios con gustos similares mediante componentes fuertemente conexas y agrupamiento.
3. Optimizar sugerencias en tiempo real comparando enfoques de **Fuerza Bruta**, **Grafos**, **Algoritmos Voraces** y **Programación Dinámica**.
4. Evaluar la complejidad algorítmica ($O$, $\Omega$, $\Theta$) midiendo empíricamente el tiempo de ejecución, uso de memoria y número de operaciones.

---

## Estructura del Proyecto

El proyecto está organizado bajo la estructura de un **Monorepo** que separa claramente la capa de algoritmos (Backend) de la interfaz interactiva (Frontend):

```text
recomendador-streaming/
├── backend/                        # Motor Algorítmico y API REST (FastAPI)
│   ├── app/
│   │   ├── api/                    # Endpoints del Servidor
│   │   │   ├── routes_recommend.py # Solicitudes de recomendación y comunidades
│   │   │   └── routes_metrics.py   # Benchmark (Tiempos ms, Memoria MB, Ops)
│   │   │
│   │   ├── algorithms/             # IMPLEMENTACIÓN DE ALGORITMOS (CORE)
│   │   │   ├── brute_force.py      # Fuerza Bruta (Comparar usuarios)
│   │   │   ├── backtracking.py     # Backtracking (Combinaciones de preferencias)
│   │   │   ├── graphs.py           # BFS (Cercanas), SCC (Tarjan/Kosaraju - Comunidades)
│   │   │   ├── max_flow.py         # Flujo Máximo (Edmonds-Karp / Dinic - Asignación)
│   │   │   ├── greedy.py           # Voraces (Recomendaciones rápidas Top-K)
│   │   │   ├── dynamic_prog.py     # DP (Sistemas recomendadores) y DP en Grafos (Rutas)
│   │   │   └── mst_clustering.py   # MST (Kruskal/Prim) y UFDS (Disjoint-Set Clustering)
│   │   │
│   │   ├── services/               # NUEVO: Servicios externos y ETL
│   │   │   └── tmdb_client.py      # Extracción y parsing de datos de la API de TMDB
│   │   │
│   │   ├── models/                 # Modelos de Datos
│   │   │   ├── graph.py            # Representación de Grafo (Listas/Matrices adyacencia)
│   │   │   └── user_movie.py       # Pydantic models (Usuario, Película, Calificación)
│   │   │
│   │   └── utils/                  # Herramientas de Medición
│   │       ├── benchmark.py        # Medidores de tiempo (perf_counter), memoria (tracemalloc)
│   │       └── metrics_exporter.py # Generador de datos comparativos (CSV/JSON de métricas)
│   │
│   ├── data/                       # Datasets
│   │   ├── raw_tmdb.json           # Datos crudos de la API TMDB
│   │   └── processed_graph.json    # Grafo de usuarios/películas procesado
│   │
│   ├── main.py                     # Entry point de FastAPI
│   └── requirements.txt            # fastAPI, uvicorn, requests, networkx, pydantic, etc.
│
├── frontend/                       # Interfaz Web e Historial (React / Vue / Svelte)
│   ├── src/
│   │   ├── components/
│   │   │   ├── GraphVisualizer.jsx # Visualizador interactivo (Vis.js / Cytoscape)
│   │   │   ├── BenchmarkChart.jsx  # Gráficas de rendimiento (Chart.js / Recharts)
│   │   │   └── MovieCard.jsx       # Tarjetas de películas recomendadas
│   │   ├── views/
│   │   │   ├── Dashboard.jsx       # Panel principal de usuario
│   │   │   ├── GraphView.jsx       # Vista de comunidades y grafos
│   │   │   └── BenchmarkView.jsx   # Vista de comparación de complejidad algorítmica
│   │   └── services/
│   │       └── api.js              # Cliente Axios/Fetch para backend
│   └── package.json
└── README.md