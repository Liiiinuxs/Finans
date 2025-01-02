import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import time

def fetch_stock_data(tickers):
    results = []
    for ticker in tickers:
        try:
            time.sleep(1)  # Fördröjning
            stock = yf.Ticker(ticker)
            hist_data = stock.history(period="1y")
            info = stock.info
            if hist_data.empty:
                continue

            # Beräkningar
            price_data = hist_data["Close"]
            returns = price_data.pct_change()
            annual_volatility = returns.std() * (252 ** 0.5) * 100
            growth = ((price_data.iloc[-1] / price_data.iloc[0]) - 1) * 100

            results.append({
                "Ticker": ticker,
                "Growth (%)": growth,
                "Volatility (%)": annual_volatility,
                "Dividend Yield (%)": info.get("dividendYield", 0) * 100,
                "P/E Ratio": info.get("forwardPE", None),
            })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    return pd.DataFrame(results)

def fetch_macro_indicators():
    api_key = "7LXFP3G15C6HVTT1"
    ts = TimeSeries(key=api_key, output_format='pandas')
    data, _ = ts.get_intraday(symbol='^GSPC', interval='1min', outputsize='compact')
    inflation = 2.5  # Dummyvärde
    interest_rate = 1.75  # Dummyvärde
    return inflation, interest_rate, data
