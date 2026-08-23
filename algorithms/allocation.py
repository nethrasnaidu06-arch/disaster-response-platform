import numpy as np
from scipy.optimize import linear_sum_assignment
from math import radians, sin, cos, sqrt, atan2


def haversine_distance(coord1, coord2):
    """
    Straight-line distance in km between two (lat, lon) points.
    Used here as a stand-in for real travel distance — in the full
    system this would call the routing engine (Dijkstra/A*) instead.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Earth's radius in km

    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def build_cost_matrix(victims, resources):
    """
    Builds a matrix where cost_matrix[i][j] = distance from
    victim i to resource j. This is what the Hungarian algorithm
    needs as input.
    """
    cost_matrix = np.zeros((len(victims), len(resources)))
    for i, victim in enumerate(victims):
        for j, resource in enumerate(resources):
            cost_matrix[i][j] = haversine_distance(victim["location"], resource["location"])
    return cost_matrix


def allocate_resources(victims, resources):
    """
    Assigns each victim to a resource (rescue unit/hospital) such that
    TOTAL travel distance across all victims is minimized — this is
    the key difference from a greedy "nearest first" approach, which
    can produce a worse overall outcome even though each individual
    choice looks locally optimal.
    """
    cost_matrix = build_cost_matrix(victims, resources)

    # linear_sum_assignment solves the optimal assignment problem
    # (this IS the Hungarian algorithm, under the hood)
    victim_indices, resource_indices = linear_sum_assignment(cost_matrix)

    assignments = []
    for v_idx, r_idx in zip(victim_indices, resource_indices):
        assignments.append({
            "victim": victims[v_idx]["name"],
            "resource": resources[r_idx]["name"],
            "distance_km": round(cost_matrix[v_idx][r_idx], 2),
        })

    return assignments


def greedy_allocate(victims, resources):
    """
    For comparison: a naive greedy approach — each victim just picks
    their nearest resource, one at a time, in order. This can lead to
    a worse TOTAL outcome, since early victims "use up" the best
    resources even if a different pairing would be better overall.
    """
    cost_matrix = build_cost_matrix(victims, resources)
    used_resources = set()
    assignments = []

    for i, victim in enumerate(victims):
        best_j = None
        best_dist = float("inf")
        for j in range(len(resources)):
            if j not in used_resources and cost_matrix[i][j] < best_dist:
                best_dist = cost_matrix[i][j]
                best_j = j
        used_resources.add(best_j)
        assignments.append({
            "victim": victim["name"],
            "resource": resources[best_j]["name"],
            "distance_km": round(best_dist, 2),
        })

    return assignments


def run_comparison(victims, hospitals, label=""):
    print(f"\n{'#'*60}")
    print(f"# {label}")
    print('#'*60)

    print("\n=== Optimal Assignment (Hungarian Algorithm) ===")
    optimal = allocate_resources(victims, hospitals)
    total_optimal = 0
    for a in optimal:
        print(f"  {a['victim']} -> {a['resource']} ({a['distance_km']} km)")
        total_optimal += a["distance_km"]
    print(f"Total distance: {total_optimal:.2f} km")

    print("\n=== Greedy Assignment (nearest-first, for comparison) ===")
    greedy = greedy_allocate(victims, hospitals)
    total_greedy = 0
    for a in greedy:
        print(f"  {a['victim']} -> {a['resource']} ({a['distance_km']} km)")
        total_greedy += a["distance_km"]
    print(f"Total distance: {total_greedy:.2f} km")

    print()
    if total_optimal < total_greedy:
        savings = total_greedy - total_optimal
        print(f"✅ Optimal assignment saved {savings:.2f} km of total travel vs greedy.")
    elif total_optimal == total_greedy:
        print("Both approaches produced the same total — no conflict in this scenario.")
    else:
        print("Unexpected: greedy beat optimal, worth double-checking.")


if __name__ == "__main__":
    # Scenario 1: no real conflict — victims and hospitals are naturally
    # well-separated, so greedy happens to match optimal here.
    victims_1 = [
        {"name": "Victim A", "location": (9.9816, 76.2999)},
        {"name": "Victim B", "location": (9.9312, 76.2673)},
        {"name": "Victim C", "location": (9.9930, 76.3378)},
    ]
    hospitals_1 = [
        {"name": "Hospital 1", "location": (9.9700, 76.2900)},
        {"name": "Hospital 2", "location": (9.9350, 76.2650)},
        {"name": "Hospital 3", "location": (9.9950, 76.3400)},
    ]
    run_comparison(victims_1, hospitals_1, label="Scenario 1: Well-separated (no conflict expected)")

    # Scenario 2: deliberately conflicting — Victim A and Victim B are
    # BOTH very close to Hospital 1, but only one can go there. A greedy
    # approach lets whoever is processed FIRST grab it, even if a
    # different pairing would be better overall.
    victims_2 = [
        {"name": "Victim A", "location": (9.9700, 76.2900)},   # right next to Hospital 1
        {"name": "Victim B", "location": (9.9705, 76.2905)},   # ALSO right next to Hospital 1
        {"name": "Victim C", "location": (9.9950, 76.3400)},   # far away, near Hospital 3
    ]
    hospitals_2 = [
        {"name": "Hospital 1", "location": (9.9700, 76.2900)},  # exact match for Victim A
        {"name": "Hospital 2", "location": (9.9990, 76.3600)},  # far from everyone
        {"name": "Hospital 3", "location": (9.9950, 76.3400)},  # close to Victim C
    ]
    run_comparison(victims_2, hospitals_2, label="Scenario 2: Conflicting (optimal should beat greedy)")