import talib

def technical_indicators(price_data):
    rsi = talib.RSI(price_data, timeperiod=14)
    macd, macdsignal, macdhist = talib.MACD(price_data)
    return rsi, macd, macdsignal
