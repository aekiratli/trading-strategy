from flask import Flask, request, jsonify
import json
import requests
from dotenv import load_dotenv
import os
from urllib.parse import urljoin
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from datetime import timedelta
from flask_cors import CORS
import numpy as np
from binance.client import Client
from datetime import datetime
import traceback
import uuid

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)

# Access environment variables
app.config['PYTHONANYWHERE_USERNAME'] = os.getenv('PYTHONANYWHERE_USERNAME')
app.config['PYTHONANYWHERE_TOKEN'] = os.getenv('PYTHONANYWHERE_TOKEN')
app.config['WORKDIR'] = os.getenv('WORKDIR')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD')
app.config['LOG_PATH'] = os.getenv('LOG_PATH')
app.config['ORDER_PATH'] = os.getenv('ORDER_PATH')
app.config['STATE_PATH'] = os.getenv('STATE_PATH')
app.config['UPDATE_PATH'] = os.getenv('UPDATE_PATH')
app.config['TELEGRAM_KEY'] = os.getenv('TELEGRAM_KEY')
app.config['CHAT_ID'] = os.getenv('CHAT_ID')

# NON GLOBAL
pythonanywhere_host = "eu.pythonanywhere.com"
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

api_base = "https://{pythonanywhere_host}/api/v0/user/{username}/".format(
    pythonanywhere_host=pythonanywhere_host,
    username=app.config['PYTHONANYWHERE_USERNAME'],
)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'admin' or password != app.config['ADMIN_PASSWORD']:
        return jsonify({"msg": "Bad username or password"}), 401
    expires = timedelta(hours=24)
    access_token = create_access_token(
        identity=username, expires_delta=expires)
    return jsonify(access_token=access_token), 200


@app.route('/list_parities')
@jwt_required()
def list_parities():
    parities = {}
    return jsonify(parities), 200


@app.route('/update_parity/<string:parity>', methods=['POST'])
@jwt_required()
def create_or_update_parity(parity):
    if not parity.endswith('.json'):
        return jsonify({"msg": "Bad parity format"}), 400
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    # lowercase  parity
    parity = parity.lower()
    data = request.get_json()
    resp = requests.post(
        urljoin(api_base, "files/path/home/{username}/{path}/{file}".format(
            username=app.config['PYTHONANYWHERE_USERNAME'], path=app.config["WORKDIR"], file=parity)),
        files={"content": json.dumps(data, indent=4)},
        headers={"Authorization": "Token {api_token}".format(
            api_token=app.config['PYTHONANYWHERE_TOKEN'])}
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
        urljoin(api_base, "files/path/home/{username}/{path}/{file}".format(
            username=app.config['PYTHONANYWHERE_USERNAME'], path=app.config["WORKDIR"], file=parity)),
        headers={"Authorization": "Token {api_token}".format(
            api_token=app.config['PYTHONANYWHERE_TOKEN'])}
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
            headers={"Authorization": "Token {api_token}".format(
                api_token=app.config['PYTHONANYWHERE_TOKEN'])}
        )
    return jsonify({"msg": "Restarted"}), 200


@app.route('/logs/<parity>')
@jwt_required()
def logs(parity):
    parity = parity + '.json'
    resp = requests.get(
        urljoin(api_base, "files/path/home/{username}/{path}/{file}".format(
            username=app.config['PYTHONANYWHERE_USERNAME'], path=app.config["LOG_PATH"], file=parity)),
        headers={"Authorization": "Token {api_token}".format(
            api_token=app.config['PYTHONANYWHERE_TOKEN'])}
    )
    msg = resp.json()
    # check if msg has details attr
    if 'detail' in msg:
        return jsonify({"msg": "file missing"}), 400
    elif msg == {}:
        return jsonify({"msg": "file empty"}), 400
    else:
        return jsonify(resp.json()), 200


@app.route('/orders/<string:status>')
@jwt_required()
def open_orders(status):
    # make sure status is open, cancelled or completed
    if status not in ['open', 'cancelled', 'completed']:
        return jsonify({"msg": "Bad status"}), 400
    # load the file
    path = f'{app.config["ORDER_PATH"]}/{status}.json'
    with open(path, 'r') as file:
        data = json.load(file)
    if not data:
        return jsonify({"msg": "No orders found"}), 404
    return jsonify(data), 200
    
@app.route('/orders/<string:id>/cancel')
@jwt_required()
def cancel_order(id):
    def update_state_file(file_name, state, state_value):
        state_file_path = f'{app.config["STATE_PATH"]}/{file_name}_state.json'

        try:
            # Read the existing state file
            with open(state_file_path, 'r') as state_file:
                data = json.load(state_file)
                
            # Update or add the new state
            data[state] = state_value

            # Write the updated content back to the file
            with open(state_file_path, 'w') as state_file:
                json.dump(data, state_file, indent=2, cls=NpEncoder)


        except FileNotFoundError:
            # Handle the case where the file doesn't exist
            print(f'Error: File {file_name}_state.json not found.')

        except json.JSONDecodeError:
            # Handle the case where the file is not a valid JSON
            print(f'Error: {file_name}_state.json is not a valid JSON file.')
    def update_update_file(file_name, should_update):
        update_file_path = f'{app.config["UPDATE_PATH"]}/{file_name}_update.json'
        with open(update_file_path, 'w') as update_file:
            json.dump({'should_update':should_update, 'is_intervened': True }, update_file, indent=2)
    open_path = f'{app.config["ORDER_PATH"]}/open.json'
    cancelled_path = f'{app.config["ORDER_PATH"]}/cancelled.json'

    with open(open_path, 'r') as file:
        existing_data = json.load(file)
    if not existing_data:
        return jsonify({"msg": "No orders found"}), 404
    order_found = False
    for order in existing_data:
        if order['id'] == id:
            client.cancel_order(
                symbol=order['symbol'],
                orderId=order['orderId'],
            )
            current_year = datetime.now().strftime('%Y')
            current_month = datetime.now().strftime('%m')
            current_date = datetime.now().strftime('%d')

            # create year, month, date and id directories if they don't exist
            year_path = f'{app.config["ORDER_PATH"]}/{current_year}'
            month_path = f'{year_path}/{current_month}'
            date_path = f'{month_path}/{current_date}'
            id_path = f'{date_path}/{id}'

            for dir_path in [year_path, month_path, date_path, id_path]:
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)

            # create the log file
            log_file = f'{id_path}/cancelled.json'
            with open(log_file, 'w') as file:
                json.dump({"cancelled": True}, file, indent=2)

            order_found = True
            with open(cancelled_path, 'r') as file:
                cancelled_data = json.load(file)
            with open(cancelled_path, 'w') as file:
                cancelled_data.append(order)
                json.dump(cancelled_data, file, indent=2)
            # active_trades.json
            with open(f'{app.config["STATE_PATH"]}/active_trades.json', 'r') as file:
                active_trades = json.load(file)
                active_trades.remove(f'{order["symbol"]}{order["interval"]}_{order["strategy"]}')
            with open(f'{app.config["STATE_PATH"]}/active_trades.json', 'w') as file:
                json.dump(active_trades, file, indent=2)

            file_name = order['symbol'] + order['interval']
            # lowercasing
            file_name = file_name.lower()
            update_update_file(file_name, True)
            if order["strategy"] == "pmax_bbands":
                update_state_file(file_name, 'pmax_bbands_bought', False)
                update_state_file(file_name, 'pmax_bbands_has_ordered', False)
            if order["strategy"] == "rsi_trading":
                update_state_file(file_name, 'rsi_trading_bought', False)
            if order["strategy"] == "rsi_trading_alt":
                update_state_file(file_name, 'rsi_trading_alt_bought', False)
            if order["strategy"] == "rsi_bbands":
                update_state_file(file_name, 'rsi_bbands_alt_bought', False)
                update_state_file(file_name, 'rsi_bbands_alt_has_ordered', False)
            if order["strategy"] == "rsi_bbands_alt":
                update_state_file(file_name, 'rsi_bbands_alt_bought', False)
                update_state_file(file_name, 'rsi_bbands_alt_has_ordered', False)
            with open(open_path, 'w') as file:
                json.dump([order for order in existing_data if order['id'] != id], file, indent=2)
        if order_found:
            # send telegram message
            requests.get(f'https://api.telegram.org/bot{app.config["TELEGRAM_KEY"]}/sendMessage?chat_id={app.config["CHAT_ID"]}&text=Order+ID%3A+{id}+cancelled')
            return jsonify({"msg": "Order cancelled"}), 200
        
    return jsonify({"msg": "Order not found"}), 404
        
@app.route('/assets')
@jwt_required()
def get_info():
    try:
        info = client.get_user_asset()        
        return jsonify(info), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    
@app.route('/cancel_is_intervened/<string:symbol>')
@jwt_required()
def cancel_is_intervened(symbol):
    file_name = symbol.lower()
    update_file_path = f'{app.config["UPDATE_PATH"]}/{file_name}_update.json'
    with open(update_file_path, 'w') as update_file:
        json.dump({'should_update': True, 'is_intervened': False }, update_file, indent=2)
    return jsonify({"msg": "Is intervened cancelled"}), 200

@app.route('/list_intervened')
@jwt_required()
def list_intervened():
    files = os.listdir(app.config["UPDATE_PATH"])
    intervened_dict = {}
    for file in files:
        if file.endswith('_update.json'):
            symbol = file.replace('_update.json', '')
            with open(f'{app.config["UPDATE_PATH"]}/{file}', 'r') as update_file:
                data = json.load(update_file)
                intervened_dict[symbol] = data.get('is_intervened', False)
    return jsonify(intervened_dict), 200

@app.route('/trades/<string:symbol>')
@jwt_required()
def trades(symbol):
    try:
        info = client.get_all_orders(symbol=symbol)       
        return jsonify(info), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    
@app.route('/binance_open_orders')
@jwt_required()
def binance_open_orders():
    try:
        orders = client.get_open_orders()
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/trades/<string:symbol>/<string:order_id>')
@jwt_required()
def order_details(symbol, order_id):
    try:
        orders = client.get_my_trades(symbol=symbol, orderId=order_id)
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    
@app.route('/price/<string:symbol>')
@jwt_required()
def price(symbol):
    try:
        price = client.get_symbol_ticker(symbol=symbol)
        return jsonify(price), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/create_order', methods=['POST'])
@jwt_required()
def create_order():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data = request.get_json()
    # get ticker size
    symbol_info = client.get_symbol_info(data['symbol'])
    filters = symbol_info['filters']
    bc = 0
    for filter in filters:
        if filter['filterType'] == 'LOT_SIZE':
            step_size = float(filter['stepSize'])
            bc += 1
        if [filter['filterType'] == 'PRICE_FILTER']:
            tick_size = float(filter['tickSize'])
            bc += 1
        if bc == 2:
                break
    try:
        order_data = {
            'symbol': data['symbol'],
            'side': data['side'],
            'type': data['type'],
        }

        if data['type'].upper() == 'LIMIT':
            order_data['timeInForce'] = "GTC"
            price = float(data['price'])
            price = round(price / tick_size) * tick_size
            order_data['price'] = price
            
        amount = float(data['amount'])
        amount = round(amount / step_size) * step_size
        order_data['quantity'] = amount

        order = client.create_order(**order_data)
        orderId = order['orderId']
        uuidv4 = str(uuid.uuid4())
        data = {
            "timestamp": order['transactTime'],
            "id": uuidv4,
            "symbol": data['symbol'],
            "interval": "",
            "action": data['side'],
            "market_type": data['type'],
            "amount": data['amount'],
            "price": data['price'],
            "orderId": orderId,
            "strategy": ""
        }
        current_year = datetime.now().strftime('%Y')
        current_month = datetime.now().strftime('%m')
        current_date = datetime.now().strftime('%d')

        # create year, month, date and id directories if they don't exist
        year_path = f'{app.config["ORDER_PATH"]}/{current_year}'
        month_path = f'{year_path}/{current_month}'
        date_path = f'{month_path}/{current_date}'
        id_path = f'{date_path}/{uuidv4}'

        for dir_path in [year_path, month_path, date_path, id_path]:
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

        # create the log file
        log_file = f'{id_path}/open.json'
        with open(log_file, 'w') as file:
            json.dump(data, file, indent=2)

        with open(f'{app.config["ORDER_PATH"]}/open.json', 'r') as file:
            existing_data = json.load(file)
        with open(f'{app.config["ORDER_PATH"]}/open.json', 'w') as file:
            existing_data.append(data)
            json.dump(existing_data, file, indent=2)
            
        requests.get(f'https://api.telegram.org/bot{app.config["TELEGRAM_KEY"]}/sendMessage?chat_id={app.config["CHAT_ID"]}&text=Order+ID%3A+{id}+created')
        return jsonify(order), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"msg": str(e)}), 500    

    
if __name__ == '__main__':
    app.run(debug=True, port=5005)
