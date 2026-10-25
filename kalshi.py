import requests

def get_kalshi_book(ticker="KXPRESIDENT2024"):
    """Fetch orderbook data from Kalshi's public API."""
    url = f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}/orderbook"
    try:
        response = requests.get(url, timeout=5)
        #if goes through turn into python dictionary, then safely looks for order book to return
        # the price levels, bids, asks w/o crashing   
        if response.status_code == 200:
            return response.json().get("orderbook", {})
    except Exception as e:
        print(f"Kalshi API error: {e}")
    return {}

#REST API 