# https://grpc.io/docs/languages/python/quickstart/
# https://medium.com/@dneprokos/sdet-exploring-grpc-testing-practical-examples-with-postman-c-and-python-clients-f1a29f91e3eb

import os
import grpc
import engine_pb2_grpc
import engine_pb2
import engine
from app.models import User, Transaction
from concurrent import futures
from sqlalchemy import func
from dotenv import load_dotenv
from upstash_redis import Redis

from database import SessionLocal

class TradingServiceServicer(engine_pb2_grpc.TradingServiceServicer):
    """
    Handles trade requests from the Web server.
    Inherits from the compiled gRPC base class
    """

    def __init__(self, redis_client, db_session=None): # Default to None to allow for prod/test start
        self.redis_client = redis_client
        self.db_session = db_session

    def ExecuteTrade(self, request, context):
        """ 
        Receives a TradeRequest message
        and executes the transaction requested.
        """

        # Check if a mock db has been passed
        is_test_environment = self.db_session is not None 
        if is_test_environment:
            db = self.db_session
        else:
            db = SessionLocal()


        # Check against invalid number of shares
        if request.quantity <= 0:
            return engine_pb2.TradeResponse(
                success=False,
                message="Quantity must be a possitive whole integer, greater than zero",
                transaction_id="",
                execution_price=0.0
            )
        
        # If production, query DB for actual user
        if not is_test_environment:
            # Query db for user record
            user_record = db.query(User).filter(User.id == request.user_id).first()
            # Validate user
            if user_record is None:
                return engine_pb2.TradeResponse(
                    success=False,
                    message="Aborted. User not found in database.",
                    transaction_id="",
                    execution_price=0.0
                )
            
            user_cash = user_record.cash_balance
        else:
            # Mock funds for testing, will be queried from DB
            user_cash = 10000.00

        # Implement BUY transaction type
        if request.trade_type == engine_pb2.BUY:
            try:
                # Execute price check and calculation
                new_balance, total_cost, cached_price = engine.execute_buy_transaction(
                    redis_client=self.redis_client,
                    current_cash=user_cash,
                    shares=request.quantity,
                    ticker=request.ticker
                )

                # Update db for user if order succeeds
                if not is_test_environment:
                    user_record.cash_balance = new_balance

                    # Store transaction in db
                    new_transaction = Transaction(
                        user_id=request.user_id,
                        shares=request.quantity,
                        ticker=request.ticker,
                        price=cached_price,
                        transaction_type="BUY"
                    )
                    db.add(new_transaction)

                    # Commit both updates to the db
                    db.commit()

                return engine_pb2.TradeResponse(
                    success=True,
                    message=f"Successfully purchased {request.quantity} shares of {request.ticker}.",
                    transaction_id="tx_generated_123",
                    execution_price=cached_price
                )
            
            except ValueError as error:
                # Catch insufficient funds/price unavailable errors
                if not is_test_environment:
                    db.rollback()  # Undo any changes in case of error

                return engine_pb2.TradeResponse(
                    success=False,
                    message=str(error),
                    transaction_id="",
                    execution_price=0.0
                )
            
            except Exception as error:
                if not is_test_environment:
                    db.rollback()
                print(f"[ERROR] Transaction failed, session rolled back: {str(error)}")
                return engine_pb2.TradeResponse(success=False, message=f"Database execution error: {str(error)}")
            
            finally:
                # Close the database connections
                if not is_test_environment:
                    db.close()

        # Implement Sell transaction type
        elif request.trade_type == engine_pb2.SELL:
            try:
                # Retrieve user record from db
                if not is_test_environment:
                    user_record = db.query(User).filter(User.id == request.user_id).first()
                    # Return failure if user not found
                    if user_record is None:
                        return engine_pb2.TradeResponse(
                            success=False,
                            message="Aborted, user not found.",
                            transaction_id="",
                            execution_price=0.0
                        )

                    user_cash = user_record.cash_balance

                    # Calculate current total of shares owned by the user 
                    # by adding BUY transactions and subtracting SELL transactions
                    bought_shares = db.query(func.sum(Transaction.shares)).filter(
                        Transaction.user_id == request.user_id,
                        Transaction.ticker == request.ticker,
                        Transaction.transaction_type == "BUY"
                    ).scalar() or 0

                    sold_shares = db.query(func.sum(Transaction.shares)).filter(
                        Transaction.user_id == request.user_id,
                        Transaction.ticker == request.ticker,
                        Transaction.transaction_type == "SELL"
                    ).scalar() or 0

                    user_held_shares = bought_shares - sold_shares
                
                else:
                    # Fallback values for testing scenarios
                    user_cash = 10000.0
                    user_held_shares = 50

                # Execute transaction
                new_balance, total_proceeds, cached_price = engine.execute_sell_order(
                    redis_client=self.redis_client,
                    current_cash=user_cash,
                    held_shares=user_held_shares,
                    shares_to_sell=request.quantity,
                    ticker=request.ticker
                )

                # Update db for user record if transaction succeeds
                if not is_test_environment:
                    user_record.cash_balance = new_balance

                    # Store transaction in db
                    new_transaction = Transaction(
                        user_id=request.user_id,
                        shares=request.quantity,
                        ticker=request.ticker,
                        price=cached_price,
                        transaction_type="SELL"
                    )
                    db.add(new_transaction)

                    # Commit both additions to the database
                    db.commit()

                return engine_pb2.TradeResponse(
                    success=True,
                    message=f"Successfully sold {request.quantity} shares of {request.ticker}.",
                    transaction_id="tx_generated_sell",  # Placeholder until UUID or auto-inc tracking is hooked up
                    execution_price=cached_price
                )

            except ValueError as error:
                # Catch errors for trying to sell too many shares
                return engine_pb2.TradeResponse(
                    success=False,
                    message=str(error),
                    transaction_id="",
                    execution_price=0.0
                )
            
            except Exception as error:
                db.rollback()
                print(f"[ERROR] Transaction failed, session rolled back: {str(error)}")
                return engine_pb2.TradeResponse(success=False, message=f"Database execution error: {str(error)}")

            finally:
                if not is_test_environment:
                    db.close()

        # Fallback return statement
            return engine_pb2.TradeResponse(
                success=False,
                message="Unsupported transaction type specified.",
                transaction_id="",
                execution_price=0.0
            )

    
    def GetPortfolio(self, request, context):
        """
        Receives a PortfolioRequest message from the web server and returns the 
        user's holdings.
        """
        # Temporary stub response
        return engine_pb2.PortfolioResponse(
            user_id=request.user_id,
            cash_balance=10000.0,
            holdings_summary="10 sahres of AAPL (stub)"
        )


def serve():
    """
    Initializes a thread pool, binds the database logic servicer,
    and opens network port 50051 to listen for FastAPI gateway requests.
    Reference: https://grpc.io and https://github.com/grpc/grpc/blob/v1.82.0/examples/python/helloworld/greeter_server.py
    """
    
    # Load environment variabnles from .env file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    shared_env_path = os.path.join(current_dir, "../../.env")
    load_dotenv(dotenv_path=shared_env_path)

    # Create Redis and PostgreSQL connection clients
    redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
    redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    redis_client = Redis(url=redis_url, token=redis_token)

    db_session = SessionLocal()
    
    # Open a standard background thread pool to handle concurrent trades
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register business logic class directly to the running network server
    # Pass a placeholder initialization instance matching class signature.
    # To be updated with prod details later.
    engine_pb2_grpc.add_TradingServiceServicer_to_server(
        TradingServiceServicer(redis_client=redis_client), 
        server
    )
    
    # Securely lock the server to handle internal insecure communication on port 50051
    server.add_insecure_port("[::]:50051")
    print("\n---------------------------------------------------------")
    print("🚀 SUCCESS: gRPC Core Trading Server is active on port 50051!")
    print("---------------------------------------------------------\n")
    
    # Fire the persistent execution loop
    server.start()
    server.wait_for_termination()
