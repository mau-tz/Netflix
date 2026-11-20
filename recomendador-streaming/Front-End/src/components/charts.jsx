const fmt = (v) => (v >= 1000 ? `${(v / 1000).toFixed(v >= 10000 ? 0 : 1)}k` : v >= 10 ? Math.round(v) : v.toFixed(2))

/** Barras horizontales. Con log=true usa escala logarítmica (necesaria cuando los valores difieren 1000x). */
export function BarChart({ items, color = 'var(--accent)', log = false, unit = '' }) {
  const rowH = 30
  const labelW = 190
  const width = 640
  const values = items.map((i) => Math.max(i.value, 0.0001))
  const scale = (v) => {
    if (!log) return v / Math.max(...values)
    const min = Math.log10(Math.min(...values)) - 0.3
    const max = Math.log10(Math.max(...values))
    return max === min ? 1 : (Math.log10(v) - min) / (max - min)
  }
  return (
    <svg className="chart" viewBox={`0 0 ${width} ${items.length * rowH + 6}`} role="img" aria-label="Gráfico de barras">
      {items.map((it, i) => {
        const w = Math.max(scale(values[i]) * (width - labelW - 80), 2)
        return (
          <g key={it.label} transform={`translate(0 ${i * rowH + 4})`}>
            <text className="label" x={labelW - 8} y={15} textAnchor="end">{it.label}</text>
            <rect x={labelW} y={3} width={w} height={18} rx={4} fill={it.color || color} />
            <text x={labelW + w + 6} y={16}>{fmt(it.value)}{unit}</text>
          </g>
        )
      })}
    </svg>
  )
}

/** Línea de crecimiento (x = tamaño N, y = valor). Ejes lineales. */
export function LineChart({ points, color = 'var(--accent)', yLabel = '' }) {
  const W = 560, H = 240, P = { l: 56, r: 16, t: 14, b: 34 }
  if (points.length < 2) return <p style={{ color: 'var(--muted)' }}>Se necesitan al menos 2 tamaños para graficar.</p>
  const xs = points.map((p) => p.x), ys = points.map((p) => p.y)
  const xMin = Math.min(...xs), xMax = Math.max(...xs), yMax = Math.max(...ys, 0.0001)
  const X = (x) => P.l + ((x - xMin) / (xMax - xMin || 1)) * (W - P.l - P.r)
  const Y = (y) => H - P.b - (y / yMax) * (H - P.t - P.b)
  const ticks = [0, 0.25, 0.5, 0.75, 1]
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Crecimiento de ${yLabel}`}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={P.l} x2={W - P.r} y1={Y(yMax * t)} y2={Y(yMax * t)} stroke="var(--line)" />
          <text x={P.l - 6} y={Y(yMax * t) + 4} textAnchor="end">{fmt(yMax * t)}</text>
        </g>
      ))}
      <polyline fill="none" stroke={color} strokeWidth="2.5" points={points.map((p) => `${X(p.x)},${Y(p.y)}`).join(' ')} />
      {points.map((p) => (
        <g key={p.x}>
          <circle cx={X(p.x)} cy={Y(p.y)} r="4" fill={color} />
          <text x={X(p.x)} y={H - 14} textAnchor="middle">{p.x}</text>
        </g>
      ))}
      <text x={W / 2} y={H - 1} textAnchor="middle">N (tamaño de entrada)</text>
    </svg>
  )
}

/** Anillo de progreso (asignadas / pedidas). */
export function Ring({ value, total }) {
  const r = 46, c = 2 * Math.PI * r
  const pct = total ? Math.min(value / total, 1) : 0
  return (
    <svg className="progress-ring" viewBox="0 0 120 120" role="img" aria-label={`${value} de ${total}`}>
      <circle cx="60" cy="60" r={r} fill="none" stroke="var(--bg-3)" strokeWidth="12" />
      <circle cx="60" cy="60" r={r} fill="none" stroke={pct === 1 ? 'var(--good)' : 'var(--warn)'} strokeWidth="12"
        strokeLinecap="round" strokeDasharray={`${c * pct} ${c}`} transform="rotate(-90 60 60)" />
      <text x="60" y="60" textAnchor="middle" style={{ fill: 'var(--text)', fontSize: 22, fontWeight: 800 }}>{value}/{total}</text>
      <text x="60" y="78" textAnchor="middle">asignadas</text>
    </svg>
  )
}
