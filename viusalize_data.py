import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

CHUNK_SIZE = 50

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

# Initialize Dash app
app = dash.Dash(__name__)

# Initial chunk index
current_chunk_index = 0

# Define layout
app.layout = html.Div(style={'backgroundColor': '#f2f2f2', 'padding': '20px'}, children=[
    html.Button('Next Chunk', id='next-button', n_clicks=0),
    dcc.Graph(
        id='candlestick-chart',
        figure={
            'data': [
                go.Candlestick(x=df['open_time'].iloc[:CHUNK_SIZE],
                               open=df['open'].iloc[:CHUNK_SIZE],
                               high=df['high'].iloc[:CHUNK_SIZE],
                               low=df['low'].iloc[:CHUNK_SIZE],
                               close=df['close'].iloc[:CHUNK_SIZE],
                               name='market data')
            ],
            'layout': {
                'title': f'{SYMBOL} - {INTERVAL} Candlesticks',
                'yaxis_title': f'{SYMBOL} Price',
                'plot_bgcolor': '#ffffff',  # Set the plot background color
                'paper_bgcolor': '#f2f2f2',  # Set the overall paper background color
                'height': 600,  # Set the height of the chart
            }
        }
    ),
])

# Callback to update the chart data on button click
@app.callback(
    Output('candlestick-chart', 'figure'),
    [Input('next-button', 'n_clicks')]
)
def update_data(n_clicks):
    global current_chunk_index

    # Calculate the start and end indices for the current chunk
    start_index = current_chunk_index * CHUNK_SIZE
    end_index = (current_chunk_index + 1) * CHUNK_SIZE

    # Slice the DataFrame to get the data for the current chunk
    chunk_df = df.iloc[start_index:end_index]

    # Increment the chunk index for the next click
    current_chunk_index += 1

    # If the end of the DataFrame is reached, reset the chunk index
    if end_index >= len(df):
        current_chunk_index = 0

    # Update the chart figure
    figure = {
        'data': [
            go.Candlestick(x=chunk_df['open_time'],
                           open=chunk_df['open'],
                           high=chunk_df['high'],
                           low=chunk_df['low'],
                           close=chunk_df['close'],
                           name='market data')
        ],
        'layout': {
            'title': f'{SYMBOL} - {INTERVAL} Candlesticks Chuck {current_chunk_index} of {len(df) // CHUNK_SIZE}',
            'yaxis_title': f'{SYMBOL} Price',
            'plot_bgcolor': '#ffffff',  # Set the plot background color
            'paper_bgcolor': '#f2f2f2'  # Set the overall paper background color
        }
    }

    return figure

# Run app and display result inline in the notebook
if __name__ == '__main__':
    app.run_server(debug=True)
