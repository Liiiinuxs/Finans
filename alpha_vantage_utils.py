import requests

# Din Alpha Vantage API-nyckel
API_KEY = "7LXFP3G15C6HVTT1"

def get_trending_stocks(limit=10):
    """
    Hämta trendande aktier från Alpha Vantage API.
    """
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
                "symbol": stock_info["01. symbol"],
                "price": float(stock_info["05. price"]),
                "change_percent": stock_info["10. change percent"]
            })

    # Begränsa resultat till det angivna antalet
    return recommended_stocks[:limit]
