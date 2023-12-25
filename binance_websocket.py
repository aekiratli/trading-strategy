from binance import AsyncClient, BinanceSocketManager
from binance.client import Client
import asyncio
import pandas as pd
import os
import json
import talib
import logging

# Configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
client = Client("","")

# Function to update the state file
def update_state_file(file_name, state, state_value):
    state_file_path = f'./state/{file_name}_state.json'
    with open(state_file_path, 'r+') as state_file:
        current_state = (json.load(state_file)[state]),
        # check if the state value is different from the current state
        current_state = current_state[0] #this is a tuple
        if current_state != state_value:
            # going to implement a msg sender here
            pass
        # clear the file
        state_file.seek(0)
        state_file.truncate()
        json.dump({state: state_value}, state_file)
        
def initialize_state_files(file_names):
    # create state directory if it doesn't exist
    if not os.path.exists('./state'):
        os.makedirs('./state')
    # create state file if it doesn't exist
    for file_name in file_names:
        state_file_path = f'./state/{file_name}_state.json'
        if not os.path.exists(state_file_path):
            with open(state_file_path, 'w') as state_file:
                json.dump({"rsi": 0}, state_file)

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

async def main(df, parity, task_id, file_name):
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
            logging.info("msg recieved: {}".format(msg_counter))
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
                logging.info(f"rsi -> {rsi.iloc[-1]}, symbol -> {parity['symbol']}")
                # Check RSI conditions and update state accordingly
                for rsi_value in parity["lower_rsi_bounds"]:
                    if rsi.iloc[-1] < rsi_value:
                        update_state_file(file_name, "rsi", rsi_value)
                for rsi_value in parity["upper_rsi_bounds"]:
                    if rsi.iloc[-1] > rsi_value:
                        update_state_file(file_name, "rsi", rsi_value)

async def run_parities():

    # create tasks for each parity
    parities, file_names = initialize_parities()
    initialize_state_files(file_names)
    tasks = []
    task_id = 0
    for parity in parities:
        if parity['is_parity_active'] == True:
            df = get_candles(parity['symbol'], parity['interval'], parity['start'])
            tasks.append(main(df, parity, task_id, file_names[task_id]))        
        task_id += 1
    # Run tasks concurrently
    await asyncio.gather(*tasks)
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_parities())
