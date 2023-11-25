import binance
import pandas as pd
import argparse

client = binance.Client()

parser = argparse.ArgumentParser()
parser.add_argument('--symbol')
parser.add_argument('--interval')
parser.add_argument('--start')
args = parser.parse_args()

# Check if the user has specified a symbol and interval
try:
    SYMBOL = args.symbol
    INTERVAL = args.interval
    START = args.start
    # Check if params are given
    if SYMBOL == None or INTERVAL == None or START == None:
        raise Exception
except:
    print('No symbol, interval, start specified')
    exit()


FORCE_DOWNLOAD = False

# Check if data.csv exists
# If it does, load it into a dataframe
# If it doesn't, download data from binance and save it to data.csv
try:
    df = pd.read_csv('data.csv')
    print('Loaded data.csv')

except:
    print('Could not load data.csv')
    FORCE_DOWNLOAD = True

# Check if .data_settings exists
# If it does, check if the symbol and interval match
# If it doesn't, download data from binance and save it to data.csv
try:
    with open('.data_settings', 'r') as f:
        data_settings = f.read().split(',')
        if data_settings[0] != SYMBOL or data_settings[1] != INTERVAL or data_settings[2] != START:
            print('Symbol or interval mismatch, downloading data from binance')
            FORCE_DOWNLOAD = True
except:
    FORCE_DOWNLOAD = True
    print('Could not load .data_settings, downloading data from binance')

if FORCE_DOWNLOAD:

    print('Downloading data from binance')
    try:
        klines = client.get_historical_klines(symbol=SYMBOL, interval=INTERVAL, start_str=START)
    # Check if the symbol is valid
    except binance.exceptions.BinanceAPIException as e:
        print(e)
        exit()
    # Check if the interval is valid
    except binance.exceptions.BinanceRequestException as e:
        print(e)
        exit()

    # Example response -> https://python-binance.readthedocs.io/en/latest/binance.html?highlight=get_historical_klines
    #     [
    #         1499040000000,      # Kline open time
    #         "0.01634790",       # Open price
    #         "0.80000000",       # High price
    #         "0.01575800",       # Low price
    #         "0.01577100",       # Close price
    #         "148976.11427815",  # Volume
    #         1499644799999,      # Kline close time
    #         "2434.19055334",    # Quote asset volume
    #         308,                # Number of trades
    #         "1756.87402397",    # Taker buy base asset volume
    #         "28.46694368",      # Taker buy quote asset volume
    #         "0"                 # Unused field. Ignore.
    #     ]
    # ]

    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    # Save to csv
    print('Saving data to data.csv')

    # Create a file called .data_settings
    # This file will store the symbol and interval of the data
    # This is used to check if the data is outdated
    with open('.data_settings', 'w') as f:
        f.write(f'{SYMBOL},{INTERVAL}, ')
    df.to_csv('data.csv', index=False)