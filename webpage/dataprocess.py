import os
import io
import shutil
import gridfs
import zipfile
from app import mongo
import pandas as pd
import plotly.io as pio
from io import StringIO
from bson import ObjectId
from datetime import datetime
from utils.data import userdata_summary
from django.core.paginator import Paginator
from utils.functions import (
    nlpBertimbau,
    graph_sentiment,
    dirs2data,
    make_heatmap,
    make_recording,
)
from utils.data import(
    userdata2frame
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
        userfound = mongo.users.find_one({"username": session["username"]})
        collection_name = f"data_{userfound['_id']}" #pasta dos documentos

        if metadata == "datetime":
            # adiciona as datas à seção
            session["dates"] = request.form.getlist("dates[]")

            # refireciona pra seleção dos traços
            return redirect(url_for("data_bp.datafilter_get", username=username, metadata="pages"))

        elif metadata == "pages":
            session["pages"] = request.form.getlist("pages[]")
            username = session.get("username")
            dates = session.get("dates")  # Supondo que as datas também estejam armazenadas na sessão

            # Preparando o DataFrame vazio com colunas definidas
            columns_trace = [
                "site", "image", "type", "time", "class", "id", "mouseClass", "mouseID", "x", "y", "scroll", "height", "keys",
            ]
            tracefiltered = pd.DataFrame(columns=columns_trace)
            
            columns_audio = [
                "site", "image", "type", "time", "class", "id", "mouseClass", "mouseID", "x", "y", "scroll", "height", "text"
            ]
            audiofiltered = pd.DataFrame(columns=columns_audio)

            # Preparando o DataFrame vazio com colunas definidas
            columns_emotions = [
                "site", "image", "type", "time", "class", "id", "mouseClass", "mouseID", "x", "y", "scroll", "height",
                "anger", "contempt", "disgust", "fear", "happy", "neutral", "sad", "surprise",
            ]
            facefiltered = pd.DataFrame(columns=columns_trace)

            # Criando o arquivo ZIP em memória
            memory_zip = io.BytesIO()
            with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:

                # Filtyrar dados para cada data especificada
                for date in dates:
                    
                    #preparando dataframes
                    trace_df = userdata2frame(
                        mongo,
                        collection_name,
                        date,
                        ["eye", "mouse", "keyboard", "freeze", "click", "wheel", "move"],
                    )
                    voice_df = userdata2frame(mongo, collection_name, date, "voice")
                    face_df = userdata2frame(mongo, collection_name, date, "face")

                    #data da coleta
                    document = mongo[collection_name].find_one({"_id": ObjectId(date)})
                    date = document["datetime"]["$date"]
                    date_obj = datetime.fromisoformat(date.rstrip("Z"))
                    date_part = date_obj.date().strftime("%d/%m/%Y")

                    #tratando os dados de acordo com as pages
                    df_site_trace = trace_df[trace_df.site.isin(session["pages"])]
                    df_site_voice = voice_df[voice_df.site.isin(session["pages"])]
                    df_site_face = face_df[face_df.site.isin(session["pages"])]

                    # Adiciona a coluna 'data' no início de todos os DataFrames
                    df_site_trace.insert(0, "data", [date_part]*len(df_site_trace.index), True)
                    df_site_voice.insert(0, "data", [date_part]*len(df_site_voice.index), True)
                    df_site_face.insert(0, "data", [date_part]*len(df_site_face.index), True)


                    #tratando os dados
                    tracefiltered = pd.concat([df_site_trace, tracefiltered])
                    audiofiltered = pd.concat([df_site_voice, audiofiltered])
                    facefiltered = pd.concat([df_site_face, facefiltered])

                    #tratando as imagens
                    image_ids = []

                    if "data" in document and isinstance(document["data"], list):
                        for site_data in document["data"]:
                            if "images" in site_data:
                                image_ids.extend(
                                    site_data["images"]
                                )


                    #guardando as imagens no zip
                    fs = gridfs.GridFS(mongo)
                    
                    for image_id in image_ids:
                        try:
                            grid_out = fs.get(image_id).read()
                            image_name = f'{str(image_id)}.png'
                            if image_name not in zipf.namelist():
                                zipf.writestr(image_name, grid_out)

                        except Exception as e:
                            abort(404, description=f"Erro ao recuperar a imagem {image_id}: {e}")

                    #verifica se os arquivos estão vazios 
                    if not tracefiltered.empty:
                        csv_buffer = io.StringIO()
                        tracefiltered.to_csv(csv_buffer, index=False)
                        csv_buffer.seek(0)
                        zipf.writestr('trace.csv', csv_buffer.read())
                    if not audiofiltered.empty:
                        csv_buffer = io.StringIO()
                        audiofiltered.to_csv(csv_buffer, index=False)
                        csv_buffer.seek(0)
                        zipf.writestr('voice.csv', csv_buffer.read())

                    if not facefiltered.empty:
                        csv_buffer = io.StringIO()
                        facefiltered.to_csv(csv_buffer, index=False)
                        csv_buffer.seek(0)
                        zipf.writestr('face.csv', csv_buffer.read())

            # Preparar o arquivo para download
            memory_zip.seek(0)
            return Response(    
                memory_zip,
                headers={
                    "Content-Type": "application/zip",
                    "Content-Disposition": f"attachment; filename={username}_data.zip;"
                }
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
        userfound = mongo.users.find_one({"username": session["username"]})
        collection_name = f"data_{userfound['_id']}" #pasta dos documentos
        documents = mongo[collection_name].find({})

        data, date_counts = userdata_summary(documents) #informações documentos

        if metadata == "datetime":
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
                #procurando os sites dos documentos pelo id
                document = mongo[collection_name].find_one({"_id": ObjectId(date)})
                site = document['sites']
                for page in site:
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
        userfound = mongo.users.find_one({"username": session["username"]})
        collection_name = f"data_{userfound['_id']}" #pasta dos documentos

        dir = request.form["dir"]
        
        if model == "kmeans":
            return
        elif model == "meanshift":
            return
        elif model == "bertimbau":
            results = {}
            df_voice = userdata2frame(mongo, collection_name, dir, "voice")
            try:
                df_audio = nlpBertimbau(df_voice)
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
        userfound = mongo.users.find_one({"username": session["username"]})
        collection_name = f"data_{userfound['_id']}"
        documents = mongo[collection_name].find({})

        data, date_counts = userdata_summary(documents)

        models = ["kmeans", "meanshift", "bertimbau"]
        if model == 'default':
            return render_template(
                "data_analysis.html", username=username, title="Análise"
            )
        elif model in models:
            # Paginação das coletas
            paginator = Paginator(data, 5)
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
    userfound = mongo.users.find_one({"username": session["username"]})
    collection_name = f"data_{userfound['_id']}"

    valueData = request.form["data"]

    df_voice = userdata2frame(mongo, collection_name, valueData, "voice")
    df_nlBertimbau = nlpBertimbau(df_voice)

    # Convertendo o DataFrame em um buffer de texto
    csv_buffer = StringIO()
    df_nlBertimbau.to_csv(csv_buffer, index=False)

    # Obtendo o conteúdo do buffer como uma string
    file_content = csv_buffer.getvalue()
    
    return Response(
        file_content,
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment; filename=voice.csv",
        },
    )


@data_bp.post("/dataview/<username>/<plot>")
def dataview_post(username, plot):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = mongo.users.find_one({"username": session["username"]})
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
            results = {}
            try:
                results['result1'] = make_recording(folder, type="mouse")
                results['result2'] = True
            except:
                results['result1'] = 'Não foi possível carregar o conteúdo'
                results['result2'] = False
            return results
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
        userfound = mongo.users.find_one({"username": session["username"]})
        if not userfound:
            abort(404)

        collection_name = f"data_{userfound['_id']}"
        documents = mongo[collection_name].find({})

        plots = ["heatmap", "recording"]

        if plot == 'default':
            return render_template(
                "data_view.html", username=username, title="Visualização"
            )
        elif plot in plots:
            data, _ = userdata_summary(documents)
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
