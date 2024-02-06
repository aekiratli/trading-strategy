import os
from dotenv import load_dotenv
import json
import numpy as np
import aiohttp
from binance.client import Client
import pandas as pd

load_dotenv()
client = Client("","")

TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")
CHAT_ID = os.getenv("CHAT_ID")
TRADING_CHAT_ID = os.getenv("TRADING_CHAT_ID")
PARITIES_PATH = os.getenv("PARITIES_PATH")
STATE_PATH = os.getenv("STATE_PATH")

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

# Function to send a message to a Telegram user or group using aoidhttp
async def telegram_bot_sendtext(msg, is_trade=False):
    
    bot_token = TELEGRAM_KEY

    if not is_trade:
        bot_chatID = CHAT_ID
        return
    else:
        bot_chatID = TRADING_CHAT_ID

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + msg
    async with aiohttp.ClientSession() as session:
        async with session.get(send_text) as resp:
            pass

def update_state_file(file_name, state, state_value):
    state_file_path = f'{STATE_PATH}/{file_name}_state.json'

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

        
def initialize_state_files(file_names):
    # create state directory if it doesn't exist
    data = {"rsi": "n",
            "pmax": "n", 
            "bbands": "n", 
            "rsi_trading_bought": False,
            "rsi_trading_alt_bought": False,
            "pmax_bbands_bought": False,
            "pmax_bbands_buy_price": 0,
            "pmax_bbands_bought_amount": 0,
            "pmax_bbands_sell_price": 0,
            "pmax_bbands_has_ordered": False,
            "rsi_bbands_buy_price": 0,
            "rsi_bbands_alt_buy_price": 0,
            "rsi_bbands_has_ordered": False,
            "rsi_bbands_alt_has_ordered": False,
            "rsi_bbands_bought_amount": 0,
            "rsi_bbands_alt_bought_amount": 0,
            "rsi_bbands_sell_price": 0,
            "rsi_bbands_alt_sell_price": 0,
            "rsi_bbands_bought": False, 
            "rsi_bbands_alt_bought": False,
            "is_n_to_l_notif_sent": False, 
            "rsi_trading_buy_price": 0,
            "rsi_trading_alt_buy_price": 0,
            "rsi_trading_bought_amount": 0,
            "rsi_trading_alt_bought_amount": 0,
            "pmax_candle_counter": 0
            }

    if not os.path.exists(STATE_PATH):
        os.makedirs(STATE_PATH)
    # create state file if it doesn't exist
    for file_name in file_names:
        state_file_path = f'{STATE_PATH}/{file_name}_state.json'
        if not os.path.exists(state_file_path):
            with open(state_file_path, 'w') as state_file:
                json.dump(data, state_file, indent=2)

def read_state_file(file_name) -> dict:
    state_file_path = f'{STATE_PATH}/{file_name}_state.json'
    with open(state_file_path, 'r') as state_file:
        state = json.load(state_file)
        return state
    
def calculate_rsi_states(parity):
    bounds = parity['lower_rsi_bounds'] + parity['upper_rsi_bounds']
    bounds_keys = parity["rsi_states"]
    bounds = sorted(bounds, reverse=True)
    # print(bounds) [50, 45, 40, 35, 30]
    # print(bounds_keys) ['h2', 'h1', 'n', 'l1', 'l2']
    # create dict corresponding to the bounds with rsi_states
    # e.g -> 51 is h2, 46 is h1, 41 is n, 36 is l1, 29 is l2
    rsi_states = dict(zip(bounds_keys, bounds))
    # add the last key to the dict using array index
    rsi_states.update({bounds_keys[-1]: 0})
    return rsi_states


def calculate_rsi_state(rsi, rsi_states) -> str:
    # example rsi_states -> {'h2': 50, 'h1': 45, 'n': 40, 'l1': 35, 'l2': 30, 'l3': 0}
    # find the first key that is greater than the rsi
    # e.g -> rsi = 51, rsi_state = h2
    # e.g -> rsi = 46, rsi_state = h1
    # e.g -> rsi = 41, rsi_state = n
    # e.g -> rsi = 36, rsi_state = l1
    # e.g -> rsi = 29, rsi_state = l2
    # e.g -> rsi = 0, rsi_state = l3
    for key, value in rsi_states.items():
        if rsi >= value:
            return key


def initialize_parities() -> list:
    # Get the list of files in the directory
    files = os.listdir(PARITIES_PATH)

    # Filter only JSON files
    parities = []
    file_names = []
    json_files = [file for file in files if file.endswith('.json')]

    # Import and process each JSON file
    for json_file in json_files:
        file_path = os.path.join(PARITIES_PATH, json_file)
        # remove .json from file name
        file_names.append(json_file[:-5])

        with open(file_path, 'r') as file:
            data = json.load(file)
            parities.append(data)
    return parities, file_names


def get_candles(symbol, interval, start) -> pd.DataFrame:
    klines = client.get_historical_klines(symbol=symbol, interval=interval, start_str=start)
    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    return df

def get_amount_to_buy(quota, symbol):
    # calculate the amount to buy based on the quota using client
    # get the price of the symbol
    price = client.get_symbol_ticker(symbol=symbol)['price']
    # calculate the amount to buy
    amount_to_buy = quota / float(price)
    # use decimal  of 4
    amount_to_buy = round(amount_to_buy, 4)
    return amount_to_buy

def update_state_file_and_state(file_name, state_key ,state, state_value):
    update_state_file(file_name, state_key, state_value)
    # update key from state
    state[state_key] = state_value
    return state