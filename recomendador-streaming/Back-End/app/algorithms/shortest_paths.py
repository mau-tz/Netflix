class ShortestPaths:
    def __init__(self):
        self.operation_count = 0

    def bellman_ford(self, nodes: list, edges: list, source) -> tuple:
        """
        Bellman-Ford: caminos mínimos desde 'source'. Admite pesos negativos y detecta ciclos
        negativos alcanzables. edges: [(u, v, peso)] dirigidas.
        Termina antes si una pasada completa no relaja ninguna arista.
        Complejidad: O(V * E)
        Devuelve (dist, pred, hay_ciclo_negativo).
        """
        self.operation_count = 0
        dist = {n: float("inf") for n in nodes}
        pred = {n: None for n in nodes}
        dist[source] = 0

        for _ in range(len(nodes) - 1):
            changed = False
            for u, v, w in edges:
                self.operation_count += 1
                if dist[u] != float("inf") and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    pred[v] = u
                    changed = True
            if not changed:
                break

        for u, v, w in edges:
            self.operation_count += 1
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                return dist, pred, True
        return dist, pred, False

    @staticmethod
    def build_path(pred: dict, source, target) -> list:
        """Reconstruye source -> target a partir de los predecesores ([] si no hay camino)."""
        path, node = [], target
        while node is not None:
            path.append(node)
            if node == source:
                return path[::-1]
            node = pred[node]
        return []

    def floyd_warshall(self, nodes: list, edges: list) -> tuple:
        """
        Floyd-Warshall: distancias mínimas entre TODOS los pares. O(V^3)
        Devuelve (dist, next_hop) con dist[u][v] y next_hop[u][v] para reconstruir rutas.
        """
        self.operation_count = 0
        inf = float("inf")
        dist = {u: {v: (0 if u == v else inf) for v in nodes} for u in nodes}
        next_hop = {u: {v: None for v in nodes} for u in nodes}

        for u, v, w in edges:
            if w < dist[u][v]:
                dist[u][v] = w
                next_hop[u][v] = v

        for k in nodes:
            dist_k = dist[k]
            for i in nodes:
                dik = dist[i][k]
                if dik == inf:
                    continue
                dist_i = dist[i]
                for j in nodes:
                    self.operation_count += 1
                    if dik + dist_k[j] < dist_i[j]:
                        dist_i[j] = dik + dist_k[j]
                        next_hop[i][j] = next_hop[i][k]

        return dist, next_hop

    @staticmethod
    def floyd_path(next_hop: dict, source, target) -> list:
        if source != target and next_hop[source][target] is None:
            return []
        path = [source]
        while source != target:
            source = next_hop[source][target]
            path.append(source)
        return path
