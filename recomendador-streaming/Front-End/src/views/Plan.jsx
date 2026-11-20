import { useState } from 'react'
import { api } from '../services/api'
import { useDebounced, useRequest } from '../hooks/useRequest'
import { Advanced, Empty, ErrorBox, GenreSelect, Loader, PageHead, Segmented, Slider, Tabs, hours, year } from '../components/ui'
import { Poster, MiniStrip } from '../components/MovieCard'
import { useMovieModal } from '../components/MovieModal'

export default function Plan() {
  const [tab, setTab] = useState('marathon')
  return (
    <>
      <PageHead title="Planifica tu tiempo">
        Dos maneras de llenar tu tiempo libre: una maratón que aprovecha al máximo tus horas, o varias combinaciones de películas para una noche.
      </PageHead>
      <Tabs value={tab} onChange={setTab} tabs={[
        { value: 'marathon', label: 'Maratón óptima' },
        { value: 'combos', label: 'Noche de cine' },
      ]} />
      {tab === 'marathon' ? <Marathon /> : <Combos />}
    </>
  )
}

const PALETTE = ['#e50914', '#f5a524', '#3ecf8e', '#4aa8ff', '#b36bff', '#ff6bb5', '#2dd4bf', '#ff8a4c']

function Marathon() {
  const [hoursAvail, setHoursAvail] = useState(5)
  const [genre, setGenre] = useState('')
  const [pool, setPool] = useState(150)
  const minutes = useDebounced(Math.round(hoursAvail * 60), 300)
  const dPool = useDebounced(pool, 300)
  const { open } = useMovieModal()
  const { data, loading, error } = useRequest(
    (signal) => api.marathon({ available_minutes: minutes, genre, pool: dPool }, signal), [minutes, genre, dPool])

  return (
    <>
      <div className="controls">
        <Slider label="Tiempo disponible" value={hoursAvail} onChange={setHoursAvail} min={1} max={24} step={0.5} format={(v) => hours(v * 60)} width={260} />
        <GenreSelect value={genre} onChange={setGenre} />
      </div>
      <Advanced>
        <Slider label="Títulos considerados" value={pool} min={20} max={500} step={10} onChange={setPool} hint="Cuántas de las mejor valoradas se consideran" />
      </Advanced>

      <ErrorBox message={error} />
      {loading && !data && <Loader text="Armando tu maratón…" />}
      {data && (
        <div className={loading ? 'loading-dim' : ''}>
          <div className="stats">
            <div className="stat"><span>Películas</span><b>{data.selected_movies_count}</b></div>
            <div className="stat"><span>Tiempo usado</span><b>{hours(data.used_time_minutes)}</b></div>
            <div className="stat"><span>Tiempo libre</span><b>{hours(data.available_time_minutes - data.used_time_minutes)}</b></div>
            <div className="stat"><span>Satisfacción</span><b>{data.total_satisfaction_score}</b></div>
          </div>
          {data.playlist.length ? (
            <>
              <div className="timeline" aria-label="Línea de tiempo de la maratón">
                {data.playlist.map((m, i) => (
                  <div key={m.id} title={`${m.title} · ${m.runtime} min`}
                    style={{ width: `${(m.runtime / data.available_time_minutes) * 100}%`, background: PALETTE[i % PALETTE.length] }}>
                    {i + 1}
                  </div>
                ))}
                <div className="free" style={{ flex: 1 }}>libre</div>
              </div>
              <div className="list" style={{ marginTop: 16 }}>
                {data.playlist.map((m, i) => (
                  <button key={m.id} className="row-item" onClick={() => open(m)}>
                    <span className="num" style={{ color: PALETTE[i % PALETTE.length] }}>{m.position}</span>
                    <div className="poster"><Poster movie={m} /></div>
                    <div className="grow">
                      <b>{m.title}</b>
                      <div className="card-meta"><span className="star">★ {m.rating.toFixed(1)}</span><span>{year(m)}</span><span>{m.genres.slice(0, 3).join(', ')}</span></div>
                    </div>
                    <span className="chip">{hours(m.runtime)}</span>
                  </button>
                ))}
              </div>
              <p style={{ color: 'var(--muted)', fontSize: 13 }}>Las sagas se ordenan por fecha de estreno para que no veas una secuela antes que su original.</p>
            </>
          ) : <Empty>No hay películas que quepan en ese tiempo.</Empty>}
        </div>
      )}
    </>
  )
}
function Combos() {
  const [genre, setGenre] = useState('')
  const [count, setCount] = useState(3)
  const [minRating, setMinRating] = useState(7.5)
  const [limitTime, setLimitTime] = useState(true)
  const [maxHours, setMaxHours] = useState(6)
  const [pool, setPool] = useState(40)
  const [maxResults, setMaxResults] = useState(30)
  const req = useRequest((signal) => api.backtracking({
    genre, max_movies: count, min_rating: minRating,
    max_total_minutes: limitTime ? Math.round(maxHours * 60) : undefined, pool, max_results: maxResults,
  }, signal), [], false)

  return (
    <>
      <div className="controls">
        <GenreSelect value={genre} onChange={setGenre} />
        <Segmented label="Películas por noche" options={[1, 2, 3, 4, 5].map((n) => ({ value: n, label: String(n) }))} value={count} onChange={setCount} />
        <Slider label="Nota mínima de cada una" value={minRating} onChange={setMinRating} min={5} max={9} step={0.1} format={(v) => v.toFixed(1)} hint="Se compara con la valoración ponderada" />
        <div className="field" style={{ minWidth: 220 }}>
          <label><input type="checkbox" checked={limitTime} onChange={(e) => setLimitTime(e.target.checked)} /> Limitar duración total</label>
          {limitTime && <input type="range" min={1} max={16} step={0.5} value={maxHours} onChange={(e) => setMaxHours(Number(e.target.value))} />}
          {limitTime && <small>Máximo <b>{hours(maxHours * 60)}</b> en total</small>}
        </div>
        <button className="btn" onClick={req.run} disabled={req.loading}>Buscar combinaciones</button>
      </div>
      <Advanced>
        <Slider label="Títulos considerados" value={pool} min={10} max={100} step={5} onChange={setPool} hint="Más títulos = más combinaciones posibles" />
        <Slider label="Máximo de resultados" value={maxResults} min={5} max={200} step={5} onChange={setMaxResults} />
      </Advanced>

      <ErrorBox message={req.error} />
      {req.loading && <Loader text="Buscando combinaciones…" />}
      {!req.data && !req.loading && !req.error && <Empty>Configura tus condiciones y pulsa «Buscar combinaciones».</Empty>}
      {req.data && !req.loading && (
        <>
          <p style={{ color: 'var(--muted)' }}>
            <b style={{ color: 'var(--text)' }}>{req.data.total_combinations_found}</b> combinaciones
            {req.data.truncated && ' (se detuvo al llegar al máximo; se muestran las mejores encontradas)'}.
          </p>
          {req.data.results.length === 0 && <Empty>Ninguna combinación cumple esas condiciones. Baja la nota mínima o aumenta el tiempo.</Empty>}
          <div className="cols">
            {req.data.results.map((r, i) => (
              <div key={i} className="combo">
                <div className="combo-head">
                  <span>Opción {i + 1}</span>
                  <span>★ <b>{r.avg_rating}</b> · <b>{hours(r.total_minutes)}</b></span>
                </div>
                <MiniStrip movies={r.movies} />
                <div style={{ marginTop: 8, fontSize: 13, color: 'var(--muted)' }}>{r.movies.map((m) => m.title).join(' + ')}</div>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  )
}
