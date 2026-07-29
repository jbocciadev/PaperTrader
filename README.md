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

29/07: Moved away from NGINX in favour of CADDY. Site is now live under papertrader.cc

... https://stackoverflow.com/questions/1838873/visualizing-branch-topology-in-git
... https://gitdiagram.com/

### Production Infrastructure & Security Architecture

The production environment for **Paper Trader** is deployed as an isolated microservice mesh on an AWS EC2 instance, utilizing a portable, multi-container orchestration layer.

- **Edge Reverse Proxy Tier:** A containerized **Caddy Server** handles all incoming public network traffic. It binds natively to ports `80` and `443` to enforce an HTTPS-only gateway, managing automated SSL/TLS certificate handshakes, installations, and renewals securely via Let's Encrypt.
- **Encrypted ASGI Network Pipeline:** The **FastAPI** web gateway runs behind the Caddy edge block inside an isolated Docker internal network (`paper-trader-overlay`). Uvicorn is configured with `--proxy-headers` and `FORWARDED_ALLOW_IPS=*` to safely process upstream headers, ensuring all absolute asset URLs (`url_for`) render natively over secure `https://` schemas without mixed-content vulnerabilities.
- **Microservice Inter-Container DNS Routing:** Cross-tier data transactions between the FastAPI web gateway and the Python trading execution core communicate via structured **gRPC over port 50051**, leveraging Docker's internal, sandboxed service-discovery DNS resolution.
