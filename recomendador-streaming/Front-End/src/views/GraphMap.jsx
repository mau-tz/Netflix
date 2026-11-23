import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../services/api'
import { useRequest } from '../hooks/useRequest'
import { ErrorBox, Loader, PageHead, Slider } from '../components/ui'
import { useMovieModal } from '../components/MovieModal'
import './GraphMap.css'

// Mismos colores que la imagen de referencia, en el mismo orden que los grupos del back-end.
const COLORS = ['#ff5c5c', '#ffd60a', '#b57edc', '#7f93a8']
const HIT_RADIUS = 7 // píxeles de tolerancia para detectar el nodo bajo el mouse
const CELL = 8 // tamaño de celda (unidades del mundo) de la grilla de búsqueda

export default function GraphMap() {
  const [k, setK] = useState(3)
  const [appliedK, setAppliedK] = useState(3)
  const req = useRequest((signal) => api.graphOverview({ k: appliedK }, signal), [appliedK])

  return (
    <>
      <PageHead title="Mapa del grafo completo">
        Todas las películas del catálogo como puntos; cada una se conecta con sus más parecidas.
        Pasa el mouse sobre un punto para ver sus conexiones y haz clic para abrir su ficha.
      </PageHead>
      <div className="controls">
        <Slider label="Vecinas por película" value={k} min={1} max={6} onChange={setK} hint="Más vecinas = más aristas" />
        <button className="btn" onClick={() => setAppliedK(k)} disabled={req.loading || k === appliedK}>Actualizar grafo</button>
      </div>
      <ErrorBox message={req.error} />
      {req.loading && <Loader text="Construyendo el grafo de todas las películas…" />}
      {req.data && !req.loading && (
        <>
          <div className="stats">
            <div className="stat"><span>Películas (nodos)</span><b>{req.data.total_nodes.toLocaleString('es')}</b></div>
            <div className="stat"><span>Conexiones (aristas)</span><b>{req.data.total_edges.toLocaleString('es')}</b></div>
            <div className="stat"><span>Aristas entre grupos</span><b>{req.data.cross_group_edges.toLocaleString('es')}</b></div>
          </div>
          <GraphCanvas data={req.data} />
          <p className="gm-hint">Rueda del mouse: zoom · Arrastrar: mover · Doble clic: restablecer vista · Clic en la leyenda: ocultar un grupo.</p>
        </>
      )}
    </>
  )
}

function GraphCanvas({ data }) {
  const { open } = useMovieModal()
  const wrapRef = useRef(null)
  const canvasRef = useRef(null)
  const view = useRef({ scale: 1, tx: 0, ty: 0 }) // transformación mundo -> pantalla
  const hover = useRef(-1)
  const dirty = useRef(true)
  const [hidden, setHidden] = useState(() => new Set())
  const [tip, setTip] = useState(null)
  const hiddenRef = useRef(hidden)
  hiddenRef.current = hidden

  const { x, y, group, edges, world } = data
  const n = x.length

  // Lista de adyacencia (para resaltar las conexiones del nodo bajo el mouse).
  const adjacency = useMemo(() => {
    const adj = Array.from({ length: n }, () => [])
    for (let i = 0; i < edges.length; i += 2) {
      adj[edges[i]].push(edges[i + 1])
      adj[edges[i + 1]].push(edges[i])
    }
    return adj
  }, [edges, n])

  // Grilla espacial: encontrar el nodo más cercano al mouse sin recorrer los 20.000.
  const grid = useMemo(() => {
    const cols = Math.ceil(world.width / CELL) + 1
    const cells = new Map()
    for (let i = 0; i < n; i++) {
      const key = Math.floor(y[i] / CELL) * cols + Math.floor(x[i] / CELL)
      const bucket = cells.get(key)
      if (bucket) bucket.push(i); else cells.set(key, [i])
    }
    return { cols, cells }
  }, [x, y, n, world.width])

  const fit = useCallback(() => {
    const c = canvasRef.current
    if (!c) return
    const margin = 24
    const scale = Math.min((c.clientWidth - margin * 2) / world.width, (c.clientHeight - margin * 2) / world.height)
    view.current = {
      scale,
      tx: (c.clientWidth - world.width * scale) / 2,
      ty: (c.clientHeight - world.height * scale) / 2 + 10,
    }
    dirty.current = true
  }, [world.width, world.height])

  const draw = useCallback(() => {
    const c = canvasRef.current
    if (!c) return
    const dpr = window.devicePixelRatio || 1
    const w = c.clientWidth, h = c.clientHeight
    if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) {
      c.width = Math.round(w * dpr); c.height = Math.round(h * dpr)
    }
    const ctx = c.getContext('2d')
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.fillStyle = '#000'
    ctx.fillRect(0, 0, w, h)

    const { scale, tx, ty } = view.current
    const hid = hiddenRef.current
    const h0 = hover.current
    const visible = (i) => !hid.has(group[i])

    // Aristas (un solo trazo: rápido incluso con ~40.000)
    ctx.lineWidth = 0.6
    ctx.strokeStyle = 'rgba(255,255,255,0.07)'
    ctx.beginPath()
    for (let i = 0; i < edges.length; i += 2) {
      const a = edges[i], b = edges[i + 1]
      if (!visible(a) || !visible(b)) continue
      ctx.moveTo(x[a] * scale + tx, y[a] * scale + ty)
      ctx.lineTo(x[b] * scale + tx, y[b] * scale + ty)
    }
    ctx.stroke()

    // Nodos, un color a la vez
    const r = Math.max(1.1, Math.min(3, scale * 1.4))
    for (let g = 0; g < COLORS.length; g++) {
      if (hid.has(g)) continue
      ctx.fillStyle = COLORS[g]
      ctx.beginPath()
      for (let i = 0; i < n; i++) {
        if (group[i] !== g) continue
        const px = x[i] * scale + tx, py = y[i] * scale + ty
        if (px < -4 || py < -4 || px > w + 4 || py > h + 4) continue
        ctx.moveTo(px + r, py)
        ctx.arc(px, py, r, 0, 6.2832)
      }
      ctx.fill()
    }

    // Nodo bajo el mouse y sus conexiones
    if (h0 >= 0 && visible(h0)) {
      const hx = x[h0] * scale + tx, hy = y[h0] * scale + ty
      ctx.strokeStyle = 'rgba(255,255,255,0.85)'
      ctx.lineWidth = 1.2
      ctx.beginPath()
      for (const nb of adjacency[h0]) {
        if (!visible(nb)) continue
        ctx.moveTo(hx, hy)
        ctx.lineTo(x[nb] * scale + tx, y[nb] * scale + ty)
      }
      ctx.stroke()
      for (const nb of adjacency[h0]) {
        if (!visible(nb)) continue
        ctx.fillStyle = '#fff'
        ctx.beginPath(); ctx.arc(x[nb] * scale + tx, y[nb] * scale + ty, r + 1.5, 0, 6.2832); ctx.fill()
      }
      ctx.fillStyle = COLORS[group[h0]]
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 2
      ctx.beginPath(); ctx.arc(hx, hy, r + 4, 0, 6.2832); ctx.fill(); ctx.stroke()
    }
  }, [x, y, group, edges, n, adjacency])

  // Bucle de dibujo: solo repinta cuando algo cambió.
  useEffect(() => {
    fit()
    let raf
    const loop = () => {
      if (dirty.current) { dirty.current = false; draw() }
      raf = requestAnimationFrame(loop)
    }
    loop()
    const ro = new ResizeObserver(() => { fit() })
    ro.observe(wrapRef.current)
    return () => { cancelAnimationFrame(raf); ro.disconnect() }
  }, [fit, draw])

  useEffect(() => { dirty.current = true }, [hidden])

  const nodeAt = (px, py) => {
    const { scale, tx, ty } = view.current
    const wx = (px - tx) / scale, wy = (py - ty) / scale
    const reach = HIT_RADIUS / scale
    let best = -1, bestD = reach * reach
    const c0 = Math.floor((wx - reach) / CELL), c1 = Math.floor((wx + reach) / CELL)
    const r0 = Math.floor((wy - reach) / CELL), r1 = Math.floor((wy + reach) / CELL)
    for (let rr = r0; rr <= r1; rr++) {
      for (let cc = c0; cc <= c1; cc++) {
        const bucket = grid.cells.get(rr * grid.cols + cc)
        if (!bucket) continue
        for (const i of bucket) {
          if (hiddenRef.current.has(group[i])) continue
          const d = (x[i] - wx) ** 2 + (y[i] - wy) ** 2
          if (d < bestD) { bestD = d; best = i }
        }
      }
    }
    return best
  }

  const drag = useRef(null)
  const onDown = (e) => {
    drag.current = { x: e.clientX, y: e.clientY, tx: view.current.tx, ty: view.current.ty, moved: false }
    canvasRef.current.setPointerCapture(e.pointerId)
  }
  const onMove = (e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const px = e.clientX - rect.left, py = e.clientY - rect.top
    const d = drag.current
    if (d) {
      const dx = e.clientX - d.x, dy = e.clientY - d.y
      if (Math.abs(dx) + Math.abs(dy) > 3) d.moved = true
      if (d.moved) {
        view.current.tx = d.tx + dx; view.current.ty = d.ty + dy
        hover.current = -1; setTip(null); dirty.current = true
        return
      }
    }
    const i = nodeAt(px, py)
    if (i !== hover.current) {
      hover.current = i
      dirty.current = true
      setTip(i >= 0 ? { i, px, py } : null)
    } else if (i >= 0) setTip({ i, px, py })
  }
  const onUp = (e) => {
    const d = drag.current
    drag.current = null
    if (d && !d.moved) {
      const rect = canvasRef.current.getBoundingClientRect()
      const i = nodeAt(e.clientX - rect.left, e.clientY - rect.top)
      if (i >= 0) api.graphNode(data.ids[i]).then(open).catch(() => {})
    }
  }
  const zoomAt = (factor, px, py) => {
    const v = view.current
    const next = Math.min(Math.max(v.scale * factor, 0.3), 40)
    const f = next / v.scale
    v.tx = px - (px - v.tx) * f
    v.ty = py - (py - v.ty) * f
    v.scale = next
    dirty.current = true
  }
  // El listener de rueda debe ser no-pasivo para poder evitar el scroll de la página.
  useEffect(() => {
    const c = canvasRef.current
    const onWheel = (e) => {
      e.preventDefault()
      const rect = c.getBoundingClientRect()
      zoomAt(e.deltaY < 0 ? 1.2 : 1 / 1.2, e.clientX - rect.left, e.clientY - rect.top)
    }
    c.addEventListener('wheel', onWheel, { passive: false })
    return () => c.removeEventListener('wheel', onWheel)
  }, [])

  const toggle = (g) => setHidden((prev) => {
    const next = new Set(prev)
    next.has(g) ? next.delete(g) : next.add(g)
    return next
  })
  const center = () => [canvasRef.current.clientWidth / 2, canvasRef.current.clientHeight / 2]

  return (
    <div className="gm-wrap" ref={wrapRef}>
      <canvas
        ref={canvasRef}
        className="gm-canvas"
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerLeave={() => { hover.current = -1; setTip(null); dirty.current = true }}
        onDoubleClick={fit}
        aria-label="Grafo de películas por similitud"
      />
      <div className="gm-title">
        Visualización completa del catálogo (grafo de películas TMDB)
        <small>{data.total_nodes.toLocaleString('es')} películas conectadas por similitud de metadatos</small>
      </div>
      <div className="gm-legend">
        {data.groups.map((g) => (
          <button key={g.id} className={hidden.has(g.id) ? 'off' : ''} onClick={() => toggle(g.id)} title="Mostrar / ocultar grupo">
            <i style={{ background: COLORS[g.id] }} />{g.name} <span style={{ color: 'var(--muted)' }}>({g.count.toLocaleString('es')})</span>
          </button>
        ))}
      </div>
      <div className="gm-zoom">
        <button onClick={() => zoomAt(1.4, ...center())} aria-label="Acercar">+</button>
        <button onClick={() => zoomAt(1 / 1.4, ...center())} aria-label="Alejar">−</button>
        <button onClick={fit} aria-label="Restablecer vista">⟲</button>
      </div>
      {tip && (
        <div className="gm-tip" style={{ left: tip.px, top: tip.py }}>
          <b>{data.titles[tip.i]}</b>
          <span>★ {data.ratings[tip.i].toFixed(1)} · {data.groups[group[tip.i]].name} · {adjacency[tip.i].length} conexiones</span>
        </div>
      )}
    </div>
  )
}
