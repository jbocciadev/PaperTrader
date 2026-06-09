import dotenv from "dotenv";
import axios from "axios";
import { createClient, ReconnectStrategyError, RedisClient } from "redis";

dotenv.config({
    path: "../.env",
});

const redisClient = createClient({ url: process.env.REDIS_URL });
redisClient.on("error", (err) => console.error("Redis client error: ", err));

// Finnhub API client setup
const FINNHUB_API_KEY = process.env.FINNHUB_API_KEY;

// Declare variable with stock symbols (tickers).
const tickers = process.env.TICKERS.split(",");

// Declare empty object that will capture all ther eturned values
const openingValues = {};

async function openingPrices() {
    try {
        console.log("polling prices...");
        // Traverse through values in tickers and call the finnhub api for market information.

        // Map tickers array into an array of unresolved Axios promises
        const promises = tickers.map((ticker) => {
            // Source: https://finnhub.io/docs/api/quote => see cURL path
            const url = `https://finnhub.io/api/v1/quote?symbol=${ticker}&token=${FINNHUB_API_KEY}`;
            return axios.get(url).then((response) => ({
                ticker,
                data: response.data,
            }));
        });

        // Fire all axios calls simultaneously
        const results = await Promise.all(promises);

        // Parse responses into object
        for (let result of results) {
            openingValues[result.ticker] = result.data;
        }

        // for (let ticker of tickers) {
        //     // Source: https://finnhub.io/docs/api/quote => see cURL path
        //     const url = `https://finnhub.io/api/v1/quote?symbol=${ticker}&token=${FINNHUB_API_KEY}`;
        //     const response = await axios.get(url);

        //     openingValues[ticker] = response.data;
        // }
        console.log("responses: \n\n", openingValues);
    } catch (error) {
        console.error("Error fetching initial ticker prices.", error.message);
    }
}

async function startApp() {
    // Connect to the redis service
    await redisClient.connect();
    console.log("Connected to Redis server successfully");

    // poll market prices for the tickers in the list
    await openingPrices();
}

startApp();
