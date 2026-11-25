"""Random scenario generator for stress-testing larger inputs."""
import random


def generate(n_nodes=18, n_parcels=40, capacity=60, seed=1):
    rnd = random.Random(seed)
    nodes = ["Depot"] + [f"N{i}" for i in range(1, n_nodes)]
    edges = [[nodes[i], nodes[rnd.randrange(i)], rnd.randint(2, 15)] for i in range(1, n_nodes)]
    for _ in range(n_nodes):
        a, b = rnd.sample(nodes, 2)
        edges.append([a, b, rnd.randint(2, 20)])
    parcels = [{"id": f"P{i:03d}", "dest": rnd.choice(nodes[1:]), "weight": rnd.randint(2, 25),
                "priority": rnd.randint(1, 5), "deadline": rnd.randint(2, 24)}
               for i in range(1, n_parcels + 1)]
    return {"depot": "Depot", "vehicle_capacity": capacity, "edges": edges, "parcels": parcels}
