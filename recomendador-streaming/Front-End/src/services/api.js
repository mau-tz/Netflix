// Un único punto de contacto con el back-end FastAPI. Cada función = un endpoint.
const BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

function buildQuery(params = {}) {
  const qs = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue
    if (Array.isArray(value)) value.forEach((v) => qs.append(key, v))
    else qs.append(key, value)
  }
  const text = qs.toString()
  return text ? `?${text}` : ''
}

async function request(path, { params, method = 'GET', body, signal } = {}) {
  let response
  try {
    response = await fetch(`${BASE}${path}${buildQuery(params)}`, {
      method,
      signal,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    })
  } catch (err) {
    if (err.name === 'AbortError') throw err
    throw new Error(`No se pudo conectar con el servidor (${BASE}). ¿Está encendido el back-end?`)
  }
  if (!response.ok) {
    let detail = `Error ${response.status}`
    try {
      const data = await response.json()
      if (typeof data.detail === 'string') detail = data.detail
      else if (Array.isArray(data.detail)) detail = data.detail.map((d) => `${d.loc?.slice(-1)}: ${d.msg}`).join(' · ')
    } catch { /* cuerpo no JSON */ }
    throw new Error(detail)
  }
  return response.json()
}

export const api = {
  // Voraz
  topK: (params, signal) => request('/recommend/top-k', { params, signal }),
  // Divide y Vencerás
  catalog: (params, signal) => request('/recommend/catalog', { params, signal }),
  // Fuerza Bruta
  similar: (params, signal) => request('/recommend/similar', { params, signal }),
  // BFS
  related: (movieId, params, signal) => request(`/recommend/related/${movieId}`, { params, signal }),
  // Programación Dinámica (+ topológico)
  marathon: (params, signal) => request('/recommend/marathon', { params, signal }),
  // Backtracking
  backtracking: (params, signal) => request('/recommend/filter-backtracking', { params, signal }),
  // Ordenamiento topológico
  watchOrder: (params, signal) => request('/recommend/watch-order', { params, signal }),
  // Tarjan / UFDS
  communities: (params, signal) => request('/recommend/communities', { params, signal }),
  // Kruskal
  clustersMst: (params, signal) => request('/recommend/clusters-mst', { params, signal }),
  // Bellman-Ford
  discoveryPath: (params, signal) => request('/recommend/discovery-path', { params, signal }),
  // Floyd-Warshall
  hubs: (params, signal) => request('/recommend/hubs', { params, signal }),
  // Flujo máximo
  allocate: (body, signal) => request('/recommend/allocate', { method: 'POST', body, signal }),
  // Benchmark
  compare: (params, signal) => request('/metrics/compare', { params, signal }),
  scaling: (params, signal) => request('/metrics/scaling', { params, signal }),
}

export const GENRES = [
  'Acción', 'Aventura', 'Animación', 'Comedia', 'Crimen', 'Documental', 'Drama', 'Familia',
  'Fantasía', 'Historia', 'Terror', 'Música', 'Misterio', 'Romance', 'Ciencia ficción',
  'Suspense', 'Bélica', 'Western',
]
