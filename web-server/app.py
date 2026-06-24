import grpc
# gRPC stubs
import engine_pb2
import engine_pb2_grpc

from contextlib import asynccontextmanager
from fastapi import FastAPI

# Placeholder for grpc client reference
grpc_client = {}

@asynccontextmanager
async def lifespan(app:FastAPI):
    # Reference: https://medium.com/@marcnealer/fastapi-after-the-getting-started-867ecaa99de9
    """
    Manages opening and closing of gRPC pipe on server startup and shutdown
    """

    # Establish gRPC channel
    # Reference: https://realpython.com/python-microservices-grpc/
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

from pydantic import BaseModel, Field

# Define the model against which data will be validated
# Reference: https://fastapi.tiangolo.com/#requirements
class TradeRequestModel(BaseModel):
    user_id: int
    ticker: str = Field(..., min_length=1, max_length=5) # string of up to 5 chars
    quantity: int = Field(..., gt=0) # integer greater than 0
    trade_type: str 

@app.post("/trade")
def handle_trade_route(payload: TradeRequestModel):

    # Transform the request into a gRPC packet
    if payload.trade_type.upper == "BUY":
        chosen_type = engine_pb2.BUY
    elif payload.trade_type.upper == "SELL":
        chosen_type = engine_pb2.SELL
    else:
        return {"success": False, "message": "Invalid trade type (only BUY or SELL are allowed)."}
    # Build the packet
    grpc_request = engine_pb2.TradeRequest(
        user_id=payload.user_id,
        ticker=payload.ticker.upper(),
        quantity=payload.quantity,
        trade_type=chosen_type
    )

    try:
        # Send the packet down the pipeline and capture the response
        engine_response = grpc_client["stub"].ExecuteTrade(grpc_request)

        # Return response to the user browser
        return {
            "success": engine_response.success,
            "message": engine_response.message,
            "transaction_id": engine_response.transaction_id,
            "execution_rice": engine_response.execution_price
        }
    except Exception as error:
        return {"success": False, "message": f"Could not connect to the engine: {str(error)}"}
