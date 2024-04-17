import os
import shutil
import zipfile
from app import db
from utils.functions import format_ISO
from flask import render_template, Blueprint, request, session, abort, Response

index_bp = Blueprint("index_bp", "__name__", template_folder="templates", static_folder="static")


# Define a rota para a página principal
@index_bp.post("/")
def index_post():
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = db.users.find_one({"username": session["username"]})
        userid = userfound["_id"]
        datadir = f"./Samples/{userid}"

        folder = request.form.getlist("dates[]")
        folder = folder[0]

        # normalizando o caminho base
        base_path = os.path.normpath(datadir)

        # normalizando o caminho completo
        fullpath = os.path.normpath(os.path.join(base_path, folder))

        # verificando se o caminho completo começa com o caminho base
        if not fullpath.startswith(base_path):
            abort(403)

        # cria um zip para inserção dos dados selecionados
        with zipfile.ZipFile(f"{folder}_data.zip", "w") as zipf:
            for file in os.listdir(fullpath):
                shutil.copy(os.path.join(fullpath, file), file)
                zipf.write(file)
                os.remove(file)

        # limpando o zip criado
        with open(f"{folder}_data.zip", "rb") as f:
            data = f.readlines()
        os.remove(f"{folder}_data.zip")

        # fornecendo o zip pra download
        return Response(
            data,
            headers={
                "Content-Type": "application/zip",
                "Content-Disposition": f"attachment; filename={folder}_data.zip;",
            },
        )

    else:
        return render_template("index.html", session=False, title="Home")
        
@index_bp.get("/")
def index_get():
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = db.users.find_one({"username": session["username"]})
        userid = userfound["_id"]
        datadir = f"./Samples/{userid}"

        # verifica quais datas estão disponíveis e limpa a string
        dates = []
        folder = []
        figdata = {}
        i = 0

        # pegar o nome dos arquivos
        for pasta in userfound["data"]:
            if pasta in os.listdir(datadir):
                folder.append(pasta)

        folder_reverse = folder[::-1]

        try:
            # pegar o nome dos arquivos
            for pasta in userfound["data"]:
                if pasta in os.listdir(datadir):
                    folder.append(pasta)

            folder_reverse = folder[::-1]
            for folder in userfound["data"]:
                # print(folder)
                date = userfound["data"][folder]["date"]
                if date not in figdata.keys():
                    figdata[date] = 1
                else:
                    figdata[date] += 1
                if i <= 4:
                    date_info = userfound["data"][folder_reverse[i]]
                    dates.append(
                        [
                            date_info["date"],
                            date_info["hour"],
                            date_info["sites"],
                            folder_reverse[i],
                        ]
                    )
                    i += 1

        except:
            None

        datas = format_ISO(figdata.keys())
        values = list(figdata.values())

        # lista de coletas
        return render_template(
            "index.html",
            session=True,
            username=session["username"],
            title="Home",
            dates=dates,
            datas=datas,
            values=values,
        )
    else:
        return render_template("index.html", session=False, title="Home")
