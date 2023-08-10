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
import plotly.graph_objects as go
from PIL import Image
import base64

folderBert = "bertimbau-finetuned"

tokenizer = AutoTokenizer.from_pretrained(folderBert)
modelBert = AutoModelForSequenceClassification.from_pretrained(folderBert)

id2label = {
    0:"RAIVA",
    1:"MEDO",
    2:"TRISTEZA",
    3:"SURPRESA",
    4:"ALEGRIA",
    5:"NOJO",
}

def nlpBertimbau(folder):
    try:
        df_audio = pd.read_csv(f'{folder}/audio.csv')
    except:
        return 'Não foi possível processar a coleta, áudio ausente!'
    
    texts=[]
    for text in df_audio['text']:
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            logits = modelBert(**inputs).logits
            
        normalize = lambda x, vec: 100 * (x - vec.min()) / (vec.max() - vec.min())
        normalized_logits = [normalize(element, logits) for element in logits]
        output = id2label[normalized_logits[0].argmax().item()]
        texts.append(output)

    df_audio['feeling'] = texts
    return df_audio.to_html(classes='table table-stripped table-hover table-sm')

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
    folders = sorted(os.listdir(dir))
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

def dirs2data(dir):
    data = []
    folders = sorted(os.listdir(dir))
    for item in folders:
        df = pd.read_csv(f'{dir}/{item}/trace.csv')
        data.append({  
                    'date': f'{item[6:8]}/{item[4:6]}/{item[0:4]}',
                    'hour': f'{item[9:11]}:{item[11:13]}:{item[13:15]}',
                    'pages': df.site.unique(),
                    'dir': item
                    })
    return data

def id_generator():
    chars=string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(8))

###############
#plot functions
def make_heatmap(folder, **kwargs):
    df_trace = pd.read_csv(f'{folder}/trace.csv')
    try:
        df_audio = pd.read_csv(f'{folder}/audio.csv')
    except:
        df_audio = pd.DataFrame(columns=['site','time','text','image','class','id','mouseClass','mouseId','x','y','scroll','height'])
    try:
        im = Image.open(f'{folder}/{df_trace.image[0]}')
        im0 = base64.b64encode(open(f'{folder}/{df_trace.image[0]}', 'rb').read())
    except:
        try:
            im = Image.open(f'{folder}/{df_trace.image[10]}')
            im0 = base64.b64encode(open(f'{folder}/{df_trace.image[10]}', 'rb').read())
        except:
            return 'Não foi possível gerar o mapa de calor, imagens ausentes!'

    width, height = im.size
    key_list = {'mouse': ['move', 'click', 'freeze', 'wheel'],
                'eye': ['eye']}
    frames = []
    for time in range(df_trace['time'].max()):
        filtered_df = df_trace[df_trace['time'] == time]
        filtered_df = filtered_df[filtered_df['type'].isin(key_list[kwargs['type']])]
        for image in filtered_df.image.unique():
            plot_df = filtered_df[filtered_df['image'] == image]
            y = (abs(plot_df['y']-plot_df['scroll'])).values
            z = plot_df[['time','x','y']].value_counts()[plot_df.time.unique()].values
            if time in df_audio.time.values:
                audio2text = df_audio.query(f'time == {time}')['text'].values
                try:
                    img = base64.b64encode(open(f'{folder}/{image}', 'rb').read())
                    frames.append(go.Frame(data=go.Scatter(x=plot_df['x'], y=y, marker_size=np.mean(z)*32, mode='markers+text'),
                                        name=time, layout=dict(images=[dict(source='data:image/jpg;base64,{}'.format(img.decode()))],
                                                    annotations=[dict(x=0.5, y=0.04, xref="paper", yref="paper",
                                                                        text=f"Falado: {audio2text[0]}",
                                                                        font=dict(
                                                                            family="Courier New, monospace",
                                                                            size=18,
                                                                            color="#ffffff"
                                                                            ),
                                                                        bordercolor="#c7c7c7", borderwidth=2, borderpad=8,
                                                                        bgcolor="rgb(36, 36, 36)", opacity=1)])))
                except:
                    None
            else:
                try:
                    img = base64.b64encode(open(f'{folder}/{image}', 'rb').read())
                    frames.append(go.Frame(data=go.Scatter(x=plot_df['x'], y=y, marker_size=z[0]*32, mode='markers+text'),
                                        name=time, layout=dict(images=[dict(source='data:image/jpg;base64,{}'.format(img.decode()))])))
                except:
                    None
    fig = go.Figure(
        data=frames[0].data,
        layout=go.Layout(
            xaxis=dict(range=[0, width], autorange=False, rangeslider=dict(
            visible=False
        )),
            yaxis=dict(range=[0, height], autorange=False),
            images=[dict(
                        source='data:image/jpg;base64,{}'.format(im0.decode()),
                        xref="x",
                        yref="y",
                        x=0,
                        y=height,
                        sizex=width,
                        sizey=height,
                        sizing="fill",
                        opacity=1,
                        layer="below"
                    )]
        ),
        frames=frames
    )
    
    # Configure axes
    fig.update_xaxes(
        visible=False
    )

    fig.update_yaxes(
        visible=False,
        # the scaleanchor attribute ensures that the aspect ratio stays constant
        scaleanchor="x"
    )
    fig.update_traces(marker=dict(size=32, color='rgba(255, 255, 0, 0)',line=dict(color='rgba(0, 0, 255, 0.003)',width=6
                )),
                    marker_gradient=dict(color='rgba(255, 0, 0, 0.35)', type='radial'),
                    selector=dict(type='scatter'))
            
    # Configure other layout
    fig.update_layout(
        # iterate over frames to generate steps... NB frame name...
        sliders=[{"steps": [{"args": [[f.name],{"frame": {"duration": 0, "redraw": True},
                                            "mode": "immediate",},],
                         "label": f.name, "method": "animate",}
                         
                        for f in frames],
                    'x':0,
                    'y':-0.07,
                    'font':{'size':12},
                    'ticklen':4,
                    'currentvalue':{"prefix": "Time(s):", 'visible':True}}],
        width=width*0.5,
        height=height*0.5,
        margin={"l": 0, "r": 0, "t": 0, "b": 140},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig['layout']['updatemenus'] = [
        {
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 300, 'redraw': True},
                            'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                    'label': 'Play',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate',
                    'transition': {'duration': 0}}],
                    'label': 'Pause',
                    'method': 'animate'
                }
            ],
            'direction': 'left',
            'pad': {'r': 0, 't': 0, 'b':0, 'l':0},
            'showactive': False,
            'type': 'buttons',
            'x': 0.12,
            'xanchor': 'right',
            'y': -0.02,
            'yanchor': 'top',
            'bgcolor': 'rgb(190, 190, 190)',
            'font':{'color':'rgb(0, 0, 0)'}
        }
    ]
    fig.update_xaxes(rangeslider_thickness = 0.1)
    plot_as_string = fig.to_html(div_id='plotDiv')

    return plot_as_string