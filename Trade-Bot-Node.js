const express = require('express');
const { Client } = require('binance-api-node');
const DataFrame = require('dataframe-js');
const { json } = require('express');

// Set up Express server
const app = express();
const port = 3000;

// Define the symbol and time frame
const symbol = 'BTCUSDT';
const timeframe = '1d';

// Define Bollinger Bands parameters
const period = 20;
const stdDev = 2;

// Create a Binance client
const client = new Client();

// Function to calculate Bollinger Bands
function calculateBollingerBands(closes) {
  const rolling_mean = closes.rollingMean(period);
  const rolling_std = closes.rollingStandardDeviation(period);
  const upperBand = rolling_mean.add(rolling_std.multiply(stdDev));
  const middleBand = rolling_mean;
  const lowerBand = rolling_mean.subtract(rolling_std.multiply(stdDev));
  return [upperBand, middleBand, lowerBand];
}

// Route to fetch Bollinger Bands data
app.get('/api/bollinger-bands', async (req, res) => {
  try {
    // Fetch historical OHLCV data
    const candles = await client.candles({ symbol, interval: timeframe, limit: period + 1 });

    // Extract close prices from the candles
    const closes = new DataFrame(candles.map(candle => parseFloat(candle.close)));

    // Calculate Bollinger Bands
    const [upperBand, middleBand, lowerBand] = calculateBollingerBands(closes);

    // Prepare the response
    const response = {
      upperBand: upperBand.toArray(),
      middleBand: middleBand.toArray(),
      lowerBand: lowerBand.toArray()
    };

    // Log successful connection to Binance
    console.log('Connected to Binance successfully');

    // Send the response
    res.json(response);
  } catch (error) {
    console.log('Error fetching Bollinger Bands data:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// Function to place a trade using Bollinger Bands strategy
async function placeTrade() {
  try {
    // Fetch historical OHLCV data
    const candles = await client.candles({ symbol, interval: timeframe, limit: period + 2 });

    // Extract close prices from the candles
    const closes = new DataFrame(candles.map(candle => parseFloat(candle.close)));

    // Calculate Bollinger Bands
    const [upperBand, middleBand, lowerBand] = calculateBollingerBands(closes);

    // Get the current price
    const current_price = closes.last().get(0);

    // Get the previous upper band and lower band values
    const previous_upper_band = upperBand.last(2).first().get(0);
    const previous_lower_band = lowerBand.last(2).first().get(0);

    // Get the current upper band and lower band values
    const current_upper_band = upperBand.last().first().get(0);
    const current_lower_band = lowerBand.last().first().get(0);

    // Check if the price crossed above the upper band
    if (current_price > previous_upper_band && current_price < current_upper_band) {
      // Place a buy trade here
      // Replace with your buy trade logic
      const quantity = 0.001;  // Example quantity to buy
      const order = await client.order({
        symbol,
        side: 'BUY',
        type: 'MARKET',
        quantity
      });
      console.log('Buy trade placed at price:', current_price);
      console.log('Order response:', order);
    }

    // Check if the price crossed below the lower band
    if (current_price < previous_lower_band && current_price > current_lower_band) {
      // Place a sell trade here
      // Replace with your sell trade logic
      const quantity = 0.001;  // Example quantity to sell
      const order = await client.order({
        symbol,
        side: 'SELL',
        type: 'MARKET',
        quantity
      });
      console.log('Sell trade placed at price:', current_price);
      console.log('Order response:', order);
    }
  } catch (error) {
    console.log('Error placing trade:', error);
  }
}

// Start the server
app.listen(port, () => {
  console.log('Server is running on port', port);
});
