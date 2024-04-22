from flask_mail import Message
from app import mongo, mail, mail_username
from utils.functions import id_generator
from flask import render_template, Blueprint, request, session, jsonify

external_auth_bp = Blueprint(
    "external_auth_bp", "__name__", template_folder="templates", static_folder="static"
)


@external_auth_bp.post("/userAuth")
def userAuth():
    username = request.form["username"]
    password = request.form["password"]
    userfound = mongo.users.find_one({"username": username, "password": password})

    if userfound != None:
        userid = userfound["_id"]
        session["username"] = request.form["username"]
        response = {"id": str(userid), "status": 200}
    # Credenciais incorretas
    else:
        response = {"id": None, "status": 401}

    return jsonify(response)


@external_auth_bp.post("/userRegister")
def userRegister():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]

    # Verifica se o usuário já existe
    userfound = mongo.users.find_one({"$or": [{"email": email}, {"username": username}]})
    if userfound == None:
        mongo.users.insert_one(
            {"username": username, "password": password, "email": email, "data": {}}
        )
        userfound = mongo.users.find_one({"username": username, "password": password})
        response = {"id": str(userfound["_id"]), "status": 200}
    else:
        response = {"id": None, "status": 401}

    return jsonify(response)


@external_auth_bp.post("/userRecover")
def userRecover():
    # Obtém o usuário e email informados no formulário
    email = request.form["email"]
    userfound = mongo.users.find_one({"email": email})

    if userfound != None:
        # Nova senha gerada
        generatedPass = id_generator()

        # Requisição por email
        msg = Message(
            "UX-Tracking password reset.",
            sender=mail_username,
            recipients=[email],
        )

        # estilizando a mensagem de e-mail
        msg.html = render_template(
            "email_forgot_pass.html",
            username=userfound["username"],
            generatedPass=generatedPass,
        )

        # Nova senha enviada
        mail.send(msg)

        # senha alterada
        _id = userfound["_id"]
        mongo.users.update_one({"_id": _id}, {"$set": {"password": generatedPass}})

        response = {"status": 200}

    # Se as credenciais estiverem incorretas, retorna para a página de redefinir senha
    else:
        response = {"status": 401}

    return jsonify(response)
