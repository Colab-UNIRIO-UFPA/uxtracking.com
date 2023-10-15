from flask_pymongo import pymongo
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    Response,
    flash,
    jsonify,
    session,
)
import json
import os
import base64
import re
from flask_mail import Mail, Message
from simple_colors import *
import csv
from pathlib import Path
import pandas as pd
import zipfile
import shutil
import plotly.graph_objects as go
import datetime
from plotly.graph_objects import Layout
from dotenv import load_dotenv
from bson import ObjectId
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
from unidecode import unidecode
import dash
from dash import dcc, html

# delete se estiver utilizando windows
load_dotenv()
# funções nativas
from functions import (
    id_generator,
    list_dates,
    nlpBertimbau,
    dirs2data,
    make_heatmap,
    make_recording,
)

# conexão com a base
CONNECTION_STRING = os.environ["URI_DATABASE"]
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database("users")

# declarando o servidor
app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

# configurando o serviço de email
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=os.environ["MAIL_NAME"],
    MAIL_PASSWORD=os.environ["MAIL_PASSWORD"],
)
mail = Mail(app)


# Define a rota para o envio dos dados pela ferramenta
# Organização do patch:
# (Diretório de samples)/(ID do usuário, gerado pela função generate_user_id em functions.py)/(YYYYMMDD-HHMMSS da coleta)/(dados da coleta)
@app.route("/receiver", methods=["POST"])
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
        if not os.path.exists(f"Samples/{userid}"):
            os.makedirs(f"Samples/{userid}", exist_ok=True)
        else:
            if not os.path.exists(f"Samples/{userid}/" + str(metadata["dateTime"])):
                os.makedirs(
                    f"Samples/{userid}/" + str(metadata["dateTime"]), exist_ok=True
                )

    try:
        if data["imageData"] != "NO":
            if not os.path.exists(
                f"Samples/{userid}/"
                + str(metadata["dateTime"])
                + "/"
                + str(data["imageName"])
            ):
                imageData = base64.b64decode(
                    re.sub("^data:image/\w+;base64,", "", data["imageData"])
                )
                with open(
                    f"Samples/{userid}/"
                    + str(metadata["dateTime"])
                    + "/"
                    + str(data["imageName"]),
                    "wb",
                ) as fh:
                    fh.write(imageData)

    except:
        None

    traceData = ["eye", "mouse", "keyboard", "freeze", "click", "wheel", "move"]
    if str(metadata["type"]) in traceData:
        if not os.path.exists(f"Samples/{userid}/{dateTime}/trace.csv"):
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

            file = Path(f"Samples/{userid}/{dateTime}/trace.csv")
            file.touch(exist_ok=True)

            with open(f"Samples/{userid}/{dateTime}/trace.csv", "w") as csvfile:
                # criando um objeto csv dict writer
                csvwriter = csv.writer(csvfile)
                # escrever cabeçalhos (nomes de campo)
                csvwriter.writerow(fields)

        with open(f"Samples/{userid}/{dateTime}/trace.csv", "a", newline="") as csvfile:
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

        with open(
            f"Samples/{userid}/" + str(metadata["dateTime"]) + "/lastTime.txt", "w"
        ) as f:
            f.write(str(metadata["dateTime"]))

        return "received"

    # se for um dado de voz
    else:
        if not os.path.exists(f"Samples/{userid}/{dateTime}/audio.csv"):
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

            file = Path(f"Samples/{userid}/{dateTime}/audio.csv")
            file.touch(exist_ok=True)

            with open(f"Samples/{userid}/{dateTime}/audio.csv", "w") as csvfile:
                # criando um objeto csv dict writer
                csvwriter = csv.writer(csvfile)
                # escrever cabeçalhos (nomes de campo)
                csvwriter.writerow(fields)

        with open(f"Samples/{userid}/{dateTime}/audio.csv", "a", newline="") as csvfile:
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

        with open(
            f"Samples/{userid}/" + str(metadata["dateTime"]) + "/lastTime.txt", "w"
        ) as f:
            f.write(str(metadata["dateTime"]))

        return "received"


# Define a rota para o envio dos dados pela ferramenta
# Organização do patch:
# (Diretório de samples)/(ID do usuário, gerado pela função generate_user_id em functions.py)/(data+hora da coleta)/(dados da coleta)
@app.route("/sample_checker", methods=["POST"])
def sample_checker():
    if request.method == "POST":
        time = request.form["dateTime"]
        userid = request.form["userId"]
        if not os.path.exists(f"Samples/{userid}/" + time):
            os.makedirs(f"Samples/{userid}/" + time, mode=0o777, exist_ok=True)
        filename = f"Samples/{userid}/" + time + "/lastTime.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                content = file.read()
                return content
        else:
            return "0"


# Define a rota para a página de registro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Obtém o usuário e a senha informados no formulário
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        # Verifica se o usuário já existe
        userfound = db.users.find_one({"email": email})
        if userfound == None:
            db.users.insert_one(
                {"username": username, "password": password, "email": email, "data": {}}
            )
        else:
            flash("Esse email já foi cadastrado")
            return render_template("register.html", title="Registrar")
        # Redireciona para a página de login
        return redirect(url_for("login", title="Login"))

    else:
        # Se a requisição for GET, exibe a página de registro
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return render_template("register.html", session=False, title="Registrar")


# Define a rota para a página de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Obtém o usuário e a senha informados no formulário
        username = request.form["username"]
        password = request.form["password"]
        userfound = db.users.find_one({"username": username, "password": password})

        if userfound != None:
            session["username"] = request.form["username"]
            return redirect(url_for("index"))
        else:
            # Se as credenciais estiverem incorretas, exibe uma mensagem de erro
            flash("Usuário ou senha incorretos.")
            return render_template("login.html", session=False, title="Login")
    else:
        # Se a requisição for GET, exibe a página de login
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return render_template("login.html", session=False, title="Login")


# Define a rota para o logout
@app.route("/logout")
def logout():
    # remove the username from the session if it's there
    session.pop("username", None)
    return redirect(url_for("index"))


# Define a rota para reset de password
@app.route("/forgot_pass", methods=["GET", "POST"])
def forgot_pass():
    if request.method == "POST":
        # Obtém o usuário e email informados no formulário
        username = request.form["username"]
        email = request.form["email"]
        userfound = db.users.find_one({"username": username, "email": email})

        if userfound != None:
            # Se as credenciais estiverem corretas, envia um email para o usuário
            # com a nova senha criada e redireciona para o login

            # Nova senha gerada
            generatedPass = id_generator()

            # Requisição por email
            msg = Message(
                "UX-Tracking password reset.",
                sender=app.config.get("MAIL_USERNAME"),
                recipients=[email],
            )

            #estilizando a mensagem de e-mail
            msg.html = render_template("email_forgot_pass.html", username= username, generatedPass = generatedPass)

            # Nova senha enviada
            mail.send(msg)

            flash('E-mail enviado com sucesso!')

            # senha alterada
            _id = userfound["_id"]
            db.users.update_one({"_id": _id}, {"$set": {"password": generatedPass}})

            # Redirecionar para o login após o envio do email e atualização da senha
            return redirect(url_for("login", title="Login", session=False))
        
        #Se as credenciais estiverem incorretas, retorna para a página de redefinir senha
        else: 
            flash('Usuário incorreto')
            return render_template('forgot_pass.html', session=False, title='Esqueci a senha')
    else:
        return render_template(
            "forgot_pass.html", session=False, title="Esqueci a senha"
        )


# Define a rota para a página de alteração de senha
@app.route("/change_pass", methods=["POST"])
def change_pass():
    if request.method == "POST":
        if "username" in session:
            # Obtém o usuário e a senha informados no formulário
            username = session["username"]
            password = request.form["password"]
            newpassword = request.form["newpassword"]
            newpassword2 = request.form["confirm_newpassword"]

            # Verifica se as credenciais estão corretas
            userfound = db.users.find_one({"username": username, "password": password})
            if userfound != None:
                if newpassword == newpassword2:
                    idd = userfound["_id"]
                    db.users.update_one(
                        {"_id": idd}, {"$set": {"password": newpassword}}
                    )
                    # Usuário logado
                    return redirect(
                        url_for(
                            "index",
                            session=True,
                            title="Home",
                            username=session["username"],
                        )
                    )

                else:
                    flash(
                        "Verifique se ambas as novas senhas são iguais e tente novamente!"
                    )
                    return render_template("index.html", session=True, title="Home")
            else:
                flash("A senha atual está incorreta!")
                return render_template("index.html", session=True, title="Home")

        else:
            flash("Faça o login!")
            return render_template("login.html", session=False, title="Login")


# Define a rota para a página principal
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "username" in session:
            # faz a leitura da base de dados de coletas do usuário
            userfound = db.users.find_one({"username": session["username"]})
            userid = userfound["_id"]
            datadir = f"./Samples/{userid}"

            folder = request.form.getlist("dates[]")
            folder = folder[0]

            # cria um zip para inserção dos dados selecionados
            with zipfile.ZipFile(f"{folder}_data.zip", "w") as zipf:
                for file in os.listdir(f"{datadir}/{folder}/"):
                    shutil.copy(f"{datadir}/{folder}/{file}", file)
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
    else:
        if "username" in session:
            # faz a leitura da base de dados de coletas do usuário
            userfound = db.users.find_one({"username": session["username"]})
            userid = userfound["_id"]
            datadir = f"./Samples/{userid}"

            # verifica quais datas estão disponíveis e limpa a string
            dates = []
            figdata = {}
            i = 0
            try:
                for folder in userfound["data"]:
                    date = userfound["data"][folder]["date"]
                    if date not in figdata.keys():
                        figdata[date] = 1
                    else:
                        figdata[date] += 1
                    if i <= 4:
                        i += 1
                        dates.append(
                            [
                                userfound["data"][folder]["date"],
                                userfound["data"][folder]["hour"],
                                userfound["data"][folder]["sites"],
                                folder,
                            ]
                        )

            except:
                None
            # gera o gráfico de últimas atividades
            layout = Layout(plot_bgcolor="rgba(0,0,0,0)")
            fig = go.Figure(layout=layout)
            fig.add_trace(
                go.Scatter(
                    x=list(figdata.keys()),
                    y=list(figdata.values()),
                    marker_size=10,
                    fill="tozeroy",
                    mode="lines+markers",  # override default markers+lines
                )
            )
            fig.update_xaxes(tick0=0, dtick=1)
            fig.update_yaxes(tick0=0, dtick=1)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                template="simple_white",
                font_color="#969696",
                xaxis_title="Data",
                yaxis_title="Coletas",
            )
            fig.update_xaxes(
                showline=True,
                linewidth=2,
                linecolor="#969696",
                gridcolor="#969696",
                mirror=True,
            )
            fig.update_yaxes(
                showgrid=True,
                showline=True,
                gridwidth=1,
                linewidth=2,
                linecolor="#969696",
                gridcolor="#969696",
                mirror=True,
                dtick=3,
            )

            plot_as_string = fig.to_html()
            # lista de coletas
            return render_template(
                "index.html",
                session=True,
                username=session["username"],
                title="Home",
                dates=dates,
                plot=plot_as_string,
            )
        else:
            return render_template("index.html", session=False, title="Home")

@app.route("/datafilter/<username>/<metadata>", methods=["GET", "POST"])
def datafilter(username, metadata):
    if request.method == "POST":
        if "username" in session:
            # faz a leitura da base de dados de coletas do usuário
            userfound = db.users.find_one({"username": session["username"]})
            userid = userfound["_id"]
            datadir = f"./Samples/{userid}"
            if metadata == "datetime":
                # adiciona as datas à seção
                session["dates"] = request.form.getlist("dates[]")
                # refireciona pra seleção dos traços
                return redirect(
                    url_for("datafilter", username=username, metadata="pages")
                )

            elif metadata == "pages":
                # adiciona as páginas à seção
                session["pages"] = request.form.getlist("pages[]")

                # cria csv para dados de traços
                tracefiltered = pd.DataFrame(
                    columns=[
                        "datetime",
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
                )

                # cria csv para dados de audio
                audiofiltered = pd.DataFrame(
                    columns=[
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
                )

                # cria um zip para inserção dos dados filtrados
                with zipfile.ZipFile(f"{username}_data.zip", "w") as zipf:
                    # filtragem dos dados utilizados
                    for date in session["dates"]:
                        df = pd.read_csv(f"{datadir}/{date}/trace.csv")
                        df = df[df.site.isin(session["pages"])]
                        df.insert(0, "datetime", [date] * len(df.index), True)
                        tracefiltered = pd.concat(
                            [tracefiltered, df], ignore_index=False
                        )
                        try:
                            df_audio = pd.read_csv(f"{datadir}/{date}/audio.csv")
                            df_audio = df_audio[df_audio.site.isin(session["pages"])]
                            df_audio.insert(
                                0, "datetime", [date] * len(df_audio.index), True
                            )
                            audiofiltered = pd.concat(
                                [audiofiltered, df_audio], ignore_index=False
                            )
                        except:
                            None
                        for image in df.image.unique():
                            try:
                                # adiciona as imagens ao zip
                                shutil.copy(f"{datadir}/{date}/{image}", image)
                                zipf.write(image)
                                os.remove(image)
                            except:
                                pass

                    # Criar diretório temporário
                    temp_dir = "/temp"
                    os.makedirs(temp_dir, exist_ok=True)
                    tracefiltered.to_csv(f"{temp_dir}/trace.csv", index=False)
                    audiofiltered.to_csv(f"{temp_dir}/audio.csv", index=False)

                    # escreve o traço concatenado
                    zipf.write(f"{temp_dir}/trace.csv", "trace.csv")
                    try:
                        zipf.write(f"{temp_dir}/audio.csv", "audio.csv")
                    except:
                        None
                    # Remover diretório temporário
                    shutil.rmtree(temp_dir)

                # limpando o zip criado
                with open(f"{username}_data.zip", "rb") as f:
                    data = f.readlines()
                os.remove(f"{username}_data.zip")

                # limpar os dados da sessão para nova consulta
                session.pop("dates", None)
                session.pop("pages", None)

                # fornecendo o zip pra download
                return Response(
                    data,
                    headers={
                        "Content-Type": "application/zip",
                        "Content-Disposition": f"attachment; filename={username}_data.zip;",
                    },
                )

            else:
                flash("404\nPage not found!")
                return render_template(
                    "data_filter.html", username=username, title="Coletas"
                )

        # se o usuário não está logado
        else:
            return render_template("index.html", session=False, title="Home")

    # método GET
    else:
        if "username" in session:
            # faz a leitura da base de dados de coletas do usuário
            userfound = db.users.find_one({"username": session["username"]})
            userid = userfound["_id"]
            datadir = f"./Samples/{userid}"

            if metadata == "datetime":
                # verifica quais datas estão disponíveis
                try:
                    dates = list_dates(datadir)
                except:
                    dates = []
                return render_template(
                    "data_filter.html",
                    username=username,
                    metadata=metadata,
                    items=dates,
                    title="Coletas",
                )

            elif metadata == "pages":
                dates = session["dates"]

                # verifica quais datas estão disponíveis
                pages = []
                for date in dates:
                    # Lendo as páginas no csv
                    df = pd.read_csv(f"{datadir}/{date}/trace.csv")
                    for page in df.site.unique():
                        if page not in pages:
                            pages.append(page)

                return render_template(
                    "data_filter.html",
                    username=username,
                    metadata=metadata,
                    items=pages,
                    title="Coletas",
                )

            else:
                flash("404\nPage not found!")
                return render_template(
                    "data_filter.html", username=username, title="Coletas"
                )

        # se o usuário não está logado
        else:
            return redirect(url_for("index"))


@app.route("/dataanalysis/<username>/", methods=["GET", "POST"])
@app.route("/dataanalysis/<username>/<model>", methods=["GET", "POST"])
def dataanalysis(username, model=None):
    if request.method == "POST":
        if "username" in session:
            # faz a leitura da base de dados de coletas do usuário
            userfound = db.users.find_one({"username": session["username"]})
            userid = userfound["_id"]
            datadir = f"./Samples/{userid}"

            dir = request.form["dir"]
            folder = f"{datadir}/{dir}"
            if model == "kmeans":
                return
            elif model == "meanshift":
                return
            elif model == "bertimbau":
                return nlpBertimbau(folder)
            else:
                flash("404\nPage not found!")
                return render_template(
                    "data_analysis.html", username=username, title="Análise"
                )

        # usuário não está logado
        else:
            flash("Faça o login para continuar!")
            return render_template("login.html", session=False, title="Login")

    # método GET
    else:
        if "username" in session:
            # faz a leitura da base de dados de coletas do usuário
            userfound = db.users.find_one({"username": session["username"]})
            userid = userfound["_id"]
            datadir = f"./Samples/{userid}"
            models = ["kmeans", "meanshift", "bertimbau"]
            if model == None:
                return render_template(
                    "data_analysis.html", username=username, title="Análise"
                )
            elif model in models:
                data = dirs2data(userfound)
                return render_template(
                    "data_analysis.html",
                    username=username,
                    model=model,
                    items=data,
                    title="Análise",
                )
            else:
                flash("404\nPage not found!")
                return render_template(
                    "data_analysis.html", username=username, title="Análise"
                )
        else:
            flash("Faça o login para continuar!")
            return render_template("login.html", session=False, title="Login")


@app.route("/dataview/<username>/", methods=["GET", "POST"])
@app.route("/dataview/<username>/<plot>", methods=["GET", "POST"])
def dataview(username, plot=None):
    if request.method == "POST":
        if "username" in session:
            # faz a leitura da base de dados de coletas do usuário
            userfound = db.users.find_one({"username": session["username"]})
            userid = userfound["_id"]
            datadir = f"./Samples/{userid}"

            dir = request.form["dir"]
            folder = f"{datadir}/{dir}"
            if plot == "heatmap":
                return make_heatmap(folder, type="mouse")
            elif plot == "recording":
                return make_recording(folder)
            elif plot == "nlp":
                return 
            else:
                flash("404\nPage not found!")
                return render_template(
                    "data_analysis.html", username=username, title="Análise"
                )

        # usuário não está logado
        else:
            flash("Faça o login para continuar!")
            return render_template("login.html", session=False, title="Login")

    # método GET
    else:
        if "username" in session:
            # faz a leitura da base de dados de coletas do usuário
            userfound = db.users.find_one({"username": session["username"]})
            userid = userfound["_id"]
            datadir = f"./Samples/{userid}"
            plots = ["heatmap", "recording"]

            if plot == None:
                return render_template(
                    "data_view.html", username=username, title="Visualização"
                )
            elif plot in plots:
                data = dirs2data(userfound)
                return render_template(
                    "data_view.html",
                    username=username,
                    plot=plot,
                    items=data,
                    title="Visualização",
                )
            else:
                flash("404\nPage not found!")
                return render_template(
                    "data_view.html", username=username, title="Visualização"
                )
        else:
            flash("Faça o login para continuar!")
            return render_template("login.html", session=False, title="Login")

@app.route("/external/", methods=["POST"])
@app.route("/external/userAuth", methods=["POST"])
def userAuth():
    username = request.form["username"]
    password = request.form["password"]
    userfound = db.users.find_one({"username": username, "password": password})

    if userfound != None:
        userid = userfound["_id"]
        session["username"] = request.form["username"]
        response = {"id": str(userid), 'status': 200}
    #Credenciais incorretas
    else:
        response = {"id": None, 'status': 401}

    return jsonify(response)

def send_email(subject, body):
    # Configurar as informações de email
    sender_email = app.config.get("MAIL_USERNAME")
    sender_password = app.config.get("MAIL_PASSWORD")
    receiver_email = 'flavio.moura@itec.ufpa.br'

    # Criar o objeto de mensagem
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Adicionar o corpo da mensagem
    message.attach(MIMEText(body, 'plain'))

    # Enviar o email usando SMTP
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()

if __name__ == "__main__":
    try:
        app.run(debug=False, host="0.0.0.0")
    except BaseException as e:
        dt = datetime.datetime.today()
        dt = f'{dt.day}/{dt.month}/{dt.year}'
        error_context = sys.exc_info()[1].__context__.strerror
        error_context = unidecode(error_context)
        error_msg = f'The application failed to start in {dt}.\r The message of error is: {sys.exc_info()[0]}:{e} - {error_context}'
        send_email("UX-Tracking Initialization Failed.", error_msg)
