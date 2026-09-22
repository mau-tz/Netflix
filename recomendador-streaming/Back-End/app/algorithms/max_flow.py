from collections import deque

class MaxFlowAllocator:
    def __init__(self):
        self.operation_count = 0

    def edmonds_karp(self, capacity_matrix: dict, source: str, sink: str) -> tuple:
        """
        Calcula el Flujo Máximo de asignación de contenido usando BFS (Edmonds-Karp).
        Complejidad: O(V * E^2)
        """
        self.operation_count = 0
        # Crear grafo residual
        residual = {}
        for u in capacity_matrix:
            residual[u] = {}
            for v, cap in capacity_matrix[u].items():
                residual[u][v] = cap
                if v not in residual:
                    residual[v] = {}
                if u not in residual[v]:
                    residual[v][u] = 0

        parent = {}
        max_flow = 0

        def bfs():
            nonlocal parent
            parent = {}
            queue = deque([source])
            while queue:
                u = queue.popleft()
                self.operation_count += 1
                if u == sink:
                    return True
                for v, cap in residual.get(u, {}).items():
                    if v not in parent and cap > 0:
                        parent[v] = u
                        queue.append(v)
            return False

        while bfs():
            path_flow = float('Inf')
            s = sink
            while s != source:
                path_flow = min(path_flow, residual[parent[s]][s])
                s = parent[s]

            max_flow += path_flow
            v = sink
            while v != source:
                u = parent[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow
                v = parent[v]

        return max_flow, residual