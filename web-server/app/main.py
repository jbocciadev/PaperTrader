import os
import asyncio
import grpc
import jwt

# gRPC stubs
from app import engine_pb2
from app import engine_pb2_grpc

# Hashing library for security purposes
import hashlib

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, Form, Cookie
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from upstash_redis import Redis
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

# Load credentials from environment file
load_dotenv(dotenv_path="../.env")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# gRPC client object
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

    

# Wire-up the Redis server connection
# Reference: https://upstash.com/docs/redis/tutorials/pythonapi

redis_url = os.getenv("REDIS_URL")
redis_token = os.getenv("REDIS_TOKEN")

# Start Redis client from imported class
redis_client = Redis(url=redis_url, token=redis_token)


# Reference: https://realpython.com/async-io-python/
@app.websocket("/ws/prices/{ticker}")
async def websocket_price_stream(websocket: WebSocket, ticker: str):
    """
    Websocket endpoint for Redis cloud server to stream updates to the user browser.
    """
    await websocket.accept()
    print(f"Client connected to real-time stream for ticker: {ticker.upper()}")

    try:
        # infinite loop to stream updates while the connection is open
        while True:
            # get the latest price
            cache_key = f"stock:{ticker.upper()}:price"
            latest_price = redis_client.get(cache_key)

            if latest_price is not None:
                # Ref: https://fastapi.tiangolo.com/reference/websockets/#fastapi.WebSocket.send_json
                await websocket.send_json({
                    "ticker": ticker.upper(),
                    "price": str(latest_price),
                    "timestamp": "Live"
                })
                # 1-second interval to prevent overwhelming Redis server
                await asyncio.sleep(1)
    except WebSocketDisconnect:
        # Cach error when the websocket is disconnected.
        print(f"Client disconnected cleanly from price stream: {ticker.upper()}")


# Web server routes ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ 

# Reference templates folder to be served
templates=Jinja2Templates(directory="app/templates")

# Define home route
@app.get("/")
def home(
    request: Request,
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
    ):
    # Reference: https://fastapi.tiangolo.com/advanced/templates/
    """
    Route that serves the main landing page. If a user is logged in, it will rende the dashboard
    """

    current_user = None

    # Try to validate token credentials
    if access_token:
        try:
            decoded_payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = decoded_payload.get("user_id")
            current_user = db.query(User).filter(User.id == user_id).first()
        except jwt.PyJWTError:
            current_user = None

    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={"user": current_user}
    )

# Routes for the register workflow ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ 
@app.get("/register")
def show_register_page(request: Request):
    """
    Serves the visual signup form view to the client browser.
    """
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"user": None}
        )

@app.post("/register")
def process_registration(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Parses the form submitted within constraints and saves data in PostgreSQL DB
    """
    # Check if username is already taken
    existing_user = db.query(User).filter(User.username == username).first()
    
    if existing_user is not None:
        # If the username exists, return error message to the browser
        return {"error": "Username already exists. Please choose a different name."}
    
    # Use hash to encrypt the passord
    hashed_pwd = hashlib.sha256(password.encode("utf-8")).hexdigest()
        
    # Create the new user record profile object (starting with $10,000 cash)
    new_user = User(
        username=username,
        password_hash=hashed_pwd,  # Storing as a plain text string token for simplicity
        cash_balance=10000.00
    )
    
    # Commit the changes to the database tables
    db.add(new_user)
    db.commit()
    
    # Redirect the browser to the login interface
    return RedirectResponse(url="/login", status_code=303)

# Routes for the login workflow ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ 
@app.get("/login")
def show_login_page(request: Request):
    """
    Serves the login page to the user's browser
    """
    return templates.TemplateResponse(
        request=request, 
        name="login.html",
        context={"user":None}
        )

@app.post("/login")
def process_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Validates the submitted password against the hashed version stored in 
    the PostgreSQL server and inserts a token for the user session
    """
    # Encrypt the submitted pwd to check against the one in the db
    incoming_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # Query the db for an entry with both username and hashed password
    user_record = db.query(User).filter(
        User.username == username,
        User.password_hash == incoming_hash
    ).first()

    # Return the same page with an error message if credentials don't match
    if user_record is None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid Username or password. Please try again."
            }
        )
    
    # If a matching record is found, create the token to be served
    # Reference: https://pyjwt.readthedocs.io/en/stable/usage.html#encoding-decoding-tokens-with-hs256
    token_payload = {"user_id": user_record.id}
    generated_token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Effectively log the user in and rediret them to the dashboard
    # Reference: https://fastapi.tiangolo.com/reference/responses/#fastapi.responses.RedirectResponse
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=generated_token,
        httponly=True,
        path="/"
    )
    print(f"User session successfully initiated for usert ID: {user_record.id}")
    return response

# Routes for the logout workflow ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ 
@app.get("/logout")
def process_logout():
    """
    Clears the cookie from the browser and redirtects to login
    """
    
    response = RedirectResponse(url="/login", status_code=303)    
    # Delete the cookie from the session in the response to be sent
    response.delete_cookie(key="access_token", path="/")
    
    print("User session terminated cleanly. Cookie deleted.")
    return response


# Routes for the Dashboard ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ ¬ 
@app.get("/dashboard")
def show_dashboard_page(
    request: Request,
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):

    """
    Validates the session token via cookies and presents the user's dashboard
    """
    # If cookie is missing, redirect to Login
    if not access_token:
        print("Dashboard access not authorized: token is missing.")
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        # Decode the token sent by the browser
        decoded_payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = decoded_payload.get("user_id")

        # Retrieve account details from db
        current_user = db.query(User).filter(User.id == user_id).first()

        # If the token is for an invalid user ID (expired/deleted), redirect the user to login
        if current_user is None:
            return RedirectResponse(url="/login", status_code=303)
        
        # If the token is good, render the dashboard, passing the user info to the jinja template
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={"user": current_user}
        )
    
    except jwt.PyJWTError:
        # Cath corrupted tokens and redirect to login page
        print("Dashboard access not authorized: token is invalid/corrupted.")
        return RedirectResponse(url="/login", status_code=303)


# Define the model against which data will be validated
# Reference: https://fastapi.tiangolo.com/#requirements
class TradeRequestModel(BaseModel):
    user_id: int
    ticker: str = Field(..., min_length=1, max_length=5) # string of up to 5 chars
    quantity: int = Field(..., gt=0) # integer greater than 0
    trade_type: str 

# FastAPI Reference for Forms https://fastapi.tiangolo.com/tutorial/request-forms/
@app.post("/trade")
def handle_trade_route(
    request: Request,
    ticker: str = Form(...),
    quantity: int = Form(...),
    trade_type: str = Form(...),
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
                       ):
# This route parses the data sent in the form and sends the gRPC request down
# to the trading system to execute

    # Check that there is a token submitted with the form
    if not access_token:
        return RedirectResponse(url="/login", status_code=303) # Send user to login
    
    try:
        # Extract the user id from the token
        decoded_payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = decoded_payload.get("user_id")
        current_user = db.query(User).filter(User.id == user_id).first()
        
        # If there is no match in the db for the user sent with the token
        if current_user is None:
            return RedirectResponse(url="/login", status_code=303) # Send user back to login

        # parse the values submitted in the form to be sent with the proto file
        if trade_type.upper() == "BUY":
            proto_trade_type = engine_pb2.BUY
        elif trade_type.upper() == "SELL":
            proto_trade_type = engine_pb2.SELL
        else:
            # Return an error as the type submitted is not supported
            return templates.TemplateResponse(
                request=request,
                name="dashboard.html",
                context={
                    "user": current_user, "error": f"Invalid operation type specified: {trade_type.upper()}"
                }
            )
        
        # Compile all fields into gRPC request to be sent
        proto_request = engine_pb2.TradeRequest(
            user_id=user_id,
            ticker=ticker.upper().strip(),
            quantity=quantity,
            trade_type=proto_trade_type
        )

        # Send the request using the stub generated in the context manager
        response = grpc_client["stub"].ExecuteTrade(proto_request, timeout=5)

        # Redirect user to dashboard with success or error message
        if response.success:
            feedback_msg = f"Order executed! {trade_type.upper().strip()} {quantity} shares of {ticker.upper().strip()} at ${response.execution_price:.2f}"
            updated_user = db.query(User).filter(User.id == user_id).first() # Query db again for user with new details
            return templates.TemplateResponse(
                request=request,
                name="dashboard.html",
                context={
                    "user": updated_user,
                    "success": feedback_msg
                }
            )
        else:
            return templates.TemplateResponse(
                request=request,
                name="dashboard.html",
                context={
                    "user": current_user,
                    "error": response.message
                }
            )
    except jwt.PyJWTError:
        return RedirectResponse(url="/login", status_code=303)
    
    except grpc.RpcError as error:
        # Gracefullt catch connection errrs from gRPC trading engine
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "user": current_user,
                "error": f"Main transaction engne connection failure: {error.details()}"
            }
        )


# # ¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬
#     # Transform the request into a gRPC packet
#     if payload.trade_type.upper == "BUY":
#         chosen_type = engine_pb2.BUY
#     elif payload.trade_type.upper == "SELL":
#         chosen_type = engine_pb2.SELL
#     else:
#         return {"success": False, "message": "Invalid trade type (only BUY or SELL are allowed)."}
#     # Build the packet
#     grpc_request = engine_pb2.TradeRequest(
#         user_id=payload.user_id,
#         ticker=payload.ticker.upper(),
#         quantity=payload.quantity,
#         trade_type=chosen_type
#     )

#     try:
#         # Send the packet down the pipeline and capture the response
#         engine_response = grpc_client["stub"].ExecuteTrade(grpc_request)

#         # Return response to the user browser
#         return {
#             "success": engine_response.success,
#             "message": engine_response.message,
#             "transaction_id": engine_response.transaction_id,
#             "execution_rice": engine_response.execution_price
#         }
#     except Exception as error:
#         return {"success": False, "message": f"Could not connect to the engine: {str(error)}"}
