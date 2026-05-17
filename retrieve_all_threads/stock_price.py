import requests
from langchain_core.tools import tool


@tool
def stock_price(symbol: str):
    """
    Fetch the latest stock price for a given ticker symbol
    (e.g. 'AAPL', 'TSLA', 'RELIANCE.NS') using Alpha Vantage.
    """
    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey=AIXAHRQNKU26V9P3"
    )
    r = requests.get(url)
    return r.json()
