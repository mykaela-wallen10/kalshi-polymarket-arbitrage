import asyncio
import random
import time
from typing import List, Dict, Tuple, Optional

#class setup 
class OrderBookLevel:
    """each instance is the quantity & price of all the same price sells for one event"""
    def __init__(self, price: float, quantity: float):
        #need to be object instance so self.
        self.price: float = price
        self.quantity: float = quantity

    def __repr__(self) -> str:
        return f"Level(price={self.price:.3f}, qty={self.quantity})"


class SimulatedVenue:
    """
    Simulates a Central Limit Order Book (CLOB) exchange (e.g., Kalshi or Polymarket)
    with simulated order book depth, taker fees, and network latency jitter.
    """
    #instance is basically the orderbook from either kalshi or polymarket for one specific event
    def __init__(self, name: str, taker_fee_pct: float, base_latency_ms: float):
        self.name: str = name
        self.taker_fee_pct: float = taker_fee_pct  
        self.base_latency_ms: float = base_latency_ms
        self.bids: List[OrderBookLevel] = []  # Sorted high -> low (Buyers)
        self.asks: List[OrderBookLevel] = []  # Sorted low -> high (Sellers)

    async def fetch_order_book(self) -> Tuple[List[OrderBookLevel], List[OrderBookLevel]]:
        """Simulates network request with latency jitter to fetch L2 depth."""
        # Add random jitter (5ms to 30ms delay) to simulate real network transmission
        #speed isnt consistant so make it random for most accuracy 
        jitter = random.uniform(0.005, 0.030)

        #pause execution to show actual wait for response time dont pause CPU
        await asyncio.sleep((self.base_latency_ms / 1000.0) + jitter)
        return self.bids, self.asks

    def set_mock_depth(self, bids: List[Tuple[float, float]], asks: List[Tuple[float, float]]):
        """Populates the order book with (price, quantity) pairs."""
        # Bids sorted descending (highest buyer first)
        #for loop while lambda sorting while populating 
        self.bids = [OrderBookLevel(p, q) for p, q in sorted(bids, key=lambda x: x[0], reverse=True)]
        # Asks sorted ascending (lowest seller first)
        self.asks = [OrderBookLevel(p, q) for p, q in sorted(asks, key=lambda x: x[0])]

        #buy high->low bc highest buyer matches w loest seller to make most money 



#actual engine part

class ArbitrageEngine:
    def __init__(self, venue_a: SimulatedVenue, venue_b: SimulatedVenue):
        self.venue_a = venue_a
        self.venue_b = venue_b

    @staticmethod
    def calculate_vwap_buy(asks: List[OrderBookLevel], target_quantity: float) -> Tuple[float, float]:
        """
        Calculates the Volume-Weighted Average Price (VWAP) for BUYING a target quantity.
        Goes through ask list until the wanted quantity is filled then finidng avg price for if a level doesnt fill wanted quantity.
        """
        accumulated_qty = 0.0
        total_cost = 0.0

        for level in asks:
            #how many i still need
            needed = target_quantity - accumulated_qty
            if needed <= 0:
                break
            
            # Take minimum of what's available at this level vs what we still need
            exec_qty = min(level.quantity, needed)
            total_cost += exec_qty * level.price
            accumulated_qty += exec_qty
            #go up to next price level and then check if still needed 


        #CHANCE THERES NOT ENOUGH DONT FORGET
        if accumulated_qty < target_quantity:
            # Insufficient liquidity in the book to fill the full size
            return 0.0, 0.0

        #avg price to get vwap
        vwap_price = total_cost / target_quantity
        return vwap_price, accumulated_qty

    @staticmethod
    def calculate_vwap_sell(bids: List[OrderBookLevel], target_quantity: float) -> Tuple[float, float]:
        """
        Calculates the Volume-Weighted Average Price (VWAP) for SELLING a target quantity.
        Goes through bids list until the wanted quantity is filled then finidng avg price for if a level doesnt fill wanted quantity.
        """
        accumulated_qty = 0.0
        total_revenue = 0.0

        for level in bids:
            needed = target_quantity - accumulated_qty
            if needed <= 0:
                break
            
            exec_qty = min(level.quantity, needed)
            total_revenue += exec_qty * level.price
            accumulated_qty += exec_qty

        if accumulated_qty < target_quantity:
            return 0.0, 0.0

        vwap_price = total_revenue / target_quantity
        return vwap_price, accumulated_qty

    #now actually do the math to find poss wins 
    async def evaluate_cross_venue_opportunity(self, target_size: float):
        """
        Asynchronously fetches books from both venues concurrently, checks for 
        fee-adjusted VWAP arbitrage, and outputs execution results.
        """
        start_time = time.perf_counter()

        # Execute concurrent async API fetches (simulating parallel REST/WebSocket calls)
        (bids_a, asks_a), (bids_b, asks_b) = await asyncio.gather(
            self.venue_a.fetch_order_book(),
            self.venue_b.fetch_order_book()
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        print(f"\n--- [Tick Evaluation | Latency: {latency_ms:.2f}ms] ---")

        # Poss Profit 1 -> Buy Venue A, Sell Venue B
        vwap_buy_a, fill_a = self.calculate_vwap_buy(asks_a, target_size)
        vwap_sell_b, fill_b = self.calculate_vwap_sell(bids_b, target_size)


        #check liquidity to see if itll fill
        if fill_a == target_size and fill_b == target_size:
            # Apply taker fees to get net effective execution costs
            #FEE ADJUST!!!!
            effective_buy_price = vwap_buy_a * (1.0 + self.venue_a.taker_fee_pct)
            effective_sell_price = vwap_sell_b * (1.0 - self.venue_b.taker_fee_pct)
            net_spread = effective_sell_price - effective_buy_price
            net_pnl = net_spread * target_size

            if net_spread > 0:
                print(f"FOUND WINN: Buy {self.venue_a.name} -> Sell {self.venue_b.name}")
                print(f"   Raw Buy VWAP: ${vwap_buy_a:.4f} | Fee-Adjusted Buy: ${effective_buy_price:.4f}")
                print(f"   Raw Sell VWAP: ${vwap_sell_b:.4f} | Fee-Adjusted Sell: ${effective_sell_price:.4f}")
                print(f"   Target Vol: {target_size} | Net Profit PnL: ${net_pnl:.4f}")
                return

        # Poss Profit 2 -> Buy Venue B, Sell Venue A
        vwap_buy_b, fill_b2 = self.calculate_vwap_buy(asks_b, target_size)
        vwap_sell_a, fill_a2 = self.calculate_vwap_sell(bids_a, target_size)

        #check liquidity to see if itll fill
        if fill_b2 == target_size and fill_a2 == target_size:
            #FEE ADJUST!!!!
            effective_buy_price = vwap_buy_b * (1.0 + self.venue_b.taker_fee_pct)
            effective_sell_price = vwap_sell_a * (1.0 - self.venue_a.taker_fee_pct)
            net_spread = effective_sell_price - effective_buy_price
            net_pnl = net_spread * target_size

            if net_spread > 0:
                print(f"FOUND WINN: Buy {self.venue_b.name} -> Sell {self.venue_a.name}")
                print(f"   Raw Buy VWAP: ${vwap_buy_b:.4f} | Fee-Adjusted Buy: ${effective_buy_price:.4f}")
                print(f"   Raw Sell VWAP: ${vwap_sell_a:.4f} | Fee-Adjusted Sell: ${effective_sell_price:.4f}")
                print(f"   Target Vol: {target_size} | Net Profit PnL: ${net_pnl:.4f}")
                return

        #else no trade!!!
        print("Cannot make a trade there is no executable arbitrage (fees, depth, or negative spread blocked trade).")


