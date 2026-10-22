class UnionFind:
    def __init__(self, nodes):
        self.parent = {node: node for node in nodes}
        self.rank = {node: 0 for node in nodes}
        self.operations = 0

    def find(self, i):
        # Iterativo con compresión de caminos (path halving): evita la recursión profunda
        while self.parent[i] != i:
            self.operations += 1
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)

        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                root_i, root_j = root_j, root_i
            self.parent[root_j] = root_i
            if self.rank[root_i] == self.rank[root_j]:
                self.rank[root_i] += 1
            return True
        return False


class MSTClustering:
    def __init__(self):
        self.operation_count = 0

    def kruskal_mst(self, nodes: list, edges: list) -> list:
        """
        Construye el MST para encontrar las conexiones mínimas clave en la red.
        edges: list of tuples (weight, node1, node2)
        Complejidad: O(E log E)
        """
        self.operation_count = 0
        uf = UnionFind(nodes)
        sorted_edges = sorted(edges, key=lambda x: x[0])
        mst = []

        for weight, u, v in sorted_edges:
            self.operation_count += 1
            if uf.union(u, v):
                mst.append((u, v, weight))

        self.operation_count += uf.operations
        return mst

    def get_clusters_ufds(self, nodes: list, connections: list) -> dict:
        """
        Agrupa usuarios en comunidades utilizando UFDS.
        """
        uf = UnionFind(nodes)
        for u, v in connections:
            uf.union(u, v)

        clusters = {}
        for node in nodes:
            root = uf.find(node)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(node)

        self.operation_count = uf.operations
        return clusters

    def mst_clusters(self, nodes: list, edges: list, k: int) -> tuple:
        """
        Clustering por MST (single-linkage): Kruskal se detiene cuando quedan k componentes,
        lo que equivale a construir el MST y eliminar sus k-1 aristas más pesadas.
        edges: [(peso, u, v)]. Devuelve (clusters {raíz: [nodos]}, aristas_del_mst_usadas).
        """
        uf = UnionFind(nodes)
        components = len(nodes)
        used = []
        for weight, u, v in sorted(edges, key=lambda x: x[0]):
            self.operation_count += 1
            if components <= k:
                break
            if uf.union(u, v):
                used.append((u, v, weight))
                components -= 1

        clusters = {}
        for node in nodes:
            clusters.setdefault(uf.find(node), []).append(node)
        self.operation_count += uf.operations
        return clusters, used
