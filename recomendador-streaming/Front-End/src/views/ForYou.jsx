import { useState } from 'react'
import { api } from '../services/api'
import { useRequest } from '../hooks/useRequest'
import { Empty, ErrorBox, GenreSelect, Loader, PageHead, Slider } from '../components/ui'
import MovieCard, { Poster } from '../components/MovieCard'
import MoviePicker from '../components/MoviePicker'

export default function ForYou() {
  const [liked, setLiked] = useState([])
  const [genre, setGenre] = useState('')
  const [k, setK] = useState(12)

  const starters = useRequest((signal) => api.topK({ k: 14, criteria: 'weighted_rating' }, signal), [])
  const ids = liked.map((m) => m.id)
  const { data, loading, error } = useRequest(
    (signal) => (ids.length ? api.similar({ liked: ids, k, genre }, signal) : Promise.resolve(null)),
    [ids.join(','), k, genre],
  )

  const toggle = (movie) =>
    setLiked((cur) => (cur.some((m) => m.id === movie.id) ? cur.filter((m) => m.id !== movie.id) : [...cur, movie]))

  return (
    <>
      <PageHead title="Para ti">
        Dinos qué películas te gustaron y te recomendamos las más afines según géneros y calificación.
      </PageHead>

      <div className="panel" style={{ marginBottom: 20 }}>
        <div className="controls" style={{ marginBottom: 12 }}>
          <div className="field" style={{ flex: '1 1 280px' }}>
            <label>Busca películas que te gustaron</label>
            <MoviePicker value={liked} onChange={setLiked} placeholder="Escribe al menos 2 letras…" />
          </div>
          <GenreSelect value={genre} onChange={setGenre} label="Recomendar solo de" />
          <Slider label="Cantidad" value={k} min={4} max={30} onChange={setK} width={150} />
        </div>
        <span className="field-label">…o toca algunas de las mejor valoradas</span>
        <div className="mini-strip" style={{ marginTop: 8 }}>
          {starters.data?.data.map((m) => {
            const on = liked.some((l) => l.id === m.id)
            return (
              <button key={m.id} className="card mini" style={{ flexBasis: 74, transform: 'none' }} onClick={() => toggle(m)} title={m.title}>
                <div style={{ outline: on ? '3px solid var(--accent)' : 'none', borderRadius: 10, outlineOffset: 1 }}><Poster movie={m} /></div>
              </button>
            )
          })}
        </div>
      </div>

      <ErrorBox message={error} />
      {!ids.length && <Empty>Elige al menos una película para ver tus recomendaciones.</Empty>}
      {ids.length > 0 && loading && !data && <Loader text="Comparando contra todo el catálogo…" />}
      {data && (
        <div className={loading ? 'loading-dim' : ''}>
          <h3 style={{ marginBottom: 14 }}>Porque te gustó {liked.map((m) => m.title).join(', ')}</h3>
          <div className="grid">
            {data.recommendations.map((m) => (
              <MovieCard key={m.id} movie={m} corner={`${Math.round(m.match_score * 100)}%`} />
            ))}
          </div>
        </div>
      )}
    </>
  )
}
