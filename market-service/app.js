import dotenv from "dotenv";
import axios from "axios";
import { createClient, ErrorReply } from "redis";
import WebSocket from "ws";

// Configure environment variables
dotenv.config({
    path: "../.env",
});

// Configure Redis cloud database
const redisClient = createClient({
    url: process.env.REDIS_URL,
    socket: {
        connectTimeout: 10000, // Wait max 10 seconds to connect
        keepAlive: 30000, // Keep TCP connection alive (pinging)
        // Establish reconnections policy
        reconnectStrategy: (retries) => {
            console.log(`Redis reconnect attempt #${retries}`);
            return Math.min(retries * 100, 3000); // Backoff retry delay
        },
    },
});
redisClient.on("error", (err) => console.error("Redis client error: ", err));

redisClient.on("connect", () => {
    console.log("[REDIS] Connecting to Redis server...");
});

redisClient.on("ready", () => {
    console.log("[REDIS] Redis connection ready.");
});

redisClient.on("reconnecting", () => {
    console.log("[REDIS] Attempting to reconnect to Redis...");
});

redisClient.on("end", () => {
    console.warn("[REDIS] Redis connection closed.");
});

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

        console.log("responses: \n\n", openingValues);
    } catch (error) {
        console.error("Error fetching initial ticker prices.", error.message);
    }
}

// Function to connect to finnhub's websocket and actions to take
// Track the active Finnhub WebSocket connection
let finnhubSocket = null;

// Prevent multiple reconnect timers from being created
let reconnectTimer = null;

// Function to connect to Finnhub's WebSocket
async function startWebsocket() {
    // Prevent duplicate connections
    if (
        finnhubSocket &&
        (finnhubSocket.readyState === WebSocket.OPEN ||
            finnhubSocket.readyState === WebSocket.CONNECTING)
    ) {
        console.log("Finnhub WebSocket is already connected or connecting.");
        return;
    }

    console.log("Connecting to Finnhub WebSocket...");

    finnhubSocket = new WebSocket(
        `wss://ws.finnhub.io?token=${FINNHUB_API_KEY}`
    );

    // Handle successful WebSocket connection
    finnhubSocket.on("open", function () {
        console.log("Connected to Finnhub WebSocket.");

        // Clear any pending reconnect timer
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }

        // Subscribe to all configured tickers
        for (const ticker of tickers) {
            finnhubSocket.send(
                JSON.stringify({
                    type: "subscribe",
                    symbol: ticker,
                })
            );

            console.log(`Subscribed to Finnhub ticker: ${ticker}`);
        }
    });

    // Handle WebSocket messages
    finnhubSocket.on("message", async function (data) {
        try {
            // Parse the message received from Finnhub
            const payload = JSON.parse(data.toString());

            // Ignore Finnhub heartbeat messages
            if (payload.type === "ping") {
                return;
            }

            // Process real market trade data
            if (payload.type === "trade" && payload.data) {
                for (const item of payload.data) {
                    const ticker = item.s;
                    const latestPrice = item.p;

                    // Redis key for the latest live price
                    const redisPriceKey = `stock:${ticker}:price`;

                    try {
                        // Store latest market price in Redis
                        await redisClient.set(
                            redisPriceKey,
                            latestPrice.toString()
                        );

                        console.log(
                            `Last price update ---> ${ticker}: $ ${latestPrice}`
                        );
                    } catch (redisError) {
                        // Handle Redis failures without crashing
                        // the Finnhub WebSocket message handler
                        console.error(
                            `[REDIS WRITE ERROR] Failed to update ${ticker}:`,
                            redisError.message
                        );
                    }
                }
            }
        } catch (error) {
            console.error("Error parsing WebSocket message:", error.message);
        }
    });

    // Handle WebSocket errors
    finnhubSocket.on("error", function (error) {
        console.error("[FINNHUB WEBSOCKET ERROR]:", error.message);
    });

    // Handle remote WebSocket closure
    finnhubSocket.on("close", function (code, reason) {
        console.warn(`Finnhub WebSocket disconnected. Code: ${code}.`);

        if (reason) {
            console.warn(`Disconnect reason: ${reason.toString()}`);
        }

        // Clear the reference to the closed socket
        finnhubSocket = null;

        // Prevent duplicate reconnect timers
        if (!reconnectTimer) {
            console.log(
                "Finnhub WebSocket will attempt to reconnect in 5 seconds..."
            );

            reconnectTimer = setTimeout(() => {
                reconnectTimer = null;
                startWebsocket();
            }, 5000);
        }
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
