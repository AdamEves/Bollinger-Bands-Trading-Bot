from flask import Flask, jsonify
from binance import Client
import numpy as np
import pandas as pd

# Set up Binance API credentials
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

# Create a Binance client
client = Client(api_key, api_secret)

# Set up Flask server
app = Flask(__name__)
port = 3000

# Define the symbol and time frame
symbol = 'BTCUSDT'
timeframe = '1d'

# Define Bollinger Bands parameters
period = 20
stdDev = 2

# Function to calculate Bollinger Bands
def calculateBollingerBands(closes):
    rolling_mean = closes.rolling(window=period).mean()
    rolling_std = closes.rolling(window=period).std()
    upperBand = rolling_mean + (rolling_std * stdDev)
    middleBand = rolling_mean
    lowerBand = rolling_mean - (rolling_std * stdDev)
    return upperBand, middleBand, lowerBand

# Route to fetch Bollinger Bands data
@app.route('/api/bollinger-bands')
def getBollingerBands():
    try:
        # Fetch historical OHLCV data
        candles = client.get_historical_klines(symbol, timeframe, period + 1)

        # Extract close prices from the candles
        closes = pd.DataFrame(candles, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        closes = closes['Close'].astype(float)

        # Calculate Bollinger Bands
        upperBand, middleBand, lowerBand = calculateBollingerBands(closes)

        # Prepare the response
        response = {
            'upperBand': upperBand.tolist(),
            'middleBand': middleBand.tolist(),
            'lowerBand': lowerBand.tolist()
        }

        # Log successful connection to Binance
        print('Connected to Binance successfully')

        # Send the response
        return jsonify(response)
    except Exception as e:
        print('Error fetching Bollinger Bands data:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

# Function to place a trade (example implementation, modify as needed)
def placeTrade():
    try:
        # Place your trade logic here

        # Log successful trade placement
        print('Trade placed successfully')
    except Exception as e:
        print('Error placing trade:', e)

# Example route to place a trade
@app.route('/api/place-trade')
def placeTradeRoute():
    placeTrade()
    return jsonify({'message': 'Trade placed'})

# Start the server
if __name__ == '__main__':
    # Log server start
    print('Server is running on port', port)
    app.run(port=port)
