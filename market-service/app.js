import dotenv from "dotenv";
import axios from "axios";
import { createClient, ErrorReply } from "redis";
import WebSocket from "ws";

// Configure environment variables
dotenv.config({
    path: ".env",
});

// Configure Redis cloud database
const redisClient = createClient({
    url: process.env.REDIS_URL,
    socket: {
        connectTimeout: 10000, // Wait max 10 seconds to connect
        keepAlive: 5000, // Check connection is alive by pinging the server every 5 seconds
    },
});
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
        for (const result of results) {
            openingValues[result.ticker] = result.data;
            // Send values to redis server
            // Redis namespace convention uses colons for categorisation
            const redisKey = `stock:${result.ticker}:snapshot`;

            await redisClient.set(redisKey, JSON.stringify(result.data));
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

// Function to connect to finnhub's websocket and actions to take
async function startWebsocket() {
    const socket = new WebSocket(
        `wss://ws.finnhub.io?token=${FINNHUB_API_KEY}`,
    );

    // Handle initial opening of the websocket
    socket.on("open", function (event) {
        // loop through tickers list and send a subscribe request to the finnhub ws server
        for (const ticker of tickers) {
            socket.send(JSON.stringify({ type: "subscribe", symbol: ticker }));
        }
    });

    // Handle websockt messages
    socket.on("message", async function (data) {
        try {
            // Parse the data inside the message received
            const payload = JSON.parse(data.toString());
            // Check for ping messages and ignore
            if (payload.type == "ping") {
                return;
                // console.log("ping msg");
            }

            // Check if message is real trade from market and process
            if (payload.type == "trade" && payload.data) {
                for (const item of payload.data) {
                    const ticker = item.s;
                    const latestPrice = item.p;

                    // Send info to Redis cloud server
                    const redisPriceKey = `stock:${ticker}:price`;
                    await redisClient.set(
                        redisPriceKey,
                        latestPrice.toString(),
                    );
                    console.log(
                        `Last price update ---> ${ticker}: $ ${latestPrice}`,
                    );
                }
            }
        } catch (error) {
            console.error("Error parsing Websocket message: ", error.message);
        }
    });

    // Handle errors from websocket
    socket.on("error", function (error) {
        console.error(`Websocket error received: `, error.message);
    });

    // Handle remote closure of websocker
    socket.on("close", function () {
        console.warn(
            "Websocket disconnected. Will attempt reconnect in 5 seconds",
        );
        setTimeout(startWebsocket, 5000);
    });
}

async function startApp() {
    // Connect to the redis service
    await redisClient.connect();
    console.log("Connected to Redis server successfully");

    // poll market prices for the tickers in the list
    await openingPrices();
    // run the websocket function
    await startWebsocket();
}

startApp();
