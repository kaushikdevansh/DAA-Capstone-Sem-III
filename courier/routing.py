"""ROUTING module: TSP - exact DP (Held-Karp) + approximation (MST 2-approx, 2-opt)."""
from .graph import prim_mst, INF


def route_cost(dist, route):
    return sum(dist[a][b] for a, b in zip(route, route[1:]))


def held_karp(dist, depot, stops):
    """EXACT dynamic programming, O(n^2 * 2^n). dp[mask][j] = cheapest way to
    visit set `mask` starting at depot and ending at stops[j]."""
    n = len(stops)
    if n == 0:
        return 0, [depot, depot]
    dp = [[INF] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]
    for j in range(n):
        dp[1 << j][j] = dist[depot][stops[j]]
    for mask in range(1, 1 << n):
        for j in range(n):
            if not mask & (1 << j) or dp[mask][j] == INF:
                continue
            for k in range(n):
                if mask & (1 << k):
                    continue
                nm = mask | (1 << k)
                c = dp[mask][j] + dist[stops[j]][stops[k]]
                if c < dp[nm][k]:
                    dp[nm][k], parent[nm][k] = c, j
    full = (1 << n) - 1
    last = min(range(n), key=lambda j: dp[full][j] + dist[stops[j]][depot])
    cost = dp[full][last] + dist[stops[last]][depot]
    order, mask, j = [], full, last
    while j != -1:
        order.append(stops[j])
        pj = parent[mask][j]
        mask ^= 1 << j
        j = pj
    return cost, [depot] + order[::-1] + [depot]


def mst_two_approx(dist, depot, stops):
    """APPROXIMATION: MST + preorder walk with shortcuts.
    On a metric (triangle inequality) cost <= 2 * OPT."""
    nodes = [depot] + list(stops)
    children = prim_mst(nodes, dist, depot)
    order, stack = [], [depot]
    while stack:
        u = stack.pop()
        order.append(u)
        stack.extend(reversed(children[u]))
    route = order + [depot]
    return route_cost(dist, route), route


def nearest_neighbor(dist, depot, stops):
    left, cur, route = set(stops), depot, [depot]
    while left:
        cur = min(left, key=lambda x: dist[cur][x])
        left.remove(cur)
        route.append(cur)
    route.append(depot)
    return route_cost(dist, route), route


def two_opt(dist, route):
    """Local-search improvement: reverse segments while it shortens the tour."""
    route = list(route)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                a, b, c, d = route[i - 1], route[i], route[j], route[j + 1]
                if dist[a][c] + dist[b][d] < dist[a][b] + dist[c][d] - 1e-9:
                    route[i:j + 1] = reversed(route[i:j + 1])
                    improved = True
    return route_cost(dist, route), route


def solve_route(dist, depot, stops, exact_limit=12):
    """Pick exact DP for small instances, approximation + 2-opt for large ones."""
    stops = list(stops)
    if len(stops) <= exact_limit:
        cost, route = held_karp(dist, depot, stops)
        return {"method": "Held-Karp (exact DP)", "cost": cost, "route": route}
    c1, r1 = mst_two_approx(dist, depot, stops)
    c2, r2 = two_opt(dist, r1)
    return {"method": "MST 2-approximation + 2-opt", "cost": c2, "route": r2,
            "mst_cost": c1, "guarantee": "<= 2 x optimal (before 2-opt)"}
