from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_recommend import router as recommend_router
from app.api.routes_metrics import router as metrics_router

app = FastAPI(
    title="Motor Algorítmico Recomendador de Streaming",
    description="API REST para recomendación de películas basada en Grafos, Voraces, DP y Benchmarking Asintótico.",
    version="1.0.0"
)

# Permitir peticiones desde el Frontend React/Vue (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(recommend_router)
app.include_router(metrics_router)

@app.get("/")
def root():
    return {
        "message": "API del Recomendador de Streaming Operativa",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)