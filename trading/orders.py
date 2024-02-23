import os
import json
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import uuid
from utils import *
from binance.client import AsyncClient

load_dotenv()

ORDER_PATH = os.getenv("ORDER_PATH")

class Orders:
    def __init__(self, parity: str, client: AsyncClient):
        self.parity = parity
        self.client = client
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
        # use 4 decimal places for the price and amount
        price = round(price, 4)
        amount = round(amount, 4)
        order_data = {
            'symbol': self.parity["symbol"],
            'side': AsyncClient.SIDE_BUY if action == 'buy' else AsyncClient.SIDE_SELL,
            'type': AsyncClient.ORDER_TYPE_LIMIT if market_type == 'limit' else AsyncClient.ORDER_TYPE_MARKET,
            'quantity': amount,
        }

        if market_type == 'limit':
            order_data['timeInForce'] = AsyncClient.TIME_IN_FORCE_GTC
            order_data['price'] = price

        order = await self.client.create_order(**order_data)
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

        # create a log file with the following folder structure
        # <year>/<month>/<date>/<id>/created.json

        # get current year, month and date
        current_year = datetime.now().strftime('%Y')
        current_month = datetime.now().strftime('%m')
        current_date = datetime.now().strftime('%d')

        # create year, month, date and id directories if they don't exist
        year_path = f'{self.main_path}/{current_year}'
        month_path = f'{year_path}/{current_month}'
        date_path = f'{month_path}/{current_date}'
        id_path = f'{date_path}/{id}'

        for dir_path in [year_path, month_path, date_path, id_path]:
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

        # create the log file
        log_file = f'{id_path}/created.json'
        with open(log_file, 'w') as file:
            json.dump({"created": True}, file, indent=2)

        async with asyncio.Lock():

            with open(file_name, 'r') as file:
                existing_data = json.load(file)

            existing_data.append(data)

            with open(file_name, 'w') as file:
                json.dump(existing_data, file, indent=2)

    async def complete_order(self, id):
        file_name = f'{self.open_path}'
        completed_path = f'{self.completed_path}'

        current_year = datetime.now().strftime('%Y')
        current_month = datetime.now().strftime('%m')
        current_date = datetime.now().strftime('%d')

        # create year, month, date and id directories if they don't exist
        year_path = f'{self.main_path}/{current_year}'
        month_path = f'{year_path}/{current_month}'
        date_path = f'{month_path}/{current_date}'
        id_path = f'{date_path}/{id}'

        for dir_path in [year_path, month_path, date_path, id_path]:
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

        # create the log file
        log_file = f'{id_path}/completed.json'
        with open(log_file, 'w') as file:
            json.dump({"completed": True}, file, indent=2)
            
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

        current_year = datetime.now().strftime('%Y')
        current_month = datetime.now().strftime('%m')
        current_date = datetime.now().strftime('%d')

        # create year, month, date and id directories if they don't exist
        year_path = f'{self.main_path}/{current_year}'
        month_path = f'{year_path}/{current_month}'
        date_path = f'{month_path}/{current_date}'
        id_path = f'{date_path}/{id}'

        for dir_path in [year_path, month_path, date_path, id_path]:
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

        # create the log file
        log_file = f'{id_path}/cancelled.json'
        with open(log_file, 'w') as file:
            json.dump({"cancelled": True}, file, indent=2)

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