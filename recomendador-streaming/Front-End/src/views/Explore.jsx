import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { useDebounced, useRequest } from '../hooks/useRequest'
import { Empty, ErrorBox, GenreSelect, Loader, PageHead, Pagination } from '../components/ui'
import { MovieGrid } from '../components/MovieCard'

const SORTS = [
  { value: 'weighted_rating', label: 'Valoración ponderada', numeric: true, step: 0.1 },
  { value: 'rating', label: 'Nota promedio', numeric: true, step: 0.1 },
  { value: 'popularity', label: 'Popularidad', numeric: true, step: 10 },
  { value: 'votes', label: 'Cantidad de votos', numeric: true, step: 100 },
  { value: 'runtime', label: 'Duración (min)', numeric: true, step: 5 },
  { value: 'release_date', label: 'Fecha de estreno', numeric: false },
]
const SIZE = 18

export default function Explore() {
  const [q, setQ] = useState('')
  const [sortBy, setSortBy] = useState('weighted_rating')
  const [order, setOrder] = useState('desc')
  const [genre, setGenre] = useState('')
  const [minValue, setMinValue] = useState('')
  const [maxValue, setMaxValue] = useState('')
  const [page, setPage] = useState(1)
  const dq = useDebounced(q, 350)
  const dMin = useDebounced(minValue, 500)
  const dMax = useDebounced(maxValue, 500)
  const sort = SORTS.find((s) => s.value === sortBy)

  useEffect(() => { setPage(1) }, [dq, sortBy, order, genre, dMin, dMax])
  useEffect(() => { setMinValue(''); setMaxValue('') }, [sortBy])

  const { data, loading, error } = useRequest(
    (signal) => api.catalog({
      q: dq, sort_by: sortBy, order, genre, page, size: SIZE,
      min_value: sort.numeric ? dMin : undefined, max_value: sort.numeric ? dMax : undefined,
    }, signal),
    [dq, sortBy, order, genre, dMin, dMax, page],
  )

  return (
    <>
      <PageHead title="Explorar el catálogo">
        Busca por título, filtra por género, ordena como prefieras y acota por rango de valores.
      </PageHead>

      <div className="controls">
        <div className="field" style={{ flex: '1 1 220px' }}>
          <label>Buscar por título</label>
          <input type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ej. Spider-Man, Batman…" />
        </div>
        <GenreSelect value={genre} onChange={setGenre} />
        <div className="field">
          <label>Ordenar por</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            {SORTS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
        <div className="field" style={{ minWidth: 110 }}>
          <label>Orden</label>
          <select value={order} onChange={(e) => setOrder(e.target.value)}>
            <option value="desc">Mayor a menor</option>
            <option value="asc">Menor a mayor</option>
          </select>
        </div>
        {sort.numeric && (
          <div className="field" style={{ minWidth: 220 }}>
            <label>Rango de «{sort.label}»</label>
            <div style={{ display: 'flex', gap: 8 }}>
              <input type="number" step={sort.step} placeholder="mín." value={minValue} onChange={(e) => setMinValue(e.target.value)} />
              <input type="number" step={sort.step} placeholder="máx." value={maxValue} onChange={(e) => setMaxValue(e.target.value)} />
            </div>
          </div>
        )}
      </div>

      <ErrorBox message={error} />
      {loading && !data && <Loader />}
      {data && (
        <div className={loading ? 'loading-dim' : ''}>
          <p style={{ color: 'var(--muted)', marginTop: 0 }}><b style={{ color: 'var(--text)' }}>{data.total_results.toLocaleString('es')}</b> películas</p>
          {data.data.length ? <MovieGrid movies={data.data} /> : <Empty>No hay resultados con esos filtros.</Empty>}
          <Pagination page={page} size={SIZE} total={data.total_results} onChange={setPage} />
        </div>
      )}
    </>
  )
}
