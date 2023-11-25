import plotly.graph_objects as go
import pandas as pd

# Load data from data.csv
try:
    df = pd.read_csv('data.csv')
except:
    print('Could not load data.csv')
    exit()

# Get symbol and interval from .data_settings
try:
    with open('.data_settings', 'r') as f:
        data_settings = f.read().split(',')
        SYMBOL = data_settings[0]
        INTERVAL = data_settings[1]
except:
    print('Could not load .data_settings')
    exit()
    
# Convert unix timestamps to datetime
df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

# Create figure
fig = go.Figure()

# Candlestick
fig.add_trace(go.Candlestick(x=df['open_time'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'], name = 'market data'))

# Add titles
fig.update_layout(
    title=f'{SYMBOL} - {INTERVAL} Candlesticks',
    yaxis_title=f'{SYMBOL} Price')

# Show
fig.show()

