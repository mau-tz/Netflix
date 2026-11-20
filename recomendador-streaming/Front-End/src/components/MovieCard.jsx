import { useMovieModal } from './MovieModal'
import { year } from './ui'

export function Poster({ movie }) {
  return (
    <div className="poster">
      {movie.poster
        ? <img src={movie.poster} alt={`Póster de ${movie.title}`} loading="lazy" />
        : <div className="fallback">{movie.title}</div>}
    </div>
  )
}

export default function MovieCard({ movie, rank, corner, extra }) {
  const { open } = useMovieModal()
  return (
    <button className="card" onClick={() => open(movie)} title={movie.title}>
      <div style={{ position: 'relative' }}>
        <Poster movie={movie} />
        {rank && <span className="rank">#{rank}</span>}
        {corner && <span className="pill-corner">{corner}</span>}
      </div>
      <div className="card-title">{movie.title}</div>
      <div className="card-meta">
        <span><span className="star">★</span> {movie.rating ? movie.rating.toFixed(1) : '—'}</span>
        <span>{year(movie)}</span>
        {movie.runtime ? <span>{movie.runtime} min</span> : null}
      </div>
      {extra}
    </button>
  )
}

export function MovieGrid({ movies, rankStart, corner, className = '' }) {
  return (
    <div className={`grid ${className}`}>
      {movies.map((m, i) => (
        <MovieCard key={m.id} movie={m} rank={rankStart ? rankStart + i : undefined} corner={corner ? corner(m) : undefined} />
      ))}
    </div>
  )
}

/** Fila compacta de pósters pequeños. */
export function MiniStrip({ movies, max = 14 }) {
  const { open } = useMovieModal()
  return (
    <div className="mini-strip">
      {movies.slice(0, max).map((m) => (
        <button key={m.id} className="card mini" style={{ transform: 'none' }} onClick={() => open(m)} title={m.title}>
          <Poster movie={m} />
        </button>
      ))}
      {movies.length > max && <span className="chip" style={{ alignSelf: 'center' }}>+{movies.length - max}</span>}
    </div>
  )
}
