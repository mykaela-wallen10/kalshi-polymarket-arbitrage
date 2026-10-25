import asyncio
from arbitrage_engine import SimulatedVenue, ArbitrageEngine

async def main():
    print("ENGINE TESTING")

    #small order on top 
    print("\n" + "="*58)
    print("SCENARIO 1: Small Order (50 contracts) - Top-of-Book Fill")
    print("="*58)

    kalshi_1 = SimulatedVenue(name="Kalshi", taker_fee_pct=0.01, base_latency_ms=15.0)
    poly_1 = SimulatedVenue(name="Polymarket", taker_fee_pct=0.005, base_latency_ms=10.0)

    # Kalshi Asks: Cheapest is $0.48
    kalshi_1.set_mock_depth(
        bids=[(0.46, 200), (0.45, 500), (0.43, 1000)],
        asks=[(0.48, 150), (0.50, 300), (0.52, 600), (0.55, 1200)]
    )

    # Polymarket Bids: Highest buyer is $0.53
    poly_1.set_mock_depth(
        bids=[(0.53, 200), (0.51, 400), (0.49, 800), (0.47, 1500)],
        asks=[(0.55, 300), (0.57, 500), (0.60, 1000)]
    )

    engine_1 = ArbitrageEngine(kalshi_1, poly_1)
    await engine_1.evaluate_cross_venue_opportunity(target_size=50)


    #go through bigger list 
    print("\n" + "="*58)
    print("SCENARIO 2: Medium Order (400 contracts) - Multi-Level Slippage")
    print("="*58)

    kalshi_2 = SimulatedVenue(name="Kalshi", taker_fee_pct=0.01, base_latency_ms=18.0)
    poly_2 = SimulatedVenue(name="Polymarket", taker_fee_pct=0.005, base_latency_ms=12.0)

    # Need 400 contracts: Kalshi Asks will walk 100 @ 0.47 + 200 @ 0.49 + 100 @ 0.52
    kalshi_2.set_mock_depth(
        bids=[(0.45, 300), (0.44, 600), (0.42, 1200)],
        asks=[(0.47, 100), (0.49, 200), (0.52, 400), (0.56, 800), (0.60, 1500)]
    )

    # Need 400 contracts: Poly Bids will walk 250 @ 0.56 + 150 @ 0.54
    poly_2.set_mock_depth(
        bids=[(0.56, 250), (0.54, 300), (0.51, 500), (0.48, 1000)],
        asks=[(0.58, 200), (0.61, 500), (0.65, 900)]
    )

    engine_2 = ArbitrageEngine(kalshi_2, poly_2)
    await engine_2.evaluate_cross_venue_opportunity(target_size=400)



    #bigger slipping through level orders ->deep test 
    print("\n" + "="*58)
    print("SCENARIO 3: Institutional Order (1,000 contracts) - Deep Book Sweep")
    print("="*58)

    kalshi_3 = SimulatedVenue(name="Kalshi", taker_fee_pct=0.012, base_latency_ms=22.0)
    poly_3 = SimulatedVenue(name="Polymarket", taker_fee_pct=0.008, base_latency_ms=14.0)

    # Large sweep forcing execution across 4 distinct price levels
    kalshi_3.set_mock_depth(
        bids=[(0.40, 500), (0.38, 1000)],
        asks=[(0.42, 200), (0.45, 300), (0.49, 300), (0.54, 500), (0.60, 1000)]
    )

    poly_3.set_mock_depth(
        bids=[(0.58, 300), (0.55, 300), (0.52, 400), (0.48, 800)],
        asks=[(0.60, 400), (0.63, 800)]
    )

    engine_3 = ArbitrageEngine(kalshi_3, poly_3)
    await engine_3.evaluate_cross_venue_opportunity(target_size=1000)


    #NO TRADE TEST DONT FORGETTTT!!!
    print("\n" + "="*58)
    print("SCENARIO 4: Unprofitable Spread (Fees & Slippage Erase Profit)")
    print("="*58)

    kalshi_4 = SimulatedVenue(name="Kalshi", taker_fee_pct=0.015, base_latency_ms=15.0)
    poly_4 = SimulatedVenue(name="Polymarket", taker_fee_pct=0.01, base_latency_ms=10.0)

    # Raw spread looks close ($0.50 vs $0.51), but after fees it's negative PnL!
    kalshi_4.set_mock_depth(
        bids=[(0.48, 300), (0.46, 500)],
        asks=[(0.50, 200), (0.53, 400)]
    )

    poly_4.set_mock_depth(
        bids=[(0.51, 150), (0.49, 300)],
        asks=[(0.53, 200), (0.56, 500)]
    )

    engine_4 = ArbitrageEngine(kalshi_4, poly_4)
    await engine_4.evaluate_cross_venue_opportunity(target_size=200)

if __name__ == "__main__":
    asyncio.run(main())