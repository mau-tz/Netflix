# Front-End · Netflix

React + Vite. Consume el back-end FastAPI (por defecto `http://localhost:8000`).

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # genera dist/
```

Para apuntar a otro servidor: `cp .env.example .env` y cambia `VITE_API_URL`.

## Estructura
- `src/services/api.js` — una función por endpoint.
- `src/hooks/useRequest.js` — peticiones cancelables y con debounce.
- `src/components/` — tarjetas, modal de detalle, buscador de películas, gráficos SVG.
- `src/views/` — una vista por grupo de endpoints (ver `src/App.jsx`).
