document.addEventListener("DOMContentLoaded", () => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(
        `${protocol}//${window.location.host}/ws/market-feed`
    );

    const streamStatus = document.getElementById("stream-status");
    const priceCache = {}; // Tracks history states locally to handle flash direction changes

    ws.onopen = () => {
        if (streamStatus) {
            streamStatus.innerText = "Live";
            streamStatus.className =
                "badge bg-danger text-white fw-bold animate-pulse";
        }
    };

    ws.onmessage = (event) => {
        const marketUpdateMatrix = JSON.parse(event.data);

        for (const [ticker, data] of Object.entries(marketUpdateMatrix)) {
            const priceElement = document.getElementById(`price-${ticker}`);
            const changeElement = document.getElementById(`change-${ticker}`);

            if (!priceElement) continue; // Skip if ticker isn't drawn on this user interface screen layout

            const newPrice = data.price;
            priceElement.innerText = `$${newPrice.toFixed(2)}`;

            // Update change indicators if elements exist
            if (changeElement) {
                const changeVal = data.change;
                const pctVal = data.pct_change;
                changeElement.innerText = `${changeVal >= 0 ? "+" : ""}${changeVal.toFixed(2)} (${pctVal.toFixed(2)}%)`;
                changeElement.className =
                    changeVal >= 0
                        ? "text-success small fw-bold"
                        : "text-danger small fw-bold";
            }

            // Pull the old price to determine your custom cell flash trigger
            const oldPrice = priceCache[ticker] || 0.0;

            if (oldPrice > 0.0 && newPrice !== oldPrice) {
                priceElement.classList.remove("flash-up", "flash-down");
                void priceElement.offsetWidth; // Force a synchronous layout engine DOM reflow to clear memory state

                if (newPrice > oldPrice) {
                    priceElement.classList.add("flash-up");
                } else {
                    priceElement.classList.add("flash-down");
                }
            }
            priceCache[ticker] = newPrice;
        }
    };

    ws.onerror = () => {
        if (streamStatus) {
            streamStatus.innerText = "Offline";
            streamStatus.className = "badge bg-secondary text-white fw-bold";
        }
    };
});
