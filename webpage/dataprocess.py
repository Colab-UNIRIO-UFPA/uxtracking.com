import os
import shutil
import zipfile
from app import db
import pandas as pd
import plotly.io as pio
from django.core.paginator import Paginator
from utils.functions import (
    nlpBertimbau,
    graph_sentiment,
    dirs2data,
    make_heatmap,
    make_recording,
)
from flask import (
    render_template,
    Blueprint,
    redirect,
    session,
    url_for,
    request,
    flash,
    Response,
    abort,
)

data_bp = Blueprint("data_bp", "__name__", template_folder="templates", static_folder="static")


@data_bp.post("/datafilter/<username>/<metadata>")
def datafilter_post(username, metadata):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = db.users.find_one({"username": session["username"]})
        userid = userfound["_id"]
        datadir = f"./Samples/{userid}"
        if metadata == "datetime":
            # adiciona as datas à seção
            session["dates"] = request.form.getlist("dates[]")

            # refireciona pra seleção dos traços
            return redirect(url_for("data_bp.datafilter_get", username=username, metadata="pages"))

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
                    df = pd.read_csv(
                        f"{datadir}/{date}/trace.csv", encoding="iso-8859-1"
                    )
                    df = df[df.site.isin(session["pages"])]
                    df.insert(0, "datetime", [date] * len(df.index), True)
                    tracefiltered = pd.concat([tracefiltered, df], ignore_index=False)
                    try:
                        df_audio = pd.read_csv(
                            f"{datadir}/{date}/audio.csv", encoding="iso-8859-1"
                        )
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


@data_bp.get("/datafilter/<username>/<metadata>")
def datafilter_get(username, metadata):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = db.users.find_one({"username": session["username"]})
        userid = userfound["_id"]
        datadir = f"./Samples/{userid}"

        if metadata == "datetime":
            data = dirs2data(userfound, datadir)
            data = data[::-1]

            # Paginação das coletas
            paginator = Paginator(data, 5)
            page_number = request.args.get("page_number", 1, type=int)
            page_obj = paginator.get_page(page_number)
            page_coleta = paginator.page(page_number).object_list

            return render_template(
                "data_filter.html",
                username=username,
                metadata=metadata,
                items=page_coleta,
                page_obj=page_obj,
                title="Coletas",
            )

        elif metadata == "pages":
            dates = session["dates"]

            # verifica quais datas estão disponíveis
            pages = []
            for date in dates:
                # Lendo as páginas no csv
                df = pd.read_csv(f"{datadir}/{date}/trace.csv", encoding="iso-8859-1")
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
        return redirect(url_for("index_bp.index_get"))


@data_bp.post("/dataanalysis/<username>/<model>")
def dataanalysis_post(username, model):
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
            results = {}
            try:
                df_audio = nlpBertimbau(folder)
                fig = graph_sentiment(df_audio)
                results["result1"] = pio.to_json(fig)
                results["result2"] = True
            except:
                results["result1"] = (
                    "Não foi possível processar a coleta, áudio ausente!"
                )
                results["result2"] = False

            return results

        else:
            flash("404\nPage not found!")
            return render_template(
                "data_analysis.html", username=username, title="Análise"
            )

    # usuário não está logado
    else:
        flash("Faça o login para continuar!")
        return render_template("login.html", session=False, title="Login")


@data_bp.get("/dataanalysis/<username>/<model>")
def dataanalysis_get(username, model):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = db.users.find_one({"username": session["username"]})
        userid = userfound["_id"]
        datadir = f"./Samples/{userid}"
        models = ["kmeans", "meanshift", "bertimbau"]
        if model == 'default':
            return render_template(
                "data_analysis.html", username=username, title="Análise"
            )
        elif model in models:
            data = dirs2data(userfound, datadir)
            data = data[::-1]

            # Paginação das coletas
            paginator = Paginator(data, 7)
            page_number = request.args.get("page_number", 1, type=int)
            page_obj = paginator.get_page(page_number)
            page_coleta = paginator.page(page_number).object_list

            return render_template(
                "data_analysis.html",
                username=username,
                model=model,
                items=page_coleta,
                page_obj=page_obj,
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


@data_bp.post("/downloadAudio")
def downloadAudio():
    userfound = db.users.find_one({"username": session["username"]})
    userid = userfound["_id"]
    datadir = f"./Samples/{userid}"

    valueData = request.form["data"]

    base_path = os.path.normpath(datadir)

    file_path = os.path.normpath(os.path.join(datadir, valueData, "audio.csv"))

    if not file_path.startswith(base_path):
        abort(403)

    with open(file_path, "rb") as file:
        file_content = file.read()

    return Response(
        file_content,
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment; filename=audio.csv",
        },
    )


@data_bp.post("/dataview/<username>/<plot>")
def dataview_post(username, plot):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = db.users.find_one({"username": session["username"]})
        userid = userfound["_id"]
        datadir = f"./Samples/{userid}"

        dir = request.form["dir"]

        # normalizando caminho base
        base_path = os.path.normpath(datadir)

        # normalizando caminho completo
        folder = os.path.normpath(os.path.join(base_path, dir))

        if not folder.startswith(base_path):
            abort(403)

        if plot == "heatmap":
            return make_heatmap(folder)
        elif plot == "recording":
            return make_recording(folder, type="mouse")
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


@data_bp.get("/dataview/<username>/<plot>")
def dataview_get(username, plot):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = db.users.find_one({"username": session["username"]})
        userid = userfound["_id"]
        datadir = f"./Samples/{userid}"
        plots = ["heatmap", "recording"]

        if plot == 'default':
            return render_template(
                "data_view.html", username=username, title="Visualização"
            )
        elif plot in plots:
            data = dirs2data(userfound, datadir)
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
