# Smart Courier Planner

## Website

1. Install Python 3.9+.
2. Open this folder in a terminal.
3. Run `python server.py`.
4. Visit `http://127.0.0.1:8000` in your browser.

The website supports the included sample, custom scenario JSON, and random scenarios. See `README_WEBSITE.md` for details.

## Command line

Run `python main.py` to use the original command-line interface.

## Planner algorithms

Given parcels + a road network, it produces **which parcels go on which trip**,
**the order to load them**, and **the shortest delivery route**.

| Requirement | Where | Technique |
|---|---|---|
| Sorting | `courier/sorting.py` | Stable merge sort (multi-key), randomized quick sort |
| Dynamic programming | `courier/packing.py`, `courier/routing.py` | 0/1 knapsack (truck load), Held-Karp (exact TSP) |
| Graph algorithms | `courier/graph.py` | Dijkstra, Floyd-Warshall, Prim MST |
| Approximation | `courier/routing.py`, `courier/packing.py` | MST 2-approx TSP + 2-opt, First-Fit-Decreasing bin packing |

## Pipeline
1. **Sort** parcels by priority (desc) -> deadline (asc) -> weight (desc).
2. **Filter** parcels that are too heavy or have an unreachable address.
3. **Pack** (DP): each trip = value-optimal knapsack of remaining parcels, so urgent parcels go first.
4. **Graph**: Dijkstra builds the shortest-distance matrix between depot and stops.
5. **Route**: <= 12 stops -> exact Held-Karp DP; more -> MST 2-approximation improved with 2-opt.
6. **Report**: route, road path, LIFO loading order, distance vs naive order, FFD bin count vs lower bound.

## Run in VS Code
1. Install Python 3.9+ (python.org) and VS Code with the **Python** extension.
2. Unzip, then **File -> Open Folder** -> `courier_planner`.
3. Open the terminal (**Ctrl + `**) and run:
   ```
   python main.py                               # sample data
   python main.py --random 40 --nodes 20        # bigger random case
   python main.py --random 80 --nodes 25 --exact-limit 4   # force the approximation path
   python main.py --output result.json          # save results
   python -m unittest discover -s tests -v      # run tests
   ```
   Or press **F5** and choose a configuration from `.vscode/launch.json`.

No third-party libraries are needed. Works the same in PyCharm, Replit, Google Colab (upload folder) or any terminal.

## Input format (`data/sample.json`)
`depot`, `vehicle_capacity` (int kg), `edges` = `[nodeA, nodeB, distance]`,
`parcels` = `{id, dest, weight, priority 1-5, deadline hours}`.

See `docs/REPORT.md` for complexity analysis and approximation guarantees.
