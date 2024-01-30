import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = os.getenv("LOG_PATH")

class Logger:
    def __init__(self, parity: str):
        self.parity = parity
        self.main_path = f'{LOG_PATH}/{self.parity}'
        # Create the main folder and parent directories if they don't exist
        os.makedirs(self.main_path, exist_ok=True)

    def save(self, data, strategy: str):
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')   
        strategy_path = f'{self.main_path}/{strategy}'
        file_path = f'{strategy_path}/{ts}.json'

        # Create the strategy folder if it doesn't exist
        os.makedirs(strategy_path, exist_ok=True)

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)