# from utils import get_amount_to_buy, telegram_bot_sendtext, update_state_file
from utils import get_amount_to_buy, telegram_bot_sendtext, update_state_file, initialize_parities, initialize_state_files, read_state_file, update_state_file_and_state
import logging
from logger import Logger
import asyncio

async def rsi_bbands_alt(parity, state, file_name, logger, lowerband, rsi_value, close):
    if parity["rsi_bbands_alt"] == True and parity["rsi"] == True and parity["bbands"] == True:

        if rsi_value <= parity["rsi_bbands_alt_buy_limit"] and close > lowerband and state["rsi_bbands_alt_has_ordered"] == False:

            buy, sell = parity["rsi_bbands_alt_percentages"][0], parity["rsi_bbands_alt_percentages"][1]
            buy_price = close * buy
            sell_price = close * sell
            buy_price = round(buy_price, 4)
            sell_price = round(sell_price, 4)
            logging.info(
                f"buying for rsi_bbands_alt -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_bbands_alt_quota']
            # calculate the amount to buy
            amount_to_buy = quota / float(buy_price)
            # use decimal  of 4
            amount = round(amount_to_buy, 4)
            await telegram_bot_sendtext(f"* {parity['symbol']}-{parity['interval']} - RSI-BBANDS-ALT - LIMIT BUY ORDER* Buy Price = {buy_price}, Amount = {amount}%0A%0A * {parity['symbol']}-{parity['interval']} - RSI-BBANDS-ALT - LIMIT SELL ORDER * Sell Price = {sell_price}, Amount = {amount}", True)

            state = update_state_file_and_state(
                file_name, 'rsi_bbands_alt_bought_amount', state, amount)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_alt_buy_price', state, buy_price)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_alt_sell_price', state, sell_price)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_alt_has_ordered', state, True)

        if close <= state["rsi_bbands_alt_buy_price"] and state["rsi_bbands_alt_has_ordered"] == True and state["rsi_bbands_alt_bought"] == False:

            quota = parity['rsi_bbands_alt_quota']
            amount = state["rsi_bbands_alt_bought_amount"]
            await logger.save({"zone":"buy","bbands": lowerband, "rsi": rsi_value, "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_alt"})
            await telegram_bot_sendtext(f"*{parity['symbol']}-{parity['interval']} - RSI-BBANDS-ALT - LIMIT BUY ORDER COMPLETED* Buy Price = {close}, Amount = {amount}", True)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_alt_bought', state, True)

        # sell if price is higher than sell price
        if close >= state["rsi_bbands_alt_sell_price"] and state["rsi_bbands_alt_bought"] == True:

            logging.info(
                f"selling for rsi_bbands_alt -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_bbands_alt_quota']
            amount = state["rsi_bbands_alt_bought_amount"]
            await logger.save({"zone":"sell", "bbands": lowerband, "rsi": rsi_value, "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_alt"})
            await telegram_bot_sendtext(f"* {parity['symbol']}-{parity['interval']} - RSI-BBANDS-ALT - LIMIT SELL ORDER COMPLETED* Sell Price = {close}, Amount = {amount}", True)

            state = update_state_file_and_state(
                file_name, 'rsi_bbands_alt_bought', state, False)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_alt_bought_amount', state, 0)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_alt_buy_price', state, 0)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_alt_sell_price', state, 0)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_alt_has_ordered', state, False)
    return state


async def rsi_bbands(parity, state, file_name, logger, lowerband, rsi_value, close):
    if parity["rsi_bbands"] == True and parity["rsi"] == True and parity["bbands"] == True:
        if rsi_value <= parity["rsi_bbands_buy_limit"] and close > lowerband and state["rsi_bbands_has_ordered"] == False:
            buy, sell = parity["rsi_bbands_percentages"][0], parity["rsi_bbands_percentages"][1]
            buy_price = close * buy
            sell_price = close * sell
            # round to 4 decimal places
            buy_price = round(buy_price, 4)
            sell_price = round(sell_price, 4)
            logging.info(
                f"buying for rsi_bbands -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_bbands_quota']
            # calculate the amount to buy
            amount_to_buy = quota / float(buy_price)
            # use decimal  of 4
            amount = round(amount_to_buy, 4)
            await telegram_bot_sendtext(f"*{parity['symbol']}-{parity['interval']} - RSI-BBANDS - LIMIT BUY ORDER* Buy Price = {buy_price}, Amount = {amount}%0A%0A *{parity['symbol']}-{parity['interval']} - RSI-BBANDS - LIMIT SELL ORDER* Sell Price = {sell_price}, Amount = {amount}", True)

            state = update_state_file_and_state(
                file_name, 'rsi_bbands_bought_amount', state, amount)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_buy_price', state, buy_price)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_sell_price', state, sell_price)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_has_ordered', state, True)

        if close <= state["rsi_bbands_buy_price"] and state["rsi_bbands_has_ordered"] == True and state["rsi_bbands_bought"] == False:

            quota = parity['rsi_bbands_quota']
            amount = state["rsi_bbands_bought_amount"]
            await logger.save({"zone":"buy", "bbands": lowerband, "rsi": rsi_value, "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands"})
            await telegram_bot_sendtext(f"* {parity['symbol']}-{parity['interval']} - RSI-BBANDS - LIMIT BUY ORDER COMPLETED* Buy Price = {close}, Amount = {amount}", True)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_bought', state, True)

        # sell if price is higher than sell price
        if close >= state["rsi_bbands_sell_price"] and state["rsi_bbands_bought"] == True:

            logging.info(
                f"selling for rsi_bbands -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['rsi_bbands_quota']
            amount = state["rsi_bbands_bought_amount"]
            await logger.save({"zone":"sell","bbands": lowerband, "rsi": rsi_value, "price": close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands"})
            await telegram_bot_sendtext(f"* {parity['symbol']}-{parity['interval']} - RSI-BBANDS - LIMIT SELL ORDER COMPLETED * Sell Price = {close}, Amount = {amount}", True)

            state = update_state_file_and_state(
                file_name, 'rsi_bbands_bought', state, False)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_bought_amount', state, 0)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_buy_price', state, 0)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_sell_price', state, 0)
            state = update_state_file_and_state(
                file_name, 'rsi_bbands_has_ordered', state, False)
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
