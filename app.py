# Organização do patch:
#/Samples (Diretório de samples)
#   /ID (ID do usuário, gerado pela função generate_user_id em functions.py)
#       /wwwsitecom (site coletado)
#           /YYYYMMDD-HHMMSS (data da coleta)
#               Dados (dados da coleta)
#/static (diretório de arquivos estáticos carregáveis pelo Flask)
#   /css (estilo das páginas HTML)
#   /js (códigos javascript de estilo para as páginas HTML)
#   logo
#   UX-Tracking Extension (zipado da extensão para download)
#   UX-Tracking Tools (ferramentas de plotagem - Será retirado)
#/templates (páginas das rotas)
#app.py (arquivo principal do serviço em Flask)
#functions.py (funções chamadas no código do serviço)

from flask import Flask, render_template, request, redirect, url_for
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
import os
import base64
import re
from functions import auth, generate_user_id, clean
from flask import session, send_file

app = Flask(__name__)
app.secret_key = '9214u012jr120421jk490124'

# Define a rota para o envio dos dados pela ferramenta
@app.route('/receiver', methods=['POST'])
def receiver():
    metadata = request.form['metadata']
    data = request.form['data']
    metadata = json.loads(metadata)
    userid = metadata['userId']
    data = json.loads(data)
    sample = clean(metadata['sample'])
    if not os.path.exists("Samples"):
        os.makedirs("Samples", exist_ok=True)
    else:
        if not os.path.exists(f'Samples/{userid}/'+ sample):
            os.makedirs(f'Samples/{userid}', exist_ok=True)
            os.makedirs(f'Samples/{userid}/'+sample, exist_ok=True)
        else:
            if not os.path.exists(f'Samples/{userid}/' + sample + '/' + str(metadata['dateTime'])):
                os.makedirs(f'Samples/{userid}/' + sample + '/' + str(metadata['dateTime']), exist_ok=True)

    try:
        if data['imageData'] != "NO":
            if not os.path.exists(f'Samples/{userid}/' + sample + '/' + str(metadata['dateTime']) + '/' + str(data['imageName'])):
                imageData = base64.b64decode(re.sub('^data:image/\w+;base64,', '', data['imageData']))
                with open(f'Samples/{userid}/' + sample + '/' + str(metadata['dateTime']) + '/' + str(data['imageName']), "wb") as fh:
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
    with open(f'Samples/{userid}/' + sample + '/' + str(metadata['dateTime']) + '/trace.xml', 'a') as f:
        txt = "<rawtrace type=\"" + str(metadata['type']) + "\" image=\"" + str(data['imageName']) + "\" time=\"" + str(metadata['dateTime']) + "\" Class=\"" + str(data['Class']) + "\" Id=\"" + str(data['Id']) + "\" MouseClass=\"" + str(data['mouseClass']) + "\" MouseId=\"" + str(data['mouseId']) + "\" X=\"" + str(data['X']) + "\" Y=\"" + str(data['Y']) + "\" keys=\"" + str(data['Typed']) + "\" scroll=\"" + str(metadata['scroll']) + "\" height=\"" + str(metadata['height']) + "\" url=\"" + str(metadata['url']) + "\" />"
        f.write(txt + '\n')
    with open(f'Samples/{userid}/' + sample + '/' + str(metadata['dateTime']) + '/lastTime.txt', 'w') as f:
        f.write(str(metadata['dateTime']))
    return "received"

# Define a rota para o envio dos dados pela ferramenta
@app.route('/sample_checker', methods=['POST'])
def sample_checker():
    if request.method == 'POST':
        time = request.form['dateTime']
        userid = request.form['userId']
        domain = clean(request.form['domain'])
        if not os.path.exists(f'Samples/{userid}/'+ domain + '/' + time):
            os.makedirs(f'Samples/{userid}/' + domain + '/' + time, mode=0o777, exist_ok=True)
        filename = f'Samples/{userid}/'+ domain + '/' + time + '/lastTime.txt'
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
            session['username'] = username
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

@app.route('/forgot_pass', methods=["GET", "POST"])
def forgot_pass():
    if request.method == "POST":
        # Obtém o usuário e email informados no formulário
        username = request.form["username"]
        email = request.form["email"]

        with open("users.json", "r") as arquivo:
                users = json.load(arquivo)
        for user in users:
            if user['username'] == username and user['email'] == email:
                # Se as credenciais estiverem corretas, envia um email para o usuário
                # realizar a criação de nova senha e redireciona para o login
                email=email #IMPLEMENTAR
                #
                #
                #
                #
                #
                #
                #
                ################################
                return redirect(url_for("login"))
    else:
        return render_template("forgot_pass.html")

# Define a rota para a página principal
@app.route("/", methods=["GET", "POST"])
def index():
    if 'username' in session:
        return render_template('index.html', session=True)
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

@app.route("/download/<filename>")
def download(filename):
    if filename == "UX-Tracking Extension.zip" or filename == "UX-Tracking Tools.zip":
        return send_file({{url_for('static', filename=filename)}}, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)