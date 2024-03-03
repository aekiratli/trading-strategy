from utils import telegram_bot_sendtext, initialize_parities, initialize_state_files, read_state_file, update_state_file_and_state
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

async def rsi_bbands_alt(parity, state, file_name, logger, lowerband, rsi_value, close, orders: Orders, client: AsyncClient) -> dict:

    is_simulation = parity["rsi_bbands_alt_sim"]
    with open(f"{STATE_PATH}/active_trades.json", "r") as file:
        active_trades = json.load(file)
    try:
        if len(active_trades) == 4 and not is_simulation:
            # check if symbol+interval+_+strategy in active_trades
            if not f"{parity['symbol']}{parity['interval']}_rsi_bbands_alt" in active_trades:
                is_simulation = True
        elif state["rsi_bbands_alt_buy_orderId"] == "test_order_id":
            is_simulation = True
        elif state["rsi_bbands_alt_sell_orderId"] == "test_order_id":
            is_simulation = True
        else:
            is_simulation = False
    except KeyError:
        is_simulation = False
    except Exception as e:
        raise e

    if parity["rsi_bbands_alt"] == True and parity["rsi"] == True and parity["bbands"] == True:

        if rsi_value <= parity["rsi_bbands_alt_buy_limit"] and close > lowerband and state["rsi_bbands_alt_has_ordered"] == False:

            buy, sell = parity["rsi_bbands_alt_percentages"][0], parity["rsi_bbands_alt_percentages"][1]
            buy_price = close * buy
            sell_price = close * sell
            buy_price = round(buy_price, 4)
            sell_price = round(sell_price, 4)
            logging.info(f"buying for rsi_bbands_alt -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_bbands_alt_quota']
            # calculate the amount to buy
            amount_to_buy = quota / float(buy_price)
            # use decimal  of 4
            amount = round(amount_to_buy, 4)       
            buy_id = str(uuid.uuid4())
            orderId = await orders.create_order(amount, buy_price, "buy", 'rsi_bbands_alt', 'limit', buy_id,is_simulation)
            state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_id', state, buy_id)
            # orderId state update
            state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_orderId', state, orderId)
            await asyncio.sleep(1)
            await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - RSI-BBANDS-26 - LIMIT BUY ORDER* Buy Price = {buy_price}, Amount = {amount}", True)
            state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought_amount', state, amount)
            state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_price', state, buy_price)
            state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_price', state, sell_price)
            state = update_state_file_and_state(file_name, 'rsi_bbands_alt_has_ordered', state, True)
  

        if close <= state["rsi_bbands_alt_buy_price"] and state["rsi_bbands_alt_has_ordered"] == True and state["rsi_bbands_alt_bought"] == False:

            is_order_fullfilled = False
            if not is_order_fullfilled:
                if is_simulation:
                    is_order_fullfilled = True
                else:
                    orderId = state["rsi_bbands_alt_buy_orderId"]
                    order = await client.get_order(symbol=parity['symbol'], orderId=orderId)
                    if order["status"] == "FILLED":
                        is_order_fullfilled = True
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_orderId', state, "")
                    else:
                        await asyncio.sleep(10)
                        return state
                    
            if is_order_fullfilled:

                quota = parity['rsi_bbands_alt_quota']
                amount = state["rsi_bbands_alt_bought_amount"]
                sell_price = state["rsi_bbands_alt_sell_price"]
                sell_id = str(uuid.uuid4())
                orderId = await orders.create_order(amount, sell_price, "sell", 'rsi_bbands_alt', 'limit', sell_id,is_simulation)
                state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_id', state, sell_id)
                state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_orderId', state, orderId)
                await orders.complete_order(state["rsi_bbands_alt_buy_id"])
                await asyncio.sleep(1)

                await logger.save({"zone":"buy","bbands": lowerband, "rsi": rsi_value, "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_alt"})
                await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - RSI-BBANDS-26 - LIMIT BUY ORDER COMPLETED* Buy Price = {close}, Amount = {amount}%0A%0A * {parity['symbol']}-{parity['interval']} - RSI-BBANDS-26 - LIMIT SELL ORDER * Sell Price = {sell_price}, Amount = {amount}", True)
                state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought', state, True)
                state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_id', state, "")
                
        # sell if price is higher than sell price
        if close >= state["rsi_bbands_alt_sell_price"] and state["rsi_bbands_alt_bought"] == True:

            is_order_fullfilled = False
            if not is_order_fullfilled:
                if is_simulation:
                    is_order_fullfilled = True
                else:
                    orderId = state["rsi_bbands_alt_sell_orderId"]
                    order = await client.get_order(symbol=parity['symbol'], orderId=orderId)
                    if order["status"] == "FILLED":
                        is_order_fullfilled = True
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_orderId', state, "")
                    else:
                        await asyncio.sleep(10)
                        return state
                
            if is_order_fullfilled:

                logging.info(f"selling for rsi_bbands_alt -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                quota = parity['rsi_bbands_alt_quota']
                amount = state["rsi_bbands_alt_bought_amount"]
                await logger.save({"zone":"sell", "bbands": lowerband, "rsi": rsi_value, "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_alt"})
                await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - RSI-BBANDS-26 - LIMIT SELL ORDER COMPLETED* Sell Price = {close}, Amount = {amount}", True)
                await orders.complete_order(state["rsi_bbands_alt_sell_id"])
                state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought', state, False)
                state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought_amount', state, 0)
                state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_price', state, 0)
                state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_price', state, 0)
                state = update_state_file_and_state(file_name, 'rsi_bbands_alt_has_ordered', state, False)
                state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_id', state, "")

    return state


async def rsi_bbands(parity, state, file_name, logger, lowerband, rsi_value, close, orders: Orders, client: AsyncClient) -> dict:
    
    is_simulation = parity["rsi_bbands_sim"]
    with open(f"{STATE_PATH}/active_trades.json", "r") as file:
        active_trades = json.load(file)
    try:
        if len(active_trades) == 4 and not is_simulation:
            # check if symbol+interval+_+strategy in active_trades
            if not f"{parity['symbol']}{parity['interval']}_rsi_bbands" in active_trades:
                is_simulation = True
        elif state["rsi_bbands_buy_orderId"] == "test_order_id":
            is_simulation = True
        elif state["rsi_bbands_sell_orderId"] == "test_order_id":
            is_simulation = True
        else:
            is_simulation = False
    except KeyError:
        is_simulation = False
    except Exception as e:
        raise e
    
    if parity["rsi_bbands"] == True and parity["rsi"] == True and parity["bbands"] == True:
        if rsi_value <= parity["rsi_bbands_buy_limit"] and close > lowerband and state["rsi_bbands_has_ordered"] == False:
            buy, sell = parity["rsi_bbands_percentages"][0], parity["rsi_bbands_percentages"][1]
            buy_price = close * buy
            sell_price = close * sell
            # round to 4 decimal places
            buy_price = round(buy_price, 4)
            sell_price = round(sell_price, 4)
            logging.info(f"buying for rsi_bbands -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_bbands_quota']
            # calculate the amount to buy
            amount_to_buy = quota / float(buy_price)
            # use decimal  of 4
            amount = round(amount_to_buy, 4)
            buy_id = str(uuid.uuid4())
            orderId = await orders.create_order(amount, buy_price, "buy", 'rsi_bbands', 'limit', buy_id,is_simulation)
            state = update_state_file_and_state(file_name, 'rsi_bbands_buy_id', state, buy_id)
            state = update_state_file_and_state(file_name, 'rsi_bbands_buy_orderId', state, orderId)
            await asyncio.sleep(1)

            await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - RSI-BBANDS-21 - LIMIT BUY ORDER* Buy Price = {buy_price}, Amount = {amount}", True)

            state = update_state_file_and_state(file_name, 'rsi_bbands_bought_amount', state, amount)
            state = update_state_file_and_state(file_name, 'rsi_bbands_buy_price', state, buy_price)
            state = update_state_file_and_state(file_name, 'rsi_bbands_sell_price', state, sell_price)
            state = update_state_file_and_state(file_name, 'rsi_bbands_has_ordered', state, True)



        if close <= state["rsi_bbands_buy_price"] and state["rsi_bbands_has_ordered"] == True and state["rsi_bbands_bought"] == False:

            is_order_fullfilled = False
            if not is_order_fullfilled:
                if is_simulation:
                    is_order_fullfilled = True
                else:
                    orderId = state["rsi_bbands_buy_orderId"]
                    order = await client.get_order(symbol=parity['symbol'], orderId=orderId)
                    if order["status"] == "FILLED":
                        is_order_fullfilled = True
                        state = update_state_file_and_state(file_name, 'rsi_bbands_buy_orderId', state, "")
                    else:
                        await asyncio.sleep(10)
                        return state
            
            if is_order_fullfilled:

                quota = parity['rsi_bbands_quota']
                amount = state["rsi_bbands_bought_amount"]
                sell_price = state["rsi_bbands_sell_price"]
                sell_id = str(uuid.uuid4())

                orderId = await orders.create_order(amount, sell_price, "sell", 'rsi_bbands', 'limit', sell_id,is_simulation)
                state = update_state_file_and_state(file_name, 'rsi_bbands_sell_orderId', state, orderId)

                await orders.complete_order(state["rsi_bbands_buy_id"])
                state = update_state_file_and_state(file_name, 'rsi_bbands_buy_id', state, "")

                await logger.save({"zone":"buy", "bbands": lowerband, "rsi": rsi_value, "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands"})
                await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - RSI-BBANDS-21 - LIMIT BUY ORDER COMPLETED* Buy Price = {close}, Amount = {amount}%0A%0A *{parity['symbol']}-{parity['interval']} - RSI-BBANDS - LIMIT SELL ORDER* Sell Price = {sell_price}, Amount = {amount}", True)
                state = update_state_file_and_state(file_name, 'rsi_bbands_bought', state, True)


        # sell if price is higher than sell price
        if close >= state["rsi_bbands_sell_price"] and state["rsi_bbands_bought"] == True:

            is_order_fullfilled = False
            if not is_order_fullfilled:
                if is_simulation:
                    is_order_fullfilled = True
                else:
                    orderId = state["rsi_bbands_sell_orderId"]
                    order = await client.get_order(symbol=parity['symbol'], orderId=orderId)
                    if order["status"] == "FILLED":
                        is_order_fullfilled = True
                        state = update_state_file_and_state(file_name, 'rsi_bbands_sell_orderId', state, "")
                    else:
                        await asyncio.sleep(10)
                        return state

            logging.info(f"selling for rsi_bbands -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_bbands_quota']
            amount = state["rsi_bbands_bought_amount"]
            await logger.save({"zone":"sell","bbands": lowerband, "rsi": rsi_value, "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands"})
            await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - RSI-BBANDS - LIMIT SELL ORDER COMPLETED * Sell Price = {close}, Amount = {amount}", True)
            await orders.complete_order(state["rsi_bbands_sell_id"])
            state = update_state_file_and_state(file_name, 'rsi_bbands_bought', state, False)
            state = update_state_file_and_state(file_name, 'rsi_bbands_bought_amount', state, 0)
            state = update_state_file_and_state(file_name, 'rsi_bbands_buy_price', state, 0)
            state = update_state_file_and_state(file_name, 'rsi_bbands_sell_price', state, 0)
            state = update_state_file_and_state(file_name, 'rsi_bbands_has_ordered', state, False)
            state = update_state_file_and_state(file_name, 'rsi_bbands_sell_id', state, "")
            
    return state

if __name__ == "__main__":
    parities, file_names = initialize_parities()
    initialize_state_files(file_names),
    state = read_state_file(file_names[0])
    parity = parities[0]
    logger = Logger(f"{parity['symbol']}{parity['interval']}")
    close = 45
    rsi_value = 20
    lowerband = 30
    asyncio.run(rsi_bbands(parity, state,
                file_names[0], logger, lowerband,rsi_value, close))
