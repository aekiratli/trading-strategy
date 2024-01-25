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
jwt = JWTManager(app)
CORS(app)

# Access environment variables
app.config['PYTHONANYWHERE_USERNAME'] = os.getenv('PYTHONANYWHERE_USERNAME')
app.config['PYTHONANYWHERE_TOKEN'] = os.getenv('PYTHONANYWHERE_TOKEN')
app.config['WORKDIR'] = os.getenv('WORKDIR')
app.config['JWT_SECRET_KEY'] =  os.getenv('JWT_SECRET_KEY')
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD')

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
    return resp.json()

@app.route('/update_parity/<string:parity>')
@jwt_required()
def create_or_update_parity(parity):
    if not parity.endswith('.json'):
        return jsonify({"msg": "Bad parity format"}), 400
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data = request.get_json()
    resp = requests.post(
        urljoin(api_base, "files/path/home/{username}/{file}".format(username=app.config['PYTHONANYWHERE_USERNAME'], file=parity)),
        files={"content": json.dumps(data, indent=4)},
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
    )
    return resp.text

@app.route('/delete_parity/<string:parity>')
@jwt_required()
def delete_parity(parity):
    if not parity.endswith('.json'):
        return jsonify({"msg": "Bad parity format"}), 400

    resp = requests.delete(
        urljoin(api_base, "files/path/home/{username}/{file}".format(username=app.config['PYTHONANYWHERE_USERNAME'], file=parity)),
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
    )
    return resp.text

@app.route('/list_always_on_tasks')
@jwt_required()
def list_always_on_tasks():
    resp = requests.get(
        urljoin(api_base, "always_on"),
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])})
    return resp.json()

@app.route('/restart_always_on_task/<int:id>')
@jwt_required()
def restart_always_on_task(id):
    resp = requests.post(
        urljoin(api_base, "always_on/{id}/restart/".format(id=id)),
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
)
    return resp.json()

if __name__ == '__main__':
    app.run(debug=True)