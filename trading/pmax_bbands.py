from utils import telegram_bot_sendtext, update_state_file, initialize_parities, initialize_state_files, read_state_file, update_state_file_and_state
import logging
from logger import Logger
import asyncio
import uuid
from trading.orders import Orders
from binance.client import AsyncClient
from dotenv import load_dotenv
import os
import asyncio
import json

load_dotenv()
STATE_PATH = os.getenv("STATE_PATH")

async def pmax_bbands(parity, state, file_name, logger, zone, lowerband, pmax, close, orders: Orders, client: AsyncClient) -> dict:

    is_simulation = parity["pmax_bbands_sim"]
    with open(f"{STATE_PATH}/active_trades.json", "r") as file:
        active_trades = json.load(file)
    if len(active_trades) == 4 and not is_simulation:
        # check if symbol+interval+_+strategy in active_trades
        if not f"{parity['symbol']}{parity['interval']}_pmax_bbands" in active_trades:
            is_simulation = True

    if parity["pmax_bbands"] == True and parity["pmax"] == True and parity["bbands"] == True:

        if zone == "up" and lowerband >= pmax and state["pmax_bbands_has_ordered"] == False:

            buy, sell = parity["rsi_bbands_percentages"][0], parity["rsi_bbands_percentages"][1]
            buy_price = pmax * buy
            sell_price = pmax * sell
            # round to 4 decimal places
            buy_price = round(buy_price, 4)
            sell_price = round(sell_price, 4)
            logging.info(
                f"buying for pmax_bbands -> pmax -> {pmax}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['pmax_bbands_quota']
            # amount to buy
            amount_to_buy = quota / float(buy_price)
            amount = round(amount_to_buy, 4)
            
            buy_id = str(uuid.uuid4())
            orderId = await orders.create_order(amount, buy_price, "buy", 'pmax_bbands', 'limit', buy_id, is_simulation)
            await asyncio.sleep(1)
            state = update_state_file_and_state(
                file_name, 'pmax_bbands_buy_orderId', state, orderId)
            
            await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - PMAX-BBANDS - LIMIT BUY ORDER* Buy Price = {buy_price}, Amount = {amount}", True)
            
            state = update_state_file_and_state(
                file_name, 'pmax_bbands_has_ordered', state, True)
            state = update_state_file_and_state(
                file_name, 'pmax_bbands_bought_amount', state, amount)
            state = update_state_file_and_state(
                file_name, 'pmax_bbands_buy_price', state, buy_price)
            state = update_state_file_and_state(
                file_name, 'pmax_bbands_buy_id', state, buy_id)
            state = update_state_file_and_state(
                file_name, 'pmax_bbands_sell_price', state, sell_price)


        if close <= state["pmax_bbands_buy_price"] and state["pmax_bbands_has_ordered"] == True and state["pmax_bbands_bought"] == False:
            # check orderId every 60 seconds if it has been filled
            is_order_fullfilled = False
            if not is_order_fullfilled:
                if is_simulation:
                    is_order_fullfilled = True
                else:
                    orderId = state["pmax_bbands_buy_orderId"]
                    order = await client.get_order(symbol=parity['symbol'], orderId=orderId)
                    if order["status"] == "FILLED":
                        is_order_fullfilled = True
                    else:
                        await asyncio.sleep(10)
                        return state
            
            if is_order_fullfilled:
                quota = parity['pmax_bbands_quota']
                amount = state["pmax_bbands_bought_amount"]
                sell_price = state["pmax_bbands_sell_price"]
                await logger.save({"zone":"buy","bbands": lowerband, "pmax": pmax, "price": close, "amount": amount, "quota": quota,  "strategy": "pmax_bbands"})
                await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - PMAX-BBANDS - LIMIT BUY ORDER COMPLETED* Buy Price = {close}, Amount = {amount}%0A%0A *{parity['symbol']}-{parity['interval']} - PMAX-BBANDS - LIMIT SELL ORDER* Sell Price = {sell_price}, Amount = {amount}", True)
                state = update_state_file_and_state(file_name, 'pmax_bbands_bought', state, True)
                await orders.complete_order(state["pmax_bbands_buy_id"])
                state = update_state_file_and_state(file_name, 'pmax_bbands_buy_id', state, "")
                sell_id = str(uuid.uuid4())
                orderId = await orders.create_order(amount, sell_price, "sell", 'pmax_bbands', 'limit', sell_id, is_simulation)
                state = update_state_file_and_state(file_name, 'pmax_bbands_sell_orderId', state, orderId)
                state = update_state_file_and_state(file_name, 'pmax_bbands_sell_id', state, sell_id)
                await asyncio.sleep(1)
                state = update_state_file_and_state(file_name, 'pmax_bbands_buy_orderId', state, "")

        if close >= state["pmax_bbands_sell_price"] and state["pmax_bbands_bought"] == True:
            is_order_fullfilled = False
            if not is_order_fullfilled:
                if is_simulation:
                    is_order_fullfilled = True
                else:
                    orderId = state["pmax_bbands_sell_orderId"]
                    order = await client.get_order(symbol=parity['symbol'], orderId=orderId)
                    if order["status"] == "FILLED":
                        is_order_fullfilled = True
                    else:
                        await asyncio.sleep(10)
                        return state
                
            if is_order_fullfilled:

                logging.info(
                    f"selling for pmax_bbands -> pmax -> {pmax}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                quota = parity['pmax_bbands_quota']
                amount = state["pmax_bbands_bought_amount"]
                await logger.save({"zone":"sell","bbands": lowerband, "pmax": pmax, "price": close, "amount": amount, "quota": quota,  "strategy": "pmax_bbands"})
                await telegram_bot_sendtext(f"*simulation={is_simulation}-{parity['symbol']}-{parity['interval']} - PMAX-BBANDS - SELL ORDER COMPLETED* Sell Price = {close}, Amount = {amount}", True)
                await orders.complete_order(state["pmax_bbands_sell_id"])

                state = update_state_file_and_state(
                    file_name, 'pmax_bbands_bought', state, False)
                state = update_state_file_and_state(
                    file_name, 'pmax_bbands_bought_amount', state, 0)
                state = update_state_file_and_state(
                    file_name, 'pmax_bbands_buy_price', state, 0)
                state = update_state_file_and_state(
                    file_name, 'pmax_bbands_sell_price', state, 0)
                state = update_state_file_and_state(
                    file_name, 'pmax_bbands_has_ordered', state, False)
                state = update_state_file_and_state(
                    file_name, 'pmax_bbands_sell_id', state, "")
                state = update_state_file_and_state(file_name, 'pmax_bbands_sell_orderId', state, "")



    return state


if __name__ == "__main__":
    parities, file_names = initialize_parities()
    initialize_state_files(file_names),
    state = read_state_file(file_names[0])
    parity = parities[0]
    logger = Logger(f"{parity['symbol']}{parity['interval']}")
    close = 20
    zone="down"
    pmax = 20
    lowerband = 20
    asyncio.run(pmax_bbands(parity, state,
                file_names[0], logger,zone, lowerband, pmax, close))
