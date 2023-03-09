import pyrosm
from shapely.geometry import Point, LineString
from geopy.distance import geodesic


def calculate_move_ease_of_two_points_osm(point_a, point_b):
    # japan-latest.osm.pbfのファイルパス
    filepath = "japan-latest.osm.pbf"

    # 地点Aと地点BをPointオブジェクトに変換
    point_a = Point(point_a[1], point_a[0])
    point_b = Point(point_b[1], point_b[0])

    # 地点Aと地点Bの距離を計算
    distance = geodesic((point_a.y, point_a.x), (point_b.y, point_b.x)).km

    # 地点Aと地点Bを結ぶ直線を作成
    line = LineString([point_a, point_b])

    # pyrosmを使用して道路データを取得
    osm = pyrosm.OSM(filepath)
    road_data = []
    for way_id in osm.get_ways(tags=dict(highway=True)):
        way_nodes = osm.get_way_nodes(way_id)
        for i in range(len(way_nodes) - 1):
            node_a = osm.get_node(way_nodes[i])
            node_b = osm.get_node(way_nodes[i + 1])
            road_line = LineString([(node_a["lon"], node_a["lat"]), (node_b["lon"], node_b["lat"])])
            if road_line.intersects(line):
                road_data.append((way_id, node_a, node_b))

    # 地点Aから地点Bへの移動経路がなければ移動不可として-1.0を返す
    if not road_data:
        return -1.0

    # 移動簡易性を計算
    road_length = 0
    for data in road_data:
        way_length = osm.get_way_length(data[0])
        road_length += way_length
    ease_of_move = 1.0 - (road_length * 0.1 / distance)
    if ease_of_move < 0:
        ease_of_move = 0.0

    return ease_of_move
