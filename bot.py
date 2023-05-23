from flask import Flask, jsonify
from binance import Client
import numpy as np
import pandas as pd
import os

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

# Function to place a trade using Bollinger Bands strategy
def placeTrade():
    try:
        # Fetch historical OHLCV data
        candles = client.get_historical_klines(symbol, timeframe, period + 2)

        # Extract close prices from the candles
        closes = pd.DataFrame(candles, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        closes = closes['Close'].astype(float)

        # Calculate Bollinger Bands
        upperBand, middleBand, lowerBand = calculateBollingerBands(closes)

        # Get the current price
        current_price = closes.iloc[-1]

        # Get the previous upper band and lower band values
        previous_upper_band = upperBand.iloc[-2]
        previous_lower_band = lowerBand.iloc[-2]

        # Get the current upper band and lower band values
        current_upper_band = upperBand.iloc[-1]
        current_lower_band = lowerBand.iloc[-1]

        # Check if the price crossed above the upper band
        if current_price > previous_upper_band and current_price < current_upper_band:
            # Place a buy trade here
            # Replace with your buy trade logic
            quantity = 0.001  # Example quantity to buy
            order = client.create_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=quantity
            )
            print('Buy trade placed at price:', current_price)
            print('Order response:', order)

        # Check if the price crossed below the lower band
        if current_price < previous_lower_band and current_price > current_lower_band:
            # Place a sell trade here
            # Replace with your sell trade logic
            quantity = 0.001  # Example quantity to sell
            order = client.create_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity
            )
            print('Sell trade placed at price:', current_price)
            print('Order response:', order)

    except Exception as e:
        print('Error placing trade:', e)

# Example route to place a trade
@app.route('/api/place-trade')
def placeTradeRoute():
    placeTrade()
    print('Trade placed')
    return jsonify({'message': 'Trade placed'})

# Prompt for API keys on launch and save them in a separate file
def promptForAPIKeys():
    api_key = input('Enter your Binance API key: ')
    api_secret = input('Enter your Binance API secret: ')

    # Save API keys to a separate file
    with open('api_keys.txt', 'w') as f:
        f.write(f'API_KEY={api_key}\n')
        f.write(f'API_SECRET={api_secret}\n')

    return api_key, api_secret

# Load API keys from the separate file
def loadAPIKeys():
    with open('api_keys.txt', 'r') as f:
        lines = f.readlines()
        api_key = lines[0].strip().split('=')[1]
        api_secret = lines[1].strip().split('=')[1]
    return api_key, api_secret

# Start the server
if __name__ == '__main__':
    if os.path.exists('api_keys.txt'):
        # Load API keys from the separate file
        api_key, api_secret = loadAPIKeys()
    else:
        # Prompt for API keys on first launch
        api_key, api_secret = promptForAPIKeys()

    # Create a Binance client
    client = Client(api_key, api_secret)

    # Log server start
    print('Server is running on port', port)
    app.run(port=port)
