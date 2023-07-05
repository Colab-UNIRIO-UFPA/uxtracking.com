import csv
from sklearn.cluster import KMeans
import pandas as pd

df = pd.read_csv('trace.csv')

def model_kmeans(data, n_clusters, n_init, max_iter):
    x = data
    data['keys'] = data['keys'].fillna(0)
    data = pd.get_dummies(data)
    data = data.div(data.sum(axis=1),axis='rows')

    km = KMeans(n_clusters=n_clusters, max_iter=max_iter, n_init=n_init)
    X_t = km.fit_predict(data)

    x.loc[:,'cluster'] = X_t

    x.to_csv('Kmeans.csv', index=False)
    return