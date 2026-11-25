"""SORTING module: stable merge sort, randomized quick sort, parcel ordering."""
import random
from typing import Callable, List, TypeVar

T = TypeVar("T")


def merge_sort(items: List[T], key: Callable = lambda x: x) -> List[T]:
    """Stable O(n log n) merge sort."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left, right = merge_sort(items[:mid], key), merge_sort(items[mid:], key)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):   # <= keeps stability
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out


def quick_sort(items: List[T], key: Callable = lambda x: x) -> List[T]:
    """Randomized quick sort, expected O(n log n) (3-way partition)."""
    if len(items) <= 1:
        return list(items)
    pivot = key(random.choice(items))
    less = [x for x in items if key(x) < pivot]
    equal = [x for x in items if key(x) == pivot]
    more = [x for x in items if key(x) > pivot]
    return quick_sort(less, key) + equal + quick_sort(more, key)


def sort_parcels(parcels):
    """Order: highest priority first, then earliest deadline, then heavier first.
    Multi-key ordering via a tuple key (negatives give descending order)."""
    return merge_sort(parcels, key=lambda p: (-p.priority, p.deadline, -p.weight, p.id))
