# Project Report - Smart Courier Planner

## 1. Problem
A courier has parcels with weights, priorities, deadlines and destinations on a road network.
Vehicles have limited capacity. Decide (a) what to load on each trip, (b) in which order,
(c) which route to drive. This combines **knapsack**, **bin packing** and the **travelling salesman problem (TSP)**,
the last two being NP-hard, so exact DP is used for small inputs and approximations for large ones.

## 2. Algorithms, complexity and guarantees
| Step | Algorithm | Time | Space | Quality |
|---|---|---|---|---|
| Parcel ordering | Merge sort (stable) | O(n log n) | O(n) | exact |
| Alt. sort | Randomized quick sort | O(n log n) expected | O(n) | exact |
| Shortest paths | Dijkstra (binary heap) | O((V+E) log V) | O(V) | exact |
| Verification | Floyd-Warshall | O(V^3) | O(V^2) | exact |
| Load selection | 0/1 knapsack DP | O(nW) | O(nW) | optimal per trip |
| Bin count estimate | First-Fit-Decreasing | O(n^2) | O(n) | <= 11/9 OPT + 6/9 |
| Exact route | Held-Karp DP | O(n^2 2^n) | O(n 2^n) | optimal |
| Approx route | MST + preorder walk | O(n^2) | O(n) | <= 2 x OPT (metric) |
| Improvement | 2-opt | O(n^2) per pass | O(n) | never worse than input |

**Why the 2-approximation holds:** distances come from shortest paths, so they satisfy the triangle inequality.
Deleting one edge of the optimal tour leaves a spanning tree, so MST <= OPT. A full walk of the MST costs 2 x MST,
and shortcutting repeated vertices cannot increase cost (triangle inequality). Hence cost <= 2 x OPT.

**Greedy-per-trip note:** repeatedly solving knapsack gives each trip the best possible value given what remains
(urgent parcels first), but the total trip count is not guaranteed minimal; FFD and the weight lower bound
are reported so the gap is visible.

## 3. Design decisions
- Metric closure (Dijkstra distances) lets the TSP solvers work on a complete graph even if the road graph is sparse.
- LIFO loading: parcels for the last stop are loaded first so the first stop is reachable at the door.
- Edge cases: parcel heavier than vehicle, unreachable address, depot as destination, zero stops.

## 4. Testing (`tests/test_all.py`, 9 tests)
Sorts vs Python `sorted`; stability; Dijkstra vs Floyd-Warshall; Held-Karp vs brute-force permutations;
MST bound <= 2 x OPT; knapsack vs brute-force subsets; FFD validity and bound; end-to-end sample and large-scale runs.

## 5. Sample result (data/sample.json)
3 trips, FFD bins = lower bound = 3, total distance 97 vs 102 for naive order (4.9% saved);
P14 flagged as too heavy and P13 as unreachable. Random 40-parcel case: 15.4% distance saving.

## 6. Limitations and future work
Deadlines influence loading priority but not stop order inside a trip (time-window TSP would be next);
single vehicle type; static distances (no live traffic); possible extensions: multiple vehicles in parallel,
volume constraints (3D packing), a map visualization, and a web UI.
