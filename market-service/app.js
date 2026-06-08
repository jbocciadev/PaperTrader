import dotenv from "dotenv";

dotenv.config({
    path: "../.env",
});

console.log("API key is: ", process.env.FINNHUB_API_KEY);
