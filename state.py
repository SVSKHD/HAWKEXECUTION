# state.py

class TradingState:
    def __init__(self):
        self.state = {}

    def initialize_symbol_state(self, symbol):
        if symbol not in self.state:
            self.state[symbol] = {
                "existing_trades": 0,
                "trades_placed": False,
                "hedge_trades_placed": False,
            }

    def update_state(self, symbol, key, value):
        if symbol in self.state:
            self.state[symbol][key] = value

    def get_state(self, symbol):
        return self.state.get(symbol, None)


# Initialize state
state_manager = TradingState()