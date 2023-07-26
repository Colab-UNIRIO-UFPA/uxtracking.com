import hashlib
import json
import string
import random
import pandas as pd
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
import numpy as np

def nlpBertimbau(text):
    folder = "bertimbau-finetuned"

    tokenizer = AutoTokenizer.from_pretrained(folder)
    model = AutoModelForSequenceClassification.from_pretrained(folder)

    id2label = {
        0:"RAIVA",
        1:"MEDO",
        2:"TRISTEZA",
        3:"SURPRESA",
        4:"ALEGRIA",
        5:"NOJO",
    }

    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
        
    normalize = lambda x, vec: 100 * (x - vec.min()) / (vec.max() - vec.min())
    normalized_logits = [normalize(element, logits) for element in logits]
    output = id2label[normalized_logits[0].argmax().item()]

    return output

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

def list_dates(dir):
    dates = []
    folders = os.listdir(dir)
    for item in folders:
        df = pd.read_csv(f'{dir}/{item}/trace.csv')
        pages = df.site.unique()
        items = item.split('-')
        items.append(pages)
        dates.append(items)
    dates = list(map(lambda time:   [f'{time[0][6:8]}/{time[0][4:6]}/{time[0][0:4]}',
                                f'{time[1][0:2]}:{time[1][2:4]}:{time[1][4:6]}',
                                time[2],
                                f'{time[0]}-{time[1]}'],
                                dates))
    return dates

def id_generator():
    chars=string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(8))