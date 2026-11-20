import { useState } from 'react'
import { api } from '../services/api'
import { useRequest } from '../hooks/useRequest'
import { Advanced, Empty, ErrorBox, Loader, PageHead, Segmented, Slider } from '../components/ui'
import { MiniStrip } from '../components/MovieCard'
import { BarChart } from '../components/charts'

const METHODS = [
  { value: 'scc', label: 'Comunidades' },
  { value: 'ufds', label: 'Por similitud' },
  { value: 'mst', label: 'Cantidad fija' },
]
const EXPLAIN = {
  scc: 'Cada película se enlaza con sus más parecidas. Una comunidad es un grupo cuyas películas se recomiendan entre sí.',
  ufds: 'Agrupa películas cuya similitud supera el mínimo que elijas. Cada grupo resultante es un nicho.',
  mst: 'Tú eliges cuántos grupos quieres y el catálogo se divide en ese número de nichos.',
}

export default function Niches() {
  const [method, setMethod] = useState('scc')
  const [pool, setPool] = useState(100)
  const [neighbors, setNeighbors] = useState(3)
  const [minSim, setMinSim] = useState(0.8)
  const [minSize, setMinSize] = useState(2)
  const [k, setK] = useState(6)

  const req = useRequest((signal) => (
    method === 'mst'
      ? api.clustersMst({ k, pool }, signal)
      : api.communities({ method, pool, neighbors, min_similarity: minSim, min_size: minSize }, signal)
  ), [], false)

  const groups = req.data ? (req.data.communities || req.data.clusters) : []
  const idOf = (g) => g.community_id || g.cluster_id

  return (
    <>
      <PageHead title="Nichos y comunidades">
        Descubre grupos naturales de películas parecidas. Prueba las tres formas de agrupar y compara los resultados.
      </PageHead>
      <div className="controls">
        <Segmented label="Tipo de agrupación" options={METHODS} value={method} onChange={setMethod} />
        <Slider label="Títulos analizados" value={pool} min={20} max={method === 'mst' ? 200 : 300} step={10} onChange={setPool} />
        {method === 'scc' && <Slider label="Vecinas por película" value={neighbors} min={1} max={8} onChange={setNeighbors} />}
        {method === 'ufds' && <Slider label="Similitud mínima" value={minSim} min={0.3} max={0.95} step={0.05} onChange={setMinSim} format={(v) => v.toFixed(2)} />}
        {method === 'mst' && <Slider label="Cantidad de grupos" value={k} min={2} max={20} onChange={setK} />}
        <button className="btn" onClick={req.run} disabled={req.loading}>Analizar</button>
      </div>
      {method !== 'mst' && <Advanced><Slider label="Tamaño mínimo de grupo" value={minSize} min={1} max={10} onChange={setMinSize} hint="Oculta grupos muy pequeños" /></Advanced>}
      <p style={{ color: 'var(--muted)', maxWidth: '75ch' }}>{EXPLAIN[method]}</p>

      <ErrorBox message={req.error} />
      {req.loading && <Loader text="Buscando nichos…" />}
      {!req.data && !req.loading && !req.error && <Empty>Pulsa «Analizar» para detectar los nichos.</Empty>}
      {req.data && !req.loading && (
        <>
          <div className="stats">
            <div className="stat"><span>Grupos</span><b>{groups.length}</b></div>
            <div className="stat"><span>Películas analizadas</span><b>{req.data.pool_size}</b></div>
            {req.data.ignored_small_groups !== undefined && <div className="stat"><span>Grupos ocultos (pequeños)</span><b>{req.data.ignored_small_groups}</b></div>}
          </div>
          {groups.length > 1 && (
            <div className="panel" style={{ marginBottom: 20 }}>
              <h3 style={{ marginBottom: 10, fontSize: 15 }}>Tamaño de cada grupo</h3>
              <BarChart items={groups.slice(0, 10).map((g) => ({ label: `${idOf(g)} · ${g.dominant_genres[0] || ''}`, value: g.total_movies }))} unit=" pelis" />
            </div>
          )}
          <div className="cols">
            {groups.map((g) => (
              <div key={idOf(g)} className="community">
                <header><h3>{idOf(g)}</h3><span className="chip">{g.total_movies} películas{g.avg_rating ? ` · ★ ${g.avg_rating}` : ''}</span></header>
                <div className="chips">{g.dominant_genres.map((x) => <span key={x} className="chip on">{x}</span>)}</div>
                <MiniStrip movies={g.movies} />
              </div>
            ))}
          </div>
        </>
      )}
    </>
  )
}
