from logger import Logger

parity = {
    "is_parity_active": True,
    "symbol": "BTCUSDT",
    "interval": "1h",
    "start": "40 hours ago UTC",
    "rsi": True,
    "lower_rsi_bounds": [30,20],
    "upper_rsi_bounds": [80],
    "rsi_states": ["h1","n","l1","l2"],
    "pmax": True,
    "bbands": True,
    "atr_multiplier": 3,
    "moving_average": "sma",
    "atr_length": 10,
    "ma_length": 9,
    "pmax_states": ["l", "p", "n"],
    "pmax_percantage": 1.01
}

logger = Logger(parity)
logger.log_notification({"indicator": "bbands"})