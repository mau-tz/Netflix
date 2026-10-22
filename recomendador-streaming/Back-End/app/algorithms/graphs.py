import heapq
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
        Versión iterativa (sin recursión) para no exceder el límite de Python en grafos grandes.
        Complejidad: O(V + E)
        """
        self.operation_count = 0
        index = 0
        stack = []
        indices = {}
        lowlink = {}
        on_stack = set()
        sccs = []

        def targets(node):
            return iter([n['node'] if isinstance(n, dict) else n for n in graph.get(node, [])])

        def visit(node):
            nonlocal index
            indices[node] = lowlink[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)
            self.operation_count += 1

        for root in graph:
            if root in indices:
                continue
            visit(root)
            work = [(root, targets(root))]
            while work:
                node, neighbors = work[-1]
                descended = False
                for target in neighbors:
                    self.operation_count += 1
                    if target not in indices:
                        visit(target)
                        work.append((target, targets(target)))
                        descended = True
                        break
                    elif target in on_stack:
                        lowlink[node] = min(lowlink[node], indices[target])
                if descended:
                    continue

                work.pop()
                if work:
                    parent = work[-1][0]
                    lowlink[parent] = min(lowlink[parent], lowlink[node])
                if lowlink[node] == indices[node]:
                    scc = []
                    while True:
                        w = stack.pop()
                        on_stack.remove(w)
                        scc.append(w)
                        if w == node:
                            break
                    sccs.append(scc)

        return sccs

    def topological_sort(self, graph: dict, priority: dict = None) -> tuple:
        """
        Ordenamiento topológico (algoritmo de Kahn) de un grafo dirigido {nodo: [sucesores]}.
        Entre los nodos disponibles se elige primero el de menor 'priority' (p. ej. fecha de
        estreno), por lo que el resultado es determinista.
        Devuelve (orden, hay_ciclo). Si hay ciclo, 'orden' solo contiene los nodos ordenables.
        Complejidad: O((V + E) log V)
        """
        self.operation_count = 0
        priority = priority or {}
        nodes = set(graph)
        for successors in graph.values():
            nodes.update(successors)

        in_degree = {n: 0 for n in nodes}
        for u in graph:
            for v in graph[u]:
                self.operation_count += 1
                in_degree[v] += 1

        heap = [(priority.get(n, 0), str(n), n) for n in nodes if in_degree[n] == 0]
        heapq.heapify(heap)
        order = []
        while heap:
            _, _, u = heapq.heappop(heap)
            self.operation_count += 1
            order.append(u)
            for v in graph.get(u, []):
                self.operation_count += 1
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    heapq.heappush(heap, (priority.get(v, 0), str(v), v))

        return order, len(order) != len(nodes)
