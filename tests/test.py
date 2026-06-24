# import requests
# import os
# import sys
# import time
# from pathlib import Path


# myPath = Path(__file__).resolve()
# BASE_DIR = myPath.parent.parent
# if str(BASE_DIR) not in sys.path:
#     sys.path.insert(0, str(BASE_DIR))

# print ("base path: " , BASE_DIR)
# import config



# API_KEY = config.API_KEY # Change for actual key, get environment vars to load
# print(config.TICKERS)

# def vantUrl(ticker):
#     return f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={API_KEY}"

# SYMBOL = ["AAPL"]

# # url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={SYMBOL}&apikey={API_KEY}"

# tickers = []
# for ticker, name in config.TICKERS.items():
#     tickers.append(ticker)

# url = vantUrl(SYMBOL[0])

# response = requests.get(url, verify=False) # unsafe, for testing purposes only.
# # response = requests.get(url)
# data = response.json()

# for ticker in tickers:
#     url = vantUrl(ticker)
#     response = requests.get(url, verify=False)
#     print(response.json())
#     time.sleep(1)

# print(data)


# # NEED TO CHANGE ALPHA VANTAGE FOR FINNHUB