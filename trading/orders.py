import os
import json
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import uuid
from utils import update_update_file, telegram_bot_sendtext, initialize_parities, initialize_state_files, read_state_file, update_state_file_and_state

load_dotenv()

ORDER_PATH = os.getenv("ORDER_PATH")

class Orders:
    def __init__(self, parity: str):
        self.parity = parity
        self.main_path = f'{ORDER_PATH}'
        self.completed_path = f'{ORDER_PATH}/completed.json'
        self.cancelled_path = f'{ORDER_PATH}/cancelled.json'
        self.open_path = f'{ORDER_PATH}/open.json'

        if not os.path.exists(ORDER_PATH):
            os.mkdir(ORDER_PATH)
        
        if not os.path.exists(self.completed_path):
            with open(self.completed_path, 'w') as file:
                json.dump([], file, indent=2)

        if not os.path.exists(self.cancelled_path):
            with open(self.cancelled_path, 'w') as file:
                json.dump([], file, indent=2)

        if not os.path.exists(self.open_path):
            with open(self.open_path, 'w') as file:
                json.dump([], file, indent=2)

    async def create_order(self, amount, price, action, strategy, market_type, id):
        ts = int(datetime.now().timestamp())
        file_name = f'{self.open_path}'
        data = {
            'timestamp': ts,
            'symbol': self.parity["symbol"],
            'interval': self.parity["interval"],
            'amount': amount,
            'market_type': market_type,
            'price': price,
            'action': action,
            'trade_id': 0,
            'strategy': strategy,
            'id': id
        }

        async with asyncio.Lock():

            with open(file_name, 'r') as file:
                existing_data = json.load(file)

            existing_data.append(data)

            with open(file_name, 'w') as file:
                json.dump(existing_data, file, indent=2)

    async def complete_order(self, id):
        file_name = f'{self.open_path}'
        completed_path = f'{self.completed_path}'

        async with asyncio.Lock():

            with open(file_name, 'r') as file:
                existing_data = json.load(file)

            for order in existing_data:
                if order['id'] == id:
                    with open(completed_path, 'r') as file:
                        completed_data = json.load(file)
                    with open(completed_path, 'w') as file:
                        completed_data.append(order)
                        json.dump(completed_data, file, indent=2)
        # remove from open
        with open(file_name, 'w') as file:
            json.dump([order for order in existing_data if order['id'] != id], file, indent=2)

    async def cancel_order(self, id):
        file_name = f'{self.open_path}'
        cancelled_path = f'{self.cancelled_path}'

        async with asyncio.Lock():

            with open(file_name, 'r') as file:
                existing_data = json.load(file)

            for order in existing_data:
                if order['id'] == id:
                    with open(cancelled_path, 'r') as file:
                        cancelled_data = json.load(file)
                    with open(cancelled_path, 'w') as file:
                        cancelled_data.append(order)
                        json.dump(cancelled_data, file, indent=2)
                    update_update_file(self.parity["symbol"], True)
                    if order["strategy"] == "pmax_bbands":
                        await telegram_bot_sendtext(f"* {order['symbol']}-{order['interval']} - PMAX-BBANDS - ORDER CANCELLED* Order ID = {id}", True)
                        state = update_state_file_and_state(file_name, 'pmax_bbands_buy_id', state, "")
                        state = update_state_file_and_state(file_name, 'pmax_bbands_bought', state, False)
                        state = update_state_file_and_state(file_name, 'pmax_bbands_buy_price', state, 0)
                        state = update_state_file_and_state(file_name, 'pmax_bbands_sell_price', state, 0)
                        state = update_state_file_and_state(file_name, 'pmax_bbands_bought_amount', state, 0)
                        state = update_state_file_and_state(file_name, 'pmax_bbands_has_ordered', state, False)
                        state = update_state_file_and_state(file_name, 'pmax_bbands_sell_id', state, "")
                    if order["strategy"] == "rsi_trading":
                        await telegram_bot_sendtext(f"* {order['symbol']}-{order['interval']} - RSI-TRADING - ORDER CANCELLED* Order ID = {id}", True)
                        state = update_state_file_and_state(file_name, 'rsi_trading_bought', state,False)
                        state = update_state_file_and_state(file_name, 'rsi_trading_buy_price', state,0)
                        state = update_state_file_and_state(file_name, 'rsi_trading_bought_amount', state,0)
                    if order["strategy"] == "rsi_trading_alt":
                        await telegram_bot_sendtext(f"* {order['symbol']}-{order['interval']} - RSI-TRADING-ALT - ORDER CANCELLED* Order ID = {id}", True)
                        state = update_state_file_and_state(file_name, 'rsi_trading_alt_bought', False)
                        state = update_state_file_and_state(file_name, 'rsi_trading_alt_buy_price', 0)
                        state = update_state_file_and_state(file_name, 'rsi_trading_alt_bought_amount', 0)
                    if order["strategy"] == "rsi_bbands":
                        await telegram_bot_sendtext(f"* {order['symbol']}-{order['interval']} - RSI-BBANDS - ORDER CANCELLED* Order ID = {id}", True)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought', state, False)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought_amount', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_has_ordered', state, False)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_id', state, "")
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_id', state, "")  
                    if order["strategy"] == "rsi_bbands_alt":
                        await telegram_bot_sendtext(f"* {order['symbol']}-{order['interval']} - RSI-BBANDS-ALT - ORDER CANCELLED* Order ID = {id}", True)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought', state, False)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_bought_amount', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_price', state, 0)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_has_ordered', state, False)
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_sell_id', state, "")
                        state = update_state_file_and_state(file_name, 'rsi_bbands_alt_buy_id', state, "")

        # remove from open
        with open(file_name, 'w') as file:
            json.dump([order for order in existing_data if order['id'] != id], file, indent=2)
        
if __name__ == "__main__":
    parities, file_names = initialize_parities()
    initialize_state_files(file_names),
    state = read_state_file(file_names[2])
    parity = parities[2]
    orders = Orders(parity)
    id = str(uuid.uuid4())
    asyncio.run(orders.create_order(1, 2, 'buy', 'demo_strat2', 'limit', id))
    #id = "d5d7002d-4793-4148-9cd6-ee697b759d4c"
    asyncio.run(orders.complete_order(id))