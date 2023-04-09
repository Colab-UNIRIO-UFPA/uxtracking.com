import hashlib
import json
import re

def generate_user_id(name, email):
    string_to_hash = f"{name}{email}"
    hashed_string = hashlib.md5(string_to_hash.encode())
    return hashed_string.hexdigest()

def auth(name, email):
    with open("users.json", "r") as arquivo:
        users = json.load(arquivo)
    if any(user["name"] == name for user in users):
        return [True, "Usuário já existe."]
    if any(user["email"] == email for user in users):
        return [True, "Email já cadastrado."]
    return [False, None]

def clean(string):
    string = string.replace(' ', '-') # Substitui todos os espaços por hífens.
    return re.sub('[^A-Za-z0-9\-]+', '', string) # Remove caracteres especiais.