import io
import re
import torch
import base64
from PIL import Image
from bson import ObjectId
from datetime import datetime
from app import mongo, model, fs
import torch.nn.functional as F
from torchvision.transforms import v2 as T
from flask import abort, Blueprint, request, jsonify

external_receivedata_bp = Blueprint(
    "external_receivedata_bp",
    "__name__",
    template_folder="templates",
    static_folder="static",
)


# Define a rota para o envio dos dados pela ferramenta
@external_receivedata_bp.post("/receiver")
def receiver():
    content = request.get_json(silent=True)
    metadata, data = content.get("metadata", {}), content.get("data", {})
    userfound = mongo.users.find_one({"_id": ObjectId(metadata["userID"])})
    if not userfound:
        abort(403)
    collection_name = f"data_{userfound['_id']}"
    result = mongo[collection_name].find_one({"datetime.$date": metadata["dateTime"]})

    # inserção no mongo gridFS (id retornado)
    image_id = fs.put(
        base64.b64decode(re.sub("^data:image/\w+;base64,", "", metadata["image"]))
    )

    interactions = []
    for i in range(len(data["type"])):
        interactions.append(
            {
                "type": data["type"][i],
                "time": data["time"][i],
                "image": image_id,
                "class": data["class"][i],
                "id": data["id"][i],
                "x": data["x"][i],
                "y": data["y"][i],
                "scroll": data["scroll"][i],
                "height": metadata["height"],
                "value": data["value"][i],
            }
        )

    document = {
        "datetime": {"$date": metadata["dateTime"]},
        "sites": [metadata["site"]],
        "data": [
            {
                "site": metadata["site"],
                "images": [image_id],
                "interactions": interactions,
            }
        ],
    }

    if result:
        mongo[collection_name].update_one(
            {"_id": result["_id"]}, {"$set": document}, upsert=True
        )
    else:
        mongo[collection_name].insert_one(document)

    return "Received"


@external_receivedata_bp.post("/faceExpression")
def faceExpression():
    image_data = request.form["data"]
    # Converte a Base64 para bytes
    header, image_data = image_data.split(",", 1)
    image_bytes = base64.b64decode(image_data)
    # Abre a imagem com Pillow
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Define a sequência de transformações
    transform = T.Compose(
        [
            T.Resize(96),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )

    # Aplica as transformações na imagem
    image_transformed = transform(image).unsqueeze(0)

    # Realiza a inferência
    with torch.no_grad():
        outputs = model(image_transformed)
        outputs = F.softmax(outputs, dim=1)
    result = outputs.tolist()

    labels = [
        "anger",
        "contempt",
        "disgust",
        "fear",
        "happy",
        "neutral",
        "sad",
        "surprise",
    ]

    result_dict = {label: prob for label, prob in zip(labels, result[0])}
    return jsonify(result_dict)
