from kalshi import get_kalshi_book
from polymarket import get_polymarket_book

def check_arbitrage(kalshi_ask, poly_bid, fee=0.01):
    """Calculates spread after trading fees."""
    effective_buy = kalshi_ask * (1 + fee)
    effective_sell = poly_bid * (1 - fee)
    spread = effective_sell - effective_buy

    if spread > 0:
        print(f"🔥 ARBITRAGE OPPORTUNITY FOUND!")
        print(f"   Buy Kalshi @ {kalshi_ask:.3f} | Sell Polymarket @ {poly_bid:.3f}")
        print(f"   Net Profit Spread: {spread:.4f}")
    else:
        print(f"No Arb: Spread is {spread:.4f}")

def main():
    print("--- Fetching Market Data ---")
    
    # Test Kalshi endpoint
    kalshi_book = get_kalshi_book()
    print("Kalshi response received!")

    # Simulated test run
    print("\n--- Running Arbitrage Check (Sample Prices) ---")
    check_arbitrage(kalshi_ask=0.48, poly_bid=0.52)

if __name__ == "__main__":
    main()