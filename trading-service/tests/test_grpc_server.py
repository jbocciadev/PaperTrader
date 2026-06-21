# https://grpc.github.io/grpc/python/grpc_testing.html

import pytest
import grpc
import grpc_testing
from app import engine_pb2
from app import engine_pb2_grpc

from app.grpc_server import TradingServiceServicer


# https://docs.pytest.org/en/6.2.x/fixture.html
@pytest.fixture
def grpc_channel():
    # Source descriptor from engine_pb2
    service_description = engine_pb2.DESCRIPTOR.services_by_name['TradingService']
    
    descriptors_to_servicers = {service_description: TradingServiceServicer()}

    # Run mock server and return it
    test_server = grpc_testing.server_from_dictionary(
        descriptors_to_servicers, 
        grpc_testing.strict_real_time()
    )
    return test_server

def test_successful_grpc_buy(grpc_channel):
    # Build strictly-typed message as per .proto file definitions
    request = engine_pb2.TradeRequest(
        user_id="user_test_123",
        ticker="AAPL",
        quantity=10,
        trade_type=engine_pb2.BUY
    )

    # retrieve descriptor from engine
    method_descriptor = engine_pb2.DESCRIPTOR.services_by_name['TradingService']

    # Send request to mock server
    rpc = grpc_channel.invoke_unary_unary(
        method_descriptor,
        invocation_metadata=None,
        request=request,
        deadline=None,
    )

    # Unpack the response tuple in variables for later use
    response, _, code, _ = rpc.termination()

    # Assertions to check if call returned a success message
    assert code == grpc.StatusCode.OK
    assert response.success is True
    assert "successfully" in response.message.lower()
    assert response.execution_price > 0.0
    assert len(response.transaction_id) > 0
