import string
import random
import pandas as pd
import os
import io
import gridfs
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from app import mongo
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
from matplotlib import pyplot as plt
import cv2 as cv
import numpy as np
import plotly.graph_objects as go
from PIL import Image
import base64
from stitching import Stitcher
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots
from flask import Response
from scipy.ndimage import gaussian_filter
from io import BytesIO


folderBert = "bertimbau-finetuned"

tokenizer = AutoTokenizer.from_pretrained(folderBert)
modelBert = AutoModelForSequenceClassification.from_pretrained(folderBert)

id2label = {
    0: "RAIVA",
    1: "MEDO",
    2: "TRISTEZA",
    3: "SURPRESA",
    4: "ALEGRIA",
    5: "NOJO",
}


def format_ISO(dates):
    iso_format_dates = []

    for date in dates:
        date_obj = datetime.strptime(date, "%d/%m/%Y")
        iso_date = date_obj.strftime("%Y-%m-%d")
        iso_format_dates.append(iso_date)

    return iso_format_dates


def nlpBertimbau(df):

    if df.empty or len(df.columns) == 0:
        raise ValueError("DataFrame está vazio ou não possui colunas.")

    texts = []
    sentiment_dict = {sentiment: [] for sentiment in id2label.values()}
    for text in df["text"]:
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            logits = modelBert(**inputs).logits

        normalize = lambda x, vec: 100 * (x - vec.min()) / (vec.max() - vec.min())
        normalized_logits = [normalize(element, logits) for element in logits]
        output = id2label[normalized_logits[0].argmax().item()]
        for i in range(0, len(normalized_logits[0])):
            sentiment_current = id2label[i]
            sentiment_dict[sentiment_current].append(
                round(normalized_logits[0][i].item(), 4)
            )
        texts.append(output)

    df["feeling"] = texts
    for value in id2label.values():
        df[value.lower()] = sentiment_dict[value]

    return df


def df_graph_sentiment(df):
    # contagem dos sentimentos para grafico radar
    audio_sentiment = list(df["feeling"])

    sentiment_count = {sentiment: 0 for sentiment in id2label.values()}

    for sentiment in audio_sentiment:
        if sentiment in id2label.values():
            sentiment_count[sentiment] += 1

    # criação de datafrime para grafico radar
    df_radar = pd.DataFrame(
        dict(
            Emocao=list(sentiment_count.keys()), Contagem=list(sentiment_count.values())
        )
    )

    # informações para gráfico dos sentimentos
    df_sentiment = pd.DataFrame(
        dict(
            time=list(df["time"]),
            raiva=list(df["raiva"]),
            medo=list(df["medo"]),
            tristeza=list(df["tristeza"]),
            surpresa=list(df["surpresa"]),
            alegria=list(df["alegria"]),
            nojo=list(df["nojo"]),
        )
    )

    # transformando para string
    df_sentiment["time"] = df_sentiment["time"].astype(str)

    return df_radar, df_sentiment


def model_kmeans(data, n_clusters, n_init, max_iter):
    x = data
    data["keys"] = data["keys"].fillna(0)
    data = pd.get_dummies(data)
    data = data.div(data.sum(axis=1), axis="rows")

    km = KMeans(n_clusters=n_clusters, max_iter=max_iter, n_init=n_init)
    X_t = km.fit_predict(data)

    x.loc[:, "cluster"] = X_t

    x.to_csv("Kmeans.csv", index=False)
    return


def model_meanshift(dados, n_qualite, samples):
    x = dados
    dados["keys"] = dados["keys"].fillna(0)
    dados = pd.get_dummies(dados)
    dados = dados.div(dados.sum(axis=1), axis="rows")

    bandwidth = estimate_bandwidth(dados, quantile=n_qualite, n_samples=samples)

    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(dados)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_

    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    x.loc[:, "cluster"] = labels
    x.to_csv("Mean-Shift.csv", index=False)

    print(f"Número estimado de clusters: {n_clusters_}")
    return


def list_dates(dir):
    dates = []
    folders = sorted(os.listdir(dir))
    for item in folders:
        df = pd.read_csv(f"{dir}/{item}/trace.csv", encoding="iso-8859-1")
        pages = df.site.unique()
        items = item.split("-")
        items.append(pages)
        dates.append(items)
    dates = list(
        map(
            lambda time: [
                f"{time[0][6:8]}/{time[0][4:6]}/{time[0][0:4]}",
                f"{time[1][0:2]}:{time[1][2:4]}:{time[1][4:6]}",
                time[2],
                f"{time[0]}-{time[1]}",
            ],
            dates,
        )
    )
    return dates


def dirs2data(userfound, datadir):
    data = []
    for folder in userfound["data"]:
        if folder in os.listdir(datadir):
            data.append(
                {
                    "date": userfound["data"][folder]["date"],
                    "hour": userfound["data"][folder]["hour"],
                    "pages": userfound["data"][folder]["sites"],
                    "dir": folder,
                }
            )
    return data


def id_generator():
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(8))


def df_make_recording(df_trace):

    id_im = df_trace["image"][0]

    fs = gridfs.GridFS(mongo)
    im = fs.get(id_im).read()

    with Image.open(io.BytesIO(im)) as im:
        width, height = im.size

    frames = {}

    # verificar as primeiras ocorrencias dos frames
    for site, group in df_trace.groupby("site"):
        images = group["image"].unique()
        frames[site] = {}
        for frame in images:
            id0 = group[group["image"] == frame].index[0]
            columns = group.loc[id0, ["scroll", "height"]]
            frames[site][frame] = columns.to_dict()

    full_ims = gen_fullpage(width, height, frames)

    # Definindo os ícones para cada tipo de interação (ref: https://plotly.com/python/marker-style/)
    type_icon = {
        "freeze": "hourglass",
        "eye": "circle",
        "click": "circle",
        "move": "arrow",
        "keyboard": "hash",
    }

    return full_ims, type_icon
    # dict_site = {}

    # for site in full_ims.keys():
    #     fig = go.Figure()
    #     filtered_df = df_trace[df_trace["site"] == site]

    #     width, height = full_ims[site].size
    #     imagem = full_ims[site]
    #     buffer = BytesIO()
    #     imagem.save(buffer, format="PNG")  # Ou o formato apropriado da sua imagem
    #     imagem_base64 = base64.b64encode(buffer.getvalue()).decode()
    #     image_src = "data:image/png;base64," + imagem_base64

    #     for type, group in filtered_df.groupby("type"):
    #         if type in type_icon:
    #             x = group["x"].values
    #             y = group["y"].values + group["scroll"].values
    #             time = group["time"].values
    #             mode = "lines+markers" if type != "click" else "markers"
    #             fig.add_trace(
    #                 go.Scatter(
    #                     x=x,
    #                     y=y,
    #                     mode=mode,
    #                     name=type,
    #                     text=[
    #                         f"Time: {(t // 3600):02d}:{((t % 3600) // 60):02d}:{(t % 60):02d}"
    #                         for t in time
    #                     ],
    #                     hovertemplate=f"Interaction: {type}<br>Site: {site}<br>%{{text}}<br>X: %{{x}}<br>Y: %{{y}}</br>",
    #                     marker=dict(
    #                         symbol=type_icon[type],
    #                         size=10 if type != "click" else 35,
    #                         angleref="previous",
    #                     ),
    #                 )
    #             )
    #         else:
    #             pass

    #     fig.update_layout(
    #         xaxis=dict(
    #             range=[0, width], autorange=False, rangeslider=dict(visible=False)
    #         ),
    #         yaxis=dict(range=[height, 0], autorange=False),
    #         legend=dict(
    #                     orientation="h",
    #                     yanchor="bottom",
    #                     y=1.01,
    #                     xanchor="left",
    #                     x=0,
    #                     font = dict(color="white", size=18)
    #                     ),
    #         images=[
    #             dict(
    #                 source=image_src,
    #                 xref="paper",  # Usa o sistema de coordenadas relativo ao papel/gráfico
    #                 yref="paper",
    #                 x=0,  # Posição no canto inferior esquerdo
    #                 y=1,  # Posição no canto superior esquerdo
    #                 sizex=1,  # Estender a imagem para cobrir toda a largura do gráfico
    #                 sizey=1,  # Estender a imagem para cobrir toda a altura do gráfico
    #                 sizing="stretch",  # Esticar a imagem para preencher o espaço (alternativas: "contain", "cover")
    #                 opacity=1,  # Ajustar a opacidade conforme necessário
    #                 layer="below",  # Colocar a imagem abaixo dos dados do gráfico
    #             )
    #         ],
    #         width=width * 0.6,
    #         height=height * 0.6,
    #         margin=dict(l=0, r=0, t=0, b=0),
    #         paper_bgcolor="rgba(0, 0, 0, 0)",
    #         plot_bgcolor="rgba(0, 0, 0, 0)",
    #     )
    #     fig.update_xaxes(showgrid=False, zeroline=False, visible=False)

    #     fig.update_yaxes(
    #         showgrid=False,
    #         zeroline=False,
    #         visible=False,
    #         scaleanchor="x",
    #     )

    #     dict_site[site] = fig.to_html(div_id="plotDiv")

    # return dict_site", analise esse código profundamente e o transforme para js plotly
    
    # return dict_site


def gen_fullpage(width, height, frames):
    
    full_ims = {}

    for site, image in frames.items():
        #print("site ", site)
        #print("image ", image)
        #print("image_values ", image.values)
        height = int(height + max(item["scroll"] for item in image.values()))
        #print("height, ", height)
        compose_im = Image.new("RGB", (width, height), "white")

        for image, item in image.items():
            try:
                #print("img_try ", image)
                #print("item_try ", item)
                fs = gridfs.GridFS(mongo)
                img_data = fs.get(image).read()
                with Image.open(io.BytesIO(img_data)) as img:
                    compose_im.paste(img, (0, int(item["scroll"])))
            except:
                pass

        full_ims[site] = compose_im

    return full_ims


def plot_image(img, figsize_in_inches=(5, 5)):
    fig, ax = plt.subplots(figsize=figsize_in_inches)
    ax.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
    plt.show()
