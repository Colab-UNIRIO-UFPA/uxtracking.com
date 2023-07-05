from sklearn.cluster import AgglomerativeClustering
import pandas as pd

df = pd.read_csv('trace.csv')

def model_agglomerated(x,n_clusters):

  x['keys'] = x['keys'].fillna(0)
  x['id'] = x['id'].fillna(0)

  df_d = pd.get_dummies(x)
  X = df_d.div(df_d.sum(axis=1),axis='rows')
  
  clusterer = AgglomerativeClustering(n_clusters)
  cluster_labels = clusterer.fit_predict(X)

  df_d.loc[:,'cluster'] = cluster_labels
  df_d.to_csv('Agglomerated-clusters.csv', index=False)
  
  print (cluster_labels)
  return