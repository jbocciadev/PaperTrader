import dotenv from "dotenv";
import axios from "axios";

dotenv.config({
    path: "../.env",
});

// Finnhub API client setup
const FINNHUB_API_KEY = process.env.FINNHUB_API_KEY;

console.log("API key is: ", process.env.FINNHUB_API_KEY);

const tickers = [
    "AAPL",
    "NVDA",
    "TSLA",
    "AAPL",
    "AMZN",
    "MSFT",
    "META",
    "GOOGL",
    "AMD",
    "PLTR",
    "INTC",
];

const opening_values = {};

async function openingPrices() {
    try {
        console.log("polling prices...");
        for (var ticker of tickers) {
            console.log(ticker);
            // Source: https://finnhub.io/docs/api/quote
            const url = `https://finnhub.io/api/v1/quote?symbol=${ticker}&token=${FINNHUB_API_KEY}`;
            const response = await axios.get(url);

            // console.log(response.data);
            opening_values[ticker] = response.data;
        }
        console.log("responses: \n\n", opening_values);
    } catch (error) {
        console.error("Error fetching initial ticker prices.", error.message);
    }
}

openingPrices();
