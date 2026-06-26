# Reference: https://fastapi.tiangolo.com/advanced/testing-websockets/

import pytest
from fastapi.testclient import TestClient

# Import objects from main app file
from main import app, redis_client

client = TestClient(app)

class MockRedis:
    """
    Dummy database class to produce mock requests.
    """

    def get(self, key):
        # Pretend stock price in the cache
        return "150.20"
    
def test_websocket_price_stream_happy_path(monkeypatch):
    # Replace redis db connection with fake one using pytest.monkeypatch
    # Ref: https://docs.pytest.org/en/stable/reference/reference.html#pytest.MonkeyPatch.setattr
    fake_redis = MockRedis()
    monkeypatch.setattr("main.redis_client", fake_redis)

    # Open mock connection from client
    with client.websocket_connect("ws/prices/AAPL") as websocket:

        # Capture information sent
        data_packet = websocket.receive_json()

        assert data_packet["ticker"] == "AAPL"
        assert data_packet["price"] == "150.20"
        assert data_packet["timestamp"] == "Live"