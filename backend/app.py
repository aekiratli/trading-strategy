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
    # resp = requests.get(
    #     urljoin(api_base, "files/path/home/{username}/{path}".format(username=app.config['PYTHONANYWHERE_USERNAME'], path=app.config['WORKDIR'])),
    #     headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])})

    # parities = []
    # for parity in resp.json():
    #     resp = requests.get(
    #         urljoin(api_base, "files/path/home/{username}/{path}/{file}".format(username=app.config['PYTHONANYWHERE_USERNAME'], path=app.config["WORKDIR"],file=parity)),
    #         headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
    #     )
    #     parities.append(resp.json())
    # return parities

    demo = [{
        "symbol": "BNBUSDT",
        "atr_length": 10,
        "atr_multiplier": 3,
        "bbands": True,
        "interval": "15m",
        "is_parity_active": True,
        "lower_rsi_bounds": [
            30,
            20
        ],
        "ma_length": 9,
        "moving_average": "sma",
        "pmax": True,
        "pmax_candle_reset": 4,
        "pmax_percantage": 1.003,
        "pmax_states": [
            "l",
            "p",
            "n"
        ],
        "rsi": True,
        "rsi_states": [
            "h1",
            "n",
            "l1",
            "l2"
        ],
        "start": "40 hours ago UTC",
        
        "upper_rsi_bounds": [
            80
        ]
    },
    {
        "atr_length": 10,
                "symbol": "ARBUSDT",
        "atr_multiplier": 3,
        "bbands": True,
        "interval": "15m",
        "is_parity_active": True,
        "lower_rsi_bounds": [
            30,
            20
        ],
        "ma_length": 9,
        "moving_average": "sma",
        "pmax": True,
        "pmax_candle_reset": 4,
        "pmax_percantage": 1.003,
        "pmax_states": [
            "l",
            "p",
            "n"
        ],
        "rsi": True,
        "rsi_states": [
            "h1",
            "n",
            "l1",
            "l2"
        ],
        "start": "40 hours ago UTC",
        "upper_rsi_bounds": [
            80
        ]
    }]
    return demo

@app.route('/update_parity/<string:parity>', methods=['POST'])
@jwt_required()
def create_or_update_parity(parity):
    if not parity.endswith('.json'):
        return jsonify({"msg": "Bad parity format"}), 400
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data = request.get_json()
    print(data)
    resp = requests.post(
        urljoin(api_base, "files/path/home/{username}/{file}".format(username=app.config['PYTHONANYWHERE_USERNAME'], file=parity)),
        files={"content": json.dumps(data, indent=4)},
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
    )
    return jsonify({"msg": "Parity updated"}), 200

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
    app.run(debug=True, port=5005)