import heapq
import math
import osmnx as ox
from disaster_prone_locations import get_locations_for


def haversine_distance(coord1, coord2):
    """
    Calculates the straight-line distance (in meters) between two
    (lat, lon) points on Earth's surface. Used as A*'s heuristic —
    it's an *underestimate* of real road distance, which is required
    for A* to guarantee the correct shortest path.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371000  # Earth's radius in meters

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (math.sin(d_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def dijkstra(G, start, end):
    """
    Our own Dijkstra implementation on the real road graph.
    Explores nodes purely by "closest so far" — no sense of direction
    toward the destination.
    """
    distances = {node: float("inf") for node in G.nodes}
    distances[start] = 0
    previous = {node: None for node in G.nodes}
    pq = [(0, start)]
    visited = set()
    nodes_expanded = 0

    while pq:
        current_distance, current_node = heapq.heappop(pq)
        if current_node in visited:
            continue
        visited.add(current_node)
        nodes_expanded += 1

        if current_node == end:
            break

        for neighbor in G.neighbors(current_node):
            edge_data = G.get_edge_data(current_node, neighbor)
            weight = min(d.get("length", 1) for d in edge_data.values())
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()

    return path, distances[end], nodes_expanded


def astar(G, start, end):
    """
    Our own A* implementation. Same idea as Dijkstra, but each node's
    priority also factors in an estimated (heuristic) distance to the
    destination — so it explores in a more "directed" way instead of
    expanding equally in all directions.
    """
    node_coords = {node: (data["y"], data["x"]) for node, data in G.nodes(data=True)}
    end_coord = node_coords[end]

    g_score = {node: float("inf") for node in G.nodes}
    g_score[start] = 0
    previous = {node: None for node in G.nodes}

    # priority queue holds (f_score, node) where f_score = g_score + heuristic
    pq = [(haversine_distance(node_coords[start], end_coord), start)]
    visited = set()
    nodes_expanded = 0

    while pq:
        _, current_node = heapq.heappop(pq)
        if current_node in visited:
            continue
        visited.add(current_node)
        nodes_expanded += 1

        if current_node == end:
            break

        for neighbor in G.neighbors(current_node):
            edge_data = G.get_edge_data(current_node, neighbor)
            weight = min(d.get("length", 1) for d in edge_data.values())
            tentative_g = g_score[current_node] + weight

            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                previous[neighbor] = current_node
                f_score = tentative_g + haversine_distance(node_coords[neighbor], end_coord)
                heapq.heappush(pq, (f_score, neighbor))

    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()

    return path, g_score[end], nodes_expanded


def compare_algorithms(place_name):
    print(f"\n{'='*60}")
    print(f"Comparing Dijkstra vs A* for: {place_name}")
    print('='*60)

    G = ox.graph_from_address(place_name, dist=1500, network_type="drive")
    G = ox.truncate.largest_component(G, strongly=True)
    print(f"Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")

    nodes = list(G.nodes)
    start = nodes[0]
    end = nodes[len(nodes) // 2]

    dijkstra_path, dijkstra_dist, dijkstra_expanded = dijkstra(G, start, end)
    astar_path, astar_dist, astar_expanded = astar(G, start, end)

    print(f"\nDijkstra: distance={dijkstra_dist:.2f}m, nodes expanded={dijkstra_expanded}")
    print(f"A*:       distance={astar_dist:.2f}m, nodes expanded={astar_expanded}")

    if dijkstra_dist == astar_dist:
        print("✅ Both algorithms found the same shortest distance (as expected).")
    else:
        print("⚠️ Distances differ — something's wrong, worth double-checking.")

    reduction = (1 - astar_expanded / dijkstra_expanded) * 100
    print(f"A* explored {reduction:.1f}% fewer nodes than Dijkstra.")


if __name__ == "__main__":
    compare_algorithms(get_locations_for("flood")[0])   # Kochi
    compare_algorithms(get_locations_for("earthquake")[0])  # Dehradun