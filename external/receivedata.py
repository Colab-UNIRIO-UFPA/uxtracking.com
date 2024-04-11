import os
import io
import re
import csv
import json
import torch
import base64
from PIL import Image
from pathlib import Path
from app import db, model
from bson import ObjectId
import torch.nn.functional as F
from torchvision import transforms
from flask import abort, Blueprint, request, jsonify

external_receivedata_bp = Blueprint(
    "external_receivedata_bp", "__name__", template_folder="templates", static_folder="static"
)


# Define a rota para o envio dos dados pela ferramenta
# Organização do patch:
# (Diretório de samples)/(ID do usuário, gerado pela função generate_user_id em functions.py)/(YYYYMMDD-HHMMSS da coleta)/(dados da coleta)
@external_receivedata_bp.post("/receiver")
def receiver():
    metadata = request.form["metadata"]
    data = request.form["data"]
    metadata = json.loads(metadata)
    userid = metadata["userId"]
    userfound = db.users.find_one({"_id": ObjectId(userid)})
    dateTime = str(metadata["dateTime"])
    date = f"{dateTime[6:8]}/{dateTime[4:6]}/{dateTime[0:4]}"
    hour = f"{dateTime[9:11]}:{dateTime[11:13]}:{dateTime[13:15]}"
    data = json.loads(data)
    data_img = str(data["imageName"])
    datadir = os.path.normpath(os.path.join("Samples", userid))
    path_dateTime = os.path.normpath(os.path.join(datadir, dateTime))
    path_img = os.path.normpath(os.path.join(path_dateTime, data_img))

    # verificando se o caminho completo começa com o caminho base
    if not path_img.startswith(datadir):
        abort(403)

    # armazena metadata da coleta ao mongodb
    if userfound:
        # se for o primeiro traço coletado
        if dateTime not in userfound["data"]:
            userfound["data"][dateTime] = {
                "sites": [metadata["sample"]],
                "date": date,
                "hour": hour,
            }
            db.users.update_one({"_id": userfound["_id"]}, {"$set": userfound})
        else:
            # se for o primeiro traço coletado em um site
            if metadata["sample"] not in userfound["data"][dateTime]["sites"]:
                userfound["data"][dateTime]["sites"].append(metadata["sample"])
                db.users.update_one({"_id": userfound["_id"]}, {"$set": userfound})
    else:
        return "ERROR: Usuário não autenticado"

    if not os.path.exists("Samples"):
        os.makedirs("Samples", exist_ok=True)
    else:
        if not os.path.exists(datadir):
            os.makedirs(datadir, exist_ok=True)
        else:
            if not os.path.exists(path_dateTime):
                os.makedirs(path_dateTime, exist_ok=True)

    try:
        if data["imageData"] != "NO":
            if not os.path.exists(
                path_img,
            ):
                imageData = base64.b64decode(
                    re.sub("^data:image/\w+;base64,", "", data["imageData"])
                )
                with open(
                    path_img,
                    "wb",
                ) as fh:
                    fh.write(imageData)

    except:
        None

    traceData = ["eye", "mouse", "keyboard", "freeze", "click", "wheel", "move"]
    if str(metadata["type"]) in traceData:
        if not os.path.exists(os.path.join(path_dateTime, "trace.csv")):
            # se a base não existe, cria o csv
            fields = [
                "site",
                "type",
                "time",
                "image",
                "class",
                "id",
                "mouseClass",
                "mouseId",
                "x",
                "y",
                "keys",
                "scroll",
                "height",
            ]

            file = Path(os.path.join(path_dateTime, "trace.csv"))
            file.touch(exist_ok=True)

            with open(os.path.join(path_dateTime, "trace.csv"), "w") as csvfile:
                # criando um objeto csv dict writer
                csvwriter = csv.writer(csvfile)
                # escrever cabeçalhos (nomes de campo)
                csvwriter.writerow(fields)

        with open(os.path.join(path_dateTime, "trace.csv"), "a", newline="") as csvfile:
            # criando um objeto csv dict writer
            csvwriter = csv.writer(csvfile)
            # escrever linha (dados)
            csvwriter.writerow(
                [
                    str(metadata["sample"]),
                    str(metadata["type"]),
                    str(metadata["time"]),
                    str(data["imageName"]),
                    str(data["Class"]),
                    str(data["Id"]),
                    str(data["mouseClass"]),
                    str(data["mouseId"]),
                    str(data["X"]),
                    str(data["Y"]),
                    str(data["Typed"]),
                    str(metadata["scroll"]),
                    str(metadata["height"]),
                ]
            )

        with open(os.path.join(path_dateTime, "lastTime.txt"), "w") as f:
            f.write(str(metadata["dateTime"]))

        return "received"

    # se for um dado de voz
    elif str(metadata["type"]) == "voice":
        if not os.path.exists(os.path.join(path_dateTime, "audio.csv")):
            # se a base não existe, cria o csv
            fields = [
                "site",
                "time",
                "text",
                "image",
                "class",
                "id",
                "mouseClass",
                "mouseId",
                "x",
                "y",
                "scroll",
                "height",
            ]

            file = Path(os.path.join(path_dateTime, "audio.csv"))
            file.touch(exist_ok=True)  #

            with open(os.path.join(path_dateTime, "audio.csv"), "w") as csvfile:
                # criando um objeto csv dict writer
                csvwriter = csv.writer(csvfile)
                # escrever cabeçalhos (nomes de campo)
                csvwriter.writerow(fields)

        with open(os.path.join(path_dateTime, "audio.csv"), "a", newline="") as csvfile:
            # criando um objeto csv dict writer
            csvwriter = csv.writer(csvfile)
            # escrever linha (dados)
            csvwriter.writerow(
                [
                    str(metadata["sample"]),
                    str(metadata["time"]),
                    str(data["Spoken"]),
                    str(data["imageName"]),
                    str(data["Class"]),
                    str(data["Id"]),
                    str(data["mouseClass"]),
                    str(data["mouseId"]),
                    str(data["X"]),
                    str(data["Y"]),
                    str(metadata["scroll"]),
                    str(metadata["height"]),
                ]
            )

        with open(os.path.join(path_dateTime, "lastTime.txt"), "w") as f:
            f.write(str(metadata["dateTime"]))

        return "received"

    # se for um dado de expressão facial
    elif str(metadata["type"]) == "face":
        if not os.path.exists(os.path.join(path_dateTime, "emotions.csv")):
            # se a base não existe, cria o csv
            fields = [
                "site",
                "time",
                "image",
                "class",
                "id",
                "mouseClass",
                "mouseId",
                "x",
                "y",
                "scroll",
                "height",
                "anger",
                "contempt",
                "disgust",
                "fear",
                "happy",
                "neutral",
                "sad",
                "surprise",
            ]

            file = Path(os.path.join(path_dateTime, "emotions.csv"))
            file.touch(exist_ok=True)  #

            with open(os.path.join(path_dateTime, "emotions.csv"), "w") as csvfile:
                # criando um objeto csv dict writer
                csvwriter = csv.writer(csvfile)
                # escrever cabeçalhos (nomes de campo)
                csvwriter.writerow(fields)

        with open(
            os.path.join(path_dateTime, "emotions.csv"), "a", newline=""
        ) as csvfile:
            # criando um objeto csv dict writer
            csvwriter = csv.writer(csvfile)
            # escrever linha (dados)
            csvwriter.writerow(
                [
                    str(metadata["sample"]),
                    str(metadata["time"]),
                    str(data["imageName"]),
                    str(data["Class"]),
                    str(data["Id"]),
                    str(data["mouseClass"]),
                    str(data["mouseId"]),
                    str(data["X"]),
                    str(data["Y"]),
                    str(metadata["scroll"]),
                    str(metadata["height"]),
                    str(data["anger"]),
                    str(data["contempt"]),
                    str(data["disgust"]),
                    str(data["fear"]),
                    str(data["happy"]),
                    str(data["neutral"]),
                    str(data["sad"]),
                    str(data["surprise"]),
                ]
            )

        with open(os.path.join(path_dateTime, "lastTime.txt"), "w") as f:
            f.write(str(metadata["dateTime"]))
        return "received"

    else:
        abort(403)


# Define a rota para o envio dos dados pela ferramenta
# Organização do patch:
# (Diretório de samples)/(ID do usuário, gerado pela função generate_user_id em functions.py)/(data+hora da coleta)/(dados da coleta)
@external_receivedata_bp.post("/sample_checker")
def sample_checker():
    time = request.form["dateTime"]
    userid = request.form["userId"]
    datadir = f"Samples/{userid}/"

    # normalizando caminho base
    base_path = os.path.normpath(datadir)

    directory_path = os.path.normpath(os.path.join(datadir, time))

    if not directory_path.startswith(base_path):
        abort(403)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path, mode=0o777, exist_ok=True)

    fullpath = os.path.join(directory_path, "lastTime.txt")

    if os.path.exists(fullpath):
        with open(fullpath, "r") as file:
            content = file.read()
            return content
    else:
        return "0"


@external_receivedata_bp.post("/faceExpression")
def faceExpression():
    image_data = request.form["data"]
    # Converte a Base64 para bytes
    header, image_data = image_data.split(",", 1)
    image_bytes = base64.b64decode(image_data)
    # Abre a imagem com Pillow
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Define a sequência de transformações
    transform = transforms.Compose(
        [
            transforms.Resize(96),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
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
