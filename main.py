"""Smart Courier Planner - CLI.
  python main.py                       -> run data/sample.json
  python main.py --input my.json       -> your own data
  python main.py --random 40 --nodes 20 -> random large scenario (uses approximation)
  python main.py --output result.json  -> save full result
"""
import argparse, json
from courier.planner import plan
from courier.generator import generate


def show(r):
    print("=" * 64)
    print(" SMART COURIER PLAN")
    print("=" * 64)
    print("Parcel order after sorting (priority, deadline):")
    print("  ", ", ".join(r["sorted_order"]))
    for t in r["trips"]:
        print(f"\n--- Trip {t['trip']} | load {t['weight']}/{r['capacity']} kg | value {t['value']}")
        print("  Parcels      :", ", ".join(t["parcels"]))
        print("  Pack order   :", " -> ".join(t["pack_order_LIFO"]), "(first loaded -> last loaded)")
        print("  Algorithm    :", t["method"])
        print("  Stop order   :", " -> ".join(t["route"]))
        print("  Road path    :", " -> ".join(t["road_path"]))
        print(f"  Distance     : {t['distance']}  (naive order: {t['baseline_distance']})")
    b = r["bin_packing"]
    print("\n" + "-" * 64)
    print(f"Trips used: {len(r['trips'])} | FFD bins: {b['ffd_bins']} | lower bound: {b['lower_bound']}")
    print(f"Total distance: {r['total_distance']} vs naive {r['baseline_total']} "
          f"-> saved {r['saving_pct']}%")
    if r["too_heavy"]:
        print("Too heavy for vehicle :", ", ".join(r["too_heavy"]))
    if r["undeliverable"]:
        print("Unreachable address   :", ", ".join(r["undeliverable"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/sample.json")
    ap.add_argument("--output")
    ap.add_argument("--random", type=int, help="number of random parcels")
    ap.add_argument("--nodes", type=int, default=18)
    ap.add_argument("--capacity", type=int, default=60)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--exact-limit", type=int, default=12)
    a = ap.parse_args()
    if a.random:
        data = generate(a.nodes, a.random, a.capacity, a.seed)
    else:
        with open(a.input) as f:
            data = json.load(f)
    result = plan(data, a.exact_limit)
    show(result)
    if a.output:
        with open(a.output, "w") as f:
            json.dump(result, f, indent=2)
        print("Saved ->", a.output)
