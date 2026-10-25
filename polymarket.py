import requests

def get_polymarket_book(condition_id="0x123456789"):
    """Fetch orderbook data from Polymarket's public CLOB API."""
    url = f"https://clob.polymarket.com/book?token_id={condition_id}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            #structure just gives you the orderbook dictionary directly 
            return response.json()
    except Exception as e:
        print(f"Polymarket API error: {e}")
    return {}

#clob API