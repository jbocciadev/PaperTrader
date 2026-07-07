# Launches the trading service server

import sys
import os

# Inject the app directory into the system's path for easier access
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
# Import the main function from the server app
from grpc_server import serve

# Run the function to initialize the server
if __name__ == "__main__":
    serve()
    