from dataclasses import dataclass


@dataclass(frozen=True)
class Parcel:
    id: str
    dest: str          # delivery node in the road graph
    weight: int        # kg (integer so the knapsack DP table works)
    priority: int = 1  # 1 (low) .. 5 (express)
    deadline: int = 24 # hours from now

    @property
    def value(self) -> int:
        """Benefit of loading this parcel now: high priority + tight deadline = high value."""
        return self.priority * 10 + max(0, 24 - self.deadline)
