import pyrosm
from shapely.geometry import Point, LineString
from geopy.distance import geodesic


def calculate_move_ease_of_two_points_osm(point_a, point_b):
    # 地点Aと地点BをPointオブジェクトに変換
    point_a = Point(point_a[1], point_a[0])
    point_b = Point(point_b[1], point_b[0])

    # 地点Aと地点Bの距離を計算
    distance = geodesic((point_a.y, point_a.x), (point_b.y, point_b.x)).km

    # 地点Aと地点Bを結ぶ直線を作成
    line = LineString([point_a, point_b])

    # japan-latest.osm.pbfから地点Aと地点Bの間の道路データを取得
    road_data = []
    with pyrosm.OSM('japan-latest.osm.pbf') as osm:
        for way in osm.get_ways():
            if 'highway' in way['tags']:
                coords = osm.get_coordinates(way['nodes'])
                for i in range(len(coords) - 1):
                    node_a = coords[i]
                    node_b = coords[i + 1]
                    road_line = LineString([Point(node_a), Point(node_b)])
                    if road_line.intersects(line):
                        road_data.append((way['tags']['highway'], node_a, node_b))

    # 地点Aから地点Bへの移動経路がなければ移動不可として-1.0を返す
    if not road_data:
        return -1.0

    # 移動簡易性を計算
    road_length = 0
    for data in road_data:
        road_length += geodesic(data[1], data[2]).km
    ease_of_move = 1.0 - (road_length * 0.1 / distance)
    if ease_of_move < 0:
        ease_of_move = 0.0

    return road_length
