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
        # create LOG_PATH if it doesn't exist
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

    async def save(self, data):
        # get timestamp as int
        ts = int(datetime.now().timestamp())
        file_name = f'{self.main_path}.json'

        # Add timestamp to data
        data['timestamp'] = ts

        async with asyncio.Lock():  # Use asyncio Lock to prevent concurrent access
            # Check if file exists
            if os.path.exists(file_name):
                # Read existing data from the file
                with open(file_name, 'r') as file:
                    existing_data = json.load(file)
            else:
                existing_data = []

            # Append new data to existing data
            existing_data.append(data)

            # Write the combined data back to the file
            with open(file_name, 'w') as file:
                json.dump(existing_data, file, indent=2)