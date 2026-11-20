import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Ejecuta una petición cancelable.
 *  - auto=true: se ejecuta sola al montar y cada vez que cambian `deps`.
 *  - auto=false: solo cuando se llama a run() (botones "Calcular").
 * Una petición nueva cancela la anterior, así no llegan respuestas viejas fuera de orden.
 */
export function useRequest(fetcher, deps = [], auto = true) {
  const [state, setState] = useState({ data: null, loading: auto, error: null })
  const controller = useRef(null)
  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  const run = useCallback(async () => {
    controller.current?.abort()
    const current = new AbortController()
    controller.current = current
    setState((s) => ({ ...s, loading: true, error: null }))
    try {
      const data = await fetcherRef.current(current.signal)
      if (!current.signal.aborted) setState({ data, loading: false, error: null })
      return data
    } catch (err) {
      if (err.name === 'AbortError') return null
      setState({ data: null, loading: false, error: err.message })
      return null
    }
  }, [])

  useEffect(() => {
    if (auto) run()
    return () => controller.current?.abort()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, auto ? deps : [])

  return { ...state, run }
}

export function useDebounced(value, delay = 300) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(id)
  }, [value, delay])
  return debounced
}
