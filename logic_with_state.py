from config import symbols_list
from state import state_manager
from trade_place import trade_place, close_trades_by_symbol
import MetaTrader5 as mt5


class SymbolHedgingStrategy:
    def __init__(self, symbol_data):
        self.symbol = symbol_data["symbol"]
        self.symbol_trade_data = symbol_data
        self.lot = symbol_data["lot"]
        self.pip = symbol_data["pip"]
        self.threshold = symbol_data["threshold"]

        # Initialize state for this symbol
        state_manager.initialize_symbol_state(self.symbol)

    def calculate_pip_difference(self, start, current):
        """
        Calculate pip difference, thresholds, and direction for a given price movement.
        """
        pip_difference = start - current
        formatted_pips = pip_difference / self.pip
        threshold_no = formatted_pips / self.threshold

        direction = "neutral"
        if threshold_no > 1:
            direction = "down"
        elif threshold_no < -1:
            direction = "up"

        return {
            "symbol": self.symbol,
            "pip_difference": round(pip_difference, 5),
            "formatted_pips": round(formatted_pips, 2),
            "threshold_no": round(threshold_no, 2),
            "direction": direction,
            "start": start,
            "current": current,
        }

    def check_existing_trades(self):
        """Check the current number of trades for this symbol."""
        current_positions = 0  # Replace with MT5 API call
        postions = mt5.positions_get(symbol=self.symbol)
        if postions is not None:
            current_positions = len(postions)
        state_manager.update_state(self.symbol, "existing_trades", current_positions)

    def check_and_place_hedge(self, data):
        """Place hedge trades if thresholds are met."""
        thresholds = data["threshold_no"]
        trades_state = state_manager.get_state(self.symbol)

        # Check if hedging conditions are met
        if trades_state["existing_trades"] == 2:
            if -0.7 <= thresholds <= -0.5 and not trades_state["hedge_trades_placed"]:
                print(f"Negative hedging triggered for {self.symbol} at price {data['current']}")
                state_manager.update_state(self.symbol, "hedge_trades_placed", True)
                trade_place({"symbol": self.symbol, "lot": self.lot}, "buy", hedge=True)

            elif 0.5 <= thresholds <= 0.7 and not trades_state["hedge_trades_placed"]:
                print(f"Positive hedging triggered for {self.symbol} at price {data['current']}")
                state_manager.update_state(self.symbol, "hedge_trades_placed", True)
                trade_place({"symbol": self.symbol, "lot": self.lot}, "sell", hedge=True)

    def check_and_close_hedge(self, data):
        """Close hedge trades when conditions are no longer valid."""
        thresholds = data["threshold_no"]
        trades_state = state_manager.get_state(self.symbol)

        if trades_state["hedge_trades_placed"]:
            if data["direction"] == "neutral" and -0.5 > thresholds >= -0.7:
                print(f"Closing negative hedge trades for {self.symbol}")
                state_manager.update_state(self.symbol, "hedge_trades_placed", False)
                close_trades_by_symbol({"symbol": self.symbol})

            elif data["direction"] == "neutral" and 0.7 > thresholds > 0.5:
                print(f"Closing positive hedge trades for {self.symbol}")
                state_manager.update_state(self.symbol, "hedge_trades_placed", False)
                close_trades_by_symbol({"symbol": self.symbol})

    def execute_strategy(self, start, current):
        """Execute the main strategy for this symbol."""
        data = self.calculate_pip_difference(start, current)
        print(data)

        # Check and handle hedging logic
        self.check_and_place_hedge(data)
        self.check_and_close_hedge(data)

        # Regular trading thresholds
        thresholds = data["threshold_no"]
        if -1.5 <= thresholds <= -1:
            print(f"Threshold reached for {self.symbol} at price {current}")
            trade_place(self.symbol_trade_data, "buy", self.lot, False)
        elif -2 >= thresholds >= -2.5:
            print(f"Closing trades for {self.symbol} at price {current}")
            close_trades_by_symbol(self.symbol_trade_data)
        elif 1 <= thresholds <= 1.5:
            print(f"Threshold reached for {self.symbol} at price {current}")
            trade_place(self.symbol_trade_data,"sell", self.lot, False)

class MultiSymbolController:
    def __init__(self):
        self.strategies = [SymbolHedgingStrategy(symbol) for symbol in symbols_list]

    def execute_for_all_symbols(self, start_price, price_changes):
        for strategy in self.strategies:
            for current_price in price_changes:
                strategy.execute_strategy(start_price, current_price)