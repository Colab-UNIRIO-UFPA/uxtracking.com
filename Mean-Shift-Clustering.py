import numpy as np
import csv
from sklearn.cluster import MeanShift
import pandas as pd
from sklearn.cluster import estimate_bandwidth

df = pd.read_csv('trace.csv')

def model_meanshift (dados,n_qualite,samples):

  x = dados
  dados['keys'] = dados['keys'].fillna(0)
  dados = pd.get_dummies(dados)
  dados = dados.div(dados.sum(axis=1),axis='rows')
  
  bandwidth = estimate_bandwidth(dados,quantile=n_qualite,n_samples=samples)

  ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
  ms.fit(dados)
  labels = ms.labels_
  cluster_centers = ms.cluster_centers_

  labels_unique = np.unique(labels)
  n_clusters_ = len(labels_unique)

  x.loc[:,'cluster'] = labels
  x.to_csv('Mean-Shift.csv', index=False)

  print(f"Número estimado de clusters: {n_clusters_}")
  return