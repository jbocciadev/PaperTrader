import grpc
import engine_pb2
import engine_pb2_grpc
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Placeholder for grpc client reference
grpc_client = {}

@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    Manages opening and closing of gRPC pipe on server startup and shutdown
    """

    # Create channel
    channel = grpc.insecure_channel("localhost:50051")

    grpc_client["stub"] = engine_pb2_grpc.TradingServiceStub(channel)
    print("gRPC client channel established successfully.")

    yield

    # Cleanup connection on server shutdown
    channel.close()
    print("gRPC client channel terminated successfully.")

# Initialize app from FastAPI class
app = FastAPI(
    title="Paper trader - Web gateway",
    description="Public interface to trade actions.",
    version="1.0.0",
    lifespan=lifespan
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
        # "message": "Welcome to PaperTrader."
        "grpc-bridge": "initialized" if "stub" in grpc_client else "offline"
    }