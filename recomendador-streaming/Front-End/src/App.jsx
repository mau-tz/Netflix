import { Component, useEffect, useState } from 'react'
import { MovieModalProvider } from './components/MovieModal'
import Home from './views/Home'
import Explore from './views/Explore'
import ForYou from './views/ForYou'
import Plan from './views/Plan'
import Sagas from './views/Sagas'
import Niches from './views/Niches'
import Discover from './views/Discover'
import Allocate from './views/Allocate'
import Analysis from './views/Analysis'

const NAV = [
  { group: 'Descubrir', items: [
    { id: 'home', label: 'Top del catálogo', view: Home },
    { id: 'explore', label: 'Explorar', view: Explore },
    { id: 'foryou', label: 'Para ti', view: ForYou },
  ] },
  { group: 'Planificar', items: [
    { id: 'plan', label: 'Maratón y combinaciones', view: Plan },
    { id: 'sagas', label: 'Sagas', view: Sagas },
  ] },
  { group: 'Explorar el grafo', items: [
    { id: 'discover', label: 'Conexiones', view: Discover },
    { id: 'niches', label: 'Nichos', view: Niches },
  ] },
  { group: 'Plataforma', items: [
    { id: 'allocate', label: 'Reparto justo', view: Allocate },
    { id: 'analysis', label: 'Rendimiento', view: Analysis },
  ] },
]
// Evita que un error en una vista deje toda la pantalla en blanco.
class Boundary extends Component {
  state = { error: null }
  static getDerivedStateFromError(error) { return { error } }
  render() {
    if (this.state.error) {
      return <div className="error">Algo salió mal en esta vista: {this.state.error.message}. Cambia de sección o recarga la página.</div>
    }
    return this.props.children
  }
}

const ITEMS = NAV.flatMap((g) => g.items)

const initial = () => {
  const hash = window.location.hash.slice(1)
  return ITEMS.some((i) => i.id === hash) ? hash : 'home'
}

export default function App() {
  const [current, setCurrent] = useState(initial)
  useEffect(() => { window.location.hash = current; window.scrollTo(0, 0) }, [current])
  const View = ITEMS.find((i) => i.id === current).view

  return (
    <MovieModalProvider>
      <div className="app">
        <nav className="sidebar" aria-label="Navegación principal">
          <div className="brand"><span className="brand-logo">▶</span>Netflix</div>
          {NAV.map((g) => (
            <div key={g.group} style={{ display: 'contents' }}>
              <div className="nav-group">{g.group}</div>
              {g.items.map((i) => (
                <button key={i.id} className={`nav-item ${i.id === current ? 'active' : ''}`} onClick={() => setCurrent(i.id)}>
                  {i.label}
                </button>
              ))}
            </div>
          ))}
        </nav>
        <main className="main"><Boundary key={current}><View /></Boundary></main>
      </div>
    </MovieModalProvider>
  )
}
