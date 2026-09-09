# Netflix

**Project Structure:**

recomendador-streaming/
├── backend/                  # API Rest / Algoritmos (Python/FastAPI o Java/Spring Boot)
│   ├── app/
│   │   ├── api/              # Endpoints para el Frontend
│   │   ├── algorithms/       # CÓDIGO CORE DE COMPLEJIDAD
│   │   ├── models/           # Definición de Grafos, Nodos, Usuarios, Películas
│   │   ├── services/         # Coordinación entre algoritmos y dataset
│   │   └── utils/            # Medición de tiempos, memoria y generadores de datos
│   ├── data/                 # Datasets (JSON/CSV o Scripts de generación masiva)
│   ├── main.py               # Punto de entrada del API
│   └── requirements.txt
│
└── frontend/                 # Interfaz visual (Vue.js, React o HTML/JS)
    ├── src/
    │   ├── components/       # Componentes visuales (Lienzo del Grafo, Métricas)
    │   ├── views/            # Vistas principales (Recomendaciones, Comparativa)
    │   └── services/         # Cliente HTTP (Axios/Fetch para conectar con Backend)
    └── package.json