from binance import AsyncClient, BinanceSocketManager
from binance.client import Client
import asyncio
import pandas as pd
import os
import json
import talib

client = Client("","")

def initialize_parities() -> list:
    parities_path = './parities'
    # Get the list of files in the directory
    files = os.listdir(parities_path)

    # Filter only JSON files
    parities = []
    json_files = [file for file in files if file.endswith('.json')]

    # Import and process each JSON file
    for json_file in json_files:
        file_path = os.path.join(parities_path, json_file)

        with open(file_path, 'r') as file:
            data = json.load(file)
            parities.append(data)
    return parities

def get_candles(symbol, interval, start) -> pd.DataFrame:
    klines = client.get_historical_klines(symbol=symbol, interval=interval, start_str=start)
    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    return df

async def main(df, parity, task_id):
    SYMBOL = parity['symbol']
    INTERVAL = parity['interval']
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    ts = bm.kline_socket(SYMBOL, interval=INTERVAL)
    # then start receiving messages
    async with ts as tscm:
        msg_counter = 0
        while True:
            msg_counter += 1
            res = await tscm.recv()
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
            print(df)
            rsi = talib.RSI(df['close'], timeperiod=14)
            print(f"rsi -> {rsi}, symbol -> {parity}")

async def run_parities():

    # create tasks for each parity
    parities = initialize_parities()
    tasks = []
    task_id = 0
    for parity in parities:
        df = get_candles(parity['symbol'], parity['interval'], parity['start'])
        tasks.append(main(df, parity, task_id))
        task_id += 1
        break

    # Run tasks concurrently
    await asyncio.gather(*tasks)
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_parities())
