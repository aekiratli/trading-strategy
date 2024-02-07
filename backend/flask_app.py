from flask import Flask, request, jsonify
import json
import requests
from dotenv import load_dotenv
import os
from urllib.parse import urljoin
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from datetime import timedelta
from flask_cors import CORS

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)

# Access environment variables
app.config['PYTHONANYWHERE_USERNAME'] = os.getenv('PYTHONANYWHERE_USERNAME')
app.config['PYTHONANYWHERE_TOKEN'] = os.getenv('PYTHONANYWHERE_TOKEN')
app.config['WORKDIR'] = os.getenv('WORKDIR')
app.config['JWT_SECRET_KEY'] =  os.getenv('JWT_SECRET_KEY')
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD')
app.config['LOG_PATH'] = os.getenv('LOG_PATH')


# NON GLOBAL
pythonanywhere_host = "eu.pythonanywhere.com"

api_base = "https://{pythonanywhere_host}/api/v0/user/{username}/".format(
    pythonanywhere_host=pythonanywhere_host,
    username=app.config['PYTHONANYWHERE_USERNAME'],
)

# Login route to get a JWT token
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'admin' or password != app.config['ADMIN_PASSWORD']:
        return jsonify({"msg": "Bad username or password"}), 401
    expires = timedelta(hours=24)
    access_token = create_access_token(identity=username,expires_delta=expires)
    return jsonify(access_token=access_token), 200

@app.route('/list_parities')
@jwt_required()
def list_parities():
    resp = requests.get(
        urljoin(api_base, "files/path/home/{username}/{path}".format(username=app.config['PYTHONANYWHERE_USERNAME'], path=app.config['WORKDIR'])),
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])})

    parities = []
    for parity in resp.json():
        resp = requests.get(
            urljoin(api_base, "files/path/home/{username}/{path}/{file}".format(username=app.config['PYTHONANYWHERE_USERNAME'], path=app.config["WORKDIR"],file=parity)),
            headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
        )
        parities.append(resp.json())
    return jsonify(parities), 200

@app.route('/update_parity/<string:parity>', methods=['POST'])
@jwt_required()
def create_or_update_parity(parity):
    if not parity.endswith('.json'):
        return jsonify({"msg": "Bad parity format"}), 400
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    #lowercase  parity
    parity = parity.lower()
    data = request.get_json()
    resp = requests.post(
        urljoin(api_base, "files/path/home/{username}/{path}/{file}".format(username=app.config['PYTHONANYWHERE_USERNAME'], path=app.config["WORKDIR"], file=parity)),
        files={"content": json.dumps(data, indent=4)},
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
    )
    if resp.status_code == 201:
        return jsonify({"msg": "Parity updated/created"}), 201
    else:
        return jsonify({"msg": "Something went wrong"}), 500

@app.route('/delete_parity/<string:parity>', methods=['POST'])
@jwt_required()
def delete_parity(parity):
    if not parity.endswith('.json'):
        return jsonify({"msg": "Bad parity format"}), 400
    parity = parity.lower()
    resp = requests.delete(
        urljoin(api_base, "files/path/home/{username}/{path}/{file}".format(username=app.config['PYTHONANYWHERE_USERNAME'],path=app.config["WORKDIR"], file=parity)),
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
    )
    if resp.status_code == 204:
        return jsonify({"msg": "Parity deleted"}), 200
    else:
        return jsonify({"msg": "Something went wrong"}), 500

@app.route('/restart')
@jwt_required()
def restart():
    # list all always on tasks restart them
    resp = requests.get(
        urljoin(api_base, "always_on"),
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])})
    for job in resp.json():
        id = job['id']
        resp = requests.post(
            urljoin(api_base, "always_on/{id}/restart/".format(id=id)),
            headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
        )
    return jsonify({"msg": "Restarted"}), 200

@app.route('/logs/<parity>')
@jwt_required()
def logs(parity):
    parity = parity + '.json'
    resp = requests.get(
            urljoin(api_base, "files/path/home/{username}/{path}/{file}".format(username=app.config['PYTHONANYWHERE_USERNAME'], path=app.config["LOG_PATH"],file=parity)),
            headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
        )
    msg = resp.json()
    # check if msg has details attr
    if 'detail' in msg:
        return jsonify({"msg": "file missing"}), 400
    elif msg == {}:
        return jsonify({"msg": "file empty"}), 400
    else:
        return jsonify(resp.json()), 200

# if __name__ == '__main__':
#     app.run(debug=True, port=5005)