import logging
from utils import  get_amount_to_buy, update_state_file_and_state, telegram_bot_sendtext

async def pmax_bbands(parity, state, file_name, logger, zone, lowerband, pmax, close):

    if parity["pmax_bbands"] == True and parity["pmax"] == True and parity["bbands"] == True:


        if zone == "up" and lowerband >= pmax and state["pmax_bbands_has_ordered"] == False:

            buy, sell = parity["rsi_bbands_percentages"][0], parity["rsi_bbands_percentages"][1]
            buy_price = pmax * buy
            sell_price = pmax * sell
            logging.info(f"buying for pmax_bbands -> pmax -> {pmax}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['pmax_bbands_quota']
            amount = get_amount_to_buy(quota, parity['symbol'])
            await logger.save({"bbands": lowerband, "pmax": pmax, "price":close, "amount": amount, "quota": quota,  "strategy": "pmax_bbands"})
            await telegram_bot_sendtext(f"*PMAX-BBANDS - LIMIT BUY ORDER - {parity['symbol']}-{parity['interval']}* Buy Price = {buy_price}, Amount = {amount}%0A%0A*PMAX-BBANDS - LIMIT SELL ORDER - {parity['symbol']}-{parity['interval']}* Sell Price = {sell_price}, Amount = {amount}", True)
            
            state = update_state_file_and_state(file_name, 'pmax_bbands_has_ordered', state, True)
            state = update_state_file_and_state(file_name, 'pmax_bbands_bought_amount', state, amount)
            state = update_state_file_and_state(file_name, 'pmax_bbands_buy_price', state, buy_price)
            state = update_state_file_and_state(file_name, 'pmax_bbands_sell_price', state, sell_price)

        if close <= state["pmax_bbands_buy_price"] and state["pmax_bbands_has_ordered"] == True:
            quota = parity['pmax_bbands_quota']
            amount = state["pmax_bbands_bought_amount"]
            await logger.save({"bbands": lowerband, "pmax": pmax, "price":close, "amount": amount, "quota": quota,  "strategy": "pmax_bbands"})
            await telegram_bot_sendtext(f"*PMAX-BBANDS - LIMIT BUY ORDER COMPLETED - {parity['symbol']}-{parity['interval']}* Buy Price = {close}, Amount = {amount}", True)
            state = update_state_file_and_state(file_name, 'pmax_bbands_bought', state, True)

        if close >= state["pmax_bbands_sell_price"] and state["pmax_bbands_bought"] == True:

            logging.info(f"selling for pmax_bbands -> pmax -> {pmax}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
            quota = parity['pmax_bbands_quota']
            amount = state["pmax_bbands_bought_amount"]
            await logger.save({"bbands": lowerband, "pmax": pmax, "price":close, "amount": amount, "quota": quota,  "strategy": "pmax_bbands"})
            await telegram_bot_sendtext(f"*PMAX-BBANDS - SELL - {parity['symbol']}-{parity['interval']}* Sell Price = {close}, Amount = {amount}", True)
            
            state = update_state_file_and_state(file_name, 'pmax_bbands_bought', state, False)
            state = update_state_file_and_state(file_name, 'pmax_bbands_bought_amount', state, 0)
            state = update_state_file_and_state(file_name, 'pmax_bbands_buy_price', state, 0)
            state = update_state_file_and_state(file_name, 'pmax_bbands_sell_price', state, 0)
            state = update_state_file_and_state(file_name, 'pmax_bbands_has_ordered', state, False)
    
    return state
            