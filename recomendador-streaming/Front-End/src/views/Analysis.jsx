import { useState } from 'react'
import { api } from '../services/api'
import { useRequest } from '../hooks/useRequest'
import { Empty, ErrorBox, Loader, PageHead, Segmented, Slider, Tabs } from '../components/ui'
import { BarChart, LineChart } from '../components/charts'

export default function Analysis() {
  const [tab, setTab] = useState('compare')
  return (
    <>
      <PageHead tag="Análisis de complejidad" title="Rendimiento de los algoritmos">
        Mide tiempo, memoria y operaciones reales de cada algoritmo y compáralos con su complejidad teórica.
      </PageHead>
      <Tabs value={tab} onChange={setTab} tabs={[
        { value: 'compare', label: 'Comparar todos' },
        { value: 'scaling', label: 'Crecimiento según N' },
      ]} />
      {tab === 'compare' ? <Compare /> : <Scaling />}
    </>
  )
}

function Compare() {
  const [n, setN] = useState(200)
  const req = useRequest((signal) => api.compare({ sample_size: n }, signal), [], false)
  const results = req.data?.results || []
  return (
    <>
      <div className="controls">
        <Slider label="Tamaño de entrada N" value={n} min={10} max={1000} step={10} onChange={setN} width={260} hint="Los algoritmos costosos limitan N automáticamente" />
        <button className="btn" onClick={req.run} disabled={req.loading}>Ejecutar benchmark</button>
      </div>
      <ErrorBox message={req.error} />
      {req.loading && <Loader text="Ejecutando los 12 algoritmos…" />}
      {!req.data && !req.loading && !req.error && <Empty>Pulsa «Ejecutar benchmark». Puede tardar unos segundos con N grande.</Empty>}
      {req.data && !req.loading && (
        <>
          <div className="panel table-wrap" style={{ marginBottom: 18 }}>
            <table className="table">
              <thead><tr><th>Algoritmo</th><th>Complejidad</th><th>N usado</th><th>Tiempo (ms)</th><th>Memoria (KB)</th><th>Operaciones</th></tr></thead>
              <tbody>
                {results.map((r) => (
                  <tr key={r.key}>
                    <td>{r.algorithm}</td><td><code>{r.theoretical_complexity}</code></td><td>{r.input_size_used}</td>
                    <td>{r.execution_time_ms.toLocaleString('es')}</td><td>{r.peak_memory_kb.toLocaleString('es')}</td><td>{r.total_operations.toLocaleString('es')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="cols">
            <div className="panel"><h3 style={{ fontSize: 15, marginBottom: 8 }}>Tiempo de ejecución (ms, escala log)</h3>
              <BarChart log items={results.map((r) => ({ label: r.algorithm, value: r.execution_time_ms }))} /></div>
            <div className="panel"><h3 style={{ fontSize: 15, marginBottom: 8 }}>Operaciones (escala log)</h3>
              <BarChart log color="var(--warn)" items={results.map((r) => ({ label: r.algorithm, value: Math.max(r.total_operations, 1) }))} /></div>
          </div>
        </>
      )}
    </>
  )
}

const ALGOS = [
  ['brute_force', 'Fuerza Bruta'], ['greedy_topk', 'Voraz Top-K'], ['merge_sort', 'Merge Sort'], ['knapsack_dp', 'Mochila (DP)'],
  ['backtracking', 'Backtracking'], ['bfs', 'BFS'], ['tarjan_scc', 'Tarjan SCC'], ['topological_sort', 'Topológico'],
  ['kruskal_mst', 'Kruskal'], ['bellman_ford', 'Bellman-Ford'], ['floyd_warshall', 'Floyd-Warshall'], ['max_flow', 'Flujo máximo'],
]
const SIZE_SETS = { Pequeños: [10, 20, 30, 40, 60], Medianos: [25, 50, 100, 200, 400], Grandes: [100, 250, 500, 750, 1000] }

function Scaling() {
  const [algorithm, setAlgorithm] = useState('merge_sort')
  const [set, setSet] = useState('Medianos')
  const req = useRequest((signal) => api.scaling({ algorithm, sizes: SIZE_SETS[set] }, signal), [], false)
  const runs = req.data?.runs || []
  const capped = runs.length > 0 && new Set(runs.map((r) => r.input_size_used)).size < runs.length

  return (
    <>
      <div className="controls">
        <div className="field">
          <label>Algoritmo</label>
          <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
            {ALGOS.map(([k, l]) => <option key={k} value={k}>{l}</option>)}
          </select>
        </div>
        <Segmented label="Tamaños" options={Object.keys(SIZE_SETS)} value={set} onChange={setSet} />
        <button className="btn" onClick={req.run} disabled={req.loading}>Medir</button>
      </div>
      <ErrorBox message={req.error} />
      {req.loading && <Loader text="Midiendo…" />}
      {!req.data && !req.loading && !req.error && <Empty>Elige un algoritmo y mide cómo crece su costo al aumentar N.</Empty>}
      {req.data && !req.loading && (
        <>
          <p style={{ color: 'var(--muted)' }}>Complejidad teórica: <code>{req.data.theoretical_complexity}</code></p>
          {capped && <div className="warning">Este algoritmo limita su entrada máxima por su costo, así que los últimos tamaños se repiten.</div>}
          <div className="cols">
            <div className="panel"><h3 style={{ fontSize: 15, marginBottom: 8 }}>Operaciones vs N</h3>
              <LineChart color="var(--warn)" yLabel="operaciones" points={runs.map((r) => ({ x: r.input_size_used, y: r.total_operations }))} /></div>
            <div className="panel"><h3 style={{ fontSize: 15, marginBottom: 8 }}>Tiempo (ms) vs N</h3>
              <LineChart yLabel="tiempo" points={runs.map((r) => ({ x: r.input_size_used, y: r.execution_time_ms }))} /></div>
          </div>
          <div className="panel table-wrap" style={{ marginTop: 18 }}>
            <table className="table">
              <thead><tr><th>N</th><th>Tiempo (ms)</th><th>Memoria (KB)</th><th>Operaciones</th></tr></thead>
              <tbody>{runs.map((r, i) => (
                <tr key={i}><td>{r.input_size_used}</td><td>{r.execution_time_ms}</td><td>{r.peak_memory_kb}</td><td>{r.total_operations.toLocaleString('es')}</td></tr>
              ))}</tbody>
            </table>
          </div>
        </>
      )}
    </>
  )
}
