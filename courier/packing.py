"""PACKING module: 0/1 knapsack (DP) and bin packing (First-Fit-Decreasing approximation)."""
import math
from .sorting import merge_sort


def knapsack_01(weights, values, capacity):
    """DYNAMIC PROGRAMMING, O(n*W). Returns (best_value, chosen_indices)."""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]
            if w <= c and dp[i - 1][c - w] + v > dp[i][c]:
                dp[i][c] = dp[i - 1][c - w] + v
    chosen, c = [], capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            chosen.append(i - 1)
            c -= weights[i - 1]
    return dp[n][capacity], chosen[::-1]


def first_fit_decreasing(weights, capacity):
    """APPROXIMATION for bin packing: FFD uses <= 11/9 * OPT + 6/9 bins.
    Returns list of bins, each a list of item indices."""
    order = merge_sort(list(range(len(weights))), key=lambda i: -weights[i])
    bins, free = [], []
    for i in order:
        for b in range(len(bins)):
            if weights[i] <= free[b]:
                bins[b].append(i); free[b] -= weights[i]
                break
        else:
            bins.append([i]); free.append(capacity - weights[i])
    return bins


def plan_loads(parcels, capacity):
    """Fill vehicle trips one at a time; each trip is the value-optimal knapsack
    of what remains, so urgent parcels ride first. Returns (loads, unassignable)."""
    unassignable = [p for p in parcels if p.weight > capacity]
    remaining = [p for p in parcels if p.weight <= capacity]
    loads = []
    while remaining:
        _, idx = knapsack_01([p.weight for p in remaining],
                             [p.value for p in remaining], capacity)
        if not idx:  # safety: zero-weight edge cases
            idx = [0]
        loads.append([remaining[i] for i in idx])
        chosen = set(idx)
        remaining = [p for i, p in enumerate(remaining) if i not in chosen]
    return loads, unassignable


def bin_stats(parcels, capacity):
    ws = [p.weight for p in parcels if p.weight <= capacity]
    return {"ffd_bins": len(first_fit_decreasing(ws, capacity)),
            "lower_bound": math.ceil(sum(ws) / capacity) if ws else 0}
