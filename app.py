from pymongo import MongoClient
from flask import Flask
from authlib.integrations.flask_client import OAuth
import os
import gridfs
from flask_mail import Mail
from simple_colors import *
import datetime
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
from unidecode import unidecode
from torchvision import models
import torch.nn as nn
import torch
from utils.example_user import gen_example


# declarando o servidor
def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ["SECRET_KEY"]

    # configurando o serviço de email
    app.config.update(
        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USERNAME=os.environ["MAIL_NAME"],
        MAIL_PASSWORD=os.environ["MAIL_PASSWORD"]
    )
    mail_username = app.config.get("MAIL_USERNAME")
    mail = Mail(app)

    return app, mail, mail_username

def load_fer():
    model = models.efficientnet_b0(weights=None)
    # Add classifier
    num_ftrs = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.1),
        nn.Linear(num_ftrs, 512),
        nn.ReLU(),
        nn.BatchNorm1d(512),
        nn.Dropout(0.1),
        nn.Linear(512, 8),
    )
    model.load_state_dict(
        torch.load(
            "static/efficientnet.pth",
            map_location=torch.device("cpu"),
        )
    )
    model.to(torch.device("cpu"))
    model.eval()

    return model

def send_email(subject, body):
    # Configurar as informações de email
    sender_email = app.config.get("MAIL_USERNAME")
    sender_password = app.config.get("MAIL_PASSWORD")
    receiver_email = "flavio.moura@itec.ufpa.br"

    # Criar o objeto de mensagem
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Adicionar o corpo da mensagem
    message.attach(MIMEText(body, "plain"))

    # Enviar o email usando SMTP
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()

# delete se estiver utilizando windows
load_dotenv()

# conexão com a base
mongo = MongoClient(os.environ["MONGO_URI"]).uxtracking
fs = gridfs.GridFS(mongo)

# facial expression model
model = load_fer()

app, mail, mail_username = create_app()
model = load_fer()
# autenticação google
oauth = OAuth(app)

if __name__ == "__main__":
    try:
        mongo.command('ping')
        print("Conexão com o MongoDB foi bem-sucedida.")
    except Exception as e:
        print(f"Falha ao conectar ao MongoDB: {e}")
    
    # verifica se não há nenhum usuário no banco, então cria um usuário exemplo
    if mongo.users.count_documents({}) == 0:
        gen_example(mongo)

    # load blueprints
    from webpage.blueprints import webpage_bps
    from external.blueprints import external_bps
    for bp in webpage_bps:
        app.register_blueprint(bp, url_prefix="/")

    for bp in external_bps:
        app.register_blueprint(bp, url_prefix="/external")
    try:
        app.run(debug=False, host="0.0.0.0")
    except BaseException as e:
        dt = datetime.datetime.today()
        dt = f"{dt.day}/{dt.month}/{dt.year}"
        error_context = sys.exc_info()[1].__context__.strerror
        error_context = unidecode(error_context)
        error_msg = f"The application failed to start in {dt}.\r The message of error is: {sys.exc_info()[0]}:{e} - {error_context}"
        send_email("UX-Tracking Initialization Failed.", error_msg)
