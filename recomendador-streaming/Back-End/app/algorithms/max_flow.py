from collections import deque


class MaxFlowAllocator:
    def __init__(self):
        self.operation_count = 0

    def edmonds_karp(self, capacity_matrix: dict, source: str, sink: str) -> tuple:
        """
        Flujo Máximo (Ford-Fulkerson con BFS = Edmonds-Karp).
        capacity_matrix: {u: {v: capacidad}}
        Complejidad: O(V * E^2)
        Devuelve (flujo_máximo, grafo_residual).
        """
        self.operation_count = 0
        # Grafo residual: primero se registran todos los nodos y luego las capacidades,
        # para no pisar las aristas inversas ya creadas.
        residual = {}
        for u, neighbors in capacity_matrix.items():
            residual.setdefault(u, {})
            for v in neighbors:
                residual.setdefault(v, {})
        for u, neighbors in capacity_matrix.items():
            for v, cap in neighbors.items():
                residual[u][v] = residual[u].get(v, 0) + cap
                residual[v].setdefault(u, 0)

        if source not in residual or sink not in residual or source == sink:
            return 0, residual

        max_flow = 0
        while True:
            parent = {source: None}
            queue = deque([source])
            while queue and sink not in parent:
                u = queue.popleft()
                self.operation_count += 1
                for v, cap in residual[u].items():
                    if v not in parent and cap > 0:
                        parent[v] = u
                        queue.append(v)
            if sink not in parent:
                break

            path_flow = float("inf")
            v = sink
            while v != source:
                path_flow = min(path_flow, residual[parent[v]][v])
                v = parent[v]

            v = sink
            while v != source:
                u = parent[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow
                v = u
            max_flow += path_flow

        return max_flow, residual

    @staticmethod
    def get_flow_edges(capacity_matrix: dict, residual: dict) -> dict:
        """Flujo realmente enviado por cada arista original: {(u, v): flujo}."""
        flows = {}
        for u, neighbors in capacity_matrix.items():
            for v, cap in neighbors.items():
                sent = cap - residual[u][v]
                if sent > 0:
                    flows[(u, v)] = sent
        return flows
