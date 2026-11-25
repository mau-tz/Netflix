import { useState } from 'react'
import { api } from '../services/api'
import { useRequest } from '../hooks/useRequest'
import { Advanced, ErrorBox, GenreSelect, Loader, PageHead, Segmented, Slider, Empty } from '../components/ui'
import { MovieGrid, Poster } from '../components/MovieCard'
import { useMovieModal } from '../components/MovieModal'

const CRITERIA = [
  { value: 'trending', label: 'Tendencia' },
  { value: 'popularity', label: 'Popularidad' },
  { value: 'weighted_rating', label: 'Mejor valoradas' },
  { value: 'rating', label: 'Nota promedio' },
]

export default function Home() {
  const [genre, setGenre] = useState('')
  const [criteria, setCriteria] = useState('trending')
  const [k, setK] = useState(12)
  const [minVotes, setMinVotes] = useState(0)
  const [maxRuntime, setMaxRuntime] = useState(0)
  const { open } = useMovieModal()

  const { data, loading, error } = useRequest(
    (signal) => api.topK({ k, genre, criteria, min_votes: minVotes, max_runtime: maxRuntime || undefined }, signal),
    [k, genre, criteria, minVotes, maxRuntime],
  )
  const hero = data?.data?.[0]

  return (
    <>
      <PageHead title="Lo mejor del catálogo">
        Las películas mejor posicionadas del catálogo. Cambia el criterio o los filtros y el ranking se actualiza al instante.
      </PageHead>

      <div className="controls">
        <Segmented label="Ordenar por" options={CRITERIA} value={criteria} onChange={setCriteria} />
        <GenreSelect value={genre} onChange={setGenre} />
        <Slider label="Cantidad" value={k} min={3} max={50} onChange={setK} width={160} />
      </div>
      <Advanced>
        <Slider label="Votos mínimos" value={minVotes} min={0} max={20000} step={500} onChange={setMinVotes} hint="Descarta títulos con pocas votaciones" />
        <Slider label="Duración máxima" value={maxRuntime} min={0} max={240} step={10} onChange={setMaxRuntime}
          format={(v) => (v ? `${v} min` : 'sin límite')} />
      </Advanced>

      <ErrorBox message={error} />
      {loading && !data && <Loader />}
      {data && (
        <div className={loading ? 'loading-dim' : ''}>
          {hero ? (
            <>
              <div className="hero">
                <div className="hero-bg" style={{ backgroundImage: hero.poster ? `url(${hero.poster})` : undefined }} />
                <div className="hero-body">
                  <div className="hero-poster"><Poster movie={hero} /></div>
                  <div>
                    <span className="chip on">#1 {CRITERIA.find((c) => c.value === criteria).label}</span>
                    <h2 style={{ marginTop: 10 }}>{hero.title}</h2>
                    <p>{hero.overview || hero.genres.join(' · ')}</p>
                    <button className="btn" onClick={() => open(hero)}>Ver detalles</button>
                  </div>
                </div>
              </div>
              <MovieGrid movies={data.data.slice(1)} rankStart={2} />
            </>
          ) : <Empty>Ninguna película cumple esos filtros. Prueba con menos restricciones.</Empty>}
        </div>
      )}
    </>
  )
}
