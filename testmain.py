# main.py
from logic_with_state import MultiSymbolController
from utils import connect_mt5
import asyncio

async def main():
    connect = await connect_mt5()
    start_price = 948000
    price_changes = [945000, 945600]
    if connect:
        controller = MultiSymbolController()
        controller.execute_for_all_symbols(start_price, price_changes)

if __name__ == "__main__":
  asyncio.run(main())