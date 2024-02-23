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
        order = await client.create_order(
            symbol='BNBUSDT',
            side=AsyncClient.SIDE_BUY,
            type=AsyncClient.ORDER_TYPE_MARKET,
            #timeInForce=AsyncClient.TIME_IN_FORCE_GTC,
            quantity=0.05,
            #price='373.8000',
        )

        # print(order)
        # CANCEL ORDER
        # result = await client.cancel_order(
        #     symbol='BNBUSDT',
        #     orderId='5047831583',
        # )

        # print(result)
        #check order status
        # order = await client.get_my_trades(
        #     symbol='BNBUSDT',
        #     orderId='5047865079',
        # )
        print(order)

    except Exception as e:
        print(traceback.format_exc())
    finally:
        # close the client session and connector
        await client.close_connection()

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
