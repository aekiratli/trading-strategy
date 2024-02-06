import logging
from utils import  get_amount_to_buy, update_state_file_and_state, telegram_bot_sendtext

async def rsi_bbands_alt(parity, state, file_name, logger, lowerband, rsi_value, close):
     if parity["rsi_bbands_alt"] == True and parity["rsi"] == True and parity["bbands"] == True:

                if rsi_value <= parity["rsi_bbands_alt_buy_limit"] and close > lowerband and state["rsi_bbands_alt_has_ordered"] == False:
                        
                        buy, sell = parity["rsi_bbands_alt_percentages"][0], parity["rsi_bbands_alt_percentages"][1]
                        buy_price = close * buy
                        sell_price = close * sell
                        logging.info(f"buying for rsi_bbands -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_bbands_alt_quota']
                        amount = get_amount_to_buy(quota, parity['symbol'])
                        await telegram_bot_sendtext(f"*RSI-BBANDS-ALT - LIMIT BUY ORDER- {parity['symbol']}-{parity['interval']}* Buy Price = {buy_price}, Amount = {amount}%0A%0A*RSI-BBANDS-ALT - LIMIT SELL ORDER - {parity['symbol']}-{parity['interval']}* Sell Price = {sell_price}, Amount = {amount}", True)
                        
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_alt_bought_amount', state, amount)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_price', state, buy_price)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_price', state, sell_price)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_alt_has_ordered', state, True)

                if close <= state["rsi_bbands_alt_buy_price"] and state["rsi_bbands_alt_has_ordered"] == True:
                            
                            quota = parity['rsi_bbands_alt_quota']
                            amount = state["rsi_bbands_alt_bought_amount"]
                            await logger.save({"bbands": lowerband, "rsi": rsi_value , "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_trading"})
                            await telegram_bot_sendtext(f"*RSI-BBANDS-ALT - LIMIT BUY ORDER COMPLETED - {parity['symbol']}-{parity['interval']}* Sell Price = {close}, Amount = {amount}", True)
                            state =  update_state_file_and_state(file_name, 'rsi_bbands_alt_bought', state, True)

                # sell if price is higher than sell price
                if close >= state["rsi_bbands_alt_sell_price"] and state["rsi_bbands_alt_bought"] == True:
                        
                        logging.info(f"selling for rsi_bbands_alt -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_bbands_alt_quota']
                        amount = state["rsi_bbands_alt_bought_amount"]
                        await logger.save({"bbands": lowerband, "rsi":rsi_value , "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_trading"})
                        await telegram_bot_sendtext(f"*RSI-BBANDS-ALT - LIMIT SELL ORDER COMPLETED - {parity['symbol']}-{parity['interval']}* Sell Price = {close}, Amount = {amount}", True)

                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought', state, False)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought_amount', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_has_ordered', state, False)
     return state

async def rsi_bbands(parity, state, file_name, logger, rsi_value, close, lowerband):
            if parity["rsi_bbands"] == True and parity["rsi"] == True and parity["bbands"] == True:

                if rsi_value <= parity["rsi_bbands_buy_limit"] and close > lowerband and state["rsi_bbands_has_ordered"] == False:
                        
                        buy, sell = parity["rsi_bbands_percentages"][0], parity["rsi_bbands_percentages"][1]
                        buy_price = close * buy
                        sell_price = close * sell
                        logging.info(f"buying for rsi_bbands -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_bbands_quota']
                        amount = get_amount_to_buy(quota, parity['symbol'])
                        await telegram_bot_sendtext(f"*RSI-BBANDS - LIMIT BUY ORDER- {parity['symbol']}-{parity['interval']}* Buy Price = {buy_price}, Amount = {amount}%0A%0A*RSI-BBANDS - LIMIT SELL ORDER - {parity['symbol']}-{parity['interval']}* Sell Price = {sell_price}, Amount = {amount}", True)
                        
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_bought_amount', state, amount)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_buy_price', state, buy_price)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_sell_price', state, sell_price)
                        state =  update_state_file_and_state(file_name, 'rsi_bbands_has_ordered', state, True)

                if close <= state["rsi_bbands_buy_price"] and state["rsi_bbands_has_ordered"] == True:
                            
                            quota = parity['rsi_bbands_quota']
                            amount = state["rsi_bbands_bought_amount"]
                            await logger.save({"bbands": lowerband, "rsi": rsi_value , "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_trading"})
                            await telegram_bot_sendtext(f"*RSI-BBANDS - LIMIT BUY ORDER COMPLETED - {parity['symbol']}-{parity['interval']}* Sell Price = {close}, Amount = {amount}", True)
                            state =  update_state_file_and_state(file_name, 'rsi_bbands_bought', state, True)

                # sell if price is higher than sell price
                if close >= state["rsi_bbands_sell_price"] and state["rsi_bbands_bought"] == True:
                        
                        logging.info(f"selling for rsi_bbands -> rsi_value -> {rsi_value}, bbands -> {lowerband}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_bbands_quota']
                        amount = state["rsi_bbands_bought_amount"]
                        await logger.save({"bbands": lowerband, "rsi":rsi_value , "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_bbands_trading"})
                        await telegram_bot_sendtext(f"*RSI-BBANDS - LIMIT SELL ORDER COMPLETED - {parity['symbol']}-{parity['interval']}* Sell Price = {close}, Amount = {amount}", True)

                        state = update_state_file_and_state(file_name, 'rsi_bbands_bought', state, False)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_bought_amount', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_buy_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_sell_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_has_ordered', state, False)
            return state
           