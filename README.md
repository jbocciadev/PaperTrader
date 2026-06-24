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

- SQLite and PostgreSQL:
    - Given resource limitations, testing and development will be carried out using SQLite, to then move on to PostgreSQL in potential deployment

9/06: Moved files out of OneDrive to avoid multi-platform issues. Going forward, syncing with github only.
13/06: Out of hours: The application will allow users to execute trades outside of US market hours. However, in a production environment, these would be prevented by checking data/time stamp.

... https://stackoverflow.com/questions/1838873/visualizing-branch-topology-in-git
... https://gitdiagram.com/
