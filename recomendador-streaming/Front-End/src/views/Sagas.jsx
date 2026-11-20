import { useState } from 'react'
import { api } from '../services/api'
import { useRequest } from '../hooks/useRequest'
import { Empty, ErrorBox, Loader, PageHead, hours, year } from '../components/ui'
import { Poster } from '../components/MovieCard'
import { useMovieModal } from '../components/MovieModal'

export default function Sagas() {
  const [filter, setFilter] = useState('')
  const [selected, setSelected] = useState(null)
  const { open } = useMovieModal()
  const list = useRequest((signal) => api.watchOrder({}, signal), [])
  const order = useRequest((signal) => (selected ? api.watchOrder({ franchise: selected }, signal) : Promise.resolve(null)), [selected])

  const franchises = (list.data?.franchises || []).filter((f) => f.name.toLowerCase().includes(filter.toLowerCase()))

  return (
    <>
      <PageHead title="Sagas y orden de visionado">
        Elige una saga y te mostramos en qué orden verla: de la primera película a la última, por fecha de estreno.
      </PageHead>

      <div className="controls">
        <div className="field" style={{ flex: '1 1 260px' }}>
          <label>Filtrar sagas</label>
          <input type="search" value={filter} placeholder="Harry Potter, Bond…" onChange={(e) => setFilter(e.target.value)} />
        </div>
        {list.data && <span style={{ color: 'var(--muted)' }}>{list.data.total_franchises} sagas detectadas</span>}
      </div>
      <ErrorBox message={list.error} />
      {list.loading && <Loader text="Cargando sagas…" />}
      <div className="chips" style={{ marginBottom: 24, maxHeight: 190, overflowY: 'auto' }}>
        {franchises.map((f) => (
          <button key={f.name} className={`chip ${selected === f.name ? 'on' : ''}`} onClick={() => setSelected(f.name)}>
            {f.name} · {f.movies}
          </button>
        ))}
        {list.data && !franchises.length && <Empty>No se encontró ninguna saga con ese nombre.</Empty>}
      </div>

      {!selected && list.data && <Empty>Selecciona una saga para ver en qué orden verla.</Empty>}
      <ErrorBox message={order.error} />
      {selected && order.loading && <Loader text="Ordenando la saga…" />}
      {order.data && (
        <>
          <div className="stats">
            <div className="stat"><span>Saga</span><b style={{ fontSize: 18 }}>{order.data.franchise}</b></div>
            <div className="stat"><span>Películas</span><b>{order.data.watch_order.length}</b></div>
            <div className="stat"><span>Duración total</span><b>{hours(order.data.total_runtime_minutes)}</b></div>
            <div className="stat"><span>¿Hay ciclos?</span><b style={{ color: order.data.has_cycle ? 'var(--accent-2)' : 'var(--good)' }}>{order.data.has_cycle ? 'Sí' : 'No'}</b></div>
          </div>
          <div className="list">
            {order.data.watch_order.map((m) => (
              <button key={m.id} className="row-item" onClick={() => open(m)}>
                <span className="num">{m.position}</span>
                <div className="poster"><Poster movie={m} /></div>
                <div className="grow">
                  <b>{m.title}</b>
                  <div className="card-meta"><span>{m.release_date}</span><span className="star">★ {m.rating.toFixed(1)}</span><span>{m.genres.slice(0, 3).join(', ')}</span></div>
                </div>
                <span className="chip">{hours(m.runtime)}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </>
  )
}
