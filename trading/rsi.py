from utils import get_amount_to_buy, telegram_bot_sendtext, initialize_parities, initialize_state_files, read_state_file, update_state_file_and_state
import logging
from logger import Logger
import asyncio
from trading.orders import Orders
import uuid
from binance.client import AsyncClient
from dotenv import load_dotenv
import os
import asyncio
import json

load_dotenv()
STATE_PATH = os.getenv("STATE_PATH")

async def rsi_trading(parity, state, file_name, logger, rsi_value, close, orders: Orders, client: AsyncClient):

    is_simulation = parity["rsi_trading_sim"]
    with open(f"{STATE_PATH}/active_trades.json", "r") as file:
        active_trades = json.load(file)
    if len(active_trades) == 4 and not is_simulation:
        # check if symbol+interval+_+strategy in active_trades
        if not f"{parity['symbol']}{parity['interval']}_rsi_trading" in active_trades:
            is_simulation = True
            

    if parity["rsi_trading"] == True and parity["rsi"] == True:

        if rsi_value <= parity["rsi_trading_buy_limit"] and state["rsi_trading_bought"] == False:

            logging.info(
                f"buying for rsi_trading -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_trading_quota']
            amount = get_amount_to_buy(quota, parity['symbol'])
            buy_id = str(uuid.uuid4())
            await orders.create_order(amount, close, "buy", 'rsi_trading', 'market', buy_id, is_simulation)
            await orders.complete_order(buy_id)
            await asyncio.sleep(5)
            await logger.save({"zone": "buy", "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_trading"})
            
            sell_id = str(uuid.uuid4())
            sell_price = state["rsi_trading_buy_price"] * parity["rsi_trading_sell_percentage"]
            orderId = await orders.create_order(amount, sell_price, "sell", 'rsi_trading', 'limit', sell_id, is_simulation)
            state = update_state_file_and_state(file_name, 'rsi_trading_sell_orderId', state, orderId)
            state = update_state_file_and_state(file_name, 'rsi_trading_sell_id', state, sell_id)

            await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - RSI - MARKET BUY* Price = {close}, Amount = {amount}, RSI = {rsi_value}%0A%0A * {parity['symbol']}-{parity['interval']} - RSI - LIMIT ORDER SELL* Price = {close * parity['rsi_trading_sell_percentage'] }, Amount = {amount}", True)
            state = update_state_file_and_state(file_name, 'rsi_trading_bought', state, True)
            state = update_state_file_and_state(file_name, 'rsi_trading_buy_price', state, close)
            state = update_state_file_and_state(file_name, 'rsi_trading_bought_amount', state, amount)


        if close >= state["rsi_trading_buy_price"] * parity["rsi_trading_sell_percentage"] and state["rsi_trading_bought"] == True:

            is_order_fullfilled = False
            if not is_order_fullfilled:
                if is_simulation:
                    is_order_fullfilled = True
                else:
                    orderId = state["rsi_trading_sell_orderId"]
                    order = await client.get_order(symbol=parity['symbol'], orderId = orderId)
                    if order["status"] == "FILLED":
                        is_order_fullfilled = True
                        state = update_state_file_and_state(file_name, 'rsi_trading_sell_orderId', state, "")
                    else:
                        await asyncio.sleep(10)
                        return state

            logging.info(
                f"selling for rsi_trading -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_trading_quota']
            amount = state["rsi_trading_bought_amount"]
            sell_id = state["rsi_trading_alt_sell_id"]
            await orders.complete_order(sell_id)
            await logger.save({"zone": "sell", "price": close, "amount": amount, "quota": quota, "strategy": "rsi_trading"})
            await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - RSI - LIMIT SELL ORDER COMPLETED* Price = {close}, Amount = {amount}", True)
            state = update_state_file_and_state(file_name, 'rsi_trading_bought', state, False)
            state = update_state_file_and_state(file_name, 'rsi_trading_buy_price', state, 0)
            state = update_state_file_and_state(file_name, 'rsi_trading_bought_amount', state, 0)
            state = update_state_file_and_state(file_name, 'rsi_trading_sell_id', state, "")

    return state


async def rsi_trading_alt(parity, state, file_name, logger, rsi_value, close, orders: Orders, client: AsyncClient):

    is_simulation = parity["rsi_trading_alt_sim"]
    with open(f"{STATE_PATH}/active_trades.json", "r") as file:
        active_trades = json.load(file)
    if len(active_trades) == 4 and not is_simulation:
        # check if symbol+interval+_+strategy in active_trades
        if not f"{parity['symbol']}{parity['interval']}_rsi_trading_alt" in active_trades:
            is_simulation = True

    if parity["rsi_trading_alt"] == True and parity["rsi"] == True:

        if rsi_value <= parity["rsi_trading_alt_buy_limit"] and state["rsi_trading_alt_bought"] == False:

            logging.info(
                f"buying for rsi_trading_alt -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_trading_alt_quota']
            amount = get_amount_to_buy(quota, parity['symbol'])

            buy_id = str(uuid.uuid4())
            await orders.create_order(amount, close, "buy", 'rsi_trading_alt', 'market', buy_id, is_simulation)
            await orders.complete_order(buy_id)
            await asyncio.sleep(5)

            sell_id = str(uuid.uuid4())
            sell_price = state["rsi_trading_alt_buy_price"] * parity["rsi_trading_alt_sell_percentage"]

            orderId = await orders.create_order(amount, sell_price, "sell", 'rsi_trading_alt', 'limit', sell_id, is_simulation)
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_sell_orderId', state, orderId)
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_sell_id', state, sell_id)
            await logger.save({"zone": "buy", "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_trading_alt"})
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_bought', state, True)
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_buy_price', state, close)
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_bought_amount', state, amount)
            await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - RSI 26 - MARKET BUY* Price = {close}, Amount = {amount}, RSI = {rsi_value}%0A%0A *{parity['symbol']}-{parity['interval']} - RSI ALT - LIMIT ORDER SELL* Price = {close * parity['rsi_trading_sell_percentage']}, Amount = {amount}", True)

            
        if close >= state["rsi_trading_alt_buy_price"] * parity["rsi_trading_alt_sell_percentage"] and state["rsi_trading_alt_bought"] == True:

            is_order_fullfilled = False
            if not is_order_fullfilled:
                if is_simulation:
                    is_order_fullfilled = True
                else:
                    orderId = state["rsi_trading_alt_sell_id"]
                    order = await client.get_order(symbol=parity['symbol'], orderId = orderId)
                    if order["status"] == "FILLED":
                        is_order_fullfilled = True
                        state = update_state_file_and_state(file_name, 'rsi_trading_alt_sell_id', state, "")
                    else:
                        await asyncio.sleep(10)
                        return state
                    
            else:

                logging.info(
                    f"selling for rsi_trading_alt -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                quota = parity['rsi_trading_alt_quota']
                amount = state["rsi_trading_alt_bought_amount"]
                sell_id = state["rsi_trading_alt_sell_id"]
                await orders.complete_order(sell_id)
                await logger.save({"zone": "sell", "price": close, "amount": amount, "quota": quota, "strategy": "rsi_trading_alt"})
                await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - RSI 26 - LIMIT SELL ORDER COMPLETED* Price = {close}, Amount = {amount}", True)
                state = update_state_file_and_state(file_name, 'rsi_trading_alt_bought', state, False)
                state = update_state_file_and_state(file_name, 'rsi_trading_alt_buy_price', state, 0)
                state = update_state_file_and_state(file_name, 'rsi_trading_alt_bought_amount', state, 0)
                state = update_state_file_and_state(file_name, 'rsi_trading_alt_sell_id', state, "")

    return state

if __name__ == "__main__":
    parities, file_names = initialize_parities()
    initialize_state_files(file_names),
    state = read_state_file(file_names[2])
    parity = parities[2]
    logger = Logger(f"{'asd'}{parity['interval']}")
    close = 1
    rsi_value = 1
    asyncio.run(rsi_trading(parity, state, file_names[2], logger, rsi_value, close))
