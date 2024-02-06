from binance import AsyncClient, BinanceSocketManager
import asyncio
import pandas as pd
import os
import talib
import logging
import numpy as np
import aiohttp
from technical.indicators import PMAX
import warnings
from utils import *
from dotenv import load_dotenv
from logger import Logger

load_dotenv()
warnings.filterwarnings('ignore')
TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")
CHAT_ID = os.getenv("CHAT_ID")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main(df, parity, task_id, file_name, state, rsi_states):

    is_first_run = True
    pmax_candle_counter = state['pmax_candle_counter']
    is_n_to_l_notif_sent = state['is_n_to_l_notif_sent']

    # check if rsi_open_time attribute exists
    if hasattr(state, 'rsi_open_time'):
        pass
    else:
        # add rsi_open_time to state dict
        state.update({"rsi_open_time": df.iloc[-2]['open_time']})
        # write to state file
        update_state_file(file_name, 'rsi_open_time', df.iloc[-2]['open_time'])

    # check if pmax_open_time attribute exists
    if hasattr(state, 'pmax_open_time'):
        pass
    else:
        # add pmax_open_time to state dict
        state.update({"pmax_open_time": df.iloc[-2]['open_time']})
        # write to state file
        update_state_file(file_name, 'pmax_open_time', df.iloc[-2]['open_time'])
    # check if bbands_open_time attribute exists
    if hasattr(state, 'bbands_open_time'):
        pass
    else:
        # add bbands_open_time to state dict
        state.update({"bbands_open_time": df.iloc[-2]['open_time']})
        # write to state file
        update_state_file(file_name, 'bbands_open_time', df.iloc[-2]['open_time'])

    SYMBOL = parity['symbol']
    INTERVAL = parity['interval']
    logger = Logger(f"{parity['symbol']}{parity['interval']}")
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ts = bm.kline_socket(SYMBOL, interval=INTERVAL)

    async with ts as tscm:
        while True:
            res = await tscm.recv()

            if res['k']['x']:
                # candle is closed, concat new candle to df
                new_candle_data = [res['k']['t'], res['k']['o'], res['k']['h'], res['k']['l'], res['k']['c'], res['k']['v'], res['k']['T'], res['k']['q'], res['k']['n'], res['k']['V'], res['k']['Q'], res['k']['B']]
                new_candle = pd.DataFrame([new_candle_data], columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
                
                # Ensure the columns are in the same order and correct data types
                new_candle = new_candle.astype(df.dtypes)
                # remove first candle
                df = df.iloc[1:]
                # reassign indexes
                df.index = range(len(df))
                df = pd.concat([df, new_candle], ignore_index=True)
                # pmax related
                calculate_pmax = True
                if is_n_to_l_notif_sent == True:
                    pmax_candle_counter += 1
                    # update state file
                    if pmax_candle_counter == parity["pmax_candle_reset"]:
                        is_n_to_l_notif_sent = False
                        pmax_candle_counter = 0
                        # update state file
                        update_state_file(file_name, 'is_n_to_l_notif_sent', False)
                        update_state_file(file_name, 'pmax_candle_counter', 0)
                        logging.info(f"counter reset for symbol -> {parity['symbol']}, interval -> {parity['interval']}")
                    else:
                        update_state_file(file_name, 'pmax_candle_counter', pmax_candle_counter)

            else:
                # candle is open, update last candle
                df.loc[df.index[-1]] = [res['k']['t'], res['k']['o'], res['k']['h'], res['k']['l'], res['k']['c'], res['k']['v'], res['k']['T'], res['k']['q'], res['k']['n'], res['k']['V'], res['k']['Q'], res['k']['B']]
                calculate_pmax = False

            # pmax related
            if is_first_run == True:
                calculate_pmax = True
                is_first_run = False

            if  parity['rsi'] == True:
                rsi = talib.RSI(df['close'], timeperiod=14)
                # check if the state is the same as the current state
                rsi_state = calculate_rsi_state(rsi.iloc[-1], rsi_states)
                if state['rsi'] != rsi_state:
                    # check if the rsi_open_time has been updated
                    if state["rsi_open_time"] != df.iloc[-1]['open_time']:
                        logging.info(f"rsi_state -> {rsi_state}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, rsi -> {int(rsi.iloc[-1])}")
                        # update the rsi_open_time
                        state["rsi_open_time"] = df.iloc[-1]['open_time']
                        # update the state file
                        update_state_file(file_name, 'rsi', rsi_state)
                        update_state_file(file_name, 'rsi_open_time', df.iloc[-1]['open_time'])
                        # update the state
                        state["rsi"] = rsi_state
                        # send message if rsi_state is not n
                        if rsi_state != 'n':
                            # check if state starts with h
                            if rsi_state.startswith('h'):
                                msg = f"🟩🟩📈  *{parity['symbol']} - {parity['interval']} * - RSI = {rsi.iloc[-1]:.2f} 📈🟩🟩"
                            else:
                                msg = f"🟥🟥📉  *{parity['symbol']} - {parity['interval']} * - RSI = {rsi.iloc[-1]:.2f} 🟥🟥📉"
                            await telegram_bot_sendtext(msg)

            if parity["pmax"] == True:
                # add candle open time
                if calculate_pmax == True:
                    df['high'] = df['high'].astype(float)
                    df['low'] = df['low'].astype(float)
                    df['close'] = df['close'].astype(float)
                    pmax_df = PMAX(df, length=9, MAtype=4, src=2)
                    pmax = float(pmax_df.iloc[-2,-2])
                close = float(df.iloc[-1]['close'])

                # check buy signal
                if pmax_df.iloc[-1,-1] == "up":
                    # check if price is lower than pmax
                    if close <= pmax:
                        pmax_state = "l"
                    # check if price is higher %xxx than pmax
                    elif pmax <= close < pmax * parity['pmax_percantage']:
                        pmax_state = "p"
                    else:
                        pmax_state = "n"
                    if state['pmax'] != pmax_state:
                        if state['pmax'] == 'n' and pmax_state == 'l':
                            if pmax_candle_counter == 0:
                                pmax_candle_counter += 1
                                update_state_file(file_name, 'pmax_candle_counter', pmax_candle_counter)
                                logging.info(f"pmax_prev_state -> {state['pmax']}, pmax_state -> {pmax_state}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, pmax -> {pmax}, ma -> {pmax_df.iloc[-1,-3]}, close -> {close}")
                                msg = f"🟪🟪🟪 *{parity['symbol']} - {parity['interval']}* - Price is on PMAX = {pmax:.2f} 🟪🟪🟪"
                                await telegram_bot_sendtext(msg)
                                is_n_to_l_notif_sent = True
                            else:
                                logging.info(f"counter -> {pmax_candle_counter}, pmax_state -> {pmax_state}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, pmax -> {pmax}, ma -> {pmax_df.iloc[-1,-3]}, close -> {close}")

                        if state['pmax'] == 'p' and pmax_state == 'l':
                            if pmax_candle_counter == 0:
                                pmax_candle_counter += 1
                                update_state_file(file_name, 'pmax_candle_counter', pmax_candle_counter)
                                logging.info(f"pmax_prev_state -> {state['pmax']}, pmax_state -> {pmax_state}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, pmax -> {pmax}, ma -> {pmax_df.iloc[-1,-3]}, close -> {close}")
                                msg = f"🟪🟪🟪 *{parity['symbol']} - {parity['interval']}* - Price is on PMAX = {pmax:.2f} 🟪🟪🟪"
                                await telegram_bot_sendtext(msg)
                                is_n_to_l_notif_sent = True
                            else:
                                logging.info(f"counter -> {pmax_candle_counter}, pmax_state -> {pmax_state}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, pmax -> {pmax}, ma -> {pmax_df.iloc[-1,-3]}, close -> {close}")

                        if state['pmax'] == 'n' and pmax_state == 'p':
                            if state["pmax_open_time"] != df.iloc[-1]['open_time']:
                                logging.info(f"pmax_prev_state -> {state['pmax']}, pmax_state -> {pmax_state}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, pmax -> {pmax}, ma -> {pmax_df.iloc[-1,-3]}, close -> {close}")
                                msg = f"🟨🟨🟨 *{parity['symbol']} - {parity['interval']}* Price = {close:.2f} is close to PMAX = {pmax:.2f}  🟨🟨🟨"
                                state["pmax_open_time"] = df.iloc[-1]['open_time']
                                update_state_file(file_name, 'pmax_open_time', df.iloc[-1]['open_time'])
                                await telegram_bot_sendtext(msg)
                        update_state_file(file_name, 'pmax', pmax_state)
                        state["pmax"] = pmax_state

            # calculate bolinger bands
            if parity["bbands"] == True:
                # calculate bolinger bands
                upperband, middleband, lowerband = talib.BBANDS(df['close'], timeperiod=20, nbdevup=3, nbdevdn=3, matype=0)

                if np.float64(df.iloc[-1]['close']) < lowerband.iloc[-1]:
                    bbands_state = "l"

                else:
                    bbands_state = "n"

                if state['bbands'] != bbands_state:
                    if state["bbands_open_time"] != df.iloc[-1]['open_time']:
                        logging.info(f"bbands_state -> {bbands_state}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, lowerband -> {lowerband.iloc[-1]}, close -> {df.iloc[-1]['close']}")
                        # update the state file
                        update_state_file(file_name, 'bbands', bbands_state)
                        update_state_file(file_name, 'bbands_open_time', df.iloc[-1]['open_time'])
                        # update the state
                        state["bbands"] = bbands_state
                        state["bbands_open_time"] = df.iloc[-1]['open_time']
                        if bbands_state == 'l':
                            msg = f"🟥🟥📉 *{parity['symbol']} - {parity['interval']}* Price = {float(df.iloc[-1]['close']):.2f} is lower than Bollinger Band - Lower Band = {lowerband.iloc[-1]:.2f} 🟥🟥📉"
                            await telegram_bot_sendtext(msg)
            
            close = float(df.iloc[-1]['close'])
            rsi_value = rsi.iloc[-1]
            lowerband = lowerband.iloc[-1]

            if parity["rsi_trading"] == True and parity["rsi"] == True:

                if rsi_value <= parity["rsi_trading_buy_limit"] and state["rsi_trading_bought"] == False:
                        
                        logging.info(f"buying for rsi_trading -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_trading_quota']
                        amount = get_amount_to_buy(quota, parity['symbol'])
                        await logger.save({"zone": "buy", "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_trading"})
                        await telegram_bot_sendtext(f"*RSI - MARKET BUY - {parity['symbol']}-{parity['symbol']}* Price = {close}, Amount = {amount}, RSI = {rsi_value}\nRSI - LIMIT ORDER SELL - {parity['symbol']}-{parity['symbol']}* Price = {state["rsi_trading_buy_price"] * parity["rsi_trading_sell_percentage"] }, Amount = {amount}", True)
                        state["rsi_trading_bought"] = True
                        state["rsi_trading_bought_amount"] = amount
                        state["rsi_trading_buy_price"] = close
                        update_state_file(file_name, 'rsi_trading_bought', True)
                        update_state_file(file_name, 'rsi_trading_buy_price', close)
                        update_state_file(file_name, 'rsi_trading_bought_amount', amount)

                if close >= state["rsi_trading_buy_price"] * parity["rsi_trading_sell_percentage"]  and state["rsi_trading_bought"] == True:
                        
                        logging.info(f"selling for rsi_trading -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_trading_quota']
                        amount = state["rsi_trading_bought_amount"]
                        await logger.save({"zone": "sell", "price":close, "amount": amount, "quota": quota, "strategy": "rsi_trading"})
                        await telegram_bot_sendtext(f"*RSI - SELL - {parity['symbol']}-{parity['symbol']}* Price = {close}, Amount = {amount}", True)
                        state["rsi_trading_bought"] = False
                        state["rsi_trading_buy_price"] = 0
                        state["rsi_trading_bought_amount"] = 0
                        update_state_file(file_name, 'rsi_trading_bought', False)
                        update_state_file(file_name, 'rsi_trading_buy_price', 0)
                        update_state_file(file_name, 'rsi_trading_bought_amount', 0)

            if parity["rsi_trading_alt"] == True and parity["rsi"] == True:

                if rsi_value <= parity["rsi_trading_alt_buy_limit"] and state["rsi_trading_alt_bought"] == False:
                        
                        logging.info(f"buying for -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_trading_quota']
                        amount = get_amount_to_buy(quota, parity['symbol'])
                        await logger.save({"zone": "buy", "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_alt_trading"})
                        await telegram_bot_sendtext(f"*RSI ALT - BUY - {parity['symbol']}-{parity['symbol']}* Price = {close}, Amount = {amount}", True)
                        state["rsi_trading_alt_bought"] = True
                        state["rsi_trading_alt_bought_amount"] = amount
                        state["rsi_trading_alt_buy_price"] = close
                        update_state_file(file_name, 'rsi_trading_alt_bought', True)
                        update_state_file(file_name, 'rsi_trading_alt_buy_price', close)
                        update_state_file(file_name, 'rsi_trading_alt_bought_amount', amount)

                if close >= state["rsi_trading_alt_buy_price"] * parity["rsi_trading_alt_sell_percentage"]  and state["rsi_trading_alt_bought"] == True:
                        
                        logging.info(f"selling for -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_trading_alt_quota']
                        amount = state["rsi_trading_alt_bought_amount"]
                        await logger.save({"zone": "sell", "price":close, "amount": amount, "quota": quota, "strategy": "rsi_alt_trading"})
                        await telegram_bot_sendtext(f"*RSI ALT - SELL - {parity['symbol']}-{parity['symbol']}* Price = {close}, Amount = {amount}", True)
                        state["rsi_trading_alt_bought"] = False
                        state["rsi_trading_alt_buy_price"] = 0
                        state["rsi_trading_alt_bought_amount"] = 0
                        update_state_file(file_name, 'rsi_trading_alt_bought', False)
                        update_state_file(file_name, 'rsi_trading_alt_buy_price', 0)
                        update_state_file(file_name, 'rsi_trading_alt_bought_amount', 0)

            if parity["rsi_bbands"] == True and parity["rsi"] == True and parity["bbands"] == True:

                if rsi_value <= parity["rsi_bbands_buy_limit"] and close > lowerband and state["rsi_bbands_has_ordered"] == False:
                        
                        buy, sell = parity["rsi_bbands_percentages"][0], parity["rsi_bbands_percentages"][1]
                        buy_price = close * buy
                        sell_price = close * sell
                        logging.info(f"buying for rsi_bbands -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_bbands_quota']
                        amount = get_amount_to_buy(quota, parity['symbol'])
                        await telegram_bot_sendtext(f"*RSI-BBANDS - LIMIT BUY ORDER- {parity['symbol']}-{parity['symbol']}* Buy Price = {buy_price}, Amount = {amount}/n
                                                      *RSI-BBANDS - LIMIT SELL ORDER - {parity['symbol']}-{parity['symbol']}* Sell Price = {sell_price}, Amount = {amount}", True)
                        
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_bought_amount', state, amount)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_buy_price', state, buy_price)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_sell_price', state, sell_price)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_has_ordered', state, True)

                if close <= state["rsi_bbands_buy_price"] and state["rsi_bbands_has_ordered"] == True:
                            
                            quota = parity['rsi_bbands_quota']
                            amount = state["rsi_bbands_bought_amount"]
                            await logger.save({"bbands": lowerband, "rsi": rsi_value , "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_trading"})
                            await telegram_bot_sendtext(f"*RSI-BBANDS - LIMIT BUY ORDER COMPLETED - {parity['symbol']}-{parity['symbol']}* Sell Price = {close}, Amount = {amount}", True)
                            state =  update_state_file_and_state(file_name, 'rsi_bbands_bought', state, True)

                # sell if price is higher than sell price
                if close >= state["rsi_bbands_sell_price"] and state["rsi_bbands_bought"] == True:
                        
                        logging.info(f"selling for rsi_bbands -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_bbands_quota']
                        amount = state["rsi_bbands_bought_amount"]
                        await logger.save({"bbands": lowerband, "rsi":rsi_value , "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_trading"})
                        await telegram_bot_sendtext(f"*RSI-BBANDS - LIMIT SELL ORDER COMPLETED - {parity['symbol']}-{parity['symbol']}* Sell Price = {close}, Amount = {amount}", True)

                        state = update_state_file_and_state(file_name, 'rsi_bbands_bought', state, False)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_bought_amount', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_buy_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_sell_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_has_ordered', state, False)

            if parity["rsi_bbands_alt"] == True and parity["rsi"] == True and parity["bbands"] == True:

                if rsi_value <= parity["rsi_bbands_alt_buy_limit"] and close > lowerband and state["rsi_bbands_alt_has_ordered"] == False:
                        
                        buy, sell = parity["rsi_bbands_alt_percentages"][0], parity["rsi_bbands_alt_percentages"][1]
                        buy_price = close * buy
                        sell_price = close * sell
                        logging.info(f"buying for rsi_bbands -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_bbands_alt_quota']
                        amount = get_amount_to_buy(quota, parity['symbol'])
                        await telegram_bot_sendtext(f"*RSI-BBANDS-ALT - LIMIT BUY ORDER- {parity['symbol']}-{parity['symbol']}* Buy Price = {buy_price}, Amount = {amount}/n
                                                      *RSI-BBANDS-ALT - LIMIT SELL ORDER - {parity['symbol']}-{parity['symbol']}* Sell Price = {sell_price}, Amount = {amount}", True)
                        
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_alt_bought_amount', state, amount)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_price', state, buy_price)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_price', state, sell_price)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_alt_has_ordered', state, True)

                if close <= state["rsi_bbands_alt_buy_price"] and state["rsi_bbands_alt_has_ordered"] == True:
                            
                            quota = parity['rsi_bbands_alt_quota']
                            amount = state["rsi_bbands_alt_bought_amount"]
                            await logger.save({"bbands": lowerband, "rsi": rsi_value , "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_trading"})
                            await telegram_bot_sendtext(f"*RSI-BBANDS-ALT - LIMIT BUY ORDER COMPLETED - {parity['symbol']}-{parity['symbol']}* Sell Price = {close}, Amount = {amount}", True)
                            state =  update_state_file_and_state(file_name, 'rsi_bbands_alt_bought', state, True)

                # sell if price is higher than sell price
                if close >= state["rsi_bbands_alt_sell_price"] and state["rsi_bbands_alt_bought"] == True:
                        
                        logging.info(f"selling for rsi_bbands_alt -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_bbands_alt_quota']
                        amount = state["rsi_bbands_alt_bought_amount"]
                        await logger.save({"bbands": lowerband, "rsi":rsi_value , "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_trading"})
                        await telegram_bot_sendtext(f"*RSI-BBANDS-ALT - LIMIT SELL ORDER COMPLETED - {parity['symbol']}-{parity['symbol']}* Sell Price = {close}, Amount = {amount}", True)

                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought', state, False)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought_amount', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_has_ordered', state, False)
                        
            if parity["pmax_bbands"] == True and parity["pmax"] == True and parity["bbands"] == True:

                zone = pmax_df.iloc[-1,-2]

                if zone == "up" and lowerband >= pmax and state["pmax_bbands_has_ordered"] == False:

                    buy, sell = parity["rsi_bbands_percentages"][0], parity["rsi_bbands_percentages"][1]
                    buy_price = pmax * buy
                    sell_price = pmax * sell
                    logging.info(f"buying for pmax_bbands -> pmax -> {pmax}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                    quota = parity['pmax_bbands_quota']
                    amount = get_amount_to_buy(quota, parity['symbol'])
                    await logger.save({"bbands": lowerband, "pmax": pmax, "price":close, "amount": amount, "quota": quota,  "strategy": "pmax_bbands_trading"})
                    await telegram_bot_sendtext(f"*PMAX-BBANDS - LIMIT BUY ORDER - {parity['symbol']}-{parity['symbol']}* Buy Price = {buy_price}, Amount = {amount}/n
                                                *PMAX-BBANDS - LIMIT SELL ORDER - {parity['symbol']}-{parity['symbol']}* Sell Price = {sell_price}, Amount = {amount}", True)
                    
                    state = update_state_file_and_state(file_name, 'pmax_bbands_has_ordered', state, True)
                    state = update_state_file_and_state(file_name, 'pmax_bbands_bought_amount', state, amount)
                    state = update_state_file_and_state(file_name, 'pmax_bbands_buy_price', state, buy_price)
                    state = update_state_file_and_state(file_name, 'pmax_bbands_sell_price', state, sell_price)

                if close <= state["pmax_bbands_buy_price"] and state["pmax_bbands_has_ordered"] == True:
                    quota = parity['pmax_bbands_quota']
                    amount = state["pmax_bbands_bought_amount"]
                    await logger.save({"bbands": lowerband, "pmax": pmax, "price":close, "amount": amount, "quota": quota,  "strategy": "pmax_bbands_trading"})
                    await telegram_bot_sendtext(f"*PMAX-BBANDS - LIMIT BUY ORDER COMPLETED - {parity['symbol']}-{parity['symbol']}* Buy Price = {close}, Amount = {amount}", True)
                    state = update_state_file_and_state(file_name, 'pmax_bbands_bought', state, True)

                if close >= state["pmax_bbands_sell_price"] and state["pmax_bbands_bought"] == True:

                    logging.info(f"selling for pmax_bbands -> pmax -> {pmax}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                    quota = parity['pmax_bbands_quota']
                    amount = state["pmax_bbands_bought_amount"]
                    await logger.save({"bbands": lowerband, "pmax": pmax, "price":close, "amount": amount, "quota": quota,  "strategy": "pmax_bbands_trading"})
                    await telegram_bot_sendtext(f"*PMAX-BBANDS - SELL - {parity['symbol']}-{parity['symbol']}* Sell Price = {close}, Amount = {amount}", True)
                    
                    state = update_state_file_and_state(file_name, 'pmax_bbands_bought', state, False)
                    state = update_state_file_and_state(file_name, 'pmax_bbands_bought_amount', state, 0)
                    state = update_state_file_and_state(file_name, 'pmax_bbands_buy_price', state, 0)
                    state = update_state_file_and_state(file_name, 'pmax_bbands_sell_price', state, 0)
                    state = update_state_file_and_state(file_name, 'pmax_bbands_has_ordered', state, False)

async def run_parities():

    # create tasks for each parity
    parities, file_names = initialize_parities()
    initialize_state_files(file_names)
    tasks = []
    task_id = 0
    for parity in parities:
        if parity['is_parity_active'] == True:
            rsi_states = calculate_rsi_states(parity)
            state = read_state_file(file_names[task_id])
            df = get_candles(parity['symbol'], parity['interval'], parity['start'])
            tasks.append(main(df, parity, task_id, file_names[task_id], state,rsi_states))        
        task_id += 1
    send_text = 'https://api.telegram.org/bot' + TELEGRAM_KEY + '/sendMessage?chat_id=' + CHAT_ID + '&parse_mode=Markdown&text=' + "Bot is running"
    async with aiohttp.ClientSession() as session:
        async with session.get(send_text) as resp:
            print(await resp.text())
    #Run tasks concurrently
    await asyncio.gather(*tasks)
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_parities())
