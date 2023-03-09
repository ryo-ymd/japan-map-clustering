import pandas as pd
import folium
import numpy as np
import point_calc
from sklearn.cluster import KMeans, DBSCAN
import pyrosm
import networkx as nx
from geopy.distance import geodesic


def mark_as_circle():
    colors_array = [
        'red',
        'blue',
        'darkred',
        'lightred',
        'orange',
        'green',
        'darkgreen',
        'lightgreen',
        'darkblue',
        'lightblue',
        'purple',
        'darkpurple',
        'pink',
        'cadetblue',
    ]

    for lat, lng, name, cluster in zip(df['latitude'], df['longitude'], df['name'], df['cluster_id']):
        if cluster is None:
            color = 'gray'
            size = 5
        elif cluster == -1:
            color = 'black'
            size = 5
        else:
            color = colors_array[(cluster - 1) % 14]
            size = 10

        folium.CircleMarker(
            location=[lat, lng],
            radius=size,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup='<span style="white-space: nowrap;">' + name + '</span>',
            parse_html=False
        ).add_to(map_japan)


def mark_as_marker():
    for lat, lng, name in zip(df['latitude'], df['longitude'], df['name']):
        folium.Marker(
            location=[lat, lng],
            popup='<span style="white-space: nowrap;">' + name + '</span>',
            icon=folium.Icon(color='red', icon='home')
        ).add_to(map_japan)


# ref: https://qiita.com/nyax/items/1fd73d4c84481b918e83
def k_means():
    # Numpyの行列に変換
    cust_array = np.array([df['latitude'].tolist(),
                           df['longitude'].tolist()])
    # 行列を転置
    cust_array = cust_array.T

    kclusters = 10
    # K-means実行
    pred = KMeans(
        n_clusters=kclusters,
        n_init='auto'
    ).fit_predict(cust_array)

    # データフレームにクラスタ番号を追加
    df['cluster_id'] = pred
    df.head()

    mark_as_circle()


# ref: https://helve-blog.com/posts/python/sklearn-dbscan/
def dbscan():
    # Numpyの行列に変換
    cust_array = np.array([df['latitude'].tolist(),
                           df['longitude'].tolist()])
    # 行列を転置
    cust_array = cust_array.T

    # DBSCAN実行
    pred = DBSCAN(
        eps=0.25,
        min_samples=2
    ).fit_predict(cust_array)

    df['cluster_id'] = pred
    df.head()

    mark_as_circle()


def chatGPTStyle():
    # Numpyの行列に変換
    cust_array = np.array([df['latitude'].tolist(),
                           df['longitude'].tolist()])
    # 行列を転置
    cust_array = cust_array.T

    # 距離行列を作成する
    n_samples = cust_array.shape[0]
    dist_matrix = np.zeros((n_samples, n_samples))
    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            dist_matrix[i, j] = point_calc.calculate_move_ease_of_two_points_osm(
                [cust_array[i, 0], cust_array[i, 1]],
                [cust_array[j, 0], cust_array[j, 1]]
            )
            dist_matrix[j, i] = dist_matrix[i, j]

    # DBSCANでクラスタリングする
    epsilon = 0.1
    min_samples = 10
    pred = DBSCAN(eps=epsilon, min_samples=min_samples, metric='precomputed').fit(dist_matrix)

    df['cluster_id'] = pred
    df.head()

    mark_as_circle()


df = pd.read_csv('homes.csv', usecols=[0, 1, 2, 3])
# 欠損値があればその行を消去
df_d = df.dropna(how='any')
df_r = df_d.reset_index(drop=True)
df.head()

map_japan = folium.Map(
    location=[37.990921, 139.700258],
    zoom_start=6,
)

chatGPTStyle()
# dbscan()
# k_means()
# mark_as_circle()
map_japan.save('home-map.html')
