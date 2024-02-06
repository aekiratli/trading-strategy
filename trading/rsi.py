from utils import get_amount_to_buy, telegram_bot_sendtext, update_state_file
import logging

async def rsi_trading(parity, state, file_name, logger, rsi_value, close):

            if parity["rsi_trading"] == True and parity["rsi"] == True:

                if rsi_value <= parity["rsi_trading_buy_limit"] and state["rsi_trading_bought"] == False:
                        
                        logging.info(f"buying for rsi_trading -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                        quota = parity['rsi_trading_quota']
                        amount = get_amount_to_buy(quota, parity['symbol'])
                        await logger.save({"zone": "buy", "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_trading"})
                        await telegram_bot_sendtext(f"*RSI - MARKET BUY - {parity['symbol']}-{parity['interval']}* Price = {close}, Amount = {amount}, RSI = {rsi_value}%0A%0ARSI - LIMIT ORDER SELL - {parity['symbol']}-{parity['interval']}* Price = {state['rsi_trading_buy_price'] * parity['rsi_trading_sell_percentage'] }, Amount = {amount}", True)
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
                        await telegram_bot_sendtext(f"*RSI - LIMIT SELL ORDER COMPLETED - {parity['symbol']}-{parity['interval']}* Price = {close}, Amount = {amount}", True)
                        state["rsi_trading_bought"] = False
                        state["rsi_trading_buy_price"] = 0
                        state["rsi_trading_bought_amount"] = 0
                        update_state_file(file_name, 'rsi_trading_bought', False)
                        update_state_file(file_name, 'rsi_trading_buy_price', 0)
                        update_state_file(file_name, 'rsi_trading_bought_amount', 0)
            return state

async def rsi_trading_alt(parity, state, file_name, logger, rsi_value, close):
    if parity["rsi_trading_alt"] == True and parity["rsi"] == True:

                    if rsi_value <= parity["rsi_trading_alt_buy_limit"] and state["rsi_trading_alt_bought"] == False:
                            
                            logging.info(f"buying for -> rsi_value -> {rsi_value}, symbol -> {parity['symbol']}, interval -> {parity['interval']}, close -> {close}")
                            quota = parity['rsi_trading_quota']
                            amount = get_amount_to_buy(quota, parity['symbol'])
                            await logger.save({"zone": "buy", "price":close, "amount": amount, "quota": quota,  "strategy": "rsi_alt_trading"})
                            await telegram_bot_sendtext(f"*RSI ALT - MARKET BUY - {parity['symbol']}-{parity['interval']}* Price = {close}, Amount = {amount}, RSI = {rsi_value}%0A%0ARSI ALT - LIMIT ORDER SELL - {parity['symbol']}-{parity['interval']}* Price = {state['rsi_trading_buy_price'] * parity['rsi_trading_sell_percentage'] }, Amount = {amount}", True)
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
                            await telegram_bot_sendtext(f"*RSI ALT - LIMIT SELL ORDER COMPLETED - {parity['symbol']}-{parity['interval']}* Price = {close}, Amount = {amount}", True)
                            state["rsi_trading_alt_bought"] = False
                            state["rsi_trading_alt_buy_price"] = 0
                            state["rsi_trading_alt_bought_amount"] = 0
                            update_state_file(file_name, 'rsi_trading_alt_bought', False)
                            update_state_file(file_name, 'rsi_trading_alt_buy_price', 0)
                            update_state_file(file_name, 'rsi_trading_alt_bought_amount', 0)

    return state