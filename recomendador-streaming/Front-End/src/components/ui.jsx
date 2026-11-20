import { useState } from 'react'
import { GENRES } from '../services/api'

export function PageHead({ tag, title, children }) {
  return (
    <div className="page-head">
      {tag && <span className="tag">{tag}</span>}
      <h1>{title}</h1>
      {children && <p>{children}</p>}
    </div>
  )
}

export function Loader({ text = 'Calculando…' }) {
  return (
    <div className="state" role="status">
      <div className="spinner" />
      {text}
    </div>
  )
}

export function ErrorBox({ message }) {
  if (!message) return null
  return <div className="error" role="alert">⚠ {message}</div>
}

export function Empty({ children }) {
  return <div className="state">{children}</div>
}

export function Segmented({ options, value, onChange, label }) {
  return (
    <div className="field">
      {label && <span className="field-label">{label}</span>}
      <div className="seg" role="group" aria-label={label}>
        {options.map((o) => {
          const opt = typeof o === 'string' ? { value: o, label: o } : o
          return (
            <button key={opt.value} className={opt.value === value ? 'on' : ''} onClick={() => onChange(opt.value)}>
              {opt.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export function Slider({ label, value, onChange, min, max, step = 1, format = (v) => v, hint, width = 200 }) {
  return (
    <div className="field" style={{ minWidth: width }}>
      <label>{label}: <span className="range-value">{format(value)}</span></label>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} />
      {hint && <small>{hint}</small>}
    </div>
  )
}

export function GenreSelect({ value, onChange, label = 'Género', allLabel = 'Todos los géneros' }) {
  return (
    <div className="field">
      <label>{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">{allLabel}</option>
        {GENRES.map((g) => <option key={g} value={g}>{g}</option>)}
      </select>
    </div>
  )
}

export function GenreChips({ value, onChange }) {
  const toggle = (g) => onChange(value.includes(g) ? value.filter((x) => x !== g) : [...value, g])
  return (
    <div className="chips">
      {GENRES.map((g) => (
        <button key={g} type="button" className={`chip ${value.includes(g) ? 'on' : ''}`} onClick={() => toggle(g)}>{g}</button>
      ))}
    </div>
  )
}

export function Tabs({ tabs, value, onChange }) {
  return (
    <div className="tabs" role="tablist">
      {tabs.map((t) => (
        <button key={t.value} role="tab" aria-selected={t.value === value} className={`tab ${t.value === value ? 'on' : ''}`} onClick={() => onChange(t.value)}>
          {t.label}
        </button>
      ))}
    </div>
  )
}

export function Advanced({ children }) {
  return (
    <details className="advanced">
      <summary>Opciones avanzadas</summary>
      <div className="controls">{children}</div>
    </details>
  )
}

export function Pagination({ page, size, total, onChange }) {
  const pages = Math.max(1, Math.ceil(total / size))
  if (pages <= 1) return null
  return (
    <div className="controls" style={{ justifyContent: 'center', marginTop: 24, alignItems: 'center' }}>
      <button className="btn ghost small" disabled={page <= 1} onClick={() => onChange(page - 1)}>← Anterior</button>
      <span style={{ color: 'var(--muted)' }}>Página <b style={{ color: 'var(--text)' }}>{page}</b> de {pages}</span>
      <button className="btn ghost small" disabled={page >= pages} onClick={() => onChange(page + 1)}>Siguiente →</button>
    </div>
  )
}

export function useToggle(initial = false) {
  const [on, setOn] = useState(initial)
  return [on, () => setOn((v) => !v), setOn]
}

export const hours = (minutes) => {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h ? `${h} h ${m ? `${m} min` : ''}`.trim() : `${m} min`
}
export const year = (movie) => (movie.release_date ? movie.release_date.slice(0, 4) : '—')
