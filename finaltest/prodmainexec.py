from config import symbols_list
from prodmain import SymbolHedgingStrategy
from utils import connect_mt5
from final.fetch import fetch_price
import asyncio
from datetime import datetime


async def main():
    # Attempt to connect to MetaTrader 5
    connect = await connect_mt5()
    if not connect:
        print("Failed to connect to MetaTrader 5")
        return
    print("Connected to MetaTrader 5")

    # Initialize strategies for all symbols
    strategies = [SymbolHedgingStrategy(symbol) for symbol in symbols_list]

    while True:
        hours = datetime.now().hour
        if 0 <= hours < 19:
            print(f"Trading enabled at {datetime.now()}")

            # Fetch prices and execute strategies for each symbol
            for strategy in strategies:
                # Fetch start and current prices
                symbol_data = strategy.symbol_trade_data
                start_price = fetch_price(symbol_data, "start")
                current_price = fetch_price(symbol_data, "current")

                if start_price is None or current_price is None:
                    print(f"Failed to fetch prices for {symbol_data['symbol']}. Skipping strategy execution.")
                    continue

                # Execute the strategy with fetched prices
                await asyncio.to_thread(strategy.execute_strategy, start_price, current_price)
        else:
            print(f"Trading disabled at {datetime.now()}")

        # Wait for 1 second before repeating
        await asyncio.sleep(1)


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
