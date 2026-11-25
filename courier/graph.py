"""GRAPH module: road network, Dijkstra, Floyd-Warshall, Prim MST."""
import heapq
from collections import defaultdict
from typing import Dict, List, Tuple

INF = float("inf")


class Graph:
    def __init__(self):
        self.adj: Dict[str, List[Tuple[str, float]]] = defaultdict(list)

    def add_edge(self, u, v, w):
        self.adj[u].append((v, w))
        self.adj[v].append((u, w))

    @property
    def nodes(self):
        return list(self.adj.keys())

    def dijkstra(self, src):
        """Single-source shortest paths, O((V+E) log V). Returns (dist, prev)."""
        dist = {n: INF for n in self.adj}
        prev = {}
        dist[src] = 0
        pq = [(0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in self.adj[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v], prev[v] = nd, u
                    heapq.heappush(pq, (nd, v))
        return dist, prev

    def shortest_path(self, src, dst):
        dist, prev = self.dijkstra(src)
        if dist[dst] == INF:
            return INF, []
        path, cur = [dst], dst
        while cur != src:
            cur = prev[cur]
            path.append(cur)
        return dist[dst], path[::-1]

    def floyd_warshall(self):
        """All-pairs shortest paths, O(V^3) (DP over intermediate vertices)."""
        ns = self.nodes
        d = {a: {b: (0 if a == b else INF) for b in ns} for a in ns}
        for u in ns:
            for v, w in self.adj[u]:
                d[u][v] = min(d[u][v], w)
        for k in ns:
            for i in ns:
                for j in ns:
                    if d[i][k] + d[k][j] < d[i][j]:
                        d[i][j] = d[i][k] + d[k][j]
        return d


def prim_mst(nodes: List[str], dist, root):
    """Prim's MST on the complete metric graph, O(V^2). Returns child-lists."""
    best = {n: (dist[root][n], root) for n in nodes if n != root}
    children = defaultdict(list)
    while best:
        n = min(best, key=lambda x: best[x][0])
        _, parent = best.pop(n)
        children[parent].append(n)
        for m in best:
            if dist[n][m] < best[m][0]:
                best[m] = (dist[n][m], n)
    return children
