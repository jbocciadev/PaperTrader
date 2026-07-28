// Create a formatter for the monetary values to be presented.
const usdFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
});

// Format static values first on page load
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".usd-format").forEach((element) => {
        const value = Number(element.textContent);

        if (!Number.isNaN(value)) {
            element.textContent = usdFormatter.format(value);
        }
    });
});

// Listen for market price updates and update holdings values
document.addEventListener("marketDataUpdated", (event) => {
    const marketData = event.detail;
    let totalPortfolioValue = 0;

    // Access context variable sharesOwned and calculate values per ticker
    for (const [ticker, shares] of Object.entries(sharesOwned)) {
        const tickerData = marketData[ticker];

        if (!tickerData) {
            continue;
        }

        const currentPrice = tickerData.price;
        const holdingValue = shares * currentPrice;
        totalPortfolioValue += holdingValue;

        const priceElement = document.getElementById(`holding-price-${ticker}`);

        const valueElement = document.getElementById(`holding-value-${ticker}`);

        if (priceElement) {
            priceElement.innerText = usdFormatter.format(currentPrice);
        }

        if (valueElement) {
            valueElement.innerText = usdFormatter.format(holdingValue);
        }
    }

    // Calculate Total Net Worth from holdings value and cash
    const positionsValueElement = document.getElementById("positions-value");

    const netWorthElement = document.getElementById("net-worth");

    if (positionsValueElement) {
        positionsValueElement.innerText =
            usdFormatter.format(totalPortfolioValue);
    }

    if (netWorthElement) {
        const totalNetWorth = cashBalance + totalPortfolioValue;

        netWorthElement.innerText = usdFormatter.format(totalNetWorth);
    }
});
