import os
import json
from datetime import datetime
from dotenv import load_dotenv
import asyncio

load_dotenv()

LOG_PATH = os.getenv("LOG_PATH")

class Logger:
    def __init__(self, parity: str):
        self.parity = parity
        self.main_path = f'{LOG_PATH}/{self.parity}'
        self.summary_path = f'{LOG_PATH}/summary.json'
        
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)
        
        if not os.path.exists(self.summary_path):
            with open(self.summary_path, 'w') as file:
                json.dump({}, file)
        
    async def save(self, data):
        ts = int(datetime.now().timestamp())
        file_name = f'{self.main_path}.json'

        data['timestamp'] = ts

        async with asyncio.Lock():
            if os.path.exists(file_name):
                with open(file_name, 'r') as file:
                    existing_data = json.load(file)
            else:
                existing_data = []

            existing_data.append(data)

            with open(file_name, 'w') as file:
                json.dump(existing_data, file, indent=2)

            # Update tx count for parity in summary.json
            summary_data = {}
            if os.path.exists(self.summary_path):
                with open(self.summary_path, 'r') as file:
                    summary_data = json.load(file)

            # Update summary data for the current parity
            if self.parity not in summary_data:
                summary_data[self.parity] = {"total": 0}

            summary_data[self.parity]["total"] += 1

            # Update strategy-specific counts if provided
            if 'strategy' in data:
                strategy_name = data['strategy']
                if strategy_name not in summary_data[self.parity]:
                    summary_data[self.parity][strategy_name] = 0
                summary_data[self.parity][strategy_name] += 1

            with open(self.summary_path, 'w') as file:
                json.dump(summary_data, file, indent=2)


# test it out
if __name__ == "__main__":
    logger = Logger("BTCUSDT-1m")
    asyncio.run(logger.save({"zone": "buy", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading"}))
    asyncio.run(logger.save({"zone": "sell", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading"}))
    asyncio.run(logger.save({"zone": "buy", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading_alt"}))
    asyncio.run(logger.save({"zone": "sell", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading_alt"}))
    asyncio.run(logger.save({"zone": "buy", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading"}))
    asyncio.run(logger.save({"zone": "sell", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading"}))
    asyncio.run(logger.save({"zone": "buy", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading_alt"}))
    logger = Logger("BTCUSDT-15m")
    asyncio.run(logger.save({"zone": "sell", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading_alt"}))
    asyncio.run(logger.save({"zone": "buy", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading"}))
    asyncio.run(logger.save({"zone": "sell", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading"}))
    asyncio.run(logger.save({"zone": "buy", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading_alt"}))
    asyncio.run(logger.save({"zone": "sell", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading_alt"}))
    asyncio.run(logger.save({"zone": "buy", "price": 1, "amount": 1, "quota": 1, "strategy": "rsi_trading"}))
