from config import symbols_list
from state import state_manager
from trade_place import trade_place, close_trades_by_symbol
import MetaTrader5 as mt5


class SymbolHedgingStrategy:
    def __init__(self, symbol_data):
        self.symbol = symbol_data["symbol"]
        self.lot = symbol_data["lot"]
        self.pip = symbol_data["pip"]
        self.symbol_trade_data = symbol_data
        self.threshold = symbol_data["threshold"]

        # Initialize state for this symbol
        state_manager.initialize_symbol_state(self.symbol)
        state_manager.update_state(self.symbol,"trade_placed", False)

    def calculate_pip_difference(self, start, current):
        """
        Calculate pip difference, thresholds, and direction for a given price movement.
        """
        pip_difference =float(start - current)
        formatted_pips = float(pip_difference / self.pip)
        threshold_no = float(formatted_pips / self.threshold)

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
            "start": float(start),
            "current": float(current),
        }

    def check_existing_trades(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None:
            current_positions = 0  # No trades found
        else:
            current_positions = len(positions)  # Count active trades
        state_manager.update_state(self.symbol, "existing_trades", current_positions)

        print(f"🔍 Checked existing trades for {self.symbol}: {current_positions}")

    def check_and_place_hedge(self, data):
        """Place hedge trades if conditions are met."""
        thresholds = data["threshold_no"]
        trades_state = state_manager.get_state(self.symbol)
        hedge_trades_placed = trades_state.get("hedge_trades_placed", False)

        # ✅ Get updated trade count
        existing_trades = trades_state.get("existing_trades", 0)

        # ✅ Hedge is only placed if 2 or more trades exist AND hedge isn't already placed
        if existing_trades >= 2 and not hedge_trades_placed:
            if -0.7 <= thresholds <= -0.5:
                print(f"🔹 Negative hedge triggered for {self.symbol} at {data['current']}")
                state_manager.update_state(self.symbol, "hedge_trades_placed", True)
                trade_place({"symbol": self.symbol, "lot": self.lot}, "buy", hedge=True)

            elif 0.5 <= thresholds <= 0.7:
                print(f"🔹 Positive hedge triggered for {self.symbol} at {data['current']}")
                state_manager.update_state(self.symbol, "hedge_trades_placed", True)
                trade_place({"symbol": self.symbol, "lot": self.lot}, "sell", hedge=True)

    def check_and_close_hedge(self, data):
        """Close hedge trades when conditions are no longer valid."""
        thresholds = data["threshold_no"]
        trades_state = state_manager.get_state(self.symbol)
        hedge_trades_placed = trades_state.get("hedge_trades_placed", False)

        if hedge_trades_placed:
            if -0.5 > thresholds >= -0.7 and data["direction"] == "neutral":
                print(f"❌ Closing negative hedge trades for {self.symbol} at {data['current']}")
                close_trades_by_symbol(self.symbol_trade_data)
                state_manager.update_state(self.symbol, "hedge_trades_placed", False)

            elif 0.7 > thresholds > 0.5 and data["direction"] == "neutral":
                print(f"❌ Closing positive hedge trades for {self.symbol} at {data['current']}")
                close_trades_by_symbol(self.symbol_trade_data)
                state_manager.update_state(self.symbol, "hedge_trades_placed", False)

    def execute_strategy(self, start, current_price=None):
        """
        Execute the main strategy for this symbol.
        :param start: Starting price for calculation.
        :param current_price: Current market price (optional). If None, fetch from MT5.
        """
        if current_price is None:
            # Fetch price dynamically if not provided
            symbol_info = mt5.symbol_info_tick(self.symbol)
            if not symbol_info:
                print(f"Unable to fetch price for {self.symbol}")
                return
            current_price = symbol_info.bid

        # ✅ Update existing trades count before making decisions
        self.check_existing_trades()

        # Calculate pip difference and thresholds
        data = self.calculate_pip_difference(start, current_price)
        print(data)

        # Get symbol state
        trades_state = state_manager.get_state(self.symbol)
        trade_placed = trades_state.get("trade_placed", False)

        # Check and handle hedging logic
        self.check_and_place_hedge(data)
        self.check_and_close_hedge(data)

        # Regular trading thresholds
        thresholds = data["threshold_no"]
        if -1.5 <= thresholds <= -1:
            print(f"Threshold reached for {self.symbol} at price {current_price}")
            trade_place(self.symbol_trade_data, "buy", self.lot, False)
            state_manager.update_state(self.symbol, "trade_placed", True)
        if thresholds <= -2.5:
            print(f"Closing trades for {self.symbol} at price {current_price}")
            close_trades_by_symbol(self.symbol_trade_data)
            state_manager.update_state(self.symbol, "trade_placed", False)
        if 1 <= thresholds <= 1.5:
            print(f"Threshold reached for {self.symbol} at price {current_price}")
            trade_place(self.symbol_trade_data, "buy", self.lot, False)
            state_manager.update_state(self.symbol, "trade_placed", True)
        if 2<= thresholds <= 2.5:
            print(f"Closing trades for {self.symbol} at price {current_price}")
            close_trades_by_symbol(self.symbol_trade_data)
            state_manager.update_state(self.symbol, "trade_placed", False)


class MultiSymbolController:
    def __init__(self):
        self.strategies = [SymbolHedgingStrategy(symbol) for symbol in symbols_list]

    def execute_for_all_symbols(self, start_price, current_prices=None):
        """
        Execute strategies for all symbols.
        :param start_price: Starting price for calculation.
        :param current_prices: Dictionary of current prices for symbols (optional).
                               If None, fetch dynamically.
        """
        for strategy in self.strategies:
            current_price = (
                current_prices.get(strategy.symbol) if current_prices else None
            )
            strategy.execute_strategy(start_price, current_price)