from final.config import symbols_list
# from trade_place import trade_place, close_trades_by_symbol
# import MetaTrader5 as mt5

trades_status = {'existing_trades': 0, 'trades_placed':False, 'hedge_trades_placed':False,}


def calculate_pip_difference(symbol, start, current):
    data = {}
    pip_difference = start - current
    formatted_pips = pip_difference / symbol['pip']
    threshold_no = formatted_pips / symbol['threshold']

    # Determine direction based on threshold values
    if threshold_no > 1:
        direction = "down"  # Significant downward movement
    elif threshold_no < -1:
        direction = "up"  # Significant upward movement
    else:
        direction = "neutral"  # Within acceptable threshold range

    # Prepare output data
    data['pip_difference'] = round(pip_difference, 5)
    data['formatted_pips'] = round(formatted_pips, 2)
    data['threshold_no'] = round(threshold_no, 2)
    data['symbol'] = symbol['symbol']
    data['direction'] = direction
    data['start'] = start
    data['current'] = current
    return data


def check_existing_trades(symbol):
    symbol_name = symbol['symbol']
    lot = symbol['lot']
    positions = mt5.positions_get(symbol=symbol_name)
    if positions is not None:
        trades_status['existing_trades'] = len(positions)
    else:
        trades_status['existing_trades'] = 0


def check_and_hedge(symbol, symbol_data):
    check_existing_trades(symbol)
    thresholds = symbol_data['threshold_no']

    # Hedging logic for positive and negative thresholds
    if trades_status['existing_trades'] == 2:
        if -0.7 <= thresholds <= -0.5:
            print(f"negative hedging triggered for {symbol_data['symbol']} at price {symbol_data['current']}")
            trades_status['hedge_trades_placed'] = True
            # Example: trade_place(symbol_data['symbol'], "buy", symbol['lot'], hedge=True)
        elif 0.5 <= thresholds <= 0.7:
            print(f"positive hedging triggered for {symbol_data['symbol']} at price {symbol_data['current']}")
            trades_status['hedge_trades_placed'] = True
            # Example: trade_place(symbol_data['symbol'], "sell", symbol['lot'], hedge=True)


def check_hedging_closing_trades(symbol, symbol_data):
    symbol_name = symbol['symbol']
    direction = symbol_data['direction']
    thresholds = symbol_data['threshold_no']
    if trades_status['hedge_trades_placed']:
        if direction == "neutral" and -0.5 > thresholds >= -0.7:
            print(f"Closing negative hedging trades for {symbol_name}")
            close_trades_by_symbol(symbol)
            # Example: close_trades_by_symbol(symbol)
        elif direction == "neutral" and 0.7 > thresholds > 0.5:
            print(f"Closing positive hedging trades for {symbol_name}")
            close_trades_by_symbol(symbol)
            # Example: close_trades_by_symbol(symbol)


def check_thresholds_and_execute(symbol_data, start, current):
    data = calculate_pip_difference(symbol_data, start, current)
    threshold = data['threshold_no']
    print(data)
    # check_and_hedge(symbol_data, data)

    if -1.5 <= threshold <= -1:
        print(f"Threshold reached for {data['symbol']} at price {current}")
        # trade_place(symbol, "buy", symbol_data['lot'], False)
    if -2.5 <= threshold <= -2:
        print("=" * 50)
        # close_trades_by_symbol(symbol_data)
        print(f"2nd threshold reached for {data['symbol']} at price {current}")
        print("=" * 50)
    if 1 <= threshold < 1.5:

        print(f"Threshold reached for {data['symbol']} at price {current}")
    if 2 < threshold <= 2.5:
        print("=" * 50)
        print(f"2nd threshold reached for {data['symbol']} at price {current}")
        print("=" * 50)


# Example data
start_price = 1.0000
prices = [1.0015, 1.0020, 1.0025, 1.0030, 1.0045, 1.0060]
negative_prices = [0.9985, 0.9970, 0.9965, 0.99925 , 0.9960, 0.9945, 0.9930]

for symbol in symbols_list:
    for price in negative_prices:
        check_thresholds_and_execute(symbol, start_price, price)
