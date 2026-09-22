class UnionFind:
    def __init__(self, nodes):
        self.parent = {node: node for node in nodes}
        self.rank = {node: 0 for node in nodes}
        self.operations = 0

    def find(self, i):
        self.operations += 1
        if self.parent[i] == i:
            return i
        # Compresión de caminos (Path Compression)
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        self.operations += 1
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