from flask import Flask, render_template, request, redirect, url_for
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
import os
import base64
import re
from functions import auth, generate_user_id, clean

app = Flask(__name__)

# Define a rota para o envio dos dados pela ferramenta
# Organização do patch:
# (Diretório de samples)/(ID do usuário, gerado pela função generate_user_id em functions.py)/(site coletado)/(data+hora da coleta)/(dados da coleta)
@app.route('/receiver', methods=['POST'])
def receiver():
    metadata = request.form['metadata']
    data = request.form['data']
    metadata = json.loads(metadata)
    userid = metadata['userId']
    data = json.loads(data)
    sample = clean(metadata['sample'])
    if not os.path.exists("Samples"):
        os.mkdir("Samples")
    else:
        if not os.path.exists(f'Samples/{userid}/'+ sample):
            os.mkdir(f'Samples/{userid}')
            os.mkdir(f'Samples/{userid}/'+sample)
        else:
            if not os.path.exists(f'Samples/{userid}/' + sample + '/' + str(metadata['time'])):
                os.mkdir(f'Samples/{userid}/' + sample + '/' + str(metadata['time']))
    if data['imageData'] != "NO":
        if not os.path.exists(f'Samples/{userid}/' + sample + '/' + str(metadata['time']) + '/' + str(data['imageName'])):
            imageData = base64.b64decode(re.sub('^data:image/\w+;base64,', '', data['imageData']))
            with open(f'Samples/{userid}/' + sample + '/' + str(metadata['time']) + '/' + str(data['imageName']), "wb") as fh:
                fh.write(imageData)
    # if metadata['type'] == "eye":
    #     with open('Samples/' + sample + '/' + str(metadata['time']) + '/traceX.txt', 'a') as f:
    #         f.write(data['X'] + '\n')
    #     with open('Samples/' + sample + '/' + str(metadata['time']) + '/traceY.txt', 'a') as f:
    #         f.write(data['Y'] + '\n')
    #     with open('Samples/' + sample + '/' + str(metadata['time']) + '/traceTime.txt', 'a') as f:
    #         f.write(str(metadata['time']) + '\n')
    # else:
    with open(f'Samples/{userid}/' + sample + '/' + str(metadata['time']) + '/trace.xml', 'a') as f:
        txt = "<rawtrace type=\"" + str(metadata['type']) + "\" image=\"" + str(data['imageName']) + "\" time=\"" + str(metadata['time']) + "\" Class=\"" + str(data['Class']) + "\" Id=\"" + str(data['Id']) + "\" MouseClass=\"" + str(data['mouseClass']) + "\" MouseId=\"" + str(data['mouseId']) + "\" X=\"" + str(data['X']) + "\" Y=\"" + str(data['Y']) + "\" keys=\"" + str(data['Typed']) + "\" scroll=\"" + str(metadata['scroll']) + "\" height=\"" + str(metadata['height']) + "\" url=\"" + str(metadata['url']) + "\" />"
        f.write(txt + '\n')
    with open(f'Samples/{userid}/' + sample + '/' + str(metadata['time']) + '/lastTime.txt', 'w') as f:
        f.write(str(metadata['time']))
    return "received"

# Define a rota para o envio dos dados pela ferramenta
# Organização do patch:
# (Diretório de samples)/(ID do usuário, gerado pela função generate_user_id em functions.py)/(site coletado)/(data+hora da coleta)/(dados da coleta)
@app.route('/sample_checker', methods=['POST'])
def sample_checker():
    if request.method == 'POST':
        time = request.form['time']
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

            users.append({  "name": username,
                            "pass": password,
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
            if user['name'] == username and user['pass'] == password:
        # Se as credenciais estiverem corretas, redireciona para a página principal
                return redirect(url_for("index"))
        else:
            # Se as credenciais estiverem incorretas, exibe uma mensagem de erro
            error = "Usuário ou senha incorretos."
            return render_template("login.html", error=error)
    else:
        # Se a requisição for GET, exibe a página de login
        return render_template("login.html")

# Define a rota para a página principal
@app.route("/", methods=["GET", "POST"])
def index():
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

if __name__ == "__main__":
    app.run(debug=False)