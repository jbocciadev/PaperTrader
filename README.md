# PaperTrader

GitHub repository for PaperTrader, a paper trading application.

Notes:

- .env:
    - Implemented .env file for dotenv to manage environment variables that will not be shared to git/github (.included in .gitignore file).
    - NODE_TLS_REJECT_UNAUTHORIZED=0 This line was added to avoid rejcetion due to failed certificate. This is a workaround that would need to be resolved in a production envirnment with certificates.
    - TICKERS was added as an environment variable to add flexibility, decoupling it from the hardcoded.

- market-service:
    - Changed from Alpha vantage to finnhub as there was a strict limit usage for the free tier service.
    - Implemented the "cURL" query version for the symbol quotes so as to avoid version compatibility issues with finnhub's own js package.

9/06: Moved files out of OneDrive to avoid multi-platform issues. Going forward, syncing with github only.
