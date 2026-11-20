import { useState } from 'react'
import { api } from '../services/api'
import { useRequest } from '../hooks/useRequest'
import { Advanced, Empty, ErrorBox, GenreSelect, Loader, PageHead, Slider, Tabs } from '../components/ui'
import MovieCard, { Poster } from '../components/MovieCard'
import MoviePicker from '../components/MoviePicker'
import { useMovieModal } from '../components/MovieModal'

export default function Discover() {
  const [tab, setTab] = useState('related')
  return (
    <>
      <PageHead title="Conexiones entre películas">
        Las películas se conectan entre sí según sus géneros y calificación. Recorre esas conexiones de tres maneras.
      </PageHead>
      <Tabs value={tab} onChange={setTab} tabs={[
        { value: 'related', label: 'Relacionadas' },
        { value: 'path', label: 'Ruta de descubrimiento' },
        { value: 'hubs', label: 'Películas centrales' },
      ]} />
      {tab === 'related' && <Related />}
      {tab === 'path' && <PathFinder />}
      {tab === 'hubs' && <Hubs />}
    </>
  )
}

function Related() {
  const [movie, setMovie] = useState(null)
  const [depth, setDepth] = useState(2)
  const [neighbors, setNeighbors] = useState(4)
  const { data, loading, error } = useRequest(
    (signal) => (movie ? api.related(movie.id, { depth, neighbors }, signal) : Promise.resolve(null)), [movie?.id, depth, neighbors])
  const levels = data ? Array.from({ length: depth }, (_, i) => data.related.filter((r) => r.hops === i + 1)) : []

  return (
    <>
      <p style={{ color: 'var(--muted)', maxWidth: '75ch' }}>Parte de una película y explora por niveles: a 1 salto están las más parecidas; a 2, las parecidas de esas, y así.</p>
      <div className="controls">
        <div className="field" style={{ flex: '1 1 280px' }}><label>Película de partida</label><MoviePicker single value={movie} onChange={setMovie} /></div>
        <Slider label="Saltos máximos" value={depth} min={1} max={4} onChange={setDepth} width={160} />
        <Slider label="Vecinas por película" value={neighbors} min={1} max={8} onChange={setNeighbors} width={170} />
      </div>
      <ErrorBox message={error} />
      {!movie && <Empty>Elige una película para explorar su vecindario.</Empty>}
      {movie && loading && !data && <Loader text="Buscando películas relacionadas…" />}
      {data && (
        <div className={loading ? 'loading-dim' : ''}>
          {levels.map((items, i) => items.length > 0 && (
            <div key={i}>
              <div className="hop-title">{i + 1} {i === 0 ? 'salto' : 'saltos'} · {items.length} películas</div>
              <div className="grid">{items.map((m) => <MovieCard key={m.id} movie={m} corner={`${Math.round(m.similarity_to_seed * 100)}%`} />)}</div>
            </div>
          ))}
          {!data.related.length && <Empty>Esta película no tiene vecinas en el grafo.</Empty>}
        </div>
      )}
    </>
  )
}

function PathFinder() {
  const [from, setFrom] = useState(null)
  const [to, setTo] = useState(null)
  const [minSim, setMinSim] = useState(0.4)
  const [pool, setPool] = useState(60)
  const { open } = useMovieModal()
  const req = useRequest((signal) => api.discoveryPath({ from_id: from.id, to_id: to.id, min_similarity: minSim, pool }, signal), [], false)

  return (
    <>
      <p style={{ color: 'var(--muted)', maxWidth: '75ch' }}>Encuentra la cadena de títulos más «suave» entre dos películas: cada paso cambia lo mínimo posible. Útil para ampliar tus gustos poco a poco.</p>
      <div className="controls">
        <div className="field" style={{ flex: '1 1 260px' }}><label>Desde</label><MoviePicker single value={from} onChange={setFrom} placeholder="Una película que ya viste…" /></div>
        <div className="field" style={{ flex: '1 1 260px' }}><label>Hasta</label><MoviePicker single value={to} onChange={setTo} placeholder="Una que quieres descubrir…" /></div>
        <button className="btn" disabled={!from || !to || req.loading} onClick={req.run}>Buscar ruta</button>
      </div>
      <Advanced>
        <Slider label="Similitud mínima entre pasos" value={minSim} min={0.1} max={0.8} step={0.05} onChange={setMinSim} format={(v) => v.toFixed(2)} hint="Más alto = saltos más cortos, pero puede no haber ruta" />
        <Slider label="Títulos considerados" value={pool} min={20} max={150} step={10} onChange={setPool} />
      </Advanced>
      <ErrorBox message={req.error} />
      {req.loading && <Loader text="Buscando la ruta…" />}
      {!req.data && !req.loading && !req.error && <Empty>Elige dos películas y busca la ruta que las conecta.</Empty>}
      {req.data && !req.loading && (
        req.data.path_found ? (
          <>
            <div className="stats">
              <div className="stat"><span>Pasos</span><b>{req.data.hops}</b></div>
              <div className="stat"><span>Costo total</span><b>{req.data.total_cost}</b></div>
              <div className="stat"><span>Grafo</span><b style={{ fontSize: 16 }}>{req.data.graph.nodes} nodos · {req.data.graph.edges} aristas</b></div>
            </div>
            <div className="path">
              {req.data.path.map((m, i) => (
                <div key={m.id} style={{ display: 'contents' }}>
                  {i > 0 && <span className="arrow">→</span>}
                  <button className="card step" onClick={() => open(m)} style={{ transform: 'none' }}>
                    <Poster movie={m} />
                    <div className="card-title" style={{ fontSize: 12 }}>{m.title}</div>
                  </button>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="warning">No hay ruta entre esas películas con una similitud mínima de {minSim}. Baja el umbral en «Opciones avanzadas» o aumenta los títulos considerados.</div>
        )
      )}
    </>
  )
}

function Hubs() {
  const [genre, setGenre] = useState('')
  const [top, setTop] = useState(8)
  const [pool, setPool] = useState(50)
  const [minSim, setMinSim] = useState(0.4)
  const { open } = useMovieModal()
  const req = useRequest((signal) => api.hubs({ genre, top, pool, min_similarity: minSim }, signal), [], false)
  const max = req.data ? Math.max(...req.data.hubs.map((h) => h.centrality), 0.0001) : 1
  const sparse = req.data && req.data.graph.edges < req.data.graph.nodes

  return (
    <>
      <p style={{ color: 'var(--muted)', maxWidth: '75ch' }}>Las películas más «centrales» son las que mejor conectan con el resto del catálogo: buenos puntos de partida para conocer los gustos de alguien nuevo.</p>
      <div className="controls">
        <GenreSelect value={genre} onChange={setGenre} />
        <Slider label="Cantidad de resultados" value={top} min={3} max={20} onChange={setTop} width={190} />
        <button className="btn" onClick={req.run} disabled={req.loading}>Calcular centralidad</button>
      </div>
      <Advanced>
        <Slider label="Títulos considerados" value={pool} min={10} max={100} step={5} onChange={setPool} hint="Más títulos dan mejores resultados, pero tardan más" />
        <Slider label="Similitud mínima" value={minSim} min={0.1} max={0.9} step={0.05} onChange={setMinSim} format={(v) => v.toFixed(2)} />
      </Advanced>
      <ErrorBox message={req.error} />
      {req.loading && <Loader text="Calculando…" />}
      {!req.data && !req.loading && !req.error && <Empty>Pulsa «Calcular centralidad» para ver las películas más conectadas.</Empty>}
      {req.data && !req.loading && (
        <>
          {sparse && <div className="warning">El grafo quedó casi sin conexiones ({req.data.graph.edges} aristas). Baja la similitud mínima para obtener un resultado significativo.</div>}
          <div className="list">
            {req.data.hubs.map((m, i) => (
              <button key={m.id} className="row-item" onClick={() => open(m)}>
                <span className="num">{i + 1}</span>
                <div className="poster"><Poster movie={m} /></div>
                <div className="grow">
                  <b>{m.title}</b>
                  <div className="card-meta"><span className="star">★ {m.rating.toFixed(1)}</span><span>{m.genres.slice(0, 3).join(', ')}</span></div>
                  <div className="bar" style={{ marginTop: 8 }}><i style={{ width: `${(m.centrality / max) * 100}%` }} /></div>
                </div>
                <span className="chip" title="Centralidad armónica">{m.centrality.toFixed(2)}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </>
  )
}
