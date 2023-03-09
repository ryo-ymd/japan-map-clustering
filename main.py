import time
import pandas as pd
import folium
import numpy as np
from sklearn.cluster import KMeans, DBSCAN


def mark_as_circle():
    colors_array = [
        'red',
        'blue',
        'darkred',
        'orange',
        'green',
        'darkgreen',
        'darkblue',
        'purple',
        'cadetblue',
    ]

    for lat, lng, name, cluster in zip(df['latitude'], df['longitude'], df['name'], df['cluster_id']):
        if cluster is None:
            color = 'gray'
            size = 3
        elif cluster == -1:
            color = 'black'
            size = 3
        else:
            color = colors_array[(cluster - 1) % len(colors_array)]
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
def k_means(k_clusters):
    # Numpyの行列に変換
    cust_array = np.array([df['latitude'].tolist(),
                           df['longitude'].tolist()])
    # 行列を転置
    cust_array = cust_array.T
    # K-means実行
    pred = KMeans(
        n_clusters=k_clusters,
        n_init='auto'
    ).fit_predict(cust_array)

    # データフレームにクラスタ番号を追加
    df['cluster_id'] = pred
    df.head()

    mark_as_circle()


# ref: https://helve-blog.com/posts/python/sklearn-dbscan/
def dbscan(eps, min_samples):
    # Numpyの行列に変換
    cust_array = np.array([df['latitude'].tolist(),
                           df['longitude'].tolist()])
    # 行列を転置
    cust_array = cust_array.T

    # DBSCAN実行
    pred = DBSCAN(
        eps=eps,
        min_samples=min_samples
    ).fit_predict(cust_array)

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

# DBSCAN法 eps: 密集具合, min_samples: 最低個数
dbscan(0.09, 2)
# k-means法 k_clusters: 何分割するか
# k_means(15)

# ただ家をマッピングする場合(円としてマッピング)
# mark_as_circle()

# ただ家をマッピングする場合(家としてマッピング)
# mark_as_marker()

map_japan.save(f'home-map-{time.time()}.html')
