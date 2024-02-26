# async client
from binance.client import AsyncClient
import asyncio
from dotenv import load_dotenv
import os
import traceback

# load the environment variables
load_dotenv()
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

async def main():

    # initialise the client
    client = await AsyncClient.create(BINANCE_API_KEY, BINANCE_API_SECRET)
    try:
        resp = await client.get_symbol_info('BNBUSDT')
        amount = 0.6149
        price = 390.2896
        tick_size = float(resp['filters'][0]['tickSize'])
        step_size = float(resp['filters'][1]['stepSize'])
        print(f"tick size: {tick_size}, step size: {step_size}")

        amount = round(amount / step_size) * step_size
        price = round(price / tick_size) * tick_size
        print(f"amount: {amount}, price: {price}")

    except Exception as e:
        print(traceback.format_exc())
    finally:
        # close the client session and connector
        await client.close_connection()

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
