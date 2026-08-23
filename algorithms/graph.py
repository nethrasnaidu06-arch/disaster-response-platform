import heapq

# A small fake "city" graph.
# Each key is a location (node), and its value is a dict of
# neighboring locations with the distance (in km) to reach them.
graph = {
    "A": {"B": 4, "C": 2},
    "B": {"A": 4, "C": 1, "D": 5},
    "C": {"A": 2, "B": 1, "D": 8, "E": 10},
    "D": {"B": 5, "C": 8, "E": 2, "F": 6},
    "E": {"C": 10, "D": 2, "F": 3},
    "F": {"D": 6, "E": 3},
}


def dijkstra(graph, start, end):
    # distances[node] = shortest known distance from start to node
    distances = {node: float("inf") for node in graph}
    distances[start] = 0

    # to reconstruct the path at the end
    previous = {node: None for node in graph}

    # priority queue of (distance, node) — heapq always pops the smallest first
    pq = [(0, start)]
    visited = set()

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == end:
            break

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    # Reconstruct path by walking backwards from end to start
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()

    return path, distances[end]


if __name__ == "__main__":
    start_node = "A"
    end_node = "F"
    path, total_distance = dijkstra(graph, start_node, end_node)
    print(f"Shortest path from {start_node} to {end_node}: {' -> '.join(path)}")
    print(f"Total distance: {total_distance} km")