import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algorithms.allocation import allocate_resources


def run_allocation(victims, resources):
    """
    Takes victims and resources (each a list of dicts with 'name' and
    'location': [lat, lon]) and returns the optimal assignment using
    the Hungarian algorithm.
    """
    # Convert location lists back into (lat, lon) tuples,
    # since that's what the underlying algorithm expects.
    victims_formatted = [
        {"name": v["name"], "location": (v["location"][0], v["location"][1])}
        for v in victims
    ]
    resources_formatted = [
        {"name": r["name"], "location": (r["location"][0], r["location"][1])}
        for r in resources
    ]

    assignments = allocate_resources(victims_formatted, resources_formatted)
    return assignments