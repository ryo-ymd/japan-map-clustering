import pyrosm
import networkx as nx
from geopy.distance import geodesic


# made by ChatGPT
def calculate_move_ease_of_two_points_osm(point_a, point_b):
    # OpenStreetMapのデータをダウンロード
    bbox = [point_a[1], point_a[0], point_b[1], point_b[0]]
    osm = pyrosm.OSM(filepath="japan-latest.osm.pbf", bounding_box=bbox)

    # OSMのネットワークグラフを作成
    G = nx.MultiDiGraph()
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    G.add_nodes_from(nodes.items())
    G.add_edges_from(edges)

    # 2地点間の距離と最短経路を計算
    distance = geodesic(point_a, point_b).km
    try:
        shortest_path = nx.shortest_path(G, source=point_a, target=point_b, weight="length")
    except nx.NetworkXNoPath:
        return 0.0

    # 移動簡易性を計算
    ease_of_move = 1.0 - (len(shortest_path) * 0.1 / distance)
    if ease_of_move < 0:
        ease_of_move = 0.0

    return ease_of_move
