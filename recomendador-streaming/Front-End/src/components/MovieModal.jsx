import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../services/api'
import { useRequest } from '../hooks/useRequest'
import { Poster } from './MovieCard'
import { Empty, ErrorBox, Loader, Tabs, year, hours } from './ui'

const ModalContext = createContext({ open: () => {} })
export const useMovieModal = () => useContext(ModalContext)

export function MovieModalProvider({ children }) {
  const [movie, setMovie] = useState(null)
  return (
    <ModalContext.Provider value={{ open: setMovie }}>
      {children}
      {movie && <MovieModal movie={movie} onClose={() => setMovie(null)} onOpen={setMovie} />}
    </ModalContext.Provider>
  )
}

function MovieModal({ movie, onClose, onOpen }) {
  const [tab, setTab] = useState('similar')

  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => { document.removeEventListener('keydown', onKey); document.body.style.overflow = '' }
  }, [onClose])
  useEffect(() => { setTab('similar') }, [movie.id])

  return (
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={movie.title}>
        <button className="modal-close" onClick={onClose} aria-label="Cerrar">✕</button>
        <div className="modal-top">
          <div className="modal-poster"><Poster movie={movie} /></div>
          <div>
            <h2>{movie.title}</h2>
            <div className="chips" style={{ marginTop: 10 }}>
              {movie.genres?.map((g) => <span key={g} className="chip">{g}</span>)}
              {movie.franchise && <span className="chip on">Saga: {movie.franchise}</span>}
            </div>
            <div className="facts">
              <div className="fact"><span>Calificación</span><b><span className="star">★</span> {movie.rating?.toFixed(1)}</b></div>
              <div className="fact"><span>Ponderada</span><b>{movie.weighted_rating?.toFixed(2)}</b></div>
              <div className="fact"><span>Votos</span><b>{movie.votes?.toLocaleString('es')}</b></div>
              <div className="fact"><span>Duración</span><b>{movie.runtime ? hours(movie.runtime) : '—'}</b></div>
              <div className="fact"><span>Estreno</span><b>{movie.release_date || '—'}</b></div>
              <div className="fact"><span>Año</span><b>{year(movie)}</b></div>
            </div>
            <p style={{ color: '#d6d6df', margin: 0 }}>{movie.overview || 'Sin sinopsis disponible.'}</p>
          </div>
        </div>
        <div className="modal-body">
          <Tabs value={tab} onChange={setTab} tabs={[
            { value: 'similar', label: 'Más como esta' },
            { value: 'related', label: 'Relacionadas' },
          ]} />
          {tab === 'similar' ? <SimilarTab movie={movie} onOpen={onOpen} /> : <RelatedTab movie={movie} onOpen={onOpen} />}
        </div>
      </div>
    </div>
  )
}

function MiniRow({ items, onOpen, corner }) {
  return (
    <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(110px, 1fr))', gap: 12 }}>
      {items.map((m) => (
        <button key={m.id} className="card" onClick={() => onOpen(m)} title={m.title}>
          <div style={{ position: 'relative' }}><Poster movie={m} />{corner && <span className="pill-corner">{corner(m)}</span>}</div>
          <div className="card-title" style={{ fontSize: 12 }}>{m.title}</div>
        </button>
      ))}
    </div>
  )
}

function SimilarTab({ movie, onOpen }) {
  const { data, loading, error } = useRequest((signal) => api.similar({ liked: [movie.id], k: 8 }, signal), [movie.id])
  if (loading) return <Loader text="Buscando películas parecidas…" />
  if (error) return <ErrorBox message={error} />
  if (!data) return null
  return (
    <>
      <MiniRow items={data.recommendations} onOpen={onOpen} corner={(m) => `${Math.round(m.match_score * 100)}%`} />
    </>
  )
}

function RelatedTab({ movie, onOpen }) {
  const { data, loading, error } = useRequest((signal) => api.related(movie.id, { depth: 2, neighbors: 4 }, signal), [movie.id])
  if (loading) return <Loader text="Buscando películas relacionadas…" />
  if (error) return <ErrorBox message={error} />
  if (!data) return null
  if (!data.related.length) return <Empty>No hay películas relacionadas para este título.</Empty>
  const byHop = [1, 2].map((h) => data.related.filter((r) => r.hops === h))
  return (
    <>
      {byHop.map((items, i) => items.length > 0 && (
        <div key={i}>
          <div className="hop-title" style={{ marginTop: i ? 18 : 0 }}>{i === 0 ? 'A 1 salto — muy parecidas' : 'A 2 saltos — parecidas de las parecidas'}</div>
          <MiniRow items={items} onOpen={onOpen} corner={(m) => `${Math.round(m.similarity_to_seed * 100)}%`} />
        </div>
      ))}
    </>
  )
}
