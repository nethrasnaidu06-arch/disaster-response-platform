import osmnx as ox
import sys
import os

# Let this file import from the algorithms folder
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algorithms.astar import dijkstra, astar

# Simple in-memory cache: once we've downloaded a graph for an area,
# reuse it instead of re-downloading on every request.
_graph_cache = {}


def get_graph_for_area(place_name, dist=5000):
    """
    Downloads (or reuses a cached) road network graph for the given area.
    """
    print(f"DEBUG: get_graph_for_area called with dist={dist}")
    cache_key = f"{place_name}_{dist}"

    if cache_key in _graph_cache:
        print(f"Using cached graph for: {place_name}")
        return _graph_cache[cache_key]

    print(f"Downloading graph for: {place_name}")
    G = ox.graph_from_address(place_name, dist=dist, network_type="drive")
    G = ox.truncate.largest_component(G, strongly=True)

    _graph_cache[cache_key] = G
    return G


def find_route(place_name, start_lat, start_lon, end_lat, end_lon, algorithm="astar"):
    """
    Finds the shortest path between two coordinates within a given area,
    using either Dijkstra or A*. Downloads ONE graph and uses it for
    both the start and end point lookups.
    """
    G = get_graph_for_area(place_name, dist=5000)

    # Find the nearest actual road-network node to each given coordinate,
    # using the SAME graph for both.
    start_node = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
    end_node = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)

    print(f"DEBUG: start_node={start_node}, end_node={end_node}")
    print(f"DEBUG: graph has {len(G.nodes)} nodes total")

    if algorithm == "dijkstra":
        path, distance, nodes_expanded = dijkstra(G, start_node, end_node)
    else:
        path, distance, nodes_expanded = astar(G, start_node, end_node)

    return {
        "algorithm": algorithm,
        "start_node": start_node,
        "end_node": end_node,
        "distance_meters": round(distance, 2),
        "nodes_expanded": nodes_expanded,
        "path_length": len(path),
    }