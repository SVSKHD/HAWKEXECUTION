# main.py
from logic_with_state import MultiSymbolController

if __name__ == "__main__":
    start_price = 1.0000
    price_changes = [1.0015, 1.0005, 0.9995, 0.9975, 0.9950, 0.9945]

    controller = MultiSymbolController()
    controller.execute_for_all_symbols(start_price, price_changes)