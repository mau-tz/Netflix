from collections import deque

class GraphAlgorithms:
    def __init__(self):
        self.operation_count = 0

    def bfs_recommendations(self, graph: dict, start_node: str, max_depth: int = 2) -> list:
        """
        Explora el grafo (BFS) desde un usuario/película para encontrar contenidos o usuarios a K saltos.
        Complejidad: O(V + E)
        """
        self.operation_count = 0
        visited = {start_node}
        queue = deque([(start_node, 0)])
        recommendations = []

        while queue:
            current, depth = queue.popleft()
            self.operation_count += 1

            if 0 < depth <= max_depth:
                recommendations.append((current, depth))

            if depth < max_depth:
                for neighbor in graph.get(current, []):
                    self.operation_count += 1
                    node_id = neighbor['node'] if isinstance(neighbor, dict) else neighbor
                    if node_id not in visited:
                        visited.add(node_id)
                        queue.append((node_id, depth + 1))

        return recommendations

    def find_scc_tarjan(self, graph: dict) -> list:
        """
        Identifica Comunidades (Componentes Fuertemente Conectados) en un grafo dirigido.
        Complejidad: O(V + E)
        """
        self.operation_count = 0
        index = 0
        stack = []
        indices = {}
        lowlink = {}
        on_stack = set()
        sccs = []

        def strongconnect(node):
            nonlocal index
            self.operation_count += 1
            indices[node] = index
            lowlink[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)

            for neighbor in graph.get(node, []):
                target = neighbor['node'] if isinstance(neighbor, dict) else neighbor
                if target not in indices:
                    strongconnect(target)
                    lowlink[node] = min(lowlink[node], lowlink[target])
                elif target in on_stack:
                    lowlink[node] = min(lowlink[node], indices[target])

            if lowlink[node] == indices[node]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == node:
                        break
                sccs.append(scc)

        for node in graph:
            if node not in indices:
                strongconnect(node)

        return sccs