import osmnx as ox
import networkx as nx
from disaster_prone_locations import get_locations_for


def get_route(place_name, dist=1500):
    print(f"Downloading road network around: {place_name}")
    G = ox.graph_from_address(place_name, dist=dist, network_type="drive")
    G = ox.truncate.largest_component(G, strongly=True)
    print(f"Graph ready: {len(G.nodes)} nodes, {len(G.edges)} edges")
    return G


def find_shortest_path(G, start_node, end_node):
    route = nx.shortest_path(G, start_node, end_node, weight="length")
    route_length = nx.shortest_path_length(G, start_node, end_node, weight="length")
    return route, route_length


def test_location(place_name, output_filename):
    print(f"\n{'='*50}")
    print(f"Testing: {place_name}")
    print('='*50)

    G = get_route(place_name)

    nodes = list(G.nodes)
    start_node = nodes[0]
    end_node = nodes[len(nodes) // 2]

    route, route_length = find_shortest_path(G, start_node, end_node)

    print(f"Route from node {start_node} to node {end_node}:")
    print(f"Total distance: {route_length:.2f} meters")

    ox.plot_graph_route(G, route, show=False, close=False, save=True, filepath=output_filename)
    print(f"Route map saved as {output_filename}")


if __name__ == "__main__":
    test_location(get_locations_for("flood")[0], "route_flood_kochi.png")
    test_location(get_locations_for("cyclone")[0], "route_cyclone_puri.png")
    test_location(get_locations_for("earthquake")[0], "route_earthquake_dehradun.png")
    test_location(get_locations_for("landslide")[0], "route_landslide_wayanad.png")