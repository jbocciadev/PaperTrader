# https://grpc.io/docs/languages/python/quickstart/
# https://medium.com/@dneprokos/sdet-exploring-grpc-testing-practical-examples-with-postman-c-and-python-clients-f1a29f91e3eb

import grpc
from app import engine_pb2_grpc
from app import engine_pb2

class TradingServiceServicer(engine_pb2_grpc.TradingServiceServicer):
    """
    Handles trade requests from the Web server.
    Inherits from the compiled gRPC base class
    """

    def ExecuteTrade(self, request, context):
        """ 
        Receives a TradeRequest message
        and executes the transaction requested.
        """
        # Temporary hardcoded response for test purposes
        return engine_pb2.TradeResponse(
            success=True,
            message="Trade processed successfully (stub)",
            transaction_id="tx_stub_999",
            execution_price=150.0
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
