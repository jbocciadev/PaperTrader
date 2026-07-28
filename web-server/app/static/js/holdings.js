document.addEventListener("marketDataUpdated", (event) => {
    const marketData = event.detail;

    for (const [ticker, shares] of Object.entries(sharesOwned)) {
        const tickerData = marketData[ticker];

        if (!tickerData) {
            continue;
        }

        const currentPrice = tickerData.price;
        const holdingValue = shares * currentPrice;

        const priceElement = document.getElementById(`holding-price-${ticker}`);

        const valueElement = document.getElementById(`holding-value-${ticker}`);

        if (priceElement) {
            priceElement.innerText = `$${currentPrice.toFixed(2)}`;
        }

        if (valueElement) {
            valueElement.innerText = `$${holdingValue.toFixed(2)}`;
        }
    }
});
