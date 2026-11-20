import { useState } from 'react'
import { api } from '../services/api'
import { useRequest } from '../hooks/useRequest'
import { Advanced, ErrorBox, GenreChips, Loader, PageHead, Slider } from '../components/ui'
import { MiniStrip } from '../components/MovieCard'
import { Ring } from '../components/charts'

const DEMO = [
  { name: 'Ana', genres: ['Acción', 'Aventura'], slots: 4 },
  { name: 'Luis', genres: ['Acción', 'Ciencia ficción'], slots: 4 },
  { name: 'Marta', genres: ['Terror', 'Suspense'], slots: 3 },
]

export default function Allocate() {
  const [users, setUsers] = useState(DEMO)
  const [maxExposure, setMaxExposure] = useState(2)
  const [pool, setPool] = useState(150)

  const update = (i, patch) => setUsers((us) => us.map((u, j) => (j === i ? { ...u, ...patch } : u)))
  const valid = users.length > 0 && users.every((u) => u.name.trim() && u.genres.length && u.slots >= 1)
  const req = useRequest((signal) => api.allocate({
    users: users.map((u) => ({ ...u, name: u.name.trim() })), max_exposure: maxExposure, pool,
  }, signal), [], false)

  // Cuántos usuarios recibieron cada película (para comprobar el límite de exposición)
  const exposure = {}
  req.data?.assignments.forEach((a) => a.movies.forEach((m) => { exposure[m.id] = (exposure[m.id] || 0) + 1 }))
  const maxSeen = Math.max(0, ...Object.values(exposure))

  return (
    <>
      <PageHead title="Reparto justo de recomendaciones">
        Si todos reciben el mismo Top, unas pocas películas saturan la plataforma. Aquí cada usuario pide cierta cantidad de recomendaciones de sus géneros y cada película solo puede recomendarse a un máximo de usuarios. Calculamos el mejor reparto posible.
      </PageHead>

      <div className="user-form">
        {users.map((u, i) => (
          <div key={i} className="user-card">
            <div className="user-top">
              <div className="field" style={{ minWidth: 180 }}>
                <label>Usuario</label>
                <input type="text" value={u.name} onChange={(e) => update(i, { name: e.target.value })} />
              </div>
              <Slider label="Recomendaciones" value={u.slots} min={1} max={12} onChange={(v) => update(i, { slots: v })} width={190} />
              <button className="btn ghost small" onClick={() => setUsers(users.filter((_, j) => j !== i))} disabled={users.length === 1}>Quitar</button>
            </div>
            <div><span className="field-label">Géneros de interés</span><div style={{ marginTop: 6 }}><GenreChips value={u.genres} onChange={(g) => update(i, { genres: g })} /></div></div>
          </div>
        ))}
      </div>

      <div className="controls" style={{ marginTop: 16 }}>
        <button className="btn ghost" disabled={users.length >= 10} onClick={() => setUsers([...users, { name: `Usuario ${users.length + 1}`, genres: ['Comedia'], slots: 3 }])}>+ Agregar usuario</button>
        <Slider label="Máx. usuarios por película" value={maxExposure} min={1} max={6} onChange={setMaxExposure} width={230} hint="Límite de exposición" />
        <button className="btn" disabled={!valid || req.loading} onClick={req.run}>Calcular reparto</button>
      </div>
      <Advanced><Slider label="Títulos candidatos" value={pool} min={20} max={500} step={10} onChange={setPool} /></Advanced>

      <ErrorBox message={req.error} />
      {req.loading && <Loader text="Calculando el reparto…" />}
      {req.data && !req.loading && (
        <>
          <div className="controls" style={{ alignItems: 'center' }}>
            <Ring value={req.data.total_assigned} total={req.data.total_requested} />
            <div>
              <h3>{req.data.fully_satisfied ? '¡Todos quedaron satisfechos!' : 'Algunos usuarios recibieron menos de lo pedido'}</h3>
              <p style={{ color: 'var(--muted)', margin: '6px 0 0' }}>
                Una misma película se recomendó como máximo a <b style={{ color: 'var(--text)' }}>{maxSeen}</b> usuarios (límite: {maxExposure}).
                {!req.data.fully_satisfied && ' Sube el límite de exposición o amplía los géneros para cubrir todo lo pedido.'}
              </p>
            </div>
          </div>
          <div className="cols">
            {req.data.assignments.map((a) => (
              <div key={a.user} className="community">
                <header><h3>{a.user}</h3>
                  <span className="chip" style={a.assigned < a.requested ? { color: 'var(--warn)' } : undefined}>{a.assigned}/{a.requested}</span></header>
                {a.movies.length ? <MiniStrip movies={a.movies} /> : <span style={{ color: 'var(--muted)' }}>Sin asignaciones</span>}
                <div style={{ fontSize: 13, color: 'var(--muted)' }}>{a.movies.map((m) => m.title).join(' · ')}</div>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  )
}
