from binance import AsyncClient, BinanceSocketManager
from binance.client import Client
import asyncio
import pandas as pd
import os
import json
import talib
import logging
import numpy as np
import aiohttp
# library to .env file
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")
CHAT_ID = os.getenv("CHAT_ID")
# Configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
client = Client("","")

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
async def telegram_bot_sendtext(bot_message):
    bot_token = TELEGRAM_KEY
    bot_chatID = CHAT_ID
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    async with aiohttp.ClientSession() as session:
        async with session.get(send_text) as resp:
            print(resp.status)
            print(await resp.text())


def update_state_file(file_name, state, state_value):
    state_file_path = f'./state/{file_name}_state.json'

    try:
        # Read the existing state file
        with open(state_file_path, 'r') as state_file:
            data = json.load(state_file)
            
        # Update or add the new state
        data[state] = state_value

        # Write the updated content back to the file
        with open(state_file_path, 'w') as state_file:
            json.dump(data, state_file, indent=2, cls=NpEncoder)

        print(f'State "{state}" updated successfully in {file_name}_state.json.')

    except FileNotFoundError:
        # Handle the case where the file doesn't exist
        print(f'Error: File {file_name}_state.json not found.')

    except json.JSONDecodeError:
        # Handle the case where the file is not a valid JSON
        print(f'Error: {file_name}_state.json is not a valid JSON file.')

        
def initialize_state_files(file_names):
    # create state directory if it doesn't exist
    if not os.path.exists('./state'):
        os.makedirs('./state')
    # create state file if it doesn't exist
    for file_name in file_names:
        state_file_path = f'./state/{file_name}_state.json'
        if not os.path.exists(state_file_path):
            with open(state_file_path, 'w') as state_file:
                json.dump({"rsi": "n"}, state_file)

def read_state_file(file_name) -> dict:
    state_file_path = f'./state/{file_name}_state.json'
    with open(state_file_path, 'r') as state_file:
        state = json.load(state_file)
        return state
    
def calculate_rsi_states(parity):
    # add lower and upper bounds to the state file
    bounds = parity['lower_rsi_bounds'] + parity['upper_rsi_bounds']
    bounds_keys = parity["rsi_states"]
    bounds = sorted(bounds, reverse=True)
    print("sorted bounds", bounds)
    # create dict corresponding to the bounds with rsi_states
    rsi_states = {}
    bound_index = 0
    for bound in bounds:
        if bound_index == 0:
            rsi_states.update({bounds_keys[bound_index]: bound})
        elif bound_index == len(bounds):
            print("last bound", bound)
            rsi_states.update({bounds_keys[bound_index]: bound})
        else:
            rsi_states.update({bounds_keys[bound_index]: [bound, bounds[bound_index]]})
        bound_index += 1
    return rsi_states

def calculate_rsi_state(rsi, rsi_states) -> str:
    state_count = 0
    for state in rsi_states:
        if type(rsi_states[state]) == list:
            if rsi > rsi_states[state][0] and rsi < rsi_states[state][1]:
                return state
        elif state_count == 0:
            if rsi > rsi_states[state]:
                return state
        else:
            if rsi < rsi_states[state]:
                return state
        state_count += 1

def initialize_parities() -> list:
    parities_path = './parities'
    # Get the list of files in the directory
    files = os.listdir(parities_path)

    # Filter only JSON files
    parities = []
    file_names = []
    json_files = [file for file in files if file.endswith('.json')]

    # Import and process each JSON file
    for json_file in json_files:
        file_path = os.path.join(parities_path, json_file)
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

async def main(df, parity, task_id, file_name, state, rsi_states, is_open_time_updated):
    # check if open_time attribute exists
    if hasattr(state, 'open_time'):
        is_open_time_updated = True
        pass
    else:
        # add open_time to state dict
        state.update({"open_time": df.iloc[-1]['open_time']})
        # write to state file
        update_state_file(file_name, 'open_time', df.iloc[-1]['open_time'])
        is_open_time_updated = True

    SYMBOL = parity['symbol']
    INTERVAL = parity['interval']
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socketa
    ts = bm.kline_socket(SYMBOL, interval=INTERVAL)
    # then start receiving messages
    async with ts as tscm:
        msg_counter = 0
        while True:
            msg_counter += 1
            res = await tscm.recv()
            # logging.info("msg recieved: {}".format(msg_counter))
            if res['k']['x']:
                # candle is closed, concat new candle to df
                new_candle_data = [res['k']['t'], res['k']['o'], res['k']['h'], res['k']['l'], res['k']['c'], res['k']['v'], res['k']['T'], res['k']['q'], res['k']['n'], res['k']['V'], res['k']['Q'], res['k']['B']]
                new_candle = pd.DataFrame([new_candle_data], columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
                
                # Ensure the columns are in the same order and correct data types
                new_candle = new_candle.astype(df.dtypes)

                df = pd.concat([df, new_candle], ignore_index=True)
                # remove first candle
                df = df.iloc[1:]
                # calculate RSI using talib
            else:
                # candle is open, update last candle
                df.loc[df.index[-1]] = [res['k']['t'], res['k']['o'], res['k']['h'], res['k']['l'], res['k']['c'], res['k']['v'], res['k']['T'], res['k']['q'], res['k']['n'], res['k']['V'], res['k']['Q'], res['k']['B']]
            if  parity['rsi'] == True:
                rsi = talib.RSI(df['close'], timeperiod=14)
                # logging.info(f"rsi -> {rsi.iloc[-1]}, symbol -> {parity['symbol']}")
                # check if the state is the same as the current state
                rsi_state = calculate_rsi_state(rsi.iloc[-1], rsi_states)
                if state['rsi'] != rsi_state:
                    # check if the open_time has been updated
                    if state["open_time"] != df.iloc[-1]['open_time']:
                        # update the open_time
                        state["open_time"] = df.iloc[-1]['open_time']
                        # update the state file
                        update_state_file(file_name, 'rsi', rsi_state)
                        # update the state
                        state["rsi"] = rsi_state
                        # send telegram message including symbol interval and rsi
                        await telegram_bot_sendtext(f"rsi -> {rsi.iloc[-1]}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, state -> {rsi_state}")
                        print("state is changed")
                print(f"rsi -> {rsi.iloc[-1]}, symbol -> {parity['symbol']}, state -> {rsi_state}", "rsi_states -> ", rsi_states)


async def run_parities():

    # create tasks for each parity
    parities, file_names = initialize_parities()
    initialize_state_files(file_names)
    tasks = []
    task_id = 0
    for parity in parities:
        if parity['is_parity_active'] == True:
            is_open_time_updated = False
            rsi_states = calculate_rsi_states(parity)
            state = read_state_file(file_names[task_id])
            df = get_candles(parity['symbol'], parity['interval'], parity['start'])
            tasks.append(main(df, parity, task_id, file_names[task_id], state,rsi_states, is_open_time_updated))        
        task_id += 1
    # Run tasks concurrently
    await asyncio.gather(*tasks)
    
if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run_parities())
    parity= {
        "is_parity_active": True,
        "symbol": "BTCUSDT",
        "interval": "1m",
        "start": "60 minutes ago UTC",
        "rsi": False,
        "lower_rsi_bounds": [30,35,40],
        "upper_rsi_bounds": [45,50],
        "rsi_states": ["h2","h1","n","l1","l2","l3"]
    }
    value = 1
    rsi_states = calculate_rsi_states(parity)
    rsi_state = calculate_rsi_state(1, rsi_states)
    print(rsi_states, rsi_state , value)

