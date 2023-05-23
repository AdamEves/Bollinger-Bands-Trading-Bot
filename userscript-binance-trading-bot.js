// ==UserScript==
// @name         Binance Bollinger Bands Strategy
// @namespace    http://your-namespace-url/
// @version      1.0
// @description  Automatically trades on Binance using Bollinger Bands strategy in the spot market
// @author       Your Name
// @match        https://www.binance.com/*
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(function() {
    'use strict';

    // Binance API endpoint for fetching historical OHLCV data
    const apiUrl = 'https://api.binance.com/api/v3/klines';

    // Bollinger Bands parameters
    const symbol = 'BTCUSDT';
    const timeframe = '1d';
    const period = 20;
    const stdDev = 2;

    // Place a trade using Bollinger Bands strategy
    async function placeTrade() {
        try {
            // Fetch historical OHLCV data from Binance API
            const response = await sendRequest(apiUrl, { symbol, interval: timeframe, limit: period + 2 });

            // Extract close prices from the response
            const candles = JSON.parse(response.responseText);
            const closes = candles.map(candle => parseFloat(candle[4]));

            // Calculate Bollinger Bands
            const [upperBand, middleBand, lowerBand] = calculateBollingerBands(closes);

            // Get the current price
            const currentPrice = closes[closes.length - 1];

            // Get the previous upper band and lower band values
            const previousUpperBand = upperBand[upperBand.length - 2];
            const previousLowerBand = lowerBand[lowerBand.length - 2];

            // Get the current upper band and lower band values
            const currentUpperBand = upperBand[upperBand.length - 1];
            const currentLowerBand = lowerBand[lowerBand.length - 1];

            // Check if the price crossed above the upper band
            if (currentPrice > previousUpperBand && currentPrice < currentUpperBand) {
                // Place a buy trade here
                // Replace with your buy trade logic
                console.log('Buy trade placed at price:', currentPrice);
            }

            // Check if the price crossed below the lower band
            if (currentPrice < previousLowerBand && currentPrice > currentLowerBand) {
                // Place a sell trade here
                // Replace with your sell trade logic
                console.log('Sell trade placed at price:', currentPrice);
            }
        } catch (error) {
            console.log('Error placing trade:', error);
        }
    }

    // Function to calculate Bollinger Bands
    function calculateBollingerBands(closes) {
        const rollingMean = [];
        const rollingStd = [];

        for (let i = 0; i < closes.length; i++) {
            if (i >= period) {
                const window = closes.slice(i - period, i);
                const mean = window.reduce((sum, value) => sum + value, 0) / period;
                const std = Math.sqrt(window.reduce((sum, value) => sum + Math.pow(value - mean, 2), 0) / period);
                rollingMean.push(mean);
                rollingStd.push(std);
            } else {
                rollingMean.push(null);
                rollingStd.push(null);
            }
        }

        const upperBand = rollingMean.map((mean, i) => mean + rollingStd[i] * stdDev);
        const middleBand = rollingMean;
        const lowerBand = rollingMean.map((mean, i) => mean - rollingStd[i] * stdDev);

        return [upperBand, middleBand, lowerBand];
    }

    // Function to send a GM_xmlhttpRequest
    function sendRequest(url, params) {
        return new Promise((resolve, reject) => {
            GM_xmlhttpRequest({
                method: 'GET',
                url: url + '?' + new URLSearchParams(params).toString(),
                onload: resolve,
                onerror: reject
            });
        });
    }

    // Execute the strategy on page load
    window.addEventListener('load', placeTrade);
})();
