import itertools, json, math, os, random, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from courier.sorting import merge_sort, quick_sort
from courier.graph import Graph
from courier.routing import held_karp, mst_two_approx, two_opt, route_cost
from courier.packing import knapsack_01, first_fit_decreasing
from courier.planner import plan
from courier.generator import generate


def metric(n, seed):
    g = generate(n, 1, seed=seed)
    gr = Graph()
    for u, v, w in g["edges"]:
        gr.add_edge(u, v, w)
    return {a: gr.dijkstra(a)[0] for a in gr.nodes}, gr


class Tests(unittest.TestCase):
    def test_sorts(self):
        for s in range(20):
            r = random.Random(s)
            xs = [r.randint(0, 50) for _ in range(40)]
            self.assertEqual(merge_sort(xs), sorted(xs))
            self.assertEqual(quick_sort(xs), sorted(xs))

    def test_merge_sort_stable(self):
        xs = [(1, "a"), (0, "b"), (1, "c"), (0, "d")]
        self.assertEqual(merge_sort(xs, key=lambda t: t[0]),
                         [(0, "b"), (0, "d"), (1, "a"), (1, "c")])

    def test_dijkstra_vs_floyd(self):
        dist, g = metric(10, 3)
        fw = g.floyd_warshall()
        for a in g.nodes:
            for b in g.nodes:
                self.assertAlmostEqual(dist[a][b], fw[a][b])

    def test_held_karp_optimal(self):
        dist, g = metric(9, 5)
        stops = ["N1", "N2", "N3", "N4", "N5", "N6"]
        best = min(route_cost(dist, ["Depot", *p, "Depot"]) for p in itertools.permutations(stops))
        cost, route = held_karp(dist, "Depot", stops)
        self.assertEqual(cost, best)
        self.assertEqual(route_cost(dist, route), cost)

    def test_two_approx_bound(self):
        for seed in range(8):
            dist, g = metric(9, seed)
            stops = ["N1", "N2", "N3", "N4", "N5", "N6", "N7"]
            opt, _ = held_karp(dist, "Depot", stops)
            c, route = mst_two_approx(dist, "Depot", stops)
            self.assertLessEqual(c, 2 * opt + 1e-9)
            self.assertLessEqual(two_opt(dist, route)[0], c + 1e-9)
            self.assertEqual(sorted(route[1:-1]), sorted(stops))

    def test_knapsack_optimal(self):
        rnd = random.Random(7)
        for _ in range(30):
            n = 8
            w = [rnd.randint(1, 12) for _ in range(n)]
            v = [rnd.randint(1, 30) for _ in range(n)]
            cap = 25
            best = max(sum(v[i] for i in c) for r in range(n + 1)
                       for c in itertools.combinations(range(n), r)
                       if sum(w[i] for i in c) <= cap)
            val, idx = knapsack_01(w, v, cap)
            self.assertEqual(val, best)
            self.assertLessEqual(sum(w[i] for i in idx), cap)

    def test_ffd_valid_and_bound(self):
        rnd = random.Random(2)
        w = [rnd.randint(1, 20) for _ in range(30)]
        bins = first_fit_decreasing(w, 30)
        self.assertEqual(sorted(i for b in bins for i in b), list(range(30)))
        self.assertTrue(all(sum(w[i] for i in b) <= 30 for b in bins))
        self.assertLessEqual(len(bins), 11 / 9 * math.ceil(sum(w) / 30) + 1)

    def test_pipeline_sample(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "data", "sample.json")) as f:
            r = plan(json.load(f))
        self.assertEqual(r["too_heavy"], ["P14"])
        self.assertEqual(r["undeliverable"], ["P13"])
        delivered = [p for t in r["trips"] for p in t["parcels"]]
        self.assertEqual(len(delivered), len(set(delivered)))
        self.assertEqual(len(delivered), 12)
        for t in r["trips"]:
            self.assertLessEqual(t["weight"], 50)
            self.assertLessEqual(t["distance"], t["baseline_distance"] + 1e-9)

    def test_pipeline_large_uses_approx(self):
        r = plan(generate(25, 80, 60, seed=4), exact_limit=6)
        self.assertTrue(any("approximation" in t["method"] for t in r["trips"]))


if __name__ == "__main__":
    unittest.main()
