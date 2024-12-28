from config import symbols_list
from trade_place import trade_place, close_trades_by_symbol


def calculate_pip_difference(symbol, start, current):
    data = {}
    pip_difference = start - current
    formatted_pips = pip_difference / symbol['pip']
    threshold_no = formatted_pips / symbol['threshold']
    data['pip_difference'] = round(pip_difference, 5)
    data['formatted_pips'] = round(formatted_pips, 2)
    data['threshold_no'] = round(threshold_no, 2)
    data['symbol'] = symbol['symbol']
    return data


def check_thresholds_and_execute(symbol_data, start, current):
    data = calculate_pip_difference(symbol_data, start, current)
    threshold = data['threshold_no']

    if -1.5 <= threshold <= -1:
        print(f"Threshold reached for {data['symbol']} at price {current}")
        trade_place(symbol, "buy", symbol_data['lot'], False)
    elif -2.5 <= threshold <= -2:
        print("=" * 50)
        close_trades_by_symbol(symbol_data)
        print(f"2nd threshold reached for {data['symbol']} at price {current}")
        print("=" * 50)
    if 1 <= threshold < 1.5:

        print(f"Threshold reached for {data['symbol']} at price {current}")
    elif 2 < threshold <= 2.5:
        print("=" * 50)
        print(f"2nd threshold reached for {data['symbol']} at price {current}")
        print("=" * 50)


# Example data
start_price = 1.0000
prices = [1.0015, 1.0020, 1.0025, 1.0030, 1.0045, 1.0060]
negative_prices = [0.9985, 0.9970, 0.9965, 0.9960, 0.9945, 0.9930]

for symbol in symbols_list:
    for price in negative_prices:
        check_thresholds_and_execute(symbol, start_price, price)
