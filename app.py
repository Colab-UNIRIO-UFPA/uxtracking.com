from flask import Flask, render_template, request, redirect, url_for, Response, after_this_request
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
import os
import base64
import re
from functions import auth, generate_user_id, clean, id_generator
from flask import session, send_file
from flask_mail import Mail,  Message
from simple_colors import *
import csv
from pathlib import Path
import pandas as pd
import zipfile
import shutil

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = os.environ['MAIL_NAME'],
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
)
mail = Mail(app)

# Define a rota para o envio dos dados pela ferramenta
# Organização do patch:
# (Diretório de samples)/(ID do usuário, gerado pela função generate_user_id em functions.py)/(site coletado)/(YYYYMMDD-HHMMSS da coleta)/(dados da coleta)
@app.route('/receiver', methods=['POST'])
def receiver():
    metadata = request.form['metadata']
    data = request.form['data']
    metadata = json.loads(metadata)
    userid = metadata['userId']
    dateTime = str(metadata['dateTime'])
    data = json.loads(data)

    if not os.path.exists("Samples"):
        os.makedirs("Samples", exist_ok=True)
    else:
        if not os.path.exists(f'Samples/{userid}'):
            os.makedirs(f'Samples/{userid}', exist_ok=True)
        else:
            if not os.path.exists(f'Samples/{userid}/' + str(metadata['dateTime'])):
                os.makedirs(f'Samples/{userid}/' + str(metadata['dateTime']), exist_ok=True)

    try:
        if data['imageData'] != "NO":
            if not os.path.exists(f'Samples/{userid}/' + str(metadata['dateTime']) + '/' + str(data['imageName'])):
                imageData = base64.b64decode(re.sub('^data:image/\w+;base64,', '', data['imageData']))
                with open(f'Samples/{userid}/' + str(metadata['dateTime']) + '/' + str(data['imageName']), "wb") as fh:
                    fh.write(imageData)
    
    except:
        None
    # if metadata['type'] == "eye":
    #     with open('Samples/' + sample + '/' + str(metadata['dateTime']) + '/traceX.txt', 'a') as f:
    #         f.write(data['X'] + '\n')
    #     with open('Samples/' + sample + '/' + str(metadata['dateTime']) + '/traceY.txt', 'a') as f:
    #         f.write(data['Y'] + '\n')
    #     with open('Samples/' + sample + '/' + str(metadata['dateTime']) + '/traceTime.txt', 'a') as f:
    #         f.write(str(metadata['dateTime']) + '\n')
    # else:
    
    traceData = ['eye', 'mouse', 'keyboard', 'freeze', 'click', 'wheel', 'move']
    if str(metadata['type']) in traceData:
        if not os.path.exists(f'Samples/{userid}/{dateTime}/trace.csv'):
            # se a base não existe, cria o csv
            fields = ['site',
                    'type',
                    'time',
                    'image',
                    'class',
                    'id',
                    'mouseClass',
                    'mouseId',
                    'x',
                    'y',
                    'keys',
                    'scroll',
                    'height']
            
            file = Path(f'Samples/{userid}/{dateTime}/trace.csv')
            file.touch(exist_ok=True)
            
            with open(f'Samples/{userid}/{dateTime}/trace.csv', 'w') as csvfile:
                # criando um objeto csv dict writer
                csvwriter = csv.writer(csvfile)
                # escrever cabeçalhos (nomes de campo)
                csvwriter.writerow(fields)
            
        with open(f'Samples/{userid}/{dateTime}/trace.csv', 'a') as csvfile:
            # criando um objeto csv dict writer
            csvwriter = csv.writer(csvfile)
            # escrever linha (dados)
            csvwriter.writerow([str(metadata['sample']),
                            str(metadata['type']),
                            str(metadata['time']),
                            str(data['imageName']),
                            str(data['Class']),
                            str(data['Id']),
                            str(data['mouseClass']),
                            str(data['mouseId']),
                            str(data['X']),
                            str(data['Y']),
                            str(data['Typed']),
                            str(metadata['scroll']),
                            str(metadata['height'])])

        with open(f'Samples/{userid}/' + str(metadata['dateTime']) + '/lastTime.txt', 'w') as f:
            f.write(str(metadata['dateTime']))
            
        return "received"
    
    #se for um dado de voz
    else:
        ##########################################################
        #IMPLEMENTAR
        print(metadata['type'])
        if not os.path.exists(f'Samples/{userid}/{dateTime}/audio.csv'):
            # se a base não existe, cria o csv
            fields = ['site',
                      'time',
                    'text',
                    'image',
                    'class',
                    'id',
                    'mouseClass',
                    'mouseId',
                    'x',
                    'y',
                    'scroll',
                    'height']
            
            file = Path(f'Samples/{userid}/{dateTime}/audio.csv')
            file.touch(exist_ok=True)
            
            with open(f'Samples/{userid}/{dateTime}/audio.csv', 'w') as csvfile:
                # criando um objeto csv dict writer
                csvwriter = csv.writer(csvfile)
                # escrever cabeçalhos (nomes de campo)
                csvwriter.writerow(fields)
            
        with open(f'Samples/{userid}/{dateTime}/audio.csv', 'a') as csvfile:
            # criando um objeto csv dict writer
            csvwriter = csv.writer(csvfile)
            # escrever linha (dados)
            csvwriter.writerow([str(metadata['sample']),
                                str(metadata['time']),
                                str(data['Spoken']),
                                str(data['imageName']),
                                str(data['Class']),
                                str(data['Id']),
                                str(data['mouseClass']),
                                str(data['mouseId']),
                                str(data['X']),
                                str(data['Y']),
                                str(metadata['scroll']),
                                str(metadata['height'])])

        with open(f'Samples/{userid}/' + str(metadata['dateTime']) + '/lastTime.txt', 'w') as f:
            f.write(str(metadata['dateTime']))
            
        return "received"
        ##########################################################
# Define a rota para o envio dos dados pela ferramenta
# Organização do patch:
# (Diretório de samples)/(ID do usuário, gerado pela função generate_user_id em functions.py)/(site coletado)/(data+hora da coleta)/(dados da coleta)
@app.route('/sample_checker', methods=['POST'])
def sample_checker():
    if request.method == 'POST':
        time = request.form['dateTime']
        userid = request.form['userId']
        if not os.path.exists(f'Samples/{userid}/' + time):
            os.makedirs(f'Samples/{userid}/' + time, mode=0o777, exist_ok=True)
        filename = f'Samples/{userid}/'+ time + '/lastTime.txt'
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                content = file.read()
                return content
        else:
            return '0'

# Define a rota para a página de registro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Obtém o usuário e a senha informados no formulário
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        # Verifica se o usuário já existe
        verification = auth(username, email)
        if verification[0]:
            return render_template("register.html", error=verification[1])

        else:
            with open("users.json", "r") as arquivo:
                users = json.load(arquivo)

            users.append({  "username": username,
                            "password": password,
                            "email": email,
                            "id": generate_user_id(username, email)})
            # Abre o arquivo usuarios.json em modo de escrita
            with open("users.json", "w") as arquivo:
                # Escreve a lista de usuários atualizada no arquivo
                json.dump(users, arquivo)
        # Redireciona para a página de login
        return redirect(url_for("login"))
    
    else:
        # Se a requisição for GET, exibe a página de registro
        return render_template("register.html")

# Define a rota para a página de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Obtém o usuário e a senha informados no formulário
        username = request.form["username"]
        password = request.form["password"]

        # Verifica se as credenciais estão corretas
        with open("users.json", "r") as arquivo:
                users = json.load(arquivo)
        for user in users:
            if user['username'] == username and user['password'] == password:
        # Se as credenciais estiverem corretas, redireciona para a página principal
                session['username'] = request.form['username']
                return redirect(url_for("index"))
        else:
            # Se as credenciais estiverem incorretas, exibe uma mensagem de erro
            error = "Usuário ou senha incorretos."
            return render_template("login.html", error=error)
    else:
        # Se a requisição for GET, exibe a página de login
        return render_template("login.html")

# Define a rota para a página de login
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# Define a rota para reset de password
@app.route('/forgot_pass', methods=["GET", "POST"])
def forgot_pass():
    if request.method == "POST":
        # Obtém o usuário e email informados no formulário
        username = request.form["username"]
        email = request.form["email"]

        with open("users.json", "r") as arquivo:
                users = json.load(arquivo)
        for i in range(len(users)):
            if users[i]['username'] == username and users[i]['email'] == email:
                # Se as credenciais estiverem corretas, envia um email para o usuário
                # com a nova senha criada e redireciona para o login

                #Nova senha gerada
                generatedPass = id_generator()

                #Requisição por email
                msg = Message( 
                                'UX-Tracking password reset.', 
                                sender = app.config.get("MAIL_USERNAME"), 
                                recipients = [email] 
                            ) 
                
                msg.body = f'''
Dear {username}!
We are sending you this message because you have been asked to reset your password on our platform, the new password generated for your account is below:

{generatedPass}

If you are not the one who made the request, only you will see this password and will be able to change it on our platform.
________________________________________________________
This email was generated anonymously and automatically by an unmonitored email account, so please do not reply to this email.'''

                #Nova senha enviada
                mail.send(msg)

                #Senha do usuário alterada na BD
                users[i]['password'] = generatedPass

                # Abre o arquivo usuarios.json em modo de escrita
                with open("users.json", "w") as arquivo:
                    # Escreve a lista de usuários atualizada no arquivo
                    json.dump(users, arquivo)

                #Redirecionar para o login
                return redirect(url_for("login"))
    else:
        return render_template("forgot_pass.html")

# Define a rota para a página de alteração de senha
@app.route("/change_pass", methods=["GET", "POST"])
def change_pass():
    if request.method == "POST":
        # Obtém o usuário e a senha informados no formulário
        username = request.form["username"]
        password = request.form["password"]
        newpassword = request.form["newpassword"]

        # Verifica se as credenciais estão corretas
        with open("users.json", "r") as arquivo:
                users = json.load(arquivo)
        for i in range(len(users)):
            if users[i]['username'] == username and users[i]['password'] == password:
                if newpassword == request.form["confirm_newpassword"]:
                    #Senha do usuário alterada para a fornecida
                    users[i]['password'] = newpassword

                    # Abre o arquivo usuarios.json em modo de escrita
                    with open("users.json", "w") as arquivo:
                        # Escreve a lista de usuários atualizada no arquivo
                        json.dump(users, arquivo)

                    #Usuário logado
                    session['username'] = request.form['username']
                    return redirect(url_for("index"))
                
                else:
                    error = "Make sure the new passwords match!"
                    return render_template("change_pass.html", error=error)
            else:
                error = "The username or password is incorrect."
                return render_template("change_pass.html", error=error)
            
    else:
        # Se a requisição for GET, exibe a página de alteração de senha
        return render_template("change_pass.html")

# Define a rota para a página principal
@app.route("/", methods=["GET", "POST"])
def index():
    if 'username' in session:
        return render_template('index.html', session=True, username=session['username'])
    else:
        return render_template('index.html', session=False)

    """
    if request.method == "POST":
        # Obtém o arquivo JSON enviado pelo usuário
        file = request.files["file"]

        # Carrega os dados do arquivo JSON
        data = json.load(file)

        # Obtém os dados de navegação do arquivo JSON
        navigation_data = data["navigation_data"]

        # Cria o gráfico com os dados de navegação
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)
        fig.add_trace(go.Scatter(x=[x["page"] for x in navigation_data],
                                 y=[x["scroll_height"] - x["scroll_top"] for x in navigation_data],
                                 mode="markers",
                                 marker=dict(color=[x["trace"] for x in navigation_data],
                                             colorscale="Viridis",
                                             size=5)),
                                 row=1, col=1)
        fig.add_trace(go.Scatter(x=[x["page"] for x in navigation_data],
                                        y=[x["mouse_y"] for x in navigation_data],
                                        mode="markers",
                                        marker=dict(color=[x["trace"] for x in navigation_data],
                                                    colorscale="Viridis",
                                                    size=5)),
                                        row=2, col=1)
        fig.update_layout(height=600, title_text="Dados de Navegação do Usuário")

        # Renderiza o gráfico na página principal
        return render_template("index.html", graph_json=fig.to_json())
    else:
        # Se a requisição for GET, exibe a página principal
        return render_template("index.html")
    """

@app.route('/datafilter/<username>/<metadata>', methods=["GET", "POST"])
def datafilter(username, metadata):
    if request.method == 'POST':
        if 'username' in session:
            #faz a leitura da base de dados de coletas do usuário
            with open("users.json", "r") as arquivo:
                    users = json.load(arquivo)
            for i in range(len(users)):
                if users[i]['username'] == username:
                    userid = users[i]['id']
            datadir=f'./Samples/{userid}'


            if metadata == 'datetime':
                #adiciona as datas à seção
                session['dates'] = request.form.getlist('dates[]')
                #refireciona pra seleção dos traços
                return redirect(url_for('datafilter', username=username, metadata='pages'))

            elif metadata == 'pages':
                #adiciona as páginas à seção
                session['pages'] = request.form.getlist('pages[]')

                #cria csv para dados de traços
                tracefiltered = pd.DataFrame(columns = ['datetime',
                                                    'site',
                                                    'type',
                                                    'time',
                                                    'image',
                                                    'class',
                                                    'id',
                                                    'mouseClass',
                                                    'mouseId',
                                                    'x',
                                                    'y',
                                                    'keys',
                                                    'scroll',
                                                    'height'])
                
                #cria csv para dados de audio
                audiofiltered = pd.DataFrame(columns = ['site',
                                                        'time',
                                                        'text',
                                                        'image',
                                                        'class',
                                                        'id',
                                                        'mouseClass',
                                                        'mouseId',
                                                        'x',
                                                        'y',
                                                        'scroll',
                                                        'height'])
                
                ##################################################################
                #implementar try except para retornar dados de áudio concatenados#
                ##################################################################

                with zipfile.ZipFile(f'{username}_data.zip', 'w') as zipf:    
                    #filtragem dos dados utilizados
                    for date in session['dates']:
                        df = pd.read_csv(f'{datadir}/{date}/trace.csv')
                        df = df[df.site.isin(session['pages'])]
                        df.insert(0, 'datetime',  [date]*len(df. index), True)
                        tracefiltered = pd.concat([tracefiltered, df], ignore_index=False)

                        df_audio = pd.read_csv(f'{datadir}/{date}/audio.csv')
                        df_audio = df_audio[df_audio.site.isin(session['pages'])]
                        df_audio.insert(0, 'datetime',  [date]*len(df_audio. index), True)
                        audiofiltered = pd.concat([audiofiltered, df_audio], ignore_index=False)

                        for image in df.image.unique():
                            try:
                                #adiciona as imagens ao zip
                                shutil.copy(f'{datadir}/{date}/{image}', image)
                                zipf.write(image)
                                os.remove(image)
                            except:
                                pass
                        
                    # Criar diretório temporário
                    temp_dir = '/temp'
                    os.makedirs(temp_dir, exist_ok=True)
                    tracefiltered.to_csv(f'{temp_dir}/trace.csv',index=False)
                    audiofiltered.to_csv(f'{temp_dir}/audio.csv',index=False)
                    #escreve o traço concatenado
                    zipf.write(f'{temp_dir}/trace.csv', "trace.csv")
                    zipf.write(f'{temp_dir}/audio.csv', "audio.csv")
                    # Remover diretório temporário
                    shutil.rmtree(temp_dir)

                #limpando o zip criado
                with open(f'{username}_data.zip', 'rb') as f:
                    data = f.readlines()
                os.remove(f'{username}_data.zip')

                #limpar os dados da sessão para nova consulta
                session.pop('dates', None)
                session.pop('pages', None)

                #fornecendo o zip pra download
                return Response(data, headers={
                    'Content-Type': 'application/zip',
                    'Content-Disposition': f'attachment; filename={username}_data.zip;'
                })
            
            else:
                error = '404\nPage not found!'
                return render_template("datafilter.html", username=username, error = error)
        
        #se o usuário não está logado
        else:
            return render_template('index.html', session=False)
                
    #método GET
    else:
        if 'username' in session:
            #faz a leitura da base de dados de coletas do usuário
            with open("users.json", "r") as arquivo:
                    users = json.load(arquivo)
            for i in range(len(users)):
                if users[i]['username'] == username:
                    userid = users[i]['id']
            datadir=f'./Samples/{userid}'
            
            if metadata == 'datetime':
                dates = []
                #verifica quais datas estão disponíveis
                for date in os.listdir(datadir):
                    dates.append(date)
                
                return render_template("datafilter.html", username=username, metadata=metadata, items=dates)
            
            elif metadata == 'pages':
                dates = session['dates']
                
                #verifica quais datas estão disponíveis
                pages = []
                for date in dates:
                    # Lendo as páginas no csv 
                    df = pd.read_csv(f'{datadir}/{date}/trace.csv')
                    for page in df.site.unique():
                        if page not in pages:
                            pages.append(page)
                
                return render_template("datafilter.html", username=username, metadata=metadata, items=pages)
            
            else:
                error = '404\nPage not found!'
                return render_template("datafilter.html", username=username, error = error)
        
        #se o usuário não está logado
        else:
            return render_template('index.html', session=False)
    
if __name__ == "__main__":
    app.run(debug=False)