from werkzeug.security import generate_password_hash

def gen_example(mongo):
    # Não há usuários, então crie um novo teste
    new_user = {
        "username": "admin",
        "email": "uxtracking.service@gmail.com",
        "role": "admin",
        "password": generate_password_hash("ux12tracking")
    }
    mongo.users.insert_one(new_user)
    userfound = mongo.users.find_one({"username": "admin"})
    user_collection_name=f"data_{userfound['_id']}"
    mongo[user_collection_name].insert_one(data_admin)

data_admin = {
    "datetime": {"$date": "2024-02-01T14:50:24Z"},
    "sites": ["site1", "site2"],
    "data": [
        {
            "site": "site1",
            "images": [{"$ref": "fs.files", "$id": "id1_gridfs"}],
            "interactions": [
                {
                    "type": "eye",
                    "time": 1,
                    "image": "id1_gridfs",
                    "class": "classe1",
                    "id": "id1",
                    "mouseClass": "classe1",
                    "mouseID": "id1",
                    "x": 10,
                    "y": 10,
                    "scroll": 10,
                    "height": 1000,
                    "value": "None"
                },
                {
                    "type": "mouse",
                    "time": 2,
                    "image": "id1_gridfs",
                    "class": "classe2",
                    "id": "id2",
                    "mouseClass": "classe2",
                    "mouseID": "id2",
                    "x": 20,
                    "y": 20,
                    "scroll": 20,
                    "height": 1000,
                    "value": "None"
                },
                {
                    "type": "keyboard",
                    "time": 3,
                    "image": "id1_gridfs",
                    "class": "classe3",
                    "id": "id3",
                    "mouseClass": "classe3",
                    "mouseID": "id3",
                    "x": 30,
                    "y": 30,
                    "scroll": 30,
                    "height": 1000,
                    "value": {
                        "key": "keys"
                    }
                },
                {
                    "type": "freeze",
                    "time": 4,
                    "image": "id1_gridfs",
                    "class": "classe4",
                    "id": "id4",
                    "mouseClass": "classe4",
                    "mouseID": "id4",
                    "x": 40,
                    "y": 40,
                    "scroll": 40,
                    "height": 1000,
                    "value": "None"
                }
            ]
        },
        {
            "site": "site2",
            "images": [{"$ref": "fs.files", "$id": "id2_gridfs"}, {"$ref": "fs.files", "$id": "id3_gridfs"}],
            "interactions": [
                {
                    "type": "click",
                    "time": 5,
                    "image": "id2_gridfs",
                    "class": "classe5",
                    "id": "id5",
                    "mouseClass": "classe5",
                    "mouseID": "id5",
                    "x": 50,
                    "y": 50,
                    "scroll": 50,
                    "height": 1200,
                    "value": "None"
                },
                {
                    "type": "wheel",
                    "time": 6,
                    "image": "id2_gridfs",
                    "class": "classe6",
                    "id": "id6",
                    "mouseClass": "classe6",
                    "mouseID": "id6",
                    "x": 60,
                    "y": 60,
                    "scroll": 60,
                    "height": 1200,
                    "value": "None"
                },
                {
                    "type": "move",
                    "time": 7,
                    "image": "id2_gridfs",
                    "class": "classe7",
                    "id": "id7",
                    "mouseClass": "classe7",
                    "mouseID": "id7",
                    "x": 70,
                    "y": 70,
                    "scroll": 70,
                    "height": 1200,
                    "value": "None"
                },
                {
                    "type": "voice",
                    "time": 8,
                    "image": "id2_gridfs",
                    "class": "classe8",
                    "id": "id8",
                    "mouseClass": "classe8",
                    "mouseID": "id8",
                    "x": 80,
                    "y": 80,
                    "scroll": 80,
                    "height": 1200,
                    "value": {
                        "text": "string"
                    }
                },
                {
                    "type": "face",
                    "time": 9,
                    "image": "id3_gridfs",
                    "class": "classe9",
                    "id": "id9",
                    "mouseClass": "classe9",
                    "mouseID": "id9",
                    "x": 90,
                    "y": 90,
                    "scroll": 90,
                    "height": 1200,
                    "value": {
                        "anger": 0.1,
                        "contempt": 0.1,
                        "disgust": 0.1,
                        "fear": 0.2,
                        "happy": 0.2,
                        "neutral": 0.1,
                        "sad": 0.1,
                        "surprise": 0.1
                    }
                }
            ]
        }
    ]
}
