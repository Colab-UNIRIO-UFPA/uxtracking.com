import os
from app import oauth, db
from authlib.common.security import generate_token
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, Blueprint, request, flash, redirect, url_for, session

auth_bp = Blueprint(
    "auth_bp", "__name__", template_folder="templates", static_folder="static"
)


# Define a rota para a página de registro
@auth_bp.post("/register")
def register_post():
    # Obtém o usuário, a senha e o email informados no formulário
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")

    # Verifica se o email já existe na coleção de usuários
    email_found = mongo.users.find_one({"email": email})
    username_found = mongo.users.find_one({"username": username})

    if email_found is not None:
        flash("Esse email já foi cadastrado.")
        return render_template("register.html", title="Registrar")

    if username_found is not None:
        flash("Esse nome de usuário já está em uso.")
        return render_template("register.html", title="Registrar")

    hashed_password = generate_password_hash(password)
    # Insere o novo usuário na coleção de usuários, se nome de usuário e email estão disponíveis
    mongo.users.insert_one(
        {
            "username": username,
            "password": hashed_password,
            "email": email,
            "role": "user",
        }
    )

    # Cria uma coleção específica para o usuário com um documento inicial
    userfound = mongo.users.find_one({"username": username})
    user_collection_name=f"data_{userfound['_id']}"
    mongo[user_collection_name].insert_one(
        {"message": f"Coleção criada para o usuário {username}."}
    )

    # Redireciona para a página de login após o registro bem-sucedido
    flash("Registro bem-sucedido! Faça o login para continuar.")
    return redirect(url_for("auth_bp.login_get", title="Login"))


@auth_bp.get("/register")
def register_get():
    if "username" in session:
        return redirect(url_for("index_bp.index_get"))
    else:
        return render_template("register.html", session=False, title="Registrar")


# Define a rota para a página de login
@auth_bp.post("/login")
def login_post():
    # Obtém o usuário e a senha informados no formulário
    username = request.form["username"]
    password = request.form["password"]
    userfound = mongo.users.find_one({"username": username})

    if userfound and check_password_hash(userfound["password"], password):
        session["username"] = username
        return redirect(url_for("index_bp.index_get"))
    else:
        # Se as credenciais estiverem incorretas, exibe uma mensagem de erro
        flash("Usuário ou senha incorretos.")
        return render_template("login.html", session=False, title="Login")


@auth_bp.get("/login")
def login_get():
    # Se a requisição for GET, exibe a página de login
    if "username" in session:
        return redirect(url_for("index_bp.index_get"))
    else:
        return render_template("login.html", session=False, title="Login")


# autenticação google
@auth_bp.route("/google/")
def google():

    GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
    GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]

    CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={"scope": "openid email profile"},
    )

    # Redirect to google_auth function
    redirect_uri = url_for("auth_bp.google_auth", _external=True)
    session["nonce"] = generate_token()
    return oauth.google.authorize_redirect(redirect_uri, nonce=session["nonce"])


@auth_bp.route("/google/auth/")
def google_auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token, nonce=session["nonce"])
    username = user["name"]
    email = user["email"]
    password = user["sub"]

    # Verifica se o usuário já existe
    userfound = mongo.users.find_one({"email": email})
    if userfound == None:
        mongo.users.insert_one(
            {"username": username, "password": password, "email": email, "data": {}}
        )
    session["username"] = username
    return redirect("/")


# Define a rota para o logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index_bp.index_get"))
