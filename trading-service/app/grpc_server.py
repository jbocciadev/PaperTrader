# https://grpc.io/docs/languages/python/quickstart/
# https://medium.com/@dneprokos/sdet-exploring-grpc-testing-practical-examples-with-postman-c-and-python-clients-f1a29f91e3eb

import grpc
from app import engine_pb2_grpc
from app import engine_pb2
from app import engine
from app.models import User, Transaction

class TradingServiceServicer(engine_pb2_grpc.TradingServiceServicer):
    """
    Handles trade requests from the Web server.
    Inherits from the compiled gRPC base class
    """

    def __init__(self, redis_client, db_session):
        self.redis_client = redis_client
        self.db_session = db_session

    def ExecuteTrade(self, request, context):
        """ 
        Receives a TradeRequest message
        and executes the transaction requested.
        """
        # Check against invalid number of shares
        if request.quantity <= 0:
            return engine_pb2.TradeResponse(
                success=False,
                message="Quanitty must be a possitive whole integer, greater than zero",
                transaction_id="",
                execution_price=0.0
            )
        # Check for active db session, or None for test purposes
        if self.db_session is not None:
            # Query db for user record
            user_record = self.db_session.query(User).filter(User.id == request.user_id).first()
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
                new_balance, total_cost = engine.execute_buy_transaction(
                    redis_client=self.redis_client,
                    current_cash=user_cash,
                    shares=request.quantity,
                    ticker=request.ticker
                )

                # Get cached price
                cached_price = engine.get_cached_price(self.redis_client, request.ticker)

                # Update db if order succeeds
                if self.db_session is not None:
                    user_record.cash_balance = new_balance
                    self.db_session.commit()

                return engine_pb2.TradeResponse(
                    success=True,
                    message=f"Successfully purchased {request.quantity} shares of {request.ticker}.",
                    transaction_id="tx_generated_123",
                    execution_price=cached_price
                )
            
            except ValueError as error:
                # Catch insufficient funds/price unavailable errors
                if self.db_session is not None:
                    self.db_session.rollback() # Undo any changes in case of error
                    
                return engine_pb2.TradeResponse(
                    success=False,
                    message=str(error),
                    transaction_id="",
                    execution_price=0.0
                )
            
                    
        # Implement Sell transaction type
        elif request.trade_type == engine_pb2.SELL:
            try:
                # Mock values
                user_cash = 10000.0
                user_held_shares = 50

                # Execute transaction
                new_balance, total_proceeds = engine.execute_sell_order(
                    redis_client=self.redis_client,
                    current_cash=user_cash,
                    held_shares=user_held_shares,
                    shares_to_sell=request.quantit,
                    ticker=request.ticker
                )
            
            except ValueError as error:
                # Catch errors for trying to sell too many shares
                return engine_pb2.TradeResponse(
                    success=False,
                    message=str(error),
                    transaction_id="",
                    execution_price=0.0
                )

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
