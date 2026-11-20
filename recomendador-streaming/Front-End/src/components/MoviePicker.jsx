import { useEffect, useRef, useState } from 'react'
import { api } from '../services/api'
import { useDebounced } from '../hooks/useRequest'
import { year } from './ui'

/**
 * Buscador de películas por título (usa /recommend/catalog?q=).
 * Modo múltiple: value es un array; modo simple (single): value es una película o null.
 */
export default function MoviePicker({ value, onChange, single = false, placeholder = 'Busca una película…', max = 10 }) {
  const [text, setText] = useState('')
  const [results, setResults] = useState([])
  const [open, setOpen] = useState(false)
  const debounced = useDebounced(text, 250)
  const box = useRef(null)
  const selected = single ? (value ? [value] : []) : value

  useEffect(() => {
    if (debounced.trim().length < 2) { setResults([]); return }
    const controller = new AbortController()
    api.catalog({ q: debounced.trim(), size: 7, sort_by: 'popularity', order: 'desc' }, controller.signal)
      .then((d) => setResults(d.data))
      .catch(() => {})
    return () => controller.abort()
  }, [debounced])

  useEffect(() => {
    const close = (e) => { if (!box.current?.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [])

  const pick = (movie) => {
    if (single) onChange(movie)
    else if (!selected.some((m) => m.id === movie.id) && selected.length < max) onChange([...selected, movie])
    setText(''); setResults([]); setOpen(false)
  }
  const remove = (id) => (single ? onChange(null) : onChange(selected.filter((m) => m.id !== id)))

  return (
    <div className="picker" ref={box}>
      <input type="search" value={text} placeholder={placeholder}
        onChange={(e) => { setText(e.target.value); setOpen(true) }} onFocus={() => setOpen(true)} />
      {open && results.length > 0 && (
        <div className="picker-list">
          {results.map((m) => (
            <button key={m.id} className="picker-item" onClick={() => pick(m)}>
              {m.poster ? <img src={m.poster} alt="" /> : <span className="thumb" />}
              <span><b>{m.title}</b><small>{year(m)} · ★ {m.rating.toFixed(1)} · {m.genres.slice(0, 2).join(', ')}</small></span>
            </button>
          ))}
        </div>
      )}
      {selected.length > 0 && (
        <div className="selected">
          {selected.map((m) => (
            <span key={m.id} className="sel">
              {m.poster ? <img src={m.poster} alt="" /> : <span className="thumb" />}
              <span style={{ fontSize: 13 }}>{m.title}</span>
              <button className="chip x" aria-label={`Quitar ${m.title}`} onClick={() => remove(m.id)}>✕</button>
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
