import requests



API_KEY = "" # Change for actual key, get environment vars to load
SYMBOL = "AAPL"

url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={SYMBOL}&apikey={API_KEY}"

# response = requests.get(url, verify=False) # unsafe, for testing purposes only.
response = requests.get(url)
data = response.json()

print(data)
