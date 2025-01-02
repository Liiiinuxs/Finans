import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time

# Alpha Vantage API-konfiguration
API_KEY = "7LXFP3G15C6HVTT1"

# Funktion för att hämta dynamiska rekommenderade aktier
def get_recommended_stocks(limit=10):
    url = "https://www.alphavantage.co/query"
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "NFLX", "ADBE", "INTC"]
    recommended_stocks = []

    for symbol in symbols:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": API_KEY
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            continue

        data = response.json()
        if "Global Quote" in data:
            stock_info = data["Global Quote"]
            recommended_stocks.append({
                "Ticker": stock_info["01. symbol"],
                "Price": float(stock_info["05. price"]),
                "Change Percent": stock_info["10. change percent"]
            })

    return pd.DataFrame(recommended_stocks[:limit])

# Funktion för att lägga till suffix om nödvändigt
def apply_market_suffix(tickers, default_suffix=".ST"):
    processed_tickers = []
    for ticker in tickers:
        if "." not in ticker:  # Om det inte redan finns ett suffix, anta amerikansk aktie
            processed_tickers.append(ticker)
        else:  # Om suffix finns, behåll det
            processed_tickers.append(ticker)
    return processed_tickers

# Funktion för att hämta data från Yahoo Finance
def fetch_from_yahoo(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period="1y")
        info = stock.info

        if hist_data.empty:
            st.warning(f"Yahoo Finance returnerade ingen data för {ticker}.")
            return None, None

        return hist_data, info
    except Exception as e:
        st.error(f"Fel vid hämtning från Yahoo Finance för {ticker}: {e}")
        return None, None

# Funktion för att hämta och analysera data
def fetch_stock_data(tickers):
    results = []
    for ticker in tickers:
        try:
            time.sleep(1)  # Fördröjning för att undvika rate limiting
            hist_data, info = fetch_from_yahoo(ticker)
            if hist_data is None or info is None:
                continue
            
            if "Close" in hist_data.columns:
                price_data = hist_data["Close"]
            else:
                st.warning(f"Ingen användbar kolumn hittades för {ticker}. Hoppar över.")
                continue

            returns = price_data.pct_change()
            annual_volatility = returns.std() * (252 ** 0.5) * 100
            growth = ((price_data.iloc[-1] / price_data.iloc[0]) - 1) * 100

            dividend_yield = info.get("dividendYield", 0) * 100
            pe_ratio = info.get("forwardPE", None)

            results.append({
                "Ticker": ticker,
                "Growth (%)": growth,
                "Volatility (%)": annual_volatility,
                "Dividend Yield (%)": dividend_yield,
                "P/E Ratio": pe_ratio,
            })
        except Exception as e:
            st.error(f"Fel vid analys för {ticker}: {e}")
    return pd.DataFrame(results)

# Poängsättningsmetod
def calculate_scores(data):
    data["Growth Score"] = data["Growth (%)"] / data["Growth (%)"].max() * 100
    data["Volatility Score"] = (1 - (data["Volatility (%)"] / data["Volatility (%)"].max())) * 100
    data["Dividend Score"] = data["Dividend Yield (%)"] / data["Dividend Yield (%)"].max() * 100
    data["P/E Score"] = (1 - (data["P/E Ratio"] / data["P/E Ratio"].max())) * 100

    data["Total Score"] = (
        data["Growth Score"] * 0.4 +
        data["Volatility Score"] * 0.3 +
        data["Dividend Score"] * 0.2 +
        data["P/E Score"] * 0.1
    )

    return data

# Streamlit-applikation
st.set_page_config(page_title="Linus Capital Insights", layout="wide")

st.title("💼 Linus Capital Insights")

# Input för aktier
tickers_input = st.text_input("🔎 Ange aktiesymboler (kommaseparerade)", "AAPL, MSFT, KO, VOLV-B.ST, ERIC-B.ST")
tickers = [ticker.strip() for ticker in tickers_input.split(",")]

tickers = apply_market_suffix(tickers)

if st.button("Analysera"):
    data = fetch_stock_data(tickers)
    if not data.empty:
        data = calculate_scores(data)
        st.subheader("Dina Aktier")
        st.dataframe(data)

        st.subheader("📈 Rekommenderade Aktier")
        recommended_data = get_recommended_stocks()
        if not recommended_data.empty:
            st.dataframe(recommended_data)
        else:
            st.warning("Kunde inte hämta rekommenderade aktier.")
