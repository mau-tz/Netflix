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
├── backend/                        # Motor Algorítmico y API REST
│   ├── app/
│   │   ├── api/                    # Rutas y Controladores de la API
│   │   │   ├── routes_recommend.py # Endpoints para solicitudes de recomendación
│   │   │   └── routes_metrics.py   # Endpoints para benchmarking de complejidad
│   │   ├── algorithms/             # IMPLEMENTACIÓN CORE DE ALGORITMOS
│   │   │   ├── brute_force.py      # Fuerza Bruta y Backtracking
│   │   │   ├── graphs.py           # BFS, SCC (Tarjan / Kosaraju), Flujo Máximo
│   │   │   ├── greedy.py           # Algoritmos Voraces (Top-K)
│   │   │   ├── dynamic_prog.py     # Programación Dinámica y DP en Grafos
│   │   │   └── mst_clustering.py   # Prim / Kruskal y Disjoint-Set (UFDS)
│   │   ├── models/                 # Estructuras de datos (Grafo, Nodos, Aristas)
│   │   └── utils/                  # Medidores de tiempo, uso de memoria y profiler
│   ├── data/                       # Datasets sintéticos y reales (JSON / CSV)
│   ├── main.py                     # Punto de entrada del servidor (FastAPI / Flask)
│   └── requirements.txt            # Dependencias del Backend
│
├── frontend/                       # Interfaz Web e Historial
│   ├── src/
│   │   ├── components/             # Visualizador de Grafos (Vis.js / D3.js / Cytoscape)
│   │   ├── views/                  # Vistas principales (Panel, Grafos, Benchmark)
│   │   └── services/               # Cliente HTTP (Axios / Fetch)
│   └── package.json
└── README.md