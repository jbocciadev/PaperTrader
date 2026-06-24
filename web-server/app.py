from fastapi import FastAPI

# Initialize app from FastAPI class
app = FastAPI(
    title="Paper trader - Web gateway",
    description="Public interface to trade actions.",
    version="1.0.0"
)

# Define home route
@app.get("/")
def read_root():
    """
    Initial sample to test web server is operationsl.
    """
    return {
        "status": "online",
        "service": "web-gateway",
        "message": "Welcome to PaperTrader."
    }