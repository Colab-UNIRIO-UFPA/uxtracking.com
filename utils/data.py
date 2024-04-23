import pandas as pd
from bson import ObjectId
from datetime import datetime
from collections import Counter


def userdata2frame(mongo_db, collection_name, id, data_type):
    # Definindo as colunas básicas
    keys = [
        "site",
        "image",
        "type",
        "time",
        "class",
        "id",
        "mouseClass",
        "mouseID",
        "x",
        "y",
        "scroll",
        "height",
    ]

    # Extendendo com campos específicos de interação
    if isinstance(data_type, list):
        keys.append("keys")
    elif data_type == "voice":
        data_type = [data_type]
        keys.append("text")
    elif data_type == "face":
        data_type = [data_type]
        keys.extend(
            [
                "anger",
                "contempt",
                "disgust",
                "fear",
                "happy",
                "neutral",
                "sad",
                "surprise",
            ]
        )

    pipeline = [
        {"$match": {"_id": ObjectId(id)}},  # Filtra pelo ID do documento
        {"$unwind": "$data"},  # Desagrega o array 'data'
        {
            "$project": {  # Projetar campos necessários e filtrar interações
                "site": "$data.site",
                "images": "$data.images",
                "interactions": {
                    "$filter": {
                        "input": "$data.interactions",
                        "as": "interaction",
                        "cond": {"$in": ["$$interaction.type", data_type]},
                    }
                },
            }
        },
        {
            "$match": {"interactions.0": {"$exists": True}}
        },  # Remove subdocumentos com interações vazias
    ]

    cursor = mongo_db[collection_name].aggregate(pipeline)
    records_list = list(cursor)

    all_data = []

    for record in records_list:
        site = record.get("site")
        for interaction in record.get("interactions", []):
            line = {
                "site": site,
                "type": interaction.get("type"),
                "image": interaction.get("image"),
                "time": interaction.get("time"),
                "class": interaction.get("class"),
                "id": interaction.get("id"),
                "mouseClass": interaction.get("mouseClass"),
                "mouseID": interaction.get("mouseID"),
                "x": interaction.get("x"),
                "y": interaction.get("y"),
                "scroll": interaction.get("scroll"),
                "height": interaction.get("height"),
            }
            # Tratando o campo value
            value_data = interaction.get("value", {})
            if isinstance(value_data, dict):
                line.update(value_data)

            all_data.append(line)

    # Criando DataFrame de uma vez
    df = pd.DataFrame(all_data, columns=keys)
    return df


def userdata_summary(documents):
    data = []
    date_arr = []
    try:
        for doc in documents:
            # Obtenha a string de data e hora do documento
            date_str = doc["datetime"]["$date"]

            # Converter para data e hora
            date_obj = datetime.fromisoformat(date_str.rstrip("Z"))
            date_part = date_obj.date().strftime("%d/%m/%Y")
            time_part = date_obj.time()

            date_arr.append(date_part)
            # Criando o objeto data com todas as informações da coleta
            data.append(
                {
                    "id": doc["_id"],  # id do documento
                    "date": date_part,  # data do documento
                    "time": time_part,  # hora do documento
                    "sites": doc["sites"],  # sites presentes no documento
                }
            )

    except:
        None

    # Contar as ocorrências de cada data
    date_counts = Counter(date_arr)

    return data, date_counts
