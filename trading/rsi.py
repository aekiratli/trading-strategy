# from utils import get_amount_to_buy, telegram_bot_sendtext, update_state_file
from utils import get_amount_to_buy, telegram_bot_sendtext, update_state_file, initialize_parities, initialize_state_files, read_state_file, update_state_file_and_state
import logging
from logger import Logger
import asyncio
from trading.orders import Orders
import uuid


async def rsi_trading(parity, state, file_name, logger, rsi_value, close, orders: Orders):

    if parity["rsi_trading"] == True and parity["rsi"] == True:

        if rsi_value <= parity["rsi_trading_buy_limit"] and state["rsi_trading_bought"] == False:

            logging.info(
                f"buying for rsi_trading -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_trading_quota']
            amount = get_amount_to_buy(quota, parity['symbol'])
            await logger.save({"zone": "buy", "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_trading"})
            await telegram_bot_sendtext(f"* {parity['symbol']}-{parity['interval']} - RSI - MARKET BUY* Price = {close}, Amount = {amount}, RSI = {rsi_value}%0A%0A * {parity['symbol']}-{parity['interval']} - RSI - LIMIT ORDER SELL* Price = {close * parity['rsi_trading_sell_percentage'] }, Amount = {amount}", True)
            state = update_state_file_and_state(file_name, 'rsi_trading_bought', state, True)
            state = update_state_file_and_state(file_name, 'rsi_trading_buy_price', state, close)
            state = update_state_file_and_state(file_name, 'rsi_trading_bought_amount', state, amount)
            sell_id = str(uuid.uuid4())
            state = update_state_file_and_state(file_name, 'rsi_trading_sell_id', state, sell_id)
            await orders.create_order(amount, close, "sell", 'rsi_trading', 'limit', sell_id)
            buy_id = str(uuid.uuid4())
            await orders.create_order(amount, close, "buy", 'rsi_trading', 'market', buy_id)
            await orders.complete_order(buy_id)

        if close >= state["rsi_trading_buy_price"] * parity["rsi_trading_sell_percentage"] and state["rsi_trading_bought"] == True:

            logging.info(
                f"selling for rsi_trading -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_trading_quota']
            amount = state["rsi_trading_bought_amount"]
            await logger.save({"zone": "sell", "price": close, "amount": amount, "quota": quota, "strategy": "rsi_trading"})
            await telegram_bot_sendtext(f" *{parity['symbol']}-{parity['interval']} - RSI - LIMIT SELL ORDER COMPLETED* Price = {close}, Amount = {amount}", True)
            state = update_state_file_and_state(file_name, 'rsi_trading_bought', state, False)
            state = update_state_file_and_state(file_name, 'rsi_trading_buy_price', state, 0)
            state = update_state_file_and_state(file_name, 'rsi_trading_bought_amount', state, 0)
            state = update_state_file_and_state(file_name, 'rsi_trading_sell_id', state, "")
            await orders.complete_order(state["rsi_trading_sell_id"])

    return state


async def rsi_trading_alt(parity, state, file_name, logger, rsi_value, close, orders: Orders):
    if parity["rsi_trading_alt"] == True and parity["rsi"] == True:

        if rsi_value <= parity["rsi_trading_alt_buy_limit"] and state["rsi_trading_alt_bought"] == False:

            logging.info(
                f"buying for rsi_trading_alt -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_trading_quota']
            amount = get_amount_to_buy(quota, parity['symbol'])
            await logger.save({"zone": "buy", "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_trading_alt"})
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_bought', state, True)
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_buy_price', state, close)
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_bought_amount', state, amount)
            await telegram_bot_sendtext(f" *{parity['symbol']}-{parity['interval']} - RSI ALT - MARKET BUY* Price = {close}, Amount = {amount}, RSI = {rsi_value}%0A%0A *{parity['symbol']}-{parity['interval']} - RSI ALT - LIMIT ORDER SELL* Price = {sell_limit_price}, Amount = {amount}", True)
            sell_id = str(uuid.uuid4())
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_sell_id', state, sell_id)
            await orders.create_order(amount, close, "sell", 'rsi_trading', 'limit', sell_id)
            buy_id = str(uuid.uuid4())
            await orders.create_order(amount, close, "buy", 'rsi_trading', 'market', buy_id)
            await orders.complete_order(buy_id)
            
        if close >= state["rsi_trading_alt_buy_price"] * parity["rsi_trading_alt_sell_percentage"] and state["rsi_trading_alt_bought"] == True:

            logging.info(
                f"selling for rsi_trading_alt -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_trading_alt_quota']
            amount = state["rsi_trading_alt_bought_amount"]
            await logger.save({"zone": "sell", "price": close, "amount": amount, "quota": quota, "strategy": "rsi_trading_alt"})
            await telegram_bot_sendtext(f" *{parity['symbol']}-{parity['interval']} - RSI ALT - LIMIT SELL ORDER COMPLETED* Price = {close}, Amount = {amount}", True)
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_bought', state, False)
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_buy_price', state, 0)
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_bought_amount', state, 0)
            state = update_state_file_and_state(file_name, 'rsi_trading_alt_sell_id', state, "")
            await orders.complete_order(state["rsi_trading_alt_sell_id"])

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
