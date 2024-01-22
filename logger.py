import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv() 

LOG_PATHS = {
    "RSI": os.getenv("RSI_LOG_PATH"),
    "PMAX": os.getenv("PMAX_LOG_PATH"),
    "BBANDS": os.getenv("BBANDS_LOG_PATH"),
}

for path in LOG_PATHS.values():
    if not os.path.exists(path):
        os.makedirs(path)

class Logger:
    def __init__(self, parity):
        self.parity = parity
        symbol = parity["symbol"]
        interval = parity["interval"]
        folder_name = symbol + "_" + interval

        self.log_folders = {key: os.path.join(path, folder_name) for key, path in LOG_PATHS.items()}
        for folder_path in self.log_folders.values():
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

    def create_folder(self):
        timestamp = int(datetime.now().timestamp())
        year = datetime.fromtimestamp(timestamp).strftime('%Y')
        month = datetime.fromtimestamp(timestamp).strftime('%m')
        day = datetime.fromtimestamp(timestamp).strftime('%d')
        folder_name = year + '/' + month + '/' + day + '/'
        return folder_name
    
    def log_notification(self, notification):
        # indicator = notification["indicator"]
        # folder_name = self.create_folder()
        # for key, path in self.log_folders.items():
        #     if key in notification:
        #         with open(path + folder_name + "log.txt", "a") as f:
        #             f.write(str(notification) + "\n")
