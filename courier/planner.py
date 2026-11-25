"""PIPELINE: sort -> pack (DP) -> shortest paths (graph) -> route (DP / approx)."""
from .models import Parcel
from .sorting import sort_parcels
from .graph import Graph, INF
from .packing import plan_loads, bin_stats
from .routing import solve_route, route_cost


def expand_path(graph, route):
    """Turn stop-to-stop route into the actual road-by-road path."""
    full = [route[0]]
    for a, b in zip(route, route[1:]):
        _, p = graph.shortest_path(a, b)
        full.extend(p[1:])
    return full


def plan(data, exact_limit=12):
    g = Graph()
    for u, v, w in data["edges"]:
        g.add_edge(u, v, w)
    depot, cap = data["depot"], data["vehicle_capacity"]
    parcels = sort_parcels([Parcel(**p) for p in data["parcels"]])

    reach, _ = g.dijkstra(depot)
    undeliverable = [p for p in parcels if reach.get(p.dest, INF) == INF]
    parcels = [p for p in parcels if p not in undeliverable]

    loads, too_heavy = plan_loads(parcels, cap)
    needed = {depot} | {p.dest for p in parcels}
    dist = {n: g.dijkstra(n)[0] for n in needed}   # metric closure

    trips, total, base_total = [], 0, 0
    for k, load in enumerate(loads, 1):
        load = sort_parcels(load)
        stops = sorted({p.dest for p in load} - {depot})
        res = solve_route(dist, depot, stops, exact_limit)
        # baseline = visit stops in plain priority order, no optimisation
        naive, seen = [depot], set()
        for p in load:
            if p.dest not in seen and p.dest != depot:
                seen.add(p.dest); naive.append(p.dest)
        naive.append(depot)
        base = route_cost(dist, naive)
        order = res["route"]
        pos = {n: i for i, n in enumerate(order[:-1])}
        lifo = sorted(load, key=lambda p: -pos.get(p.dest, 0))  # last stop loaded first
        trips.append({
            "trip": k, "parcels": [p.id for p in load],
            "pack_order_LIFO": [p.id for p in lifo],
            "weight": sum(p.weight for p in load), "value": sum(p.value for p in load),
            "method": res["method"], "route": order,
            "road_path": expand_path(g, order),
            "distance": res["cost"], "baseline_distance": base,
        })
        total += res["cost"]; base_total += base
    return {
        "capacity": cap, "trips": trips,
        "total_distance": total, "baseline_total": base_total,
        "saving_pct": round(100 * (base_total - total) / base_total, 1) if base_total else 0,
        "bin_packing": bin_stats(parcels, cap),
        "too_heavy": [p.id for p in too_heavy],
        "undeliverable": [p.id for p in undeliverable],
        "sorted_order": [p.id for p in parcels],
    }
